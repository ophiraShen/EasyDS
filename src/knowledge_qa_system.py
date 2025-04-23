# src/knowledge_qa_system.py (修订版)
import os
import json
from uuid import uuid4
from typing import Dict, List, Optional, Any, Tuple

from langchain_core.messages import HumanMessage

from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem
from src.agents.workflow import create_workflow

class KnowledgeQASystem:
    """知识问答系统，整合知识点索引和智能体问答功能"""
    
    def __init__(self, 
                 indices_path: str = '/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl',
                 router_model_type: str = "deepseek",
                 teacher_model_type: str = "deepseek",
                 student_model_type: str = "deepseek"):
        """
        初始化知识问答系统
        
        Args:
            indices_path: 索引文件路径
        """
        # 加载知识点索引系统
        self.index_system = KnowledgeIndexSystem.load_indices(indices_path)
        
        # 创建智能体工作流
        self.workflow = create_workflow(router_model_type, teacher_model_type, student_model_type)

        self.sessions = {}
        
        
    def get_chapters(self) -> List[Dict]:
        """
        获取所有章节
        
        Returns:
            章节信息列表
        """

        chapters = self.index_system.get_chapter_list()
        
        # 按章节ID排序
        chapters.sort(key=lambda x: x["id"])
        return chapters
    
    def chapter_knowledge_points(self) -> Dict[str, List[str]]:
        """
        获取所有章节的知识点
        """
        chapters_knowledge_points = {}
        for chapter_id, chapter_info in self.index_system.chapter_index.items():
            chapters_knowledge_points[chapter_id] = chapter_info['knowledge_points']
        return chapters_knowledge_points
    
    def knowledge_points_summary_by_knowledge_id(self, knowledge_id: str) -> str:
        """
        获取指定知识点对应的总结
        """
        return self.index_system.get_knowledge_point(knowledge_id)['summry']
    
    def get_knowledge_name_by_knowledge_id(self, knowledge_id: str) -> str:
        """
        获取指定知识点对应的名称
        """
        return self.index_system.get_knowledge_point(knowledge_id)['title']
    
    def get_questions_by_chapter(self, chapter_id: str) -> List[Dict]:
        """
        获取指定章节的所有问题
        
        Args:
            chapter_id: 章节ID，例如 "01"
            
        Returns:
            问题列表
        """
        questions = []
        for q in self.index_system.get_questions_by_chapter(chapter_id):
            # 返回精简版的问题列表，只包含必要信息
            questions.append({
                "id": q["id"],
                "title": q["title"],
                "type": q.get("type", "选择题"),
                "difficulty": q.get("difficulty", "中等")
            })
        return questions
    
    def get_question_detail(self, question_id: str) -> Optional[Dict]:
        """
        获取问题详情
        
        Args:
            question_id: 问题ID，例如 "q011002"
            
        Returns:
            问题详情
        """
        return self.index_system.get_question(question_id)
    
    def create_session(self, question_id: str) -> str:
        """
        创建问答会话
        
        Args:
            question_id: 问题ID
            
        Returns:
            会话ID
        """
        # 获取问题详情
        question = self.index_system.get_question(question_id)
        if not question:
            raise ValueError(f"找不到问题: {question_id}")
        
        # 创建会话ID
        session_id = str(uuid4())
        
        # 初始化会话元数据 (不存储消息历史，由LangGraph管理)
        self.sessions[session_id] = {
            "question_id": question_id,
            "question": question,
            "status": "created",
            "last_evaluation": {}  # 最近一次评估结果
        }
        
        return session_id
    
    async def process_answer(self, session_id: str, answer: str):
        """
        处理用户回答
        
        Args:
            session_id: 会话ID
            answer: 用户回答内容
            
        Returns:
            处理结果，包含AI回复和评估结果
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"找不到会话: {session_id}")
        
        # 准备用户消息
        user_message = HumanMessage(content=answer)
        
        # 准备工作流配置 - 使用会话的thread_id
        config = {"configurable": {"thread_id": session_id}}
        
        # 获取当前会话的工作流状态
        inputs = {
            "messages": [user_message],  # 只传递当前消息，历史消息由LangGraph基于thread_id管理
            "question": [session["question"]],
            "evaluation": {},
            "log": ""
        }
        
        print("开始处理回答...")
        async for msg, metadata in self.workflow.astream(inputs, config, stream_mode="messages"):
            yield msg.content, metadata['langgraph_node']
        

    def get_session_info(self, session_id: str) -> Dict:
        """获取会话信息"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"找不到会话: {session_id}")
        
        return {
            "session_id": session_id,
            "question_id": session["question_id"],
            "status": session["status"],
            "last_evaluation": session["last_evaluation"]
            # 注意：我们不再返回历史消息，因为它们由LangGraph管理
        }
    
    def get_related_knowledge_points(self, question_id: str) -> List[Dict]:
        """
        获取问题相关的知识点
        
        Args:
            question_id: 问题ID
            
        Returns:
            相关知识点列表
        """
        question = self.get_question_detail(question_id)
        if not question or "knowledge_points" not in question:
            return []
        
        knowledge_points = []
        for kp_id in question["knowledge_points"]:
            kp = self.index_system.get_knowledge_point(kp_id)
            if kp:
                knowledge_points.append({
                    "id": kp_id,
                    "title": kp.get("title", ""),
                    "summry": kp.get("summry", "")
                })
        
        return knowledge_points
    
    def get_similar_questions(self, question_id: str, limit: int = 5) -> List[Dict]:
        """
        获取与当前问题相似的其他问题
        
        Args:
            question_id: 问题ID
            limit: 返回的问题数量限制
            
        Returns:
            相似问题列表
        """
        question = self.get_question_detail(question_id)
        if not question or "knowledge_points" not in question:
            return []
        
        # 基于共同知识点查找相似题目
        similar_questions = []
        seen_ids = {question_id}  # 排除当前问题
        
        for kp_id in question["knowledge_points"]:
            questions = self.index_system.get_questions_by_knowledge(kp_id)
            for q in questions:
                q_id = q["id"]
                if q_id not in seen_ids:
                    similar_questions.append({
                        "id": q_id,
                        "title": q["title"],
                        "type": q.get("type", "选择题")
                    })
                    seen_ids.add(q_id)
                    
                    if len(similar_questions) >= limit:
                        return similar_questions
        
        return similar_questions
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False