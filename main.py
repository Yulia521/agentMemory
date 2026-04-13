from agent import Agent

def main():
    # 创建智能体
    agent = Agent()

    # 预先存入用户记忆
    agent.put_knowledge("user_favorite", "喜欢川菜，预算150元")
    agent.put_knowledge("user_hate", "不吃香菜，不吃太辣")
    agent.put_knowledge("location", "希望在朝阳区")

    # 开始聊天
    while True:
        user_input = input("\n请输入消息（exit 退出）：")

        if user_input.strip() == "exit":
            print("结束对话")
            break

        reply = agent.chat(user_input)
        print(f"🤖 AI回复：{reply}")

if __name__ == "__main__":
    main()