# EasyDS/scripts/prepare_training_data.py
import json
import random
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
ROOT_DIR = Path(__file__).parent.parent.parent
print(ROOT_DIR)

from processor import SFTDataProcessor



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

def main():
    # 1. 加载原始数据
    data_path = ROOT_DIR / "data/rlhf_data/sft/sft_raw_data.jsonl"
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = [json.loads(line) for line in f]

    # 2. 划分数据集
    print("\nSplitting dataset...")
    train_data, val_data, test_data = split_dataset(data=raw_data)
    print(f"Train size: {len(train_data)}")
    print(f"Val size: {len(val_data)}")
    print(f"Test size: {len(test_data)}")

    # 3. 处理为训练格式
    print("\nProcessing data into training format...")

    processor = SFTDataProcessor()

    # 处理训练集
    train_processed = [processor.convert_to_training_format(example) 
                        for example in train_data]

    # 处理验证集
    val_processed = [processor.convert_to_training_format(example) 
                    for example in val_data]

    # 处理测试集
    test_processed = [processor.convert_to_training_format(example) 
                        for example in test_data]

    # 4. 保存处理后的数据
    output_dir = ROOT_DIR / "data/rlhf_data/sft"
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "train.jsonl", 'w', encoding='utf-8') as f:
        for item in train_processed:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(output_dir / "val.jsonl", 'w', encoding='utf-8') as f:
        for item in val_processed:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(output_dir / "test.jsonl", 'w', encoding='utf-8') as f:
        for item in test_processed:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print("\nData preparation completed!")
    print(f"Files saved to {output_dir}")

if __name__ == "__main__":
    main() 
