# src/agents/agents/student.py
import os
from langchain_core.prompts import ChatPromptTemplate
from ..base import State
from ..models import get_llm

# 获取当前文件所在的目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPTS_DIR = os.path.join(os.path.dirname(CURRENT_DIR), "prompts")

class StudentAgent:
    """学生智能体"""
    def __init__(self, model_type: str = "deepseek"):
        self.model_type = model_type
    
    async def __call__(self, state: State, config) -> State:
        """处理学生智能体逻辑"""
        try:
            curr_question = state.question[0]
            evaluation = state.evaluation
            
            prompt_path = os.path.join(PROMPTS_DIR, "student_agent_prompt2.txt")
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
                explanation=curr_question['reference_answer']['explanation'],
                is_right=evaluation['is_right'],
                is_complete=evaluation['is_complete'],
                reason=evaluation['reason']
            )
            
            llm = get_llm(model_type=self.model_type)
            chain = system_prompt | llm
            stu_feedback = await chain.ainvoke({"messages": state.messages}, config)
            
            return {"messages": stu_feedback}
            
        except Exception as e:
            return {"log": str(e)}