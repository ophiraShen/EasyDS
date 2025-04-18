from fastapi import APIRouter, HTTPException
from web.services.qa_service import QAService

router = APIRouter()
qa_service = QAService()

@router.get("/knowledge/chapters", tags=["knowledge"])
async def get_chapter_knowledge_points():
    """获取所有章节的知识点"""
    try:
        knowledge_points = qa_service.chapter_knowledge_points()
        return knowledge_points
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/{knowledge_id}", tags=["knowledge"])
async def get_knowledge_summary(knowledge_id: str):
    """获取指定知识点的概要"""
    try:
        summary = qa_service.knowledge_points_summary_by_knowledge_id(knowledge_id)
        if not summary:
            raise HTTPException(status_code=404, detail=f"知识点未找到: {knowledge_id}")
        return summary
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/{knowledge_id}/title", tags=["knowledge"])
async def get_knowledge_title(knowledge_id: str):
    """获取指定知识点的标题"""
    try:
        title = qa_service.get_knowledge_title(knowledge_id)
        if not title:
            raise HTTPException(status_code=404, detail=f"知识点标题未找到: {knowledge_id}")
        return {"id": knowledge_id, "title": title}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/knowledge/details/all", tags=["knowledge"])
async def get_all_knowledge_details():
    """获取所有知识点的详细信息（ID和标题）"""
    try:
        details = qa_service.get_all_knowledge_details()
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 