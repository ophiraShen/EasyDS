# EasyDS动态提示词生成系统设计文档

## 1. 系统概述

动态提示词生成系统是EasyDS的核心组件之一，采用DPO和RLHF两种方案进行对比实验，基于 glm-4-9b-chat 模型实现针对性的教学提示词生成。RLHF部分采用OpenRLHF框架实现，以提高训练效率和性能。

## 2. 实现进度

### 2.1 已完成部分
1. **数据准备**
   - 收集并处理了教学对话数据
   - 构建了符合OpenRLHF格式的训练数据
   - 完成了数据集的划分（训练集/测试集）

2. **RLHF-SFT阶段**
   - 基于OpenRLHF框架完成SFT训练
     * 使用LoRA进行参数高效微调
     * 采用DeepSpeed ZeRO-3优化训练过程
     * 实现了BF16精度训练
     * 启用了Flash Attention加速
   
   - LoRA模型合并
     * 成功将训练好的LoRA权重合并到基础模型

3. **基础设施**
   - 环境配置完成
   - 训练脚本开发
   - 模型保存与加载机制

4. **奖励模型(RM)数据准备**
   - 完成了奖励模型训练数据的设计方案
   - 制定了优质回答与较差回答的对比标准
   - 设计了数据处理脚本框架
   - 实现了 RewardModelDataProcessor 类用于数据处理
   - 创建了 rm_raw_data.jsonl 原始数据集

### 2.2 进行中任务
1. **奖励模型(RM)训练**
   - 数据处理脚本实现完成
   - 训练脚本优化
   - 模型评估方案实施

2. **PPO训练**
   - 环境配置
   - 训练参数优化
   - 分布式训练设置

3. **DPO方案**
   - 偏好数据构建
   - 训练框架搭建
   - 评估方案设计

## 3. 详细设计

### 3.1 RLHF实现细节（基于OpenRLHF）

#### SFT阶段（已完成）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_sft_mixtral_lora.sh`


#### LoRA模型合并（已完成）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/lora_combined.sh`


#### 奖励模型训练（进行中）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`

**数据准备详情：**
- 基于SFT数据集构建偏好对比数据
- 每个训练样本包含一个优质回答和一个较差回答
- 优质回答采用原SFT数据集中的教师回答
- 较差回答通过特定策略生成，包括：
  * 直接给答案型：违背"非必要情况下不要直接给出答案"的原则
  * 缺乏引导性：简单肯定/否定学生回答，没有进一步引导
  * 知识错误型：包含错误的数据结构知识
  * 不符合费曼学习法：没有引导学生自己思考和发现答案

**数据处理流程：**
1. 读取原始 rm_raw_data.jsonl 数据
2. 提取问题和对话内容作为 prompt
3. 使用原始教师回答作为优质回答(chosen)
4. 使用预先准备的较差回答(rejected)
5. 转换为OpenRLHF支持的格式
6. 按照 9:1 的比例分割为训练集和测试集

**数据处理实现：**
- 新增 `RewardModelDataProcessor` 类处理奖励模型数据
- 实现 `convert_to_training_format` 方法转换数据格式
- 实现 `process_file` 方法处理文件并分割数据集
- 创建 `generate_rm_data.py` 脚本用于数据处理

**数据增强策略：**
- 为同一问题构建多种类型的较差回答
- 对原始问题进行轻微变形，生成更多训练数据
- 确保较差回答的多样性，覆盖不同类型的问题

#### PPO训练（计划中）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_ppo.sh`


### 3.2 数据处理适配

为了适配OpenRLHF框架，已将数据转换为其支持的格式：

#### SFT数据格式（已完成）
data_path: `/autodl-tmp/EasyDS/data/rlhf_data/sft/train.jsonl`
```python
{'input':
    '[{"role": "system", "content": "你是一个提示词生成助手。请根据问题、用户与教师智能体的对话，生成进一步的教学指导提示词。"}, {"role": "user", "content": "问题：BFS和DFS的主要区别是什么？\\n学生回答：BFS用队列实现，按层遍历；DFS用栈实现，优先深入子节点"}]',
 'output': 
    '{"role": "assistant", "content": "现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\\n学生已准确掌握基础概念，需提升至应用层：\\n1. 设计迷宫问题比较两种算法效率\\n2. 引入加权图下的扩展应用\\n3. 探讨递归实现DFS的栈溢出风险\\n请用工程案例引导高阶思考。"}'}
```

#### 奖励模型数据格式（已完成）
data_path: `/autodl-tmp/EasyDS/data/rlhf_data/rm/train.jsonl`
```python
{
    "prompt": "问题：BFS和DFS的主要区别是什么？\n学生回答：BFS用队列实现，按层遍历；DFS用栈实现，优先深入子节点",
    "chosen": "现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\n学生已准确掌握基础概念，需提升至应用层：\n1. 设计迷宫问题比较两种算法效率\n2. 引入加权图下的扩展应用\n3. 探讨递归实现DFS的栈溢出风险\n请用工程案例引导高阶思考。",
    "rejected": "你的回答基本正确。BFS确实使用队列实现，按层次遍历图或树；而DFS使用栈实现，优先深入探索。BFS适合寻找最短路径，DFS适合探索所有可能路径。在实现上，BFS的空间复杂度通常较高，因为需要存储整层节点。"
}
```

#### PPO提示数据格式（准备中）
data_path: `/autodl-tmp/EasyDS/data/rlhf_data/ppo/train.jsonl`
```python
{
    "input": "请解释二叉树的基本概念"
}
```

