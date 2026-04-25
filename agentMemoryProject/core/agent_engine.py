# 修改 core/agent_engine.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class AgentEngine:
    def __init__(self, memory_manager=None):
        # 从环境变量读取配置
        model = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-7B-Instruct")

        # 配置LLM
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7
        )
        if memory_manager:
            self.memory = memory_manager
        else:
            # 直接创建默认的MemoryManager实例
            from core.memory_manager import MemoryManager
            self.memory = MemoryManager()
        self.prompt = ChatPromptTemplate.from_template("""
        你是一个具备分层式记忆架构的智能体。根据以下背景信息回答问题。

        {history}

        用户: {input}
        """)

    def run(self, user_id, user_input, monitor=None):
        if monitor:
            monitor.start_stage("记忆检索")
        history = self.memory.get_context(user_id, user_input)

        if monitor:
            monitor.start_stage("大模型推理")
        chain = self.prompt | self.llm
        response = chain.invoke({"history": history, "input": user_input})

        if monitor:
            monitor.start_stage("记忆保存")
        self.memory.save(user_id, user_input, response.content)

        # 提取 token 使用情况
        token_usage = 0
        try:
            # 尝试从响应对象中获取token使用情况
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                token_usage = response.usage_metadata.get('total_tokens', 0)
            elif hasattr(response, 'llm_output') and response.llm_output:
                token_usage = response.llm_output.get('token_usage', {}).get('total_tokens', 0)
        except Exception as e:
            print(f"获取token使用情况失败: {e}")

        # 获取并显示记忆条数
        memory_count = self.memory.get_memory_count(user_id)
        print(f"  > [记忆状态] 当前存储记忆条数: {memory_count}")

        return response.content, token_usage