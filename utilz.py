import json
import re
# import jieba
# import jieba.posseg as pseg
# import spacy

def load_character_profile(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def remove_think_tags(text):
    # 使用正则表达式去掉 <think> 和 </think> 之间的内容
    cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    return cleaned_text.strip()


# nlp = spacy.load("zh_core_web_sm")

# def extract_keywords(query):
#     """
#     使用 jieba 提取关键词
#     """
#     # 分词并标注词性
#     words = pseg.cut(query)
#     keywords = []
#     for word, flag in words:
#         # 提取名词、动词等关键词
#         if flag.startswith('n') or flag.startswith('v'):  # n: 名词, v: 动词
#             keywords.append(word)
#     return keywords

# def extract_entities(query):
#     """
#     使用 spaCy 提取命名实体
#     """
#     doc = nlp(query)
#     entities = []
#     for ent in doc.ents:
#         entities.append((ent.text, ent.label_))  # 实体文本和类型
#     return entities

# def extract_key_info(query):
#     """
#     提取查询中的关键信息
#     """
#     # 提取关键词
#     keywords = extract_keywords(query)
#     print("提取的关键词:", keywords)

#     # 提取命名实体
#     entities = extract_entities(query)
#     print("提取的命名实体:", entities)

#     # 合并关键信息
#     key_info = keywords + [ent[0] for ent in entities]
#     return list(set(key_info))  # 去重