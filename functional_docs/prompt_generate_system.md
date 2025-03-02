# EasyDS动态提示词生成系统设计文档

## 1. 系统概述

动态提示词生成系统是EasyDS的核心组件之一，采用DPO和RLHF两种方案进行对比实验，基于Qwen2.5模型实现针对性的教学提示词生成。RLHF部分将采用OpenRLHF框架实现，以提高训练效率和性能。

## 2. 实现进度

### 2.1 已完成部分
1. **RLHF-SFT阶段**
   - 数据预处理模块
     * 实现了InputOutputDataset类
     * 支持JSONL格式数据加载
     * 完成提示词和响应的格式化处理
   
   - SFT训练框架
     * 基于Accelerator的分布式训练
     * LoRA参数高效微调
     * 支持DeepSpeed ZeRO-3优化
     * 实现了训练状态保存和恢复

2. **基础设施**
   - 环境配置完成
   - 数据处理流程搭建
   - 训练监控体系建立

### 2.2 进行中任务
1. **OpenRLHF框架集成**
   - 环境配置与依赖安装
   - 数据格式转换适配
   - 训练脚本开发

2. **DPO方案**
   - 偏好数据构建
   - 训练框架搭建
   - 评估方案设计

## 3. 详细设计

### 3.1 RLHF实现细节（基于OpenRLHF）

#### SFT阶段
```python
# 使用OpenRLHF的SFT训练命令
# openrlhf.cli.sft --config configs/rlhf/sft_config.yaml
```

SFT配置文件示例 (configs/rlhf/sft_config.yaml):
```yaml
model:
  model_name_or_path: "Qwen/Qwen2.5-7B"
  trust_remote_code: true
  use_flash_attention: true

tokenizer:
  tokenizer_name_or_path: "Qwen/Qwen2.5-7B"
  padding_side: "right"
  truncation_side: "right"
  trust_remote_code: true

dataset:
  train_file: "data/rlhf_data/sft/sft_train_data.jsonl"
  eval_file: "data/rlhf_data/sft/sft_eval_data.jsonl"
  format: "alpaca"  # 或根据实际数据格式选择

training:
  bf16: true
  fp16: false
  deepspeed: "configs/rlhf/zero_stage3_config.json"
  num_train_epochs: 3
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 4
  learning_rate: 5.0e-5
  weight_decay: 0.0
  warmup_ratio: 0.03
  evaluation_strategy: "steps"
  eval_steps: 500
  save_strategy: "steps"
  save_steps: 500
  save_total_limit: 3
  logging_steps: 10
  output_dir: "outputs/sft"
  
lora:
  use_lora: true
  r: 8
  lora_alpha: 16
  lora_dropout: 0.05
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]
```

#### 奖励模型训练
```python
# 使用OpenRLHF的奖励模型训练命令
# openrlhf.cli.rm --config configs/rlhf/rm_config.yaml
```

奖励模型配置文件示例 (configs/rlhf/rm_config.yaml):
```yaml
model:
  model_name_or_path: "Qwen/Qwen2.5-7B"
  trust_remote_code: true
  use_flash_attention: true

tokenizer:
  tokenizer_name_or_path: "Qwen/Qwen2.5-7B"
  padding_side: "right"
  truncation_side: "right"
  trust_remote_code: true

dataset:
  train_file: "data/rlhf_data/rm/rm_train_data.jsonl"
  eval_file: "data/rlhf_data/rm/rm_eval_data.jsonl"
  format: "preference"  # 偏好数据格式

training:
  bf16: true
  fp16: false
  deepspeed: "configs/rlhf/zero_stage3_config.json"
  num_train_epochs: 3
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 8
  learning_rate: 1.0e-5
  weight_decay: 0.0
  warmup_ratio: 0.03
  evaluation_strategy: "steps"
  eval_steps: 500
  save_strategy: "steps"
  save_steps: 500
  save_total_limit: 3
  logging_steps: 10
  output_dir: "outputs/rm"
  
lora:
  use_lora: true
  r: 8
  lora_alpha: 16
  lora_dropout: 0.05
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]
```

#### PPO训练
```python
# 使用OpenRLHF的PPO训练命令
# openrlhf.cli.ppo --config configs/rlhf/ppo_config.yaml
```

