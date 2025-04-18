from fastapi import APIRouter, HTTPException
from web.services.qa_service import QAService

router = APIRouter()
qa_service = QAService()

@router.get("/chapters/{chapter_id}/questions", tags=["questions"])
async def get_questions_by_chapter(chapter_id: str):
    """获取章节下的问题列表"""
    try:
        questions = qa_service.get_questions_by_chapter(chapter_id)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{question_id}", tags=["questions"])
async def get_question_detail(question_id: str):
    """获取问题详情"""
    try:
        question = qa_service.get_question_detail(question_id)
        if not question:
            raise HTTPException(status_code=404, detail=f"问题未找到: {question_id}")
        return question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{question_id}/knowledge-points", tags=["questions"])
async def get_knowledge_points(question_id: str):
    """获取问题相关知识点"""
    try:
        kps = qa_service.get_related_knowledge_points(question_id)
        return kps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions/{question_id}/similar", tags=["questions"])
async def get_similar_questions(question_id: str):
    """获取相似问题"""
    try:
        questions = qa_service.get_similar_questions(question_id)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 