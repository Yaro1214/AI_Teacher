# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午6:56
# @Author : Yaro
# @Des: 
"""
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
model=ChatOpenAI(model="gpt-4o-mini")
query_rewrite=ChatOpenAI(model="gpt-4o-mini")
summary=ChatOpenAI(model="gpt-4o-mini")