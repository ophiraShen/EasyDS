# EasyDS动态提示词生成系统设计文档

## 1. 系统概述

### 1.1 设计目标

EasyDS动态提示词生成系统旨在为教学智能体提供高质量的教学指导提示词，通过分析学生回答特征，生成针对性的教学策略。系统采用费曼学习法的教学理念，引导学生通过思考和探索掌握数据结构知识。

主要目标包括：
- 生成符合费曼学习法的教学提示词
- 根据学生回答特征提供针对性指导
- 避免直接给出答案，鼓励学生思考
- 提供多层次的学习引导

### 1.2 技术选型

系统采用两种技术路线进行对比实验：
- **RLHF (强化学习人类反馈)**: 基于OpenRLHF框架实现
- **DPO (直接偏好优化)**: 简化的偏好学习方法

基础模型选择：
- Qwen2.5-7B-Instruct: 作为SFT、RM和PPO的基础模型

训练优化技术：
- LoRA: 参数高效微调
- DeepSpeed ZeRO-3: 内存优化
- Flash Attention: 计算加速

### 1.3 系统架构

动态提示词生成系统由以下核心组件构成：

1. **数据处理模块**
   - SFT数据处理器
   - 奖励模型数据处理器
   - PPO数据处理器

2. **模型训练模块**
   - SFT训练器
   - 奖励模型训练器
   - PPO训练器

3. **评估与对比模块**
   - 提示词质量评估
   - RLHF与DPO对比分析
   - 性能监控与优化

4. **部署与应用模块**
   - 模型服务接口
   - 与教学系统集成
   - 反馈收集机制

## 2. 实现进度

### 2.1 已完成模块

1. **数据准备**
   - 收集并处理了教学对话数据
   - 构建了符合OpenRLHF格式的训练数据
   - 完成了数据集的划分（训练集/测试集）

2. **SFT阶段**
   - 基于OpenRLHF框架完成SFT训练
   - 使用LoRA进行参数高效微调
   - 采用DeepSpeed ZeRO-3优化训练过程
   - 实现了BF16精度训练
   - 启用了Flash Attention加速
   - 完成LoRA模型合并

3. **奖励模型(RM)阶段**
   - 设计并实现奖励模型数据处理流程
   - 制定优质回答与较差回答的对比标准
   - 完成奖励模型训练
   - 评估奖励模型质量
   - 保存训练好的模型

4. **PPO数据准备**
   - 设计PPO训练数据格式
   - 实现PPODataProcessor类
   - 开发数据处理脚本
   - 从SFT数据中提取问题和对话作为提示
   - 完成数据集的划分（训练集/评估集）

### 2.2 进行中模块

1. **PPO训练**
   - 环境配置
   - 训练参数优化
   - 分布式训练设置
   - 训练脚本开发

2. **DPO方案**
   - 偏好数据构建
   - 训练框架搭建
   - 评估方案设计

### 2.3 计划中模块

1. **模型评估与对比**
   - 设计评估指标
   - 构建测试数据集
   - 实现自动评估流程

2. **系统集成**
   - 模型部署优化
   - 接口设计与实现
   - 与教学系统集成

## 3. RLHF实现方案

### 3.1 SFT阶段

**实现细节**：
- 基于Qwen2.5-7B-Instruct模型进行监督微调
- 使用LoRA技术降低训练参数量
- 采用DeepSpeed ZeRO-3优化内存使用
- 启用Flash Attention加速训练过程

**训练配置**：
- 学习率：9e-6
- 批次大小：4
- LoRA配置：rank=4, alpha=16, dropout=0.05
- 目标模块：q_proj, k_proj, v_proj, o_proj

**执行脚本**：
- 路径：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_sft_mixtral_lora.sh`

**模型合并**：
- 将训练好的LoRA权重合并到基础模型
- 执行脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/lora_combined.sh`

### 3.2 奖励模型(RM)阶段

**实现细节**：
- 基于Qwen2.5-7B-Instruct模型训练奖励模型
- 使用LoRA技术降低训练参数量
- 采用DeepSpeed ZeRO-3优化内存使用
- 启用Flash Attention加速训练过程

**数据准备策略**：
- 基于SFT数据集构建偏好对比数据
- 每个训练样本包含一个优质回答和一个较差回答
- 优质回答采用原SFT数据集中的教师回答
- 较差回答通过特定策略生成，包括：
  * 直接给答案型：违背"非必要情况下不要直接给出答案"的原则
  * 缺乏引导性：简单肯定/否定学生回答，没有进一步引导
  * 知识错误型：包含错误的数据结构知识
  * 不符合费曼学习法：没有引导学生自己思考和发现答案

