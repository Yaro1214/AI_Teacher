# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午3:12
# @Author : Yaro
# @Des: 
"""


from dotenv import load_dotenv
load_dotenv()
from database import vectordb
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from memory import get_session_history
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.document_loaders import TextLoader
from llm import model

def retrieve_documents(query: str, k=3):
    """Retrieve the most relevant documents from the vector database"""
    results = vectordb.similarity_search(query, k)
    return [result.page_content for result in results]  # Use .page_content instead of ['text']

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一名教师，请尽你所能回答问题"),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
chain = prompt | model
with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
def chat(config, question):
    retrieved_docs = retrieve_documents(question, k=3)
    context = "\n".join(retrieved_docs)
    extended_prompt = ChatPromptTemplate.from_messages(
        [("system", "你是一名教师，请尽你所能回答问题"),
         ("user", f"以下是相关文档：\n{context}"),
         MessagesPlaceholder(variable_name="messages")]
    )
    chain = extended_prompt | model
    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
    response = with_message_history.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config
    )
    print("Response:", response.content)

async def s_chat(config, question):
    retrieved_docs = retrieve_documents(question, k=3)
    context = "\n".join(retrieved_docs)
    extended_prompt = ChatPromptTemplate.from_messages(
        [("system", "你是一名教师，请尽你所能回答问题"),
         ("user", f"以下是相关文档：\n{context}"),
         MessagesPlaceholder(variable_name="messages")]
    )

    chain = extended_prompt | model

    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")

    async for response in with_message_history.astream(
        {"messages": [HumanMessage(content=question)]}, config=config
    ):
        print("Streaming Response:", response.content)
        yield response.content


def summary(config, question):
    prompt = ChatPromptTemplate.from_messages(
        [("system", "你无需回答问题，你的任务是根据用户的问题，用10个字以内为你们的对话概括一个对话名称"),
         MessagesPlaceholder(variable_name="messages")]
    )
    chain = prompt | model
    with_message_history = RunnableWithMessageHistory(chain, get_session_history, input_messages_key="messages")
    response = with_message_history.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config
    )
    return response.content


