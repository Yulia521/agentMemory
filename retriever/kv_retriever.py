# KV 键值对检索：最简单、最稳定的记忆检索方式
class KvRetriever:
    def __init__(self, memory):
        # 接收传入的“语义记忆”
        self.memory = memory

    def search(self, query_key):
        """
        根据 key 精确查找记忆
        """
        return self.memory.get(query_key)