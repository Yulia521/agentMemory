class SemanticMemory:
    def __init__(self):
        self.knowledge = {}

    def put(self, key, value):
        self.knowledge[key] = value

    def get(self, key):
        return self.knowledge.get(key)