**训练配置**：
- 学习率：9e-6
- 批次大小：4
- LoRA配置：rank=4, alpha=16, dropout=0.05
- 目标模块：q_proj, k_proj, v_proj, o_proj

**执行脚本**：
- 路径：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`

**训练结果**：
- 成功完成奖励模型训练
- 模型保存在 `/root/autodl-fs/checkpoint/rm/` 目录下

### 3.3 PPO阶段

**实现计划**：
- 基于训练好的SFT模型作为Actor模型
- 使用训练好的奖励模型评估生成质量
- 采用LoRA技术降低训练参数量
- 使用DeepSpeed ZeRO-3优化内存使用

**数据准备策略**：
- 基于SFT数据集提取问题和对话内容作为提示
- 每个训练样本包含系统提示和用户问题
- 使用PPODataProcessor类处理数据
- 按照9:1的比例分割为训练集和评估集

**训练配置计划**：
- Actor学习率：1e-6
- Critic学习率：9e-6
- KL散度系数：0.1
- 批次大小：128
- 微批次大小：4
- LoRA配置：rank=4, alpha=16, dropout=0.05
- 目标模块：q_proj, k_proj, v_proj, o_proj

**执行脚本**：
- 路径：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_ppo.sh`（待开发）

### 3.4 模型评估

**评估指标**：
- 提示词相关性：生成的提示词与学生问题的相关程度
- 教学引导效果：提示词引导学生思考的有效性
- 语言流畅度：生成内容的自然度和连贯性
- 费曼学习法符合度：是否符合引导式教学原则

**评估方法**：
- 人工评估：专家评分和反馈
- 自动评估：使用预定义指标进行自动评分
- 对比评估：与基线模型进行对比

## 4. 数据处理流程

### 4.1 SFT数据处理

**数据格式**：
```python
{
    'input': '[{"role": "system", "content": "你是一个提示词生成助手。请根据问题、用户与教师智能体的对话，生成进一步的教学指导提示词。"}, {"role": "user", "content": "问题：BFS和DFS的主要区别是什么？\\n学生回答：BFS用队列实现，按层遍历；DFS用栈实现，优先深入子节点"}]',
    'output': '{"role": "assistant", "content": "现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\\n学生已准确掌握基础概念，需提升至应用层：\\n1. 设计迷宫问题比较两种算法效率\\n2. 引入加权图下的扩展应用\\n3. 探讨递归实现DFS的栈溢出风险\\n请用工程案例引导高阶思考。"}'
}
```

**处理流程**：
1. 读取原始对话数据
2. 提取问题和学生回答
3. 构建系统提示和用户输入
4. 提取教师回答作为目标输出
5. 转换为OpenRLHF支持的格式
6. 按照9:1的比例分割为训练集和测试集

**数据路径**：
- 原始数据：`/autodl-tmp/EasyDS/data/rlhf_data/sft/sft_raw_data.jsonl`
- 处理后数据：`/autodl-tmp/EasyDS/data/rlhf_data/sft/train.jsonl`

### 4.2 RM数据处理

**数据格式**：
```python
{
    "prompt": "[{\"role\": \"user\", \"content\": \"问题：BFS和DFS的主要区别是什么？\\n学生回答：BFS用队列实现，按层遍历；DFS用栈实现，优先深入子节点\"}]",
    "chosen": "{\"role\": \"assistant\", \"content\": \"现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\\n学生已准确掌握基础概念，需提升至应用层：\\n1. 设计迷宫问题比较两种算法效率\\n2. 引入加权图下的扩展应用\\n3. 探讨递归实现DFS的栈溢出风险\\n请用工程案例引导高阶思考。\"}",
    "rejected": "{\"role\": \"assistant\", \"content\": \"你的回答基本正确。BFS确实使用队列实现，按层次遍历图或树；而DFS使用栈实现，优先深入探索。BFS适合寻找最短路径，DFS适合探索所有可能路径。在实现上，BFS的空间复杂度通常较高，因为需要存储整层节点。\"}"
}
```

**处理流程**：
1. 读取原始RM数据
2. 提取问题和对话内容作为prompt
3. 使用原始教师回答作为优质回答(chosen)
4. 使用预先准备的较差回答(rejected)
5. 转换为OpenRLHF支持的格式
6. 按照9:1的比例分割为训练集和测试集

