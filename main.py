from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory

def main():
    print("=== 三级记忆智能体启动 ===")

    # 初始化三层记忆
    working = WorkingMemory()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()

    # 测试工作记忆
    working.add("user", "我想订明天的餐厅")
    working.add("assistant", "请问你喜欢什么菜系？")
    print("\n【工作记忆】")
    for msg in working.get_context():
        print(f"{msg['role']}: {msg['content']}")

    # 测试情景记忆
    episodic.add_event("用户发起订餐请求")
    episodic.add_event("助手询问用户偏好")
    print("\n【情景记忆】")
    for e in episodic.get_recent():
        print(f"- {e}")

    # 测试语义记忆
    semantic.put("user_favorite", "喜欢川菜，预算150元")
    print("\n【语义记忆】")
    print(semantic.get("user_favorite"))

    print("\n=== 三级记忆系统测试完成 ===")

if __name__ == "__main__":
    main()