"""
EasyDS 结构化问题数据库模式定义
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class RelatedKnowledgePoint(BaseModel):
    """关联知识点"""
    id: str = Field(..., description="关联知识点ID")
    relation_type: str = Field(..., description="关系类型: prerequisite, related, extension")


class RelatedQuestion(BaseModel):
    """关联问题"""
    id: str = Field(..., description="关联问题ID")
    relation_type: str = Field(..., description="关系类型: extension, application, contrast")


class ReferenceAnswer(BaseModel):
    """参考答案"""
    content: str = Field(..., description="答案内容")
    key_points: List[str] = Field(default_factory=list, description="关键点列表")
    explanation: str = Field(default="", description="详细解释")


class Chapter(BaseModel):
    """章节模型"""
    id: str = Field(..., description="章节唯一标识符")
    title: str = Field(..., description="章节标题")
    parent_id: Optional[str] = Field(None, description="父章节ID（可选）")
    order: int = Field(0, description="排序顺序")
    description: str = Field("", description="章节描述")
    knowledge_points: List[str] = Field(default_factory=list, description="包含的知识点ID列表")
    sub_chapters: List[str] = Field(default_factory=list, description="子章节ID列表")


class KnowledgePoint(BaseModel):
    """知识点模型"""
    id: str = Field(..., description="知识点唯一标识符")
    title: str = Field(..., description="知识点标题")
    chapter_id: str = Field(..., description="所属章节ID")
    description: str = Field("", description="知识点详细描述")
    related_points: List[RelatedKnowledgePoint] = Field(default_factory=list, description="关联知识点")
    questions: List[str] = Field(default_factory=list, description="相关问题ID列表")


class Question(BaseModel):
    """问题模型"""
    id: str = Field(..., description="问题唯一标识符")
    title: str = Field(..., description="问题标题")
    content: str = Field(..., description="问题内容")
    difficulty: int = Field(1, description="难度等级 (1-5)")
    type: str = Field(..., description="问题类型 (concept, calculation, application)")
    knowledge_points: List[str] = Field(default_factory=list, description="相关知识点ID列表")
    related_questions: List[RelatedQuestion] = Field(default_factory=list, description="相关问题（用于扩展）")
    reference_answer: ReferenceAnswer = Field(..., description="参考答案")


# 数据库模式
class DatabaseSchema:
    """数据库模式定义"""
    
    @staticmethod
    def get_chapter_schema() -> Dict[str, Any]:
        """获取章节集合的模式"""
        return {
            "bsonType": "object",
            "required": ["id", "title"],
            "properties": {
                "id": {"bsonType": "string"},
                "title": {"bsonType": "string"},
                "parent_id": {"bsonType": ["string", "null"]},
                "order": {"bsonType": "int"},
                "description": {"bsonType": "string"},
                "knowledge_points": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "sub_chapters": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                }
            }
        }
    
    @staticmethod
    def get_knowledge_point_schema() -> Dict[str, Any]:
        """获取知识点集合的模式"""
        return {
            "bsonType": "object",
            "required": ["id", "title", "chapter_id"],
            "properties": {
                "id": {"bsonType": "string"},
                "title": {"bsonType": "string"},
                "chapter_id": {"bsonType": "string"},
                "description": {"bsonType": "string"},
                "related_points": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["id", "relation_type"],
                        "properties": {
                            "id": {"bsonType": "string"},
                            "relation_type": {"bsonType": "string"}
                        }
                    }
                },
                "questions": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                }
            }
        }
    
    @staticmethod
    def get_question_schema() -> Dict[str, Any]:
        """获取问题集合的模式"""
        return {
            "bsonType": "object",
            "required": ["id", "title", "content", "type", "reference_answer"],
            "properties": {
                "id": {"bsonType": "string"},
                "title": {"bsonType": "string"},
                "content": {"bsonType": "string"},
                "difficulty": {"bsonType": "int"},
                "type": {"bsonType": "string"},
                "knowledge_points": {
                    "bsonType": "array",
                    "items": {"bsonType": "string"}
                },
                "related_questions": {
                    "bsonType": "array",
                    "items": {
                        "bsonType": "object",
                        "required": ["id", "relation_type"],
                        "properties": {
                            "id": {"bsonType": "string"},
                            "relation_type": {"bsonType": "string"}
                        }
                    }
                },
                "reference_answer": {
                    "bsonType": "object",
                    "required": ["content"],
                    "properties": {
                        "content": {"bsonType": "string"},
                        "key_points": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "explanation": {"bsonType": "string"}
                    }
                }
            }
        }
} 