# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午6:45
# @Author : Yaro
# @Des: 
"""
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
store = {}
def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]