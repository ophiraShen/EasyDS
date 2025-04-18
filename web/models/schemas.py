from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

class SessionCreate(BaseModel):
    """创建会话请求模型"""
    question_id: str = Field(..., description="问题ID")

class MessageCreate(BaseModel):
    """创建消息请求模型"""
    content: str = Field(..., description="消息内容")

class SessionInfo(BaseModel):
    """会话信息模型"""
    session_id: str = Field(..., description="会话ID")
    question_id: str = Field(..., description="问题ID")
    status: str = Field(..., description="会话状态")
    last_evaluation: Dict[str, Any] = Field(default_factory=dict, description="最近一次评估结果")

class KnowledgePoint(BaseModel):
    """知识点模型"""
    id: str
    title: str
    summry: str

class Question(BaseModel):
    """问题模型"""
    id: str
    title: str
    content: str
    type: Optional[str] = "选择题"
    difficulty: Optional[str] = "中等"
    options: Optional[Dict[str, str]] = None
    knowledge_points: Optional[List[str]] = None 