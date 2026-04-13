# 关键词检索：根据输入句子，匹配相关记忆
class KeywordRetriever:
    def __init__(self, memory):
        self.memory = memory  # 传入语义记忆

    def search(self, query, top_k=3):
        """
        query: 用户问题
        top_k: 返回最相关的几条
        """
        matches = []

        # 遍历所有记忆，看关键词是否出现在内容里
        for key, content in self.memory.knowledge.items():
            if query in content:
                matches.append((key, content))

        # 按顺序返回前几条
        return matches[:top_k]