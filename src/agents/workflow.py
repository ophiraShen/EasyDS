# src/agents/workflow.py
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from .base import State
from .agents.router import RouterAgent
from .agents.student import StudentAgent 
from .agents.teacher import TeacherAgent, knowledge_summry_search

def create_workflow(
    router_model_type: str = "deepseek",
    teacher_model_type: str = "deepseek", 
    student_model_type: str = "deepseek"
):
    """
    创建工作流程图
    
    Args:
        router_model_type: 路由节点使用的模型类型
        teacher_model_type: 教师节点使用的模型类型
        student_model_type: 学生节点使用的模型类型
    """
    workflow = StateGraph(State)
    
    # 创建节点实例
    router_agent = RouterAgent(model_type=router_model_type)
    student_agent = StudentAgent(model_type=student_model_type)
    teacher_agent = TeacherAgent(model_type=teacher_model_type)
    
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