# src/agents/agents/teacher.py
import os
from typing import Literal
from langchain_core.prompts import ChatPromptTemplate
from langgraph.types import Command

from ..base import State
from ..models import get_llm
from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem

# 获取当前文件所在的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "prompts")
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR)))
DS_INDICES_PATH = os.path.join(ROOT_DIR, "data", "ds_data", "ds_indices.pkl")

async def knowledge_summry_search(knowledge_points: list):
    """根据知识点列表查询知识点概述"""
    try:
        system = await KnowledgeIndexSystem.load_indices_async(DS_INDICES_PATH)
        knowledge_summry = []
        for kp in knowledge_points:
            knowledge_point_info = await system.get_knowledge_point_async(kp)
            if knowledge_point_info:    
                knowledge_summry.append({
                    "knowledge_point": knowledge_point_info['title'],
                    "summry": knowledge_point_info['summry']
                })
        if knowledge_summry:
            return "\n".join([f"{kp['knowledge_point']}: {kp['summry']}" for kp in knowledge_summry])
        return "未找到对应知识点"
    except Exception as e:
        return str(e)

class TeacherAgent:
    """教师智能体"""
    def __init__(self, model_type: str = "deepseek"):
        self.model_type = model_type
    
    async def __call__(self, state: State, config) -> Command[Literal["tool_node", "__end__"]]:
        """处理教师智能体逻辑"""
        try:
            curr_question = state.question[0]
            evaluation = state.evaluation
            
            prompt_path = os.path.join(PROMPTS_DIR, "teacher_agent_prompt.txt")
            with open(prompt_path, "r", encoding="utf-8") as f:
                prompt = f.read()
                
            prompt = ChatPromptTemplate([
                ("system", prompt),
                ("human", "{messages}")
            ])
            
            system_prompt = prompt.partial(
                title=curr_question['title'],
                content=curr_question['content'],
                answer=curr_question['reference_answer']['content'],
                knowledge_points=curr_question['knowledge_points'],
                explanation=curr_question['reference_answer']['explanation'],
                is_right=evaluation['is_right'],
                is_complete=evaluation['is_complete'],
                reason=evaluation['reason']
            )
            
            llm = get_llm(model_type=self.model_type)
            tools = [knowledge_summry_search]
            chain = system_prompt | llm.bind_tools(tools)
            teacher_feedback = await chain.ainvoke({"messages": state.messages}, config)
            
            goto = "tool_node" if teacher_feedback.tool_calls else "__end__"
            
            return Command(
                update={"messages": teacher_feedback},
                goto=goto
            )
            
        except Exception as e:
            return Command(
                update={"log": str(e)},
                goto="__end__"
            )