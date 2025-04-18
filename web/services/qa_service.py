from src.knowledge_qa_system import KnowledgeQASystem
import logging

# 配置日志
logger = logging.getLogger(__name__)

class QAService:
    """问答服务，封装KnowledgeQASystem功能"""
    
    def __init__(self):
        """初始化服务"""
        self.qa_system = KnowledgeQASystem()
    
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
                logger.info(f"接收到底层响应 - node: {node}, chunk长度: {len(chunk)}")
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