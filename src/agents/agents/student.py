# src/agents/agents/student.py
from langchain_core.prompts import ChatPromptTemplate
from ..base import State
from ..models import get_llm

async def student_agent(state: State, config) -> State:
    """学生智能体"""
    try:
        curr_question = state.question[0]
        evaluation = state.evaluation
        
        with open("/root/autodl-tmp/EasyDS/src/agents/prompts/student_agent_prompt2.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
            
        prompt = ChatPromptTemplate([
            ("system", prompt),
            ("human", "{messages}")
        ])
        
        system_prompt = prompt.partial(
            title=curr_question['title'],
            content=curr_question['content'],
            answer=curr_question['reference_answer']['content'],
            explanation=curr_question['reference_answer']['explanation'],
            is_right=evaluation['is_right'],
            is_complete=evaluation['is_complete'],
            reason=evaluation['reason']
        )
        
        llm = get_llm()
        chain = system_prompt | llm
        stu_feedback = await chain.ainvoke({"messages": state.messages}, config)
        
        return {"messages": stu_feedback}
        
    except Exception as e:
        return {"log": str(e)}