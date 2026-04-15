# 文件路径: main.py
from core.memory_system import MultiLevelMemory

def mock_agent_response(user_input):
    # 模拟一个简单的模型回复
    return f"我听到了，你说的是: {user_input}"

def main():
    # 实例化你的记忆系统
    mem_sys = MultiLevelMemory()

    print("=== Agent 多级记忆测试启动 ===")

    # 模拟 5 轮对话，观察第 3 轮时是否触发压缩
    for i in range(1, 6):
        user_in = f"这是我的第 {i} 条消息"
        print(f"\n--- 第 {i} 轮交互 ---")

        # 1. 模拟 Agent 获取记忆
        brain_context = mem_sys.get_all_context()
        print(f"Agent 当前检索到的记忆：\n{brain_context}")

        # 2. 生成回复
        response = mock_agent_response(user_in)
        print(f"Agent 回复: {response}")

        # 3. 更新记忆（这里会触发你刚才写的压缩代码）
        mem_sys.update_and_compress(user_in, response)

if __name__ == "__main__":
    main()