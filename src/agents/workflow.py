# src/agents/workflow.py
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from .base import State
from .agents.router import router_agent
from .agents.student import student_agent 
from .agents.teacher import teacher_agent, knowledge_summry_search

def create_workflow():
    """创建工作流程图"""
    workflow = StateGraph(State)
    
    # 添加节点
    workflow.add_node("router_agent", router_agent)
    workflow.add_node("student_agent", student_agent)
    workflow.add_node("teacher_agent", teacher_agent)
    workflow.add_node("tool_node", ToolNode([knowledge_summry_search]))
    
    # 添加边
    workflow.add_edge(START, "router_agent")
    workflow.add_edge("tool_node", "teacher_agent")
    workflow.add_edge("student_agent", "__end__")
    
    # 添加检查点
    memory = MemorySaver()
    
    return workflow.compile(checkpointer=memory)