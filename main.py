from utilz import *
from RolePlay import *
from RAG import *

def main():

    SEARCH_ONLINE = False

    # 加载角色人设
    character_profile = load_character_profile("character.json")
    
    # 初始化角色扮演智能体
    agent = RolePlayAgent(character_profile)
    
    # 设置模型名称
    model_name = "deepseek-r1:14b"  # 替换为你实际使用的模型名称

    # 外部数据文件路径
    data_sources = {
        "论文": "paper",
    }

    # 初始化检索模块
    retriever = Retriever()
    retriever.build_index(data_sources)

    print(f"欢迎与{agent.name}进行对话！输入'退出'结束对话。")

    while True:
        user_input = input("你：")
        if user_input.lower() in ["退出", "exit", "bye", "拜拜"]:
            print(f"{agent.name}：再见！希望下次还能和你聊天。")
            print('------')
            break
        
        # 生成回复
        print('|| generating...', end='\r')
        response = agent.generate_response(user_input, model_name, retriever, data_sources, SEARCH_ONLINE=SEARCH_ONLINE, top_k=3)
        response_extract = remove_think_tags(response)

        print(f"{agent.name}：{response_extract}")
        print('------')
        
        # 将对话记录保存到文件
        with open("对话记录.txt", "a", encoding="utf-8") as text_file:
            text_file.write(f"用户：{user_input}\n")
            text_file.write(f"{agent.name}：{response}\n\n")

if __name__ == "__main__":
    main()