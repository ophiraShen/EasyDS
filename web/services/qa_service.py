from src.knowledge_qa_system import KnowledgeQASystem
import logging

# 配置日志
logger = logging.getLogger(__name__)

class QAService:
    """问答服务，封装KnowledgeQASystem功能"""
    
    def __init__(self):
        """初始化服务"""
        self.qa_system = KnowledgeQASystem(
            router_model_type="tongyi",
            teacher_model_type="tongyi",
            student_model_type="tongyi")
    
    def get_chapters(self):
        """获取所有章节"""
        return self.qa_system.get_chapters()
    
    def get_questions_by_chapter(self, chapter_id):
        """获取章节下的问题列表"""
        return self.qa_system.get_questions_by_chapter(chapter_id)
    
    def get_question_detail(self, question_id):
        """获取问题详情"""
        return self.qa_system.get_question_detail(question_id)
    
    def create_session(self, question_id):
        """创建会话"""
        return self.qa_system.create_session(question_id)
    
    async def process_answer(self, session_id, answer):
        """处理回答，流式输出"""
        logger.info(f"QAService.process_answer 被调用 - session_id: {session_id}")
        try:
            async for chunk, node in self.qa_system.process_answer(session_id, answer):
                # logger.info(f"接收到底层响应 - node: {node}, chunk长度: {len(chunk)}")
                yield chunk, node
        except Exception as e:
            logger.error(f"process_answer 处理错误: {str(e)}")
            # 发生错误时仍然生成一个错误消息
            yield f"处理您的回答时发生错误: {str(e)}", "system"
    
    def get_session_info(self, session_id):
        """获取会话信息"""
        return self.qa_system.get_session_info(session_id)
    
    def get_related_knowledge_points(self, question_id):
        """获取问题相关知识点"""
        return self.qa_system.get_related_knowledge_points(question_id)
    
    def get_similar_questions(self, question_id):
        """获取相似问题"""
        return self.qa_system.get_similar_questions(question_id)
    
    def delete_session(self, session_id):
        """删除会话"""
        return self.qa_system.delete_session(session_id)
        
    def chapter_knowledge_points(self):
        """获取所有章节的知识点"""
        return self.qa_system.chapter_knowledge_points()
        
    def knowledge_points_summary_by_knowledge_id(self, knowledge_id):
        """获取指定知识点的概要"""
        return self.qa_system.knowledge_points_summary_by_knowledge_id(knowledge_id)
    
    def get_knowledge_title(self, knowledge_id):
        """获取指定知识点的标题"""
        try:
            return self.qa_system.get_knowledge_name_by_knowledge_id(knowledge_id)
        except Exception as e:
            logger.error(f"获取知识点标题错误: {str(e)}")
            return ""
    
    def get_all_knowledge_details(self):
        """获取所有知识点的详细信息（ID和标题）"""
        try:
            result = {}
            all_chapter_knowledge_points = self.chapter_knowledge_points()
            
            for chapter_id, knowledge_ids in all_chapter_knowledge_points.items():
                for knowledge_id in knowledge_ids:
                    if knowledge_id not in result:
                        title = self.get_knowledge_title(knowledge_id)
                        result[knowledge_id] = {
                            "id": knowledge_id,
                            "title": title
                        }
            
            return result
        except Exception as e:
            logger.error(f"获取所有知识点详情错误: {str(e)}")
            return {} 