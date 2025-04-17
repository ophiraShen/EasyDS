# src/agents/base.py
from pydantic import BaseModel, Field
from typing import Annotated, List, Dict, Any
from langgraph.graph.message import AnyMessage, add_messages

class State(BaseModel):
    """智能体间的通讯状态"""
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list, title="对话列表")
    question: list = Field(default=[], title="当前题目信息")
    evaluation: dict = Field(default={}, title="用户回复评估")
    log: str = Field(default="", title="节点执行日志")