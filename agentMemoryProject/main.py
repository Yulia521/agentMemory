import os
import time
from dotenv import load_dotenv
from core.storage_manager import MemoryManager
from core.agent_engine import AgentEngine
from utils.monitor import PerformanceMonitor

# 1. 加载 .env 配置文件
load_dotenv()

def main():
    # 2. 初始化性能监控器
    monitor = PerformanceMonitor()

    print("正在连接云端大模型并初始化 Mem0 记忆系统...")
    try:
        # 3. 创建默认的MemoryManager实例
        memory_manager = MemoryManager()
        # 4. 创建AgentEngine实例
        agent = AgentEngine(memory_manager=memory_manager)
    except Exception as e:
        print(f"初始化失败，请检查 .env 配置或网络连接: {e}")
        return

    # 为当前实验设置一个固定的用户 ID (对应任务书中的“跨会话”测试)
    user_id = "hust_student_2026"

    print("\n" + "="*30)
    print("智能体多级记忆系统已上线")
    print(f"当前模型: {os.getenv('MODEL_NAME')}")
    print("输入 'exit' 退出程序")
    print("="*30)

    while True:
        user_input = input("\n用户: ").strip()

        if not user_input:
            continue
        if user_input.lower() in ['exit', 'quit', '退出']:
            print("正在保存记忆并退出系统...")
            break

        # --- 执行端到端链路并统计指标 ---

        # 记录开始时间
        monitor.start_timer()

        try:
            # 执行核心推理过程
            response, token_usage = agent.run(user_id=user_id, user_input=user_input, monitor=monitor)

            # 记录结束时间并获取延迟
            latency = monitor.end_timer()

            print(f"Agent: {response}")

            # 4. 打印任务书要求的硬性指标
            monitor.log_metrics(latency=latency, tokens=token_usage)

        except Exception as e:
            print(f"对话发生错误: {e}")
            print("提示：请检查 API Key 余额或网络环境。")

if __name__ == "__main__":
    main()