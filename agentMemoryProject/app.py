from flask import Flask, render_template, jsonify, request
import os
import sys
import json
from dotenv import load_dotenv

# 先加载 .env 文件
load_dotenv()

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接导入MemoryManager
from core.memory_manager import MemoryManager

# 创建memory_manager实例，使用默认存储目录
memory_manager = MemoryManager()

# 导入AgentEngine
from core.agent_engine import AgentEngine

app = Flask(__name__)

# 初始化代理引擎
agent_engine = AgentEngine(memory_manager=memory_manager)

# 其余代码保持不变...


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/memory/working', methods=['GET'])
def get_working_memory():
    """获取工作记忆"""
    try:
        return jsonify({
            'success': True,
            'data': memory_manager.working_memory
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/memory/long-term', methods=['GET'])
def get_long_term_memory():
    """获取长期记忆"""
    try:
        user_id = request.args.get('user_id', 'hust_student_2026')
        query = request.args.get('query', '')
        result = memory_manager.long_term_memory.search(query, filters={'user_id': user_id})

        # 处理搜索结果格式
        if isinstance(result, dict) and 'results' in result:
            memories = result['results']
        else:
            memories = result

        return jsonify({
            'success': True,
            'data': memories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/memory/semantic', methods=['GET'])
def get_semantic_memory():
    """获取语义记忆"""
    try:
        user_id = request.args.get('user_id', 'hust_student_2026')
        concept = request.args.get('concept', '')
        memories = memory_manager.get_semantic_memory(user_id, concept)

        return jsonify({
            'success': True,
            'data': memories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/memory/count', methods=['GET'])
def get_memory_count():
    """获取记忆数量"""
    try:
        user_id = request.args.get('user_id', 'hust_student_2026')
        count = memory_manager.get_memory_count(user_id)

        return jsonify({
            'success': True,
            'data': count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理聊天请求"""
    try:
        data = request.json
        user_id = data.get('user_id', 'hust_student_2026')
        user_input = data.get('input', '')

        if not user_input:
            return jsonify({
                'success': False,
                'error': 'Input is required'
            })

        # 执行对话
        response, token_usage = agent_engine.run(user_id=user_id, user_input=user_input)

        return jsonify({
            'success': True,
            'response': response,
            'token_usage': token_usage
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    """手动触发清理"""
    try:
        result = memory_manager.manual_cleanup()
        return jsonify({
            'success': True,
            'message': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # 创建templates目录
    if not os.path.exists('templates'):
        os.makedirs('templates')

    # 创建静态文件目录
    if not os.path.exists('static'):
        os.makedirs('static')

    app.run(debug=True, host='0.0.0.0', port=5000)