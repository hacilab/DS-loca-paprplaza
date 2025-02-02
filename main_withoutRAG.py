import ollama
import json
import re

def remove_think_tags(text):
    # 使用正则表达式去掉 <think> 和 </think> 之间的内容
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()

# 加载角色人设
def load_character_profile(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 初始化角色
class RolePlayAgent:
    def __init__(self, character_profile):
        self.profile = character_profile
        self.name = self.profile["name"]
        self.personality = self.profile["personality"]
        self.hobbies = self.profile["hobbies"]
        self.background = self.profile["background"]
        self.memory = []  

    def generate_response(self, user_input, model_name):
        
        context = (
            f"你正在与{self.name}对话。{self.name}是一个{self.personality}的人。"
            f"{self.name}的爱好是{', '.join(self.hobbies)}，背景是：{self.background}。\n"
            f"用户说：{user_input}\n"
            f"{self.name}回答："
        )

        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': context,
            },
        ])
        return response['message']['content']

# 主程序
def main():
    # 加载角色人设
    character_profile = load_character_profile("character.json")
    
    # 初始化角色扮演智能体
    agent = RolePlayAgent(character_profile)
    
    # 设置模型名称
    model_name = "deepseek-r1:8b"  # 替换为你实际使用的模型名称
    
    print(f"欢迎与{agent.name}进行对话！输入'退出'结束对话。")
    print('------')
    
    while True:
        user_input = input("你：")
        if user_input.lower() in ["退出", "exit", "bye"]:
            print(f"{agent.name}：再见！希望下次还能和你聊天。")
            print('------')
            break
        
        # 生成回复
        response = agent.generate_response(user_input, model_name)
        response = remove_think_tags(response)
        print(f"{agent.name}：{response}")
        print('------')
        
        # 将对话记录保存到文件
        with open("对话记录.txt", "a", encoding="utf-8") as text_file:
            text_file.write(f"你：{user_input}\n")
            text_file.write(f"{agent.name}：{response}\n\n")

if __name__ == "__main__":
    main()