**数据路径**：
- 原始数据：`/autodl-tmp/EasyDS/data/rlhf_data/rm/rm_raw_data.jsonl`
- 处理后数据：`/autodl-tmp/EasyDS/data/rlhf_data/rm/train.jsonl`

### 4.3 PPO数据处理

**数据格式**：
```python
{
    "input": "[{\"role\": \"system\", \"content\": \"你是一个提示词生成助手。请根据问题、用户与教师智能体的对话，生成进一步的教学指导提示词。\"}, {\"role\": \"user\", \"content\": \"问题：BFS和DFS的主要区别是什么？\\n学生回答：BFS用队列实现，按层遍历；DFS用栈实现，优先深入子节点\"}]"
}
```

**处理流程**：
1. 读取原始SFT数据
2. 提取问题和对话内容作为提示
3. 构建系统提示和用户输入
4. 转换为OpenRLHF支持的格式
5. 按照9:1的比例分割为训练集和评估集

**数据路径**：
- 原始数据：`/autodl-tmp/EasyDS/data/rlhf_data/sft/sft_raw_data.jsonl`
- 处理后数据：`/autodl-tmp/EasyDS/data/rlhf_data/ppo/ppo_train_data.jsonl`

## 5. 训练脚本与配置

### 5.1 SFT训练脚本

**脚本路径**：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_sft_mixtral_lora.sh`

**主要参数**：
- 学习率：9e-6
- 批次大小：4
- 微批次大小：1
- 最大长度：200
- LoRA配置：rank=4, alpha=16, dropout=0.05
- 目标模块：q_proj, k_proj, v_proj, o_proj

**执行命令**：
```bash
cd /autodl-tmp/EasyDS/openrlhf_workspace/scripts
chmod +x train_sft_mixtral_lora.sh
./train_sft_mixtral_lora.sh
```

### 5.2 RM训练脚本

**脚本路径**：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`

**主要参数**：
- 学习率：9e-6
- 批次大小：4
- 微批次大小：1
- 最大长度：200
- LoRA配置：rank=4, alpha=16, dropout=0.05
- 目标模块：q_proj, k_proj, v_proj, o_proj

**执行命令**：
```bash
cd /autodl-tmp/EasyDS/openrlhf_workspace/scripts
chmod +x train_rm.sh
./train_rm.sh
```

### 5.3 PPO训练脚本

**脚本路径**：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_ppo.sh`（待开发）

**计划参数**：
- Actor学习率：1e-6
- Critic学习率：9e-6
- KL散度系数：0.1
- 批次大小：128
- 微批次大小：4
- 最大长度：512
- LoRA配置：rank=4, alpha=16, dropout=0.05
- 目标模块：q_proj, k_proj, v_proj, o_proj

**执行命令**：
```bash
cd /autodl-tmp/EasyDS/openrlhf_workspace/scripts
chmod +x train_ppo.sh
./train_ppo.sh
```

### 5.4 模型合并脚本

**脚本路径**：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/lora_combined.sh`

**执行命令**：
```bash
cd /autodl-tmp/EasyDS/openrlhf_workspace/scripts
chmod +x lora_combined.sh
./lora_combined.sh
```

## 6. 评估与对比实验

### 6.1 评估指标

**质量评估指标**：
- **相关性**：生成的提示词与学生问题的相关程度
- **引导性**：提示词引导学生思考的有效性
- **专业性**：提示词中数据结构知识的准确性
- **启发性**：提示词激发学生思考的程度
- **费曼学习法符合度**：是否符合引导式教学原则

**性能评估指标**：
- **训练效率**：训练时间和资源消耗
- **推理速度**：生成提示词的响应时间
- **模型大小**：模型参数量和存储需求
- **收敛性**：训练过程中的损失函数变化

### 6.2 RLHF vs DPO对比

**训练复杂度对比**：
- RLHF：需要训练SFT、RM和PPO三个阶段
- DPO：只需要一个阶段，直接从偏好数据学习

**资源需求对比**：
- RLHF：需要同时加载多个模型，资源消耗大
- DPO：只需要加载一个模型，资源消耗相对较小

**生成质量对比**：
- RLHF：通过强化学习可能获得更精细的控制
- DPO：简化训练过程，但可能在复杂场景下表现不如RLHF

**实现难度对比**：
- RLHF：实现复杂，需要调整多个超参数
- DPO：实现简单，超参数较少

### 6.3 实验结果分析

**待完成**：
- 模型生成质量对比
- 训练效率对比
- 资源消耗对比
- 最佳实践总结

## 7. 后续计划

### 7.1 近期任务（1-2周）

