# src/agents/agents/router.py
from typing import Literal
from pydantic import Field
from typing_extensions import TypedDict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.types import Command

from ..base import State

class Evaluation(TypedDict):
    is_right: bool
    is_complete: bool
    reason: str
    next_agent: Literal["teacher", "student"]

async def router_agent(state: State, config) -> Command[Literal["teacher_agent", "student_agent"]]:
    """根据当前状态进行路由"""
    try:
        curr_question = state.question[0]
        with open("/root/autodl-tmp/EasyDS/src/agents/prompts/router_agent_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
            
        prompt = ChatPromptTemplate([
            ("system", prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        
        system_prompt = prompt.partial(
            title=curr_question['title'],
            content=curr_question['content'],
            answer=curr_question['reference_answer']['content'],
            explanation=curr_question['reference_answer']['explanation']
        )
        
        from ..models import get_llm
        llm = get_llm()
        chain = system_prompt | llm.with_structured_output(Evaluation, method="function_calling")
        router_result = await chain.ainvoke({"messages": state.messages}, config)
        
        goto = "teacher_agent" if router_result['next_agent'] == 'teacher' else "student_agent"
        
        return Command(
            update={"evaluation": router_result},
            goto=goto
        )
        
    except Exception as e:
        return Command(
            update={"log": str(e)},
            goto="teacher_agent"
        )