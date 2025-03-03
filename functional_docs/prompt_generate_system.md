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

### 2.2 进行中任务
1. **奖励模型(RM)训练**
   - 数据准备与格式转换
   - 训练脚本开发
   - 模型评估方案设计

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


#### 奖励模型训练（计划中）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`


#### 奖励模型训练（计划中）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`



#### 奖励模型训练（计划中）
执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`

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

#### 奖励模型数据格式（准备中）
data_path: `/autodl-tmp/EasyDS/data/rlhf_data/rm/train.jsonl`
```python
{
    "chosen": "用户: 请解释二叉树的基本概念\n助手: 二叉树是一种树形数据结构，其中每个节点最多有两个子节点...",
    "rejected": "用户: 请解释二叉树的基本概念\n助手: 二叉树就是有两个分支的树..."
}
```

#### PPO提示数据格式（准备中）
data_path: `/autodl-tmp/EasyDS/data/rlhf_data/ppo/train.jsonl`
```python
{
    "input": "请解释二叉树的基本概念"
}
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
1. **奖励模型训练**
   - [ ] 完成偏好数据准备
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

## 7. 参考资源

1. **OpenRLHF文档**
   - [官方文档](https://openrlhf.readthedocs.io/en/latest/index.html)
   - [快速入门指南](https://openrlhf.readthedocs.io/en/latest/quick_start.html)
   - [RLHF训练指南](https://openrlhf.readthedocs.io/en/latest/rl.html)
   - [性能调优指南](https://openrlhf.readthedocs.io/en/latest/performance.html)

2. **相关脚本**
   - SFT训练脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_sft_mixtral_lora.sh`
   - LoRA合并脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/lora_combined.sh`