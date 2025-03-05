#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成奖励模型训练数据脚本
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到系统路径
project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

from src.data.processor import RewardModelDataProcessor


def main():
    parser = argparse.ArgumentParser(description="生成奖励模型训练数据")
    parser.add_argument("--input", type=str, default="/autodl-tmp/EasyDS/data/rlhf_data/rm/rm_raw_data.jsonl",
                        help="输入的原始数据文件路径")
    parser.add_argument("--output_dir", type=str, default="/autodl-tmp/EasyDS/data/rlhf_data/rm",
                        help="输出目录")
    parser.add_argument("--test_ratio", type=float, default=0.1,
                        help="测试集比例")
    args = parser.parse_args()

    # 确保输出目录存在
    os.makedirs(args.output_dir, exist_ok=True)

    # 设置输出文件路径
    output_train_file = os.path.join(args.output_dir, "train.jsonl")
    output_test_file = os.path.join(args.output_dir, "test.jsonl")

    # 初始化数据处理器
    processor = RewardModelDataProcessor()

    # 处理数据
    processor.process_file(
        input_file=args.input,
        output_train_file=output_train_file,
        output_test_file=output_test_file,
        test_ratio=args.test_ratio
    )

    print(f"数据处理完成！")
    print(f"训练数据保存至: {output_train_file}")
    print(f"测试数据保存至: {output_test_file}")


if __name__ == "__main__":
    main() 