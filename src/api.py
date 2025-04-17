# src/api.py
import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import uvicorn
import asyncio
import json

sys.path.append("/root/autodl-tmp/EasyDS")
from src.knowledge_qa_system import KnowledgeQASystem

app = FastAPI(title="EasyDS 知识问答系统")
qa_system = KnowledgeQASystem()

# 定义请求和响应模型
class QuestionRequest(BaseModel):
    question_id: str

class AnswerRequest(BaseModel):
    answer: str

class ChapterInfo(BaseModel):
    id: str
    title: str

class QuestionInfo(BaseModel):
    id: str
    title: str
    type: str = "选择题"
    difficulty: str = "中等"

class SessionInfo(BaseModel):
    session_id: str
    question_id: str
    status: str

class KnowledgePointInfo(BaseModel):
    id: str
    title: str
    summry: str = ""

# API 端点
@app.get("/chapters", response_model=List[ChapterInfo])
async def get_chapters():
    """获取所有章节"""
    return qa_system.get_chapters()

@app.get("/chapters/{chapter_id}/questions", response_model=List[QuestionInfo])
async def get_questions_by_chapter(chapter_id: str):
    """获取指定章节的所有问题"""
    return qa_system.get_questions_by_chapter(chapter_id)

@app.get("/questions/{question_id}")
async def get_question_detail(question_id: str):
    """获取问题详情"""
    question = qa_system.get_question_detail(question_id)
    if not question:
        raise HTTPException(status_code=404, detail=f"找不到问题: {question_id}")
    return question

@app.post("/sessions")
async def create_session(request: QuestionRequest):
    """创建问答会话"""
    try:
        session_id = qa_system.create_session(request.question_id)
        return {"session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/sessions/{session_id}/answer")
async def answer_question(session_id: str, request: AnswerRequest):
    """处理用户回答 (流式响应)"""
    try:
        async def stream_response():
            async for chunk in qa_system.process_answer(session_id, request.answer):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """获取会话信息"""
    try:
        return qa_system.get_session_info(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/questions/{question_id}/knowledge-points", response_model=List[KnowledgePointInfo])
async def get_related_knowledge_points(question_id: str):
    """获取问题相关的知识点"""
    return qa_system.get_related_knowledge_points(question_id)

@app.get("/questions/{question_id}/similar", response_model=List[QuestionInfo])
async def get_similar_questions(question_id: str, limit: int = 5):
    """获取与当前问题相似的其他问题"""
    return qa_system.get_similar_questions(question_id, limit)

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    success = qa_system.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"找不到会话: {session_id}")
    return {"success": True}

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)