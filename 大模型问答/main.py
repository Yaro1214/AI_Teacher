# -*- coding: utf-8 -*-
"""
# @Create on : 2025/2/26 下午5:43
# @Author : Yaro
# @Des: 
"""
import os
from fastapi.middleware.cors import CORSMiddleware
from typing_extensions import Annotated
from fastapi import (
    Depends,
    FastAPI,
    WebSocket,
    WebSocketException,
    WebSocketDisconnect,
    status,
    File,UploadFile, HTTPException
)
import shutil
from pydantic import BaseModel
from dotenv import load_dotenv
from utils import generate_unique_id
from plan import create_lesson_plan_generator,extract_plan_information
from quiz import create_quiz_generator,extract_quiz_information
from qa import s_chat,summary
from database import  load_document
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
async def authenticate(
        websocket: WebSocket,
        userid: str,
        secret: str,
):
    if userid is None or secret is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    print(f'userid: {userid},secret: {secret}')
    if 'william' == secret:
        return 'pass'
    else:
        return 'fail'

manager = ConnectionManager()
load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问，或者用 ["http://localhost:3000"] 指定前端域
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有 Headers
)
class LessonPlanRequest(BaseModel):
    messages:str="请为我生成一份教学计划"
    subject: str="计算机组成原理"
    course_content: str="计算机组成原理的基本概念"
    course_type: str="新课"
    course_duration: str="60"
    student_level: str="初学者"
    historical_data: str="无"
class QuizRequest(BaseModel):
    messages: str="请为我生成一些习题"
    subject: str="数学"
    course_content:str="一元一次方程"
    student_level: str="初学者"
    number_of_questions:int= 5
    question_type: str="选择题"
class Request_q(BaseModel):
    question: str="请为我生成一些一元一次方程习题"
    user_id: str="123"

@app.post("/title")
async def title(request:Request_q):
    question = request.question 
    userid = request.user_id
    session_id = generate_unique_id(userid)
    config = {"configurable": {"session_id": session_id}}
    title=summary(config,question)
    return {"title":title}

@app.post("/generate_quiz/")
async def generate_lesson_plan(input_param:QuizRequest,user_id:str):
    thread_id=generate_unique_id(user_id)
    config = {"configurable": {"thread_id": thread_id}}
    quiz_generator = create_quiz_generator()
    output = quiz_generator.invoke(input_param, config)
    result=output["messages"][-1].content
    return{"result":result}

@app.post("/generate_lesson_plan/")
async def generate_lesson_plan(input_param:LessonPlanRequest,user_id:str):
    thread_id=generate_unique_id(user_id)
    config = {"configurable": {"thread_id": thread_id}}
    lesson_plan_generator = create_lesson_plan_generator()
    output = lesson_plan_generator.invoke(input_param, config)
    result=output["messages"][-1].content
    return{"result":result}

@app.post("/question_generate_quiz/")
async def question_generate_lesson_plan(request:Request_q):
    question = request.question 
    user_id = request.user_id
    thread_id=generate_unique_id(user_id)
    config = {"configurable": {"thread_id": thread_id}}
    quiz_generator = create_quiz_generator()
    input_param = extract_quiz_information(question)
    output = quiz_generator.invoke(input_param, config)
    result=output["messages"][-1].content
    return{"result":result}

@app.post("/question_generate_lesson_plan/")
async def question_generate_lesson_plan(request:Request_q):
    question = request.question 
    user_id = request.user_id
    thread_id=generate_unique_id(user_id)
    config = {"configurable": {"thread_id": thread_id}}
    lesson_plan_generator = create_lesson_plan_generator()
    input_param=extract_plan_information(question)
    output = lesson_plan_generator.invoke(input_param, config)
    result=output["messages"][-1].content
    return{"result":result}

@app.post("/upload/document/")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith((".txt", ".doc", ".docx")):
        raise HTTPException(status_code=400, detail="Unsupported file type")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        load_document(file_path)
        return {"filename": file.filename, "message": "Upload successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.websocket("/ws")
async def websocket_endpoint(*, websocket: WebSocket, userid: str, permission: Annotated[str, Depends(authenticate)], ):
    await manager.connect(websocket)
    try:
        while True:
            text = await websocket.receive_text()

            if 'fail' == permission:
                await manager.send_personal_message(
                    f"authentication failed", websocket
                )
            else:
                if text is not None and len(text) > 0:
                    session_id=generate_unique_id(userid)
                    config = {"configurable": {"session_id": session_id}}
                    async for msg in s_chat(config,text):
                        await manager.send_personal_message(msg, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client #{userid} left the chat")
        await manager.broadcast(f"Client #{userid} left the chat")





if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8888)




