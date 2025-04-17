import json
import os
import gc
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

# 读取系统提示
with open("/root/autodl-tmp/EasyDS/src/agents/prompts/knowledge_point_summry_promot.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()

# 读取知识点数据
with open("/root/autodl-tmp/EasyDS/data/ds_data/knowledgepoints/all_knowledgepoints.json", "r", encoding="utf-8") as f:
    all_knowledgepoints = json.load(f)

# 创建处理批次 - 分批处理可以降低内存压力
batch_size = 10
total_items = len(all_knowledgepoints)
batches = [range(i, min(i + batch_size, total_items)) for i in range(0, total_items, batch_size)]

# 设置线程数 - 根据当前低配置环境调整
max_workers = 2  # 低配置环境(0.5核CPU, 2GB内存)下推荐使用2个线程

# 并行处理函数
def process_item(idx):
    try:
        # 创建LLM实例 - 每个线程独立创建实例避免冲突
        llm = ChatDeepSeek(model="deepseek-chat", api_key=os.getenv("DEEPSEEK_API_KEY"))
        prompt = ChatPromptTemplate([
            ("system", system_prompt),
            ("human", "知识点名称：{title}\n知识点内容：{content}"),
        ])
        chain = prompt | llm
        
        knowledge_point = all_knowledgepoints[idx]
        summry = chain.invoke({"title": knowledge_point["title"], "content": knowledge_point["description"]})
        knowledge_point["summry"] = summry.content
        
        # 添加间隔，避免API请求过于频繁
        time.sleep(0.5)
        return idx, knowledge_point
    except Exception as e:
        print(f"处理知识点 {idx+1} 时出错: {str(e)}")
        return idx, None
    finally:
        # 主动清理内存
        gc.collect()

print(f"总共 {total_items} 条数据，分为 {len(batches)} 批次处理")

# 按批次处理
for batch_idx, batch_range in enumerate(batches):
    print(f"开始处理第 {batch_idx+1}/{len(batches)} 批")
    
    # 使用线程池并行处理当前批次
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_item, i): i for i in batch_range}
        
        # 使用tqdm显示进度条
        for future in tqdm(futures, desc=f"处理批次 {batch_idx+1}"):
            idx, result = future.result()
            if result:
                all_knowledgepoints[idx] = result
    
    # 每批次结束后保存结果
    with open("/root/autodl-tmp/EasyDS/data/ds_data/knowledgepoints/all_knowledgepoints.json", "w", encoding="utf-8") as f:
        json.dump(all_knowledgepoints, f, ensure_ascii=False, indent=4)
    print(f"完成并保存了第 {batch_idx+1} 批，已处理 {min((batch_idx+1)*batch_size, total_items)} 条数据")
    
    # 批次间清理内存
    gc.collect()
    time.sleep(1)  # 给系统喘息的时间

print("所有知识点处理完成") 