from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import fitz
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain_community.embeddings import HuggingFaceEmbeddings
import requests
# import serpapi
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist
from utilz import *
import ollama
import os

class Retriever:
    def __init__(self):
        # 加载预训练的 Sentence Transformer 模型
        self.model = SentenceTransformer('./paraphrase-MiniLM-L6-v2')
        self.indices = {}  # 存储每个数据源的索引
        self.documents = {}  # 存储每个数据源的文档
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,  # 每个块的最大长度
            chunk_overlap=50,  # 块之间的重叠长度
            separators=["\n\n", "\n", "。", "！", "？"]  # 分块分隔符
        )

    def build_index(self, data_sources):
        # 为每个数据源构建索引
        for source_name, file_path in data_sources.items():

            file_list = os.listdir('./external_data/' + file_path)

            for paper in file_list:
                print(paper)
                if paper.endswith('.pdf'):
                    # 处理 PDF 文件
                    documents = self.extract_text_from_pdf('./external_data/' + file_path + '/' + paper)
                else:
                    # 处理文本文件
                    with open('./external_data/' + file_path + '/' + paper, 'r', encoding='utf-8') as f:
                        documents = [line.strip() for line in f.readlines()]

            # 对文档进行分块
            chunks = self.text_splitter.split_text("\n".join(documents))
            self.documents[source_name] = chunks

            # 将分块后的文档转换为向量
            embeddings = self.model.encode(chunks)

            # 使用 HNSW 索引
            dimension = embeddings.shape[1]
            index = faiss.IndexHNSWFlat(dimension, 32)  # 32 是 HNSW 的参数
            index.add(np.array(embeddings))

            # 保存索引
            self.indices[source_name] = index

    def extract_text_from_pdf(self, file_path):
        # 从 PDF 文件中提取文本
        documents = []
        with fitz.open(file_path) as doc:
            for page in doc:
                text = page.get_text()
                # 将文本按段落分割
                paragraphs = text.split('\n')
                documents.extend([p.strip() for p in paragraphs if p.strip()])
        return documents

    def retrieve(self, query, data_sources, SEARCH_ONLINE, top_k=3):
        # 将查询转换为向量
        query_embedding = self.model.encode([query])

        # 检索每个数据源的相关文档
        relevant_docs_local = []
        relevant_docs_online = []
        for source_name, file_path in data_sources.items():
            if source_name in self.indices:
                print('External Data Search | source name %s...'% source_name)
                index = self.indices[source_name]
                distances, indices = index.search(np.array(query_embedding), top_k)

                file_list = os.listdir('./external_data/'+file_path)

                # 从数据源加载相关文档
                for paper in file_list:
                    if paper.endswith('.pdf'):
                        documents = self.extract_text_from_pdf('./external_data/' + file_path + '/' + paper)
                    else:
                        with open('./external_data/' + file_path + '/' + paper, 'r', encoding='utf-8') as f:
                            documents = [line.strip() for line in f.readlines()]

                    for idx in indices[0]:
                        if idx < len(documents):
                            relevant_docs_local.append(f"[{source_name}] {documents[idx].strip()}")
            
        if SEARCH_ONLINE:
            print("||searching on the internet||Q=%s||"%(query))
            relevant_docs_online = self.search_serpapi(query)
            print(f"检索到的网上数据：{relevant_docs_online}")
        
        relevant_docs = relevant_docs_local + relevant_docs_online


        return relevant_docs

    def search_serpapi(self, query, top_k=10):
        # 提取关键信息 NO GOOD IDEA TO IMPLEMENT THIS SHIT!!! 

        # key_info = extract_key_info(query)
        # if not key_info:
        #     print("未提取到关键信息，使用原始查询。")
        #     key_info = [query]
        # clean_query = " ".join(key_info)

        # prompt = """你是一位擅长理解用户意图并将其总结为简洁搜索关键词的专家。
        # 你的任务是将用户的输入提炼成一句话清晰、简短、适合搜索引擎进行精准搜索的关键词信息。
        # 用户输入：{query}
        # """
        # clean_query = remove_think_tags(ollama.chat(model='deepseek-r1:8b', messages=[
        #     {
        #         'role': 'user',
        #         'content': prompt.format(query=query)
        #     },
        # ])['message']['content'])  #UNCONTROLLABLE，bad attempts but better than rule-based method... DAMN
        
        # print('||clean_query', clean_query)


        # 网页搜索  ！！！！！增加网页搜索功能后，上下文信息联系能力变弱，，DAMN  X(，
        relevant_docs = []
        # for keyword in key_info:
        url = "https://serpapi.com/search"
        params = {
            # "q": clean_query,
            "q": query,
            "api_key": os.environ.get('SerpAPI'),  # SerpAPI 密钥
            "location": "China", 
            "gl": "cn", 
            "hl": "zh-CN"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                results = response.json()
                if "organic_results" in results:
                    for result in results["organic_results"][:top_k]:
                        relevant_docs.append(f"[网页] {result['title']}: {result['snippet']}")
            else:
                print(f"SerpAPI 请求失败，状态码: {response.status_code}")
        except Exception as e:
            print(f"SerpAPI 请求异常: {e}")
        
        return relevant_docs

    
    # Trash attempts XD... waits my time.

    # def search_serpapi(self, query, top_k=5):
    #     # Initialize the client with your API key
    #     client = serpapi.Client(api_key="xxx")
        
    #     # Define search parameters
    #     search_params = {
    #         "engine": "bing",  # Use Bing search engine
    #         "q": query,  # Search query
    #         "location": "China",  # Location for the search
    #         "gl": "cn",  # Country code for China
    #         "hl": "zh-CN",  # Language code for Chinese
    #         "num": top_k  # Number of results to return
    #     }
        
    #     try:
    #         # Perform the search
    #         results = client.search(search_params)
    #         print(results)
    #         # Extract relevant documents
    #         relevant_docs = []
    #         if "organic_results" in results:
    #             for result in results["organic_results"]:
    #                 # Filter results based on certain criteria (example: title length > 10)
    #                 if len(result.get('title', '')) > 10:
    #                     relevant_docs.append(f"[网页] {result['title']}: {result['snippet']}")
            
    #         return relevant_docs
        
    #     except Exception as e:
    #         print(f"SerpAPI 请求异常: {e}")
    #         return []