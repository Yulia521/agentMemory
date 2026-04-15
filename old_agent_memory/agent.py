from memory.working import WorkingMemory
from memory.episodic import EpisodicMemory
from memory.semantic import SemanticMemory
from retriever.kv_retriever import KvRetriever
from retriever.keyword_retriever import KeywordRetriever
from model import SimpleLLM  # 大模型

class Agent:
    def __init__(self):
        # 三层记忆
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()

        # 两个检索器
        self.kv_retriever = KvRetriever(self.semantic_memory)
        self.kw_retriever = KeywordRetriever(self.semantic_memory)

        # 大模型大脑
        self.llm = SimpleLLM()

        print("✅ 智能体初始化完成：记忆 + 检索 + 大模型")

    def chat(self, user_input):
        """用户聊天入口"""
        print("\n==============================")
        print(f"用户输入：{user_input}")

        # 1. 存入工作记忆
        self.working_memory.add("user", user_input)

        # 2. 记录事件
        self.episodic_memory.add_event(f"用户：{user_input}")

        # 3. 检索相关记忆
        retrieved = self.kw_retriever.search(user_input)
        print(f"🔍 检索到记忆：{retrieved}")

        # 4. 大模型生成回答
        reply = self.generate_reply(user_input, retrieved)

        # 5. 把AI回复也存入记忆
        self.working_memory.add("assistant", reply)

        return reply

    def generate_reply(self, user_input, retrieved_memories):
        """调用大模型生成真实回答"""
        prompt = f"用户问题：{user_input}\n相关记忆：{retrieved_memories}\n请自然回答："
        reply = self.llm.generate(prompt)
        return reply

    def put_knowledge(self, key, value):
        """存入知识"""
        self.semantic_memory.put(key, value)