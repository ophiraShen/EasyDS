from fastapi import APIRouter, HTTPException
from web.services.qa_service import QAService

router = APIRouter()
qa_service = QAService()

@router.get("/chapters", tags=["chapters"])
async def get_chapters():
    """获取所有章节"""
    try:
        chapters = qa_service.get_chapters()
        return chapters
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 