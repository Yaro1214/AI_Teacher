# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午6:30
# @Author : Yaro
# @Des: 
"""
import os
from dotenv import  load_dotenv
load_dotenv()
from typing import Sequence
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages, MessagesState
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Annotated
from llm import model,query_rewrite
import json


# 创建习题生成助手
def create_quiz_generator():
    class State(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
        subject: str
        course_content: str
        student_level: str
        number_of_questions: str
        question_type: str  # 例如：选择题、填空题、简答题等

    graph_builder = StateGraph(state_schema=State)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你是一个习题生成助手，基于以下输入信息，为课程生成习题：
                输入信息包括：
                1. 学科：{subject}
                2. 教学内容：{course_content}
                3. 学生水平：{student_level}（例如：初学者、中级、高级）
                4. 习题数量：{number_of_questions}（需要生成的习题数量）
                5. 习题类型：{question_type}（例如：选择题、填空题、简答题等）

                根据以上输入，生成相应的习题。每个习题后要提供正确答案，并确保习题难度适合学生的水平。
                """
            ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

    def chatbot(state: State):
        prompt = prompt_template.invoke(state)
        response = model.invoke(prompt)
        return {"messages": [response]}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")
    memory = MemorySaver()
    quiz_generator = graph_builder.compile(checkpointer=memory)

    return quiz_generator

def extract_quiz_information(natural_language: str) -> dict:
    extraction_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你收到一段自然语言描述，请从中提取以下信息，并将结果以 JSON 格式输出，格式如下：
                {{
                    messages:str="请为我生成一些习题"
                    "subject": "学科名称",
                    "course_content": "教学内容",
                    "student_level": "学生水平",
                    "number_of_questions":"需要生成的习题数量",
                     "question_type":"习题类型（例如：选择题、填空题、简答题等,可能会有一个或多个）"
                }}
                请确保所有字段都有值，如若描述中未提及，请填入合适的默认值。
                """
            ),
            ("user", "{natural_language}")
        ]
    )
    # 填充自然语言输入
    prompt = extraction_prompt.format(natural_language=natural_language)
    # 调用 query_rewrite 进行转换
    extraction_response = query_rewrite.invoke(prompt)
    content=extraction_response.content
    try:
        structured_data = json.loads(content)
    except Exception as e:
        # 如果解析失败，可打印错误或采用备用方案
        print("JSON解析失败：", e)
        structured_data = {'subject': '数学', 'course_content': '基础代数和几何', 'student_level': '初级', 'number_of_questions': '10',"question_type":"选择题"}
    return structured_data
