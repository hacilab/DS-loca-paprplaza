# import requests

# def search_serpapi(query, top_k=3):
#     url = "https://serpapi.com/search"
#     params = {
#         "q": query,
#         "api_key": "1c710e558abd52ae2e06934043424c49801949d5434372fe3a236647bfb40484",  # SerpAPI 密钥
#     }
#     try:
#         response = requests.get(url, params=params, timeout=10)
#         if response.status_code == 200:
#             results = response.json()
#             relevant_docs = []
#             if "organic_results" in results:
#                 for result in results["organic_results"][:top_k]:
#                     relevant_docs.append(f"[网页] {result['title']}: {result['snippet']}")
#             return relevant_docs
#         else:
#             print(f"SerpAPI 请求失败，状态码: {response.status_code}")
#             return []
#     except Exception as e:
#         print(f"SerpAPI 请求异常: {e}")
#         return []
    

# query = "春节期间，我要乘坐高铁从上海到秦皇岛玩三天，请帮我规划旅游路线"
# results = search_serpapi(query)
# print("检索到的网上数据：", results)


import re
import jieba
import jieba.analyse

# 预处理用户输入
def clean_input(user_input):
    # 去除标点符号和特殊字符
    cleaned_input = re.sub(r'[^\w\s]', '', user_input)
    return cleaned_input

def to_lowercase(user_input):
    return user_input.lower()

# 分词
def tokenize(user_input, language='zh'):
    if language == 'zh':
        return list(jieba.cut(user_input))
    else:
        return user_input.split()

# # 去除停用词
# stop_words = set(["的", "是", "and", "the", "a", "an", "in", "on", "at", "to", "for", "with", "of"])

# def remove_stop_words(tokens):
#     return [word for word in tokens if word not in stop_words]

# 提取关键词
def extract_keywords(user_input, topK=5):
    keywords = jieba.analyse.extract_tags(user_input, topK=topK)
    return keywords

# 构建查询词
def construct_query(keywords):
    return ' '.join(keywords)

# 完整流程
def process_user_input(user_input, language='en'):
    # 预处理
    cleaned_input = clean_input(user_input)
    cleaned_input = to_lowercase(cleaned_input)
    
    # 分词
    tokens = tokenize(cleaned_input, language)
    
    # # 去除停用词
    # filtered_tokens = remove_stop_words(tokens)
    
    # 提取关键词
    if language == 'zh':
        keywords = extract_keywords(' '.join(tokens))
    else:
        # 对于英文，直接使用过滤后的词作为关键词
        keywords = tokens
    
    # 构建查询词
    query = construct_query(keywords)
    return query

# 示例
user_input_zh = "春节期间，我要到秦皇岛玩三天，请帮我规划旅游路线"
query_zh = process_user_input(user_input_zh, language='zh')
print("提取的查询词 (中文):", query_zh)

