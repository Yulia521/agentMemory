class WorkingMemory:
    def __init__(self, max_size=10):
        self.max_size = max_size
        self.messages = []

    def add(self, role, content):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > self.max_size:
            self.messages.pop(0)

    def get_context(self):
        return self.messages.copy()