class EpisodicMemory:
    def __init__(self):
        self.events = []

    def add_event(self, content):
        self.events.append(content)

    def get_recent(self, n=5):
        return self.events[-n:]