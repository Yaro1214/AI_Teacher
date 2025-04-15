# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午5:41
# @Author : Yaro
# @Des: 
"""
# 教学计划生成助手

import os
from typing import Sequence
from langchain_core.messages import HumanMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict, Annotated
from dotenv import load_dotenv
from llm import model,query_rewrite
import json

load_dotenv()

# 创建教案生成助手
def create_lesson_plan_generator():
    class State(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
        subject: str
        course_content: str
        course_type: str
        course_duration: str
        student_level: str
        historical_data: str

    graph_builder = StateGraph(state_schema=State)
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你是一个教学计划生成助手，基于以下输入信息，为课程生成详细的教案：
                输入信息包括：
                1. 学科：{subject}
                2. 教学内容：{course_content}
                3. 课程类型：{course_type}（新课、讲评课、复习课）
                4. 课程时长：{course_duration}（以分钟为单位）
                5. 学生水平：{student_level}（例如：初学者、中级、高级）
                6. 历史教学记录：{historical_data}（可包括过往的教学反馈、学生表现等）

                根据以上输入，生成教学计划内容，包括以下三个方面：
                1. 教学内容安排：详细列出课程的主要教学内容和顺序。
                2. 时间分配：根据课程时长合理分配每个部分的时间。
                3. 预期成果：描述学生完成课程后应达到的学习成果。

                请确保内容全面且符合教学目标，特别是根据课程类型和学生水平调整教案的难度和重点。
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
    lesson_plan_generator = graph_builder.compile(checkpointer=memory)

    return lesson_plan_generator

def extract_plan_information(natural_language: str) -> dict:
    extraction_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
                你收到一段自然语言描述，请从中提取以下信息，并将结果以 JSON 格式输出，格式如下：
                {{
                    "messages":"请为我生成一份教学计划"
                    "subject": "学科名称",
                    "course_content": "教学内容",
                    "course_type": "新课/讲评课/复习课",
                    "course_duration": "课程时长（分钟）",
                    "student_level": "学生水平",
                    "historical_data": "历史教学记录"
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
        structured_data = {'subject': '数学', 'course_content': '基础代数和几何', 'course_type': '新课', 'course_duration': '90', 'student_level': '初级', 'historical_data': '上次课学生反馈积极'}
    return structured_data























