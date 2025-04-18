import sys
sys.path.append('/root/autodl-tmp/EasyDS')
from src.agents.workflow import create_workflow
from data.ds_data.data_processing.index_builder import KnowledgeIndexSystem
import asyncio

system = KnowledgeIndexSystem.load_indices('/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl')

graph = create_workflow()

from uuid import uuid4
config = {"configurable": {"thread_id": str(uuid4())}}
inputs = {
    "messages": [({"role": "user", "content": "A"})],
    "question": [system.get_question("q011002")],
    "evaluation": {},
    "log": ""
}

async def main():
    async for msg, metadata in graph.astream(inputs, config, stream_mode="messages"):
        print(msg.content, end="|")

if __name__ == "__main__":
    asyncio.run(main())