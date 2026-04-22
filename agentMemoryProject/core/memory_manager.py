from mem0 import Memory

class MemoryManager:
    def __init__(self):
        # 初始化 Mem0，它会自动帮你处理向量存储和实体提取 [cite: 21, 22]
        # 注意：这里我们使用默认配置，它会在本地产生一个数据库文件
        self.long_term_memory = Memory()

        # 工作记忆：LangChain 层面维护的短期对话
        self.working_memory = []

    def get_context(self, user_id, query):
        """一次性拿取短期和长期记忆 [cite: 22]"""
        # 1. 获取长期记忆 (Mem0 自动做语义检索)
        past_memories = self.long_term_memory.search(query, user_id=user_id)
        mem_str = "\n".join([m['text'] for m in past_memories])

        # 2. 获取短期记忆 (Working Memory)
        working_str = "\n".join([f"{m['role']}: {m['content']}" for m in self.working_memory[-3:]])

        return f"历史背景:\n{mem_str}\n当前对话:\n{working_str}"

    def save(self, user_id, user_input, assistant_output):
        """存入记忆 """
        # 存入短期
        self.working_memory.append({"role": "user", "content": user_input})
        self.working_memory.append({"role": "assistant", "content": assistant_output})

        # 存入长期 (Mem0 会自动压缩和去冗) [cite: 22]
        self.long_term_memory.add(f"User: {user_input}\nAssistant: {assistant_output}", user_id=user_id)