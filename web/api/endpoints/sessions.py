from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Optional
from web.models.schemas import SessionCreate
from web.services.qa_service import QAService
import json
import asyncio
import logging  # 添加日志模块

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
qa_service = QAService()

@router.post("/sessions", tags=["sessions"])
async def create_session(session_data: SessionCreate):
    """创建新会话"""
    try:
        session_id = qa_service.create_session(session_data.question_id)
        return {"session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/sessions/{session_id}/messages", tags=["sessions"])
async def send_message(session_id: str, content: str, request: Request):
    """发送消息并获取流式响应"""
    try:
        logger.info(f"接收消息请求 - session_id: {session_id}, content: {content}")
        
        # 创建一个SSE流式响应
        async def event_generator():
            logger.info("开始生成事件流")
            try:
                async for chunk, node in qa_service.process_answer(session_id, content):
                    if await request.is_disconnected():
                        logger.info("客户端断开连接")
                        break
                        
                    # 构建SSE消息
                    data = json.dumps({
                        "content": chunk,
                        "node": node
                    })
                    logger.info(f"生成消息块 - node: {node}, chunk长度: {len(chunk)}")
                    yield f"data: {data}\n\n"
                    await asyncio.sleep(0.01)  # 小延迟，防止浏览器过载
                    
                # 发送结束事件
                logger.info("完成消息生成，发送结束事件")
                yield "event: end\ndata: \n\n"
            except Exception as e:
                logger.error(f"事件生成器错误: {str(e)}")
                # 确保在发生错误时仍然发送结束事件
                yield "event: end\ndata: \n\n"
                
        logger.info("创建StreamingResponse")
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
    except ValueError as e:
        logger.error(f"发送消息错误: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/info", tags=["sessions"])
async def get_session_info(session_id: str):
    """获取会话信息"""
    try:
        info = qa_service.get_session_info(session_id)
        return info
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/sessions/{session_id}", tags=["sessions"])
async def delete_session(session_id: str):
    """删除会话"""
    try:
        success = qa_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"会话未找到: {session_id}")
        return {"message": "会话已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 