### 3.3 奖励模型数据处理实现

为了高效处理奖励模型训练数据，实现了以下数据处理类和脚本：

#### RewardModelDataProcessor 类
```python
class RewardModelDataProcessor(DataProcessor):
    """奖励模型数据处理类"""

    def convert_to_training_format(self, example: Dict) -> Dict:
        """将原始数据转换为奖励模型训练格式"""
        # 提取问题和对话内容作为prompt
        prompt = example["question"]
        if "dialogues" in example and example["dialogues"]:
            for dialogue in example["dialogues"]:
                if dialogue["role"] == "user":
                    prompt += f"\n学生回答：{dialogue['content']}"
                elif dialogue["role"] == "assistant":
                    prompt += f"\n教师回答：{dialogue['content']}"
        
        # 提取优质回答和较差回答
        chosen = example["chosen"]
        rejected = example["rejected"]
        
        return {
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected
        }
    
    def process_file(self, input_file: str, output_train_file: str, output_test_file: str, test_ratio: float = 0.1):
        """处理文件并分割为训练集和测试集"""
        # 加载原始数据
        raw_data = self.load_jsonl(input_file)
        print(f"加载了 {len(raw_data)} 条原始数据")
        
        # 转换为训练格式
        processed_data = []
        for example in raw_data:
            processed_example = self.convert_to_training_format(example)
            processed_data.append(processed_example)
        
        print(f"处理完成 {len(processed_data)} 条数据")
        
        # 分割为训练集和测试集
        train_data, test_data = self.split_data(processed_data, test_ratio)
        print(f"分割为 {len(train_data)} 条训练数据和 {len(test_data)} 条测试数据")
        
        # 保存为JSONL文件
        self.save_jsonl(train_data, output_train_file)
        self.save_jsonl(test_data, output_test_file)
        print(f"已保存训练数据到 {output_train_file}")
        print(f"已保存测试数据到 {output_test_file}")
```

#### 数据处理脚本
```python
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
```

## 4. 评估方案

### 4.1 模型评估
1. **质量评估**
   - 提示词相关性
   - 教学引导效果
   - 语言流畅度
   - 费曼学习法原则符合度

2. **性能评估**
   - 训练效率
   - 推理速度
   - 资源消耗
   - 模型收敛性

### 4.2 对比实验
1. **RLHF vs DPO**
   - 训练时长
   - 计算资源
   - 生成质量
   - 部署难度
   - 数据需求差异

2. **奖励模型质量评估**
   - 偏好预测准确率
   - 对不同类型较差回答的识别能力
   - 泛化能力测试

## 5. 后续计划

### 5.1 近期任务（1-2周）
1. **奖励模型训练**
   - [x] 设计奖励模型数据准备方案
   - [x] 创建 rm_raw_data.jsonl 原始数据
   - [x] 实现 RewardModelDataProcessor 类
   - [x] 实现数据处理脚本
   - [ ] 执行奖励模型训练
   - [ ] 评估奖励模型质量
   - [ ] 合并LoRA权重（如使用LoRA）

2. **PPO训练**
   - [ ] 准备PPO训练数据
   - [ ] 配置PPO训练参数
   - [ ] 执行PPO训练
   - [ ] 模型评估与调优

3. **DPO框架搭建**
   - [ ] 设计数据收集方案
   - [ ] 开发训练脚本
   - [ ] 构建评估体系

### 5.2 中期目标（2-4周）
1. **系统集成**
   - [ ] 模型部署优化
   - [ ] 接口设计与实现
   - [ ] 性能调优

2. **实验评估**
   - [ ] 完整对比实验
   - [ ] 数据分析与可视化
   - [ ] 撰写技术报告

## 6. 优势与挑战

### 6.1 OpenRLHF优势
- **高性能**：利用DeepSpeed ZeRO-3和Flash Attention加速训练
- **参数高效**：通过LoRA减少训练参数量，降低资源需求
- **分布式训练**：支持将Actor、Reward、Reference和Critic模型分布在不同GPU上
- **易用性**：与Huggingface模型和数据集完全兼容

### 6.2 潜在挑战
- **资源需求**：完整RLHF流程需要较多计算资源
- **训练稳定性**：PPO训练可能面临收敛不稳定的问题
- **数据质量**：奖励模型训练数据的质量对最终效果影响较大
- **超参数调优**：需要针对glm-4-9b-chat模型特点调整训练参数
- **较差回答生成**：构建高质量的较差回答需要精心设计，避免过于明显的区分

### 6.3 AutoDL环境优化
- **资源监控**：使用AutoDL提供的监控工具实时跟踪GPU使用情况
- **断点续训**：利用AutoDL的持久化存储实现训练中断后的恢复
- **模型备份**：定期将模型保存到AutoDL的永久存储区域
- **分布式训练**：根据AutoDL实例类型优化分布式训练配置

## 7. 参考资源

1. **OpenRLHF文档**
   - [官方文档](https://openrlhf.readthedocs.io/en/latest/index.html)
   - [快速入门指南](https://openrlhf.readthedocs.io/en/latest/quick_start.html)
   - [RLHF训练指南](https://openrlhf.readthedocs.io/en/latest/rl.html)
   - [性能调优指南](https://openrlhf.readthedocs.io/en/latest/performance.html)

2. **相关脚本**
   - SFT训练脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_sft_mixtral_lora.sh`
   - LoRA合并脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/lora_combined.sh`
   - 奖励模型训练脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`
   - 数据处理脚本：`/autodl-tmp/EasyDS/data_processing/generate_rm_data.py`