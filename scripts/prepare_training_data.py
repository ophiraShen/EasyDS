# EasyDS/scripts/prepare_training_data.py
# %%
import json
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
ROOT_DIR = Path(__file__).parent.parent

from src.data.processor import SFTDataProcessor
from src.data.augmenter import DataAugmenter
# %%


# 分析数据分布
def analyze_data_distribution(data):
    stats = {
        "total_samples": len(data),
        "knowledge_points": set(),
        "understanding_levels": set(),
        "avg_missing_points": 0,
        "topic_distribution": {}
    }
    
    for item in data:
        # 收集知识点
        stats["knowledge_points"].update(item["response_analysis"]["knowledge_points"])
        # 记录理解水平
        stats["understanding_levels"].add(item["response_analysis"]["understanding_level"])
        # 统计缺失点
        stats["avg_missing_points"] += len(item["response_analysis"]["missing_points"])
        # 记录主题分布
        topic = extract_main_topic(item["question"])
        stats["topic_distribution"][topic] = stats["topic_distribution"].get(topic, 0) + 1
    
    stats["avg_missing_points"] /= len(data)
    return stats

# 建议划分比例：训练集70%，验证集15%，测试集15%
def split_dataset(data_path="", data=None):
    if data is None:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = [json.loads(line) for line in f]
    
    # 随机打乱数据
    random.shuffle(data)
    
    # 计算划分点
    train_size = int(0.7 * len(data))
    val_size = int(0.15 * len(data))
    
    # 划分数据集
    train_data = data[:train_size]
    val_data = data[train_size:train_size+val_size]
    test_data = data[train_size+val_size:]
    
    return train_data, val_data, test_data

# 使用已实现的DataAugmenter进行数据增强
def augment_training_data(train_data):
    augmenter = DataAugmenter()
    augmented_data = []
    
    for example in train_data:
        # 对每个样本进行增强
        variations = augmenter.augment_example(example)
        augmented_data.extend(variations)
    
    return augmented_data

def extract_main_topic(question: str) -> str:
    """从问题中提取主要主题
    
    主题分类：
    - 数据结构：链表、栈、队列、树、图、哈希表等
    - 算法：排序、搜索、动态规划等
    - 操作：遍历、插入、删除、查找等
    """
    # 定义主题关键词映射
    topic_keywords = {
        "链表": ["链表", "指针", "节点"],
        "栈": ["栈", "LIFO", "后进先出"],
        "队列": ["队列", "FIFO", "先进先出"],
        "树": ["树", "二叉树", "平衡树", "红黑树", "AVL", "B树"],
        "图": ["图", "顶点", "边", "深度优先", "广度优先", "DFS", "BFS"],
        "哈希表": ["哈希", "散列", "冲突"],
        "排序": ["排序", "冒泡", "快速", "归并", "堆排序"],
        "搜索": ["搜索", "查找", "遍历"],
        "动态规划": ["动态规划", "DP", "最优子结构"],
        "其他": []
    }
    
    # 将问题转换为小写以进行匹配
    question_lower = question.lower()
    
    # 遍历关键词映射查找匹配
    for topic, keywords in topic_keywords.items():
        for keyword in keywords:
            if keyword.lower() in question_lower:
                return topic
    
    # 如果没有找到匹配的主题，返回"其他"
    return "其他"

# %%
# def main():
# 1. 加载原始数据
data_path = ROOT_DIR / "data/sft_raw_data.jsonl"
with open(data_path, 'r', encoding='utf-8') as f:
    raw_data = [json.loads(line) for line in f]
print(raw_data[:5])

# %%
# 2. 分析数据分布
print("Analyzing data distribution...")
stats = analyze_data_distribution(raw_data)
print(stats)
# %%

print(f"Total samples: {stats['total_samples']}")
print(f"Unique knowledge points: {len(stats['knowledge_points'])}")
print(f"Understanding levels: {stats['understanding_levels']}")
print(f"Average missing points: {stats['avg_missing_points']:.2f}")

# %%
# 3. 划分数据集
print("\nSplitting dataset...")
train_data, val_data, test_data = split_dataset(data=raw_data)
print(f"Train size: {len(train_data)}")
print(f"Val size: {len(val_data)}")
print(f"Test size: {len(test_data)}")
# %%

# 4. 数据增强
print("\nAugmenting training data...")
augmenter = DataAugmenter()
augmented_train_data = augmenter.augment_dataset(train_data)
print(f"Augmented train size: {len(augmented_train_data)}")
# %%
# 5. 处理为训练格式
print("\nProcessing data into training format...")

augmented_train_data = train_data

processor = SFTDataProcessor()

# 处理训练集
train_processed = [processor.convert_to_training_format(example) 
                    for example in augmented_train_data]
# %%

# 处理验证集
val_processed = [processor.convert_to_training_format(example) 
                for example in val_data]

# 处理测试集
test_processed = [processor.convert_to_training_format(example) 
                    for example in test_data]

# 6. 保存处理后的数据
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / "train.json", 'w', encoding='utf-8') as f:
    json.dump(train_processed, f, ensure_ascii=False, indent=2)

with open(output_dir / "val.json", 'w', encoding='utf-8') as f:
    json.dump(val_processed, f, ensure_ascii=False, indent=2)

with open(output_dir / "test.json", 'w', encoding='utf-8') as f:
    json.dump(test_processed, f, ensure_ascii=False, indent=2)

print("\nData preparation completed!")
print(f"Files saved to {output_dir}")

# if __name__ == "__main__":
#     main() 
# %%

# 在数据增强后添加
print("\nAnalyzing augmented data distribution...")
augmented_stats = analyze_data_distribution(augmented_train_data)
print("Original vs Augmented:")
print(f"Samples: {len(train_data)} -> {len(augmented_train_data)}")
print(f"Knowledge points: {len(stats['knowledge_points'])} -> {len(augmented_stats['knowledge_points'])}")
print(f"Understanding levels: {stats['understanding_levels']} -> {augmented_stats['understanding_levels']}")
print("\nTopic distribution:")
for topic in sorted(set(stats['topic_distribution'].keys()) | set(augmented_stats['topic_distribution'].keys())):
    original = stats['topic_distribution'].get(topic, 0)
    augmented = augmented_stats['topic_distribution'].get(topic, 0)
    print(f"{topic}: {original} -> {augmented}")