PPO配置文件示例 (configs/rlhf/ppo_config.yaml):
```yaml
actor:
  model_name_or_path: "outputs/sft"
  trust_remote_code: true
  use_flash_attention: true

critic:
  model_name_or_path: "outputs/sft"
  trust_remote_code: true
  use_flash_attention: true

reward_model:
  model_name_or_path: "outputs/rm"
  trust_remote_code: true
  use_flash_attention: true

initial_model:
  model_name_or_path: "outputs/sft"
  trust_remote_code: true
  use_flash_attention: true

tokenizer:
  tokenizer_name_or_path: "Qwen/Qwen2.5-7B"
  padding_side: "right"
  truncation_side: "right"
  trust_remote_code: true

dataset:
  train_file: "data/rlhf_data/ppo/ppo_train_data.jsonl"
  format: "alpaca"  # 或根据实际数据格式选择

training:
  bf16: true
  fp16: false
  num_train_epochs: 3
  per_device_train_batch_size: 4
  gradient_accumulation_steps: 4
  learning_rate: 1.0e-5
  weight_decay: 0.0
  warmup_ratio: 0.03
  evaluation_strategy: "steps"
  eval_steps: 500
  save_strategy: "steps"
  save_steps: 500
  save_total_limit: 3
  logging_steps: 10
  output_dir: "outputs/ppo"
  
ppo:
  chunk_size: 16
  ppo_epochs: 4
  init_kl_coef: 0.1
  target_kl: 0.5
  gamma: 1.0
  lam: 0.95
  cliprange: 0.2
  cliprange_value: 0.2
  vf_coef: 0.1
  scale_reward: false
  ref_mean: null
  ref_std: null
  cliprange_reward: 10
  gen_kwargs:
    max_new_tokens: 256
    top_k: 0
    top_p: 1.0
    do_sample: true
    
lora:
  use_lora: true
  r: 8
  lora_alpha: 16
  lora_dropout: 0.05
  target_modules: ["q_proj", "k_proj", "v_proj", "o_proj"]
```

### 3.2 数据处理适配

为了适配OpenRLHF框架，需要将数据转换为其支持的格式：

```python
# SFT数据格式示例
{
    "instruction": "请解释二叉树的基本概念",
    "input": "",  # 可选
    "output": "二叉树是一种树形数据结构，其中每个节点最多有两个子节点..."
}

# 奖励模型数据格式示例
{
    "instruction": "请解释二叉树的基本概念",
    "input": "",  # 可选
    "chosen": "二叉树是一种树形数据结构，其中每个节点最多有两个子节点...",
    "rejected": "二叉树就是有两个分支的树..."
}
```

### 3.3 多节点训练配置

对于大规模训练，OpenRLHF支持多节点分布式训练：

```bash
# 使用Ray进行分布式PPO训练
openrlhf.cli.ppo --config configs/rlhf/ppo_config.yaml --multi_node
```

## 4. 评估方案

### 4.1 模型评估
1. **质量评估**
   - 提示词相关性
   - 教学引导效果
   - 语言流畅度

2. **性能评估**
   - 训练效率
   - 推理速度
   - 资源消耗

### 4.2 对比实验
1. **RLHF vs DPO**
   - 训练时长
   - 计算资源
   - 生成质量
   - 部署难度

## 5. 后续计划

### 5.1 近期任务（1-2周）
1. **OpenRLHF框架集成**
   - [ ] 安装配置OpenRLHF环境
   - [ ] 数据格式转换适配
   - [ ] SFT训练脚本开发
   - [ ] 奖励模型训练脚本开发

2. **DPO框架搭建**
   - [ ] 设计数据收集方案
   - [ ] 开发训练脚本
   - [ ] 构建评估体系

### 5.2 中期目标（2-4周）
1. **PPO训练实现**
   - [ ] 配置PPO训练参数
   - [ ] 实现分布式训练
   - [ ] 模型评估与调优

2. **系统集成**
   - [ ] 模型部署优化
   - [ ] 接口设计与实现
   - [ ] 性能调优

3. **实验评估**
   - [ ] 完整对比实验
   - [ ] 数据分析与可视化
   - [ ] 撰写技术报告

## 6. 优势与挑战

### 6.1 OpenRLHF优势
- **高性能**：利用Ray和vLLM加速样本生成，大幅提升训练效率
- **分布式训练**：支持将Actor、Reward、Reference和Critic模型分布在不同GPU上
- **优化实现**：集成了多种PPO实现优化技巧，提高训练稳定性
- **易用性**：与Huggingface模型和数据集完全兼容

### 6.2 潜在挑战
- **资源需求**：完整RLHF流程需要较多计算资源
- **配置复杂性**：分布式训练配置可能需要调试
- **数据质量**：奖励模型训练数据的质量对最终效果影响较大

## 7. 参考资源

1. **OpenRLHF文档**
   - [官方文档](https://openrlhf.readthedocs.io/en/latest/index.html)
   - [快速入门指南](https://openrlhf.readthedocs.io/en/latest/quickstart.html)
   - [性能调优指南](https://openrlhf.readthedocs.io/en/latest/performance.html)

2. **相关论文**
   - PPO算法原理
   - RLHF技术细节
   - 提示词优化研究