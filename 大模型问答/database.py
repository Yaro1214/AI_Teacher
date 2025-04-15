# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午6:41
# @Author : Yaro
# @Des: 
"""
from langchain_chroma import Chroma
import os

from langchain_community.document_loaders import TextLoader, Docx2txtLoader
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

embeddings = OpenAIEmbeddings()
current_directory = os.path.dirname(os.path.abspath(__file__))
persist_directory = os.path.join(current_directory, 'vectordb')
vectordb = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

def load_document(file_path: str):
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    elif file_path.endswith(".doc") or file_path.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    else:
        raise ValueError("Unsupported file format")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=15
    )
    splits = text_splitter.split_documents(docs)
    vectordb.add_documents(splits)
    print(f"已成功在 {persist_directory} 文件夹生成向量数据库")