1. **PPO训练**
   - [x] 准备PPO训练数据
   - [ ] 开发PPO训练脚本
   - [ ] 配置PPO训练参数
   - [ ] 执行PPO训练
   - [ ] 评估PPO训练效果

2. **DPO方案**
   - [ ] 设计数据收集方案
   - [ ] 开发DPO训练脚本
   - [ ] 构建评估体系
   - [ ] 执行DPO训练

### 7.2 中期目标（2-4周）

1. **系统集成**
   - [ ] 模型部署优化
   - [ ] 接口设计与实现
   - [ ] 性能调优

2. **实验评估**
   - [ ] 完整对比实验
   - [ ] 数据分析与可视化
   - [ ] 撰写技术报告

### 7.3 长期规划

1. **模型优化**
   - [ ] 探索更高效的训练方法
   - [ ] 尝试更大规模的基础模型
   - [ ] 研究多模态提示词生成

2. **应用扩展**
   - [ ] 扩展到其他学科领域
   - [ ] 开发个性化教学策略
   - [ ] 构建教学效果反馈循环

## 8. 挑战与解决方案

### 8.1 技术挑战

1. **训练稳定性**
   - **挑战**：PPO训练可能面临收敛不稳定的问题
   - **解决方案**：调整KL散度系数，使用梯度裁剪，实施奖励归一化

2. **数据质量**
   - **挑战**：奖励模型训练数据的质量对最终效果影响较大
   - **解决方案**：精心设计较差回答，确保区分度适中，增加数据多样性

3. **超参数调优**
   - **挑战**：需要针对Qwen2.5-7B-Instruct模型特点调整训练参数
   - **解决方案**：进行小规模实验，逐步调整学习率和批次大小

### 8.2 资源限制

1. **计算资源**
   - **挑战**：完整RLHF流程需要较多GPU资源
   - **解决方案**：使用LoRA降低参数量，采用DeepSpeed ZeRO-3优化内存使用

2. **存储空间**
   - **挑战**：模型和训练数据需要大量存储空间
   - **解决方案**：定期清理中间检查点，只保留最佳模型

### 8.3 优化策略

1. **AutoDL环境优化**
   - **资源监控**：使用AutoDL提供的监控工具实时跟踪GPU使用情况
   - **断点续训**：利用AutoDL的持久化存储实现训练中断后的恢复
   - **模型备份**：定期将模型保存到AutoDL的永久存储区域
   - **分布式训练**：根据AutoDL实例类型优化分布式训练配置

2. **训练优化**
   - **梯度累积**：使用梯度累积增加有效批次大小
   - **混合精度训练**：使用BF16降低内存使用并加速训练
   - **优化器选择**：使用AdamW优化器并配置适当的权重衰减

## 9. 参考资源

### 9.1 文档资源

1. **OpenRLHF文档**
   - [官方文档](https://openrlhf.readthedocs.io/en/latest/index.html)
   - [快速入门指南](https://openrlhf.readthedocs.io/en/latest/quick_start.html)
   - [RLHF训练指南](https://openrlhf.readthedocs.io/en/latest/rl.html)
   - [性能调优指南](https://openrlhf.readthedocs.io/en/latest/performance.html)

2. **相关论文**
   - [Training language models to follow instructions with human feedback](https://arxiv.org/abs/2203.02155)
   - [Direct Preference Optimization: Your Language Model is Secretly a Reward Model](https://arxiv.org/abs/2305.18290)

### 9.2 代码资源

1. **训练脚本**
   - SFT训练脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_sft_mixtral_lora.sh`
   - LoRA合并脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/lora_combined.sh`
   - 奖励模型训练脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_rm.sh`
   - PPO训练脚本：`/autodl-tmp/EasyDS/openrlhf_workspace/scripts/train_ppo.sh`（待开发）

2. **数据处理脚本**
   - SFT数据处理：`/autodl-tmp/EasyDS/src/data/generate_sft_data.py`
   - RM数据处理：`/autodl-tmp/EasyDS/src/data/generate_rm_data.py`
   - PPO数据处理：`/autodl-tmp/EasyDS/src/data/generate_ppo_data.py`

### 9.3 相关项目

1. **OpenRLHF**
   - [GitHub仓库](https://github.com/OpenRLHF/OpenRLHF)
   - [示例代码](https://github.com/OpenRLHF/OpenRLHF/tree/main/examples)

2. **DeepSpeed**
   - [GitHub仓库](https://github.com/microsoft/DeepSpeed)
   - [ZeRO优化](https://www.deepspeed.ai/tutorials/zero/)




   