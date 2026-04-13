from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from retriever.kv_retriever import KvRetriever
from retriever.keyword_retriever import KeywordRetriever

def main():
    print("=== 三级记忆智能体启动 ===")

    # 初始化三层记忆
    working = WorkingMemory()
    episodic = EpisodicMemory()
    semantic = SemanticMemory()

    # 测试工作记忆
    working.add("user", "我想订明天的餐厅")
    working.add("assistant", "请问你喜欢什么菜系？")
    # print("\n【工作记忆】")
    # for msg in working.get_context():
    #     print(f"{msg['role']}: {msg['content']}")

    # 测试情景记忆
    episodic.add_event("用户发起订餐请求")
    episodic.add_event("助手询问用户偏好")
    # print("\n【情景记忆】")
    # for e in episodic.get_recent():
    #     print(f"- {e}")

    # 测试语义记忆
    semantic.put("user_favorite", "喜欢川菜，预算150元")
    semantic.put("user_hate", "不吃香菜，不吃太辣")
    semantic.put("restaurant_type", "偏好安静环境的餐厅")
    semantic.put("location", "希望在朝阳区")
    # print("\n【语义记忆】")
    # print(semantic.get("user_favorite"))

    # ======================
    # 新增：检索模块测试
    # ======================
    retriever = KvRetriever(semantic)
    search_result = retriever.search("user_favorite")
    print("\n【检索结果】", search_result)

    # ==============================
    # 测试：关键词检索（更智能）
    # ==============================
    kw_retriever = KeywordRetriever(semantic)
    kw_result = kw_retriever.search("川菜")  # 搜“川菜”
    print("\n【关键词检索结果】", kw_result)

    print("\n=== 三级记忆系统 + 检索模块 测试完成 ===")

if __name__ == "__main__":
    main()