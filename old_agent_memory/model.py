from transformers import pipeline

class SimpleLLM:
    def __init__(self):
        self.generator = pipeline(
            "text-generation",
            model="uer/gpt2-chinese-cluecorpussmall",
            max_new_tokens=120
        )

    def generate(self, prompt):
        res = self.generator(prompt)
        return res[0]["generated_text"].replace(prompt, "")