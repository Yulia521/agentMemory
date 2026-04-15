class MultiLevelMemory:
    def __init__(self):
        # 1. 工作记忆：用简单的列表存放最近的对话对象
        self.working_memory = []

        # 2. 情景记忆：用列表模拟（以后我们会换成向量数据库实现“检索”）
        self.episodic_memory = []

        # 3. 语义记忆：用字典模拟，存放实体信息
        self.semantic_memory = {
            "user_profile": {},
            "fixed_knowledge": {}
        }

    def get_all_context(self):
        """
        检索逻辑：合并各级记忆提供给 Agent
        """
        # 简单演示：把当前工作记忆和情景记忆的内容拼成字符串
        context = "[当前上下文]\n"
        for msg in self.working_memory:
            context += f"{msg['role']}: {msg['content']}\n"

        if self.episodic_memory:
            context += "\n[历史重要事件回顾]\n"
            context += "\n".join(self.episodic_memory)

        return context

    def update_and_compress(self, user_msg, assistant_msg):
        """
        核心逻辑：写入新记忆，并根据阈值触发压缩策略
        """
        # 第一步：写入工作记忆
        self.working_memory.append({"role": "user", "content": user_msg})
        self.working_memory.append({"role": "assistant", "content": assistant_msg})

        # 第二步：压缩策略 (Compression Strategy)
        # 任务书要求：避免“洪泛式”冗余存储
        # 设定阈值：如果对话超过 4 条（2轮），就把最老的 2 条移出内存
        if len(self.working_memory) > 4:
            # 提取需要压缩的内容
            to_compress = self.working_memory[:2]

            # 生成摘要（现在是“伪代码”阶段，我们用简单的字符串拼接模拟）
            # 以后这里会换成：summary = llm.summarize(to_compress)
            summary_item = f"事件摘要: 用户询问了'{to_compress[0]['content']}'"

            # 存入情景记忆
            self.episodic_memory.append(summary_item)

            # 从工作记忆中删除已压缩的内容
            self.working_memory = self.working_memory[2:]

            print(f"\n>>> [系统日志] 触发压缩逻辑：")
            print(f"    - 已从工作记忆移除: {len(to_compress)} 条记录")
            print(f"    - 已持久化至情景记忆: {summary_item}")