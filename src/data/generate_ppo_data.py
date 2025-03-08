# EasyDS/src/data/generate_ppo_data.py

# EasyDS/src/data/generate_ppo_data.py
import os
import argparse
from processor import PPODataProcessor

def main():
    parser = argparse.ArgumentParser(description="生成PPO训练数据")
    parser.add_argument("--input_file", type=str, default="/root/autodl-tmp/EasyDS/data/rlhf_data/sft/sft_raw_data.jsonl", 
                        help="输入SFT原始数据文件路径")
    parser.add_argument("--output_dir", type=str, default="/root/autodl-tmp/EasyDS/data/rlhf_data/ppo", 
                        help="输出PPO数据目录")
    parser.add_argument("--test_ratio", type=float, default=0.1, 
                        help="测试集比例")
    args = parser.parse_args()
    
    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 设置输出文件路径
    output_train_file = os.path.join(args.output_dir, "train_data.jsonl")
    output_test_file = os.path.join(args.output_dir, "test_data.jsonl")
    
    # 初始化处理器
    processor = PPODataProcessor()

    # 处理数据
    processor.process_file(
        input_file=args.input_file,
        output_train_file=output_train_file,
        output_test_file=output_test_file,
        test_ratio=args.test_ratio
    )
    
    # print(f"PPO数据生成完成！")
    # print(f"训练数据保存在: {output_train_file}")
    # print(f"测试数据保存在: {output_test_file}")

if __name__ == "__main__":
    main()