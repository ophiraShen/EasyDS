# src/agents/example.py
import sys
import os
from dotenv import load_dotenv
sys.path.append("/root/autodl-tmp/EasyDS")  # 添加项目根目录
load_dotenv()

from uuid import uuid4
from langchain_core.messages import HumanMessage
from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem
from src.agents import create_workflow

async def main():
    # 初始化系统
    system = KnowledgeIndexSystem.load_indices('/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl')
    question = system.get_question("q011002")

    # 创建工作流
    graph = create_workflow()
    
    # 准备输入
    config = {"configurable": {"thread_id": str(uuid4())}}
    inputs = {
        "messages": [HumanMessage(content="C")],
        "question": [question],
        "evaluation": {},
        "log": ""
    }
    
    # 运行工作流
    async for msg, metadata in graph.astream(inputs, config, stream_mode="messages"):
        print(msg.content, end="")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())