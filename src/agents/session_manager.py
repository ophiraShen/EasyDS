# src/agents/session_manager.py
import json
import os
from uuid import uuid4
from typing import Dict, List, Optional, Any
from langchain_core.messages import HumanMessage

from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem
from .workflow import create_workflow

class SessionManager:
    """会话管理器，负责管理多个对话会话和问题选择"""
    
    def __init__(self, indices_path: str = '/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl', 
                questions_dir: str = '/root/autodl-tmp/EasyDS/data/ds_data/questions'):
        """
        初始化会话管理器
        
        Args:
            indices_path: 索引文件路径
            questions_dir: 问题目录路径
        """
        self.knowledge_system = KnowledgeIndexSystem.load_indices(indices_path)
        self.questions_dir = questions_dir
        self.sessions: Dict[str, Dict] = {}  # 存储会话信息
        self.questions_map = self._load_questions_map()
        self.graph = create_workflow()
    
    def _load_questions_map(self) -> Dict[str, Dict]:
        """加载所有问题到内存"""
        questions_map = {}
        
        # 遍历问题目录下的所有json文件
        for filename in os.listdir(self.questions_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.questions_dir, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    chapter_data = json.load(f)
                    
                    # 将问题添加到映射表中
                    for question in chapter_data:
                        question_id = question.get("id")
                        if question_id:
                            questions_map[question_id] = question
        
        return questions_map
    
    def get_questions_list(self, chapter: Optional[str] = None) -> List[Dict]:
        """
        获取问题列表
        
        Args:
            chapter: 章节名称，如果提供则只返回该章节的问题
            
        Returns:
            问题列表，每个问题包含id、title等信息
        """
        result = []
        
        for question_id, question in self.questions_map.items():
            if chapter and not question_id.startswith(f"q{chapter}"):
                continue
                
            result.append({
                "id": question_id,
                "title": question.get("title", ""),
                "knowledge_points": question.get("knowledge_points", [])
            })
            
        return result
    
    def create_session(self, question_id: str) -> str:
        """
        创建新的会话
        
        Args:
            question_id: 问题ID
            
        Returns:
            会话ID
        """
        # 获取问题详情
        question = self.knowledge_system.get_question(question_id)
        if not question:
            question = self.questions_map.get(question_id)
            if not question:
                raise ValueError(f"找不到问题ID: {question_id}")
        
        # 创建会话ID
        session_id = str(uuid4())
        
        # 存储会话信息
        self.sessions[session_id] = {
            "question_id": question_id,
            "question": question,
            "messages": [],
            "thread_id": str(uuid4()),  # 为LangGraph创建一个线程ID
            "evaluation": {}
        }
        
        return session_id
    
    async def answer_question(self, session_id: str, answer: str) -> str:
        """
        回答问题
        
        Args:
            session_id: 会话ID
            answer: 用户回答
            
        Returns:
            AI回复内容
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"找不到会话ID: {session_id}")
        
        # 准备输入
        messages = session["messages"]
        if not messages:  # 如果是首次回答
            messages = [HumanMessage(content=answer)]
        else:
            # 追加用户回答
            messages.append(HumanMessage(content=answer))
        
        session["messages"] = messages
        
        config = {"configurable": {"thread_id": session["thread_id"]}}
        inputs = {
            "messages": messages,
            "question": [session["question"]],
            "evaluation": session.get("evaluation", {}),
            "log": ""
        }
        
        # 收集AI回复
        response = ""
        async for msg, metadata in self.graph.astream(inputs, config, stream_mode="messages"):
            response += msg.content
            
            # 更新会话状态
            if "evaluation" in metadata:
                session["evaluation"] = metadata["evaluation"]
        
        # 返回回复内容
        return response
    
    def get_session(self, session_id: str) -> Dict:
        """获取会话信息"""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"找不到会话ID: {session_id}")
        return session
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False