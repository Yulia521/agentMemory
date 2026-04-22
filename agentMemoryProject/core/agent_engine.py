import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from .memory_manager import MemoryManager

class AgentEngine:
    def __init__(self):
        # 从环境变量读取配置，这样代码就不用写死了
        # 获取模型名字，如果没有设置，默认用 deepseek-v3
        model = os.getenv("MODEL_NAME", "deepseek-ai/DeepSeek-OCR")

        # 这里的配置会自动读取 .env 里的 OPENAI_API_KEY 和 OPENAI_API_BASE
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7
        )
        self.memory = MemoryManager()
        self.prompt = ChatPromptTemplate.from_template("""
        你是一个具备分层式记忆架构的智能体。根据以下背景信息回答问题。

        {history}

        用户: {input}
        """)

    def run(self, user_id, user_input):
        history = self.memory.get_context(user_id, user_input)
        chain = self.prompt | self.llm
        response = chain.invoke({"history": history, "input": user_input})
        self.memory.save(user_id, user_input, response.content)
        return response.content