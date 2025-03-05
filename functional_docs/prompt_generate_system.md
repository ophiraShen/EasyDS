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
   - 完成了数据处理脚本的实现和测试
   - 优化了数据格式以适配OpenRLHF框架

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
    "prompt": "[{\"role\": \"user\", \"content\": \"问题：BFS和DFS的主要区别是什么？\\n学生回答：BFS用队列实现，按层遍历；DFS用栈实现，优先深入子节点\"}]",
    "chosen": "{\"role\": \"assistant\", \"content\": \"现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\\n学生已准确掌握基础概念，需提升至应用层：\\n1. 设计迷宫问题比较两种算法效率\\n2. 引入加权图下的扩展应用\\n3. 探讨递归实现DFS的栈溢出风险\\n请用工程案例引导高阶思考。\"}",
    "rejected": "{\"role\": \"assistant\", \"content\": \"你的回答基本正确。BFS确实使用队列实现，按层次遍历图或树；而DFS使用栈实现，优先深入探索。BFS适合寻找最短路径，DFS适合探索所有可能路径。在实现上，BFS的空间复杂度通常较高，因为需要存储整层节点。\"}"
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
from src.data.processor improt RewardModelDataProcessor
```

#### 数据处理脚本


### 3.4 数据处理优化

在实现过程中，针对奖励模型数据处理进行了以下优化：

1. **JSON格式处理**：
   - 将对话内容转换为JSON字符串，确保OpenRLHF框架能正确解析
   - 保留角色信息，使模型能够理解对话上下文

2. **数据结构优化**：
   - 为优质回答和较差回答添加角色标识，使格式与训练要求一致
   - 确保所有字段使用统一的编码方式，避免中文乱码问题

3. **错误处理**：
   - 添加了数据验证逻辑，确保输入数据格式正确
   - 实现了异常捕获和日志记录，便于调试和问题排查

4. **性能优化**：
   - 使用批量处理方式，提高数据处理效率
   - 优化文件读写操作，减少I/O开销

这些优化确保了生成的训练数据能够被OpenRLHF框架正确解析和使用，为后续的奖励模型训练奠定了基础。

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
   - [x] 优化数据格式以适配OpenRLHF框架
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