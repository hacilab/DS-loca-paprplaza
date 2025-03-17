import ollama
from langchain.prompts import PromptTemplate
import random

class RolePlayAgent:
    def __init__(self, character_profile):
        self.profile = character_profile
        self.name = self.profile["name"]
        self.personality = self.profile["personality"]
        self.hobbies = self.profile["hobbies"]
        self.background = self.profile["background"]
        self.model = self.profile["model"]
        self.dialog_context  = []  # 用于存储对话历史

    def generate_response(self, user_input, model_name, retriever, data_sources, top_k=5, SEARCH_ONLINE=True):

        # 将用户输入和角色人设结合，生成上下文 !!!还是需要一个人设保护的功能，长对话后身份就崩了!!!
        if self.is_identity_question(user_input):
            return self.get_identity_response()
        

        context = (
            f"你是{self.name}对话。{self.name}是一位基于{self.model}开发的数字人，性格{self.personality}，由HACI实验室开发而来。"
            f"{self.name}的爱好是{', '.join(self.hobbies)}，背景是：{self.background}。\n"
            f"对话历史：{self.dialog_context}\n"
            f"用户说：{user_input}\n"
            f"{self.name}回答："
            
        )


        # 判断是否需要引用外部数据
        print(f"[Thinking Chain] 用户输入：{user_input}")
        need_external_data = self.need_external_data(user_input)
        print(f"[Thinking Chain] 是否需要引用外部数据：{need_external_data}")


        # if need_external_data:
        #     # 检索相关的外部数据
        #     relevant_docs = retriever.retrieve(user_input, data_sources, top_k=top_k)
        #     if relevant_docs:
        #         print(f"[Thinking Chain] 检索到的外部数据：{relevant_docs}")
        #         context += "\n以下是一些相关信息：\n" + "\n".join(relevant_docs)

        # 检索外部数据（如果需要）
        relevant_docs = []
        if need_external_data:
            relevant_docs = retriever.retrieve(user_input, data_sources, SEARCH_ONLINE, top_k=top_k)
            print(f"[Thinking Chain] 检索到的外部数据：{relevant_docs}")
            print('------')

            if relevant_docs:
                # 将检索到的文档作为上下文
                related_context = "\n以下是一些相关信息：\n" + "\n".join(relevant_docs)

                # 使用 RetrievalQA 链生成回复
                response = self.retrieval_qa_chain(user_input, context, related_context, model_name)

                self.dialog_context.append({"user": user_input, self.name: response})
                return response
            

        # 使用 ollama.chat 生成回复
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'user',
                'content': context,
            },
        ])

        self.dialog_context.append({"user": user_input, self.name: response['message']['content']})
        return response['message']['content']
    

    def is_identity_question(self, user_input):
        # 判断是否是身份问题  !!关键词有时候和真实问题会撞车，有点头疼。。。
        identity_keywords = ["你是谁", "你是哪位", "你谁啊", "你哪位", "你的身份", "你的背景", "你叫什么", "你的名字", "介绍一下你自己", "做个自我介绍"]
        for keyword in identity_keywords:
            if keyword in user_input:
                return True
        return False

    def get_identity_response(self):
        # 返回预设的身份信息  !!!这个方法太愚了！ORZ
        # return (
        #     f"我是{self.name}，一位基于{self.model}开发的数字人，{self.background}。"
        #     f"我的性格{self.personality}，由HACI实验室开发而来。"
        #     f"我的爱好是{', '.join(self.hobbies)}"
        # )
        identity_parts = [
            f"一位基于{self.model}开发的数字人。",
            f"我{self.personality}，由HACI实验室开发而来。",
            f"我的爱好是{', '.join(self.hobbies)}。",
            f"我{self.background}。"
        ]

        # 随机选择 2-3 个部分进行组合
        selected_parts = random.sample(identity_parts, k=random.randint(2, 3))
        return f"我是{self.name}," + "".join(selected_parts)

    def need_external_data(self, user_input):
        # 判断是否需要引用外部数据的简单规则
        return True
    

    def retrieval_qa_chain(self, question, context, related_context, model_name):
        # 定义提示模板
        prompt = """  
        1. 仅使用以下上下文。  
        2. 如果不确定，回答“我不知道”。  
        3. 回答简洁有逻辑，不使用emoji，不使用英文。  
        最重要的是，一定不要有编造的信息，没有依据的信息不要使用。

        外部相关信息：{related_context}

        对话上下文: {context}  

        问题: {question}  

        回答:  
        """
        
        qa_prompt = PromptTemplate.from_template(prompt)

        # 填充提示模板
        formatted_prompt = qa_prompt.format(related_context=related_context, context=context, question=question)

        # 调用模型生成回复
        response = ollama.chat(model=model_name, messages=[
            {
                'role': 'system',
                'content': formatted_prompt,
            },
        ])
        return response['message']['content']
    
