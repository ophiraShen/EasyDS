# 数据处理设计文档

## 1. 数据收集
- 从教学资源收集数据结构相关的问题和标准答案
- 从在线教育平台收集学生的真实提问和回答
- 从教师培训资料中提取教学引导策略
- 建议收集的数据类型：
    - 基础概念题（如：什么是二叉树？）
    - 算法解释题（如：解释快速排序的工作原理）
    - 代码分析题（如：分析这段代码的时间复杂度）
    - 问题解决题（如：如何优化这个算法？）

## 2. 数据结构设计

从微调的角度来看，我们应该：
- 保持数据格式简单直接
- 只保留必要的信息
- 让模型专注于核心任务：理解问题、用户与教师智能体的对话，给出下一步的提示词

### 2.1 DPO数据格式
```python
# 原始数据格式
{
    "question": str,              # 原始问题
    "dialogs": List[dict],       # 用户与教师智能体的对话历史
    "chosen": str,               # 更好的提示词
    "rejected": str,             # 较差的提示词
    "metadata": {
        "chosen_quality": {
            "guidance_score": float,     # 引导性评分
            "teaching_method": float,    # 教学方法评分
            "feynman_alignment": float   # 费曼学习法契合度
        },
        "rejected_quality": {
            "guidance_score": float,
            "teaching_method": float,
            "feynman_alignment": float
        }
    }
}

# 示例数据
{
    "question": "请解释快速排序的基本原理",
    "dialogs": [
        {"role": "user", "content": "快速排序是选择一个基准值，然后把数组分成两部分，比基准值小的放左边，大的放右边"},
        {"role": "assistant", "content": "你说得对。那你觉得基准值的选择会影响排序的效率吗？为什么？"},
        {"role": "user", "content": "我觉得会影响，但是不太确定具体原因"}
    ],
    "chosen": """你是一个专业的数据结构教师。学生已经理解了快速排序的基本思想，现在需要引导他思考基准值选择的重要性。
请通过以下方式引导：
1. 让学生思考极端情况（如已排序数组）下基准值的选择会带来什么问题
2. 引导学生分析不同基准值选择对算法性能的影响
3. 鼓励学生自己推导出最优的基准值选择策略
记住使用费曼学习法，通过提问引导学生思考，而不是直接给出答案。""",
    "rejected": """你是一个数据结构老师。学生需要了解快速排序中基准值的选择。
讲解以下内容：
1. 基准值选择的常用方法
2. 不同选择方法的优缺点
3. 最佳实践建议""",
    "metadata": {
        "chosen_quality": {
            "guidance_score": 0.9,
            "teaching_method": 0.95,
            "feynman_alignment": 0.95
        },
        "rejected_quality": {
            "guidance_score": 0.6,
            "teaching_method": 0.5,
            "feynman_alignment": 0.3
        }
    }
}

# 转换后的训练格式
{
    "prompt": "问题：请解释快速排序的基本原理\n对话历史：\n用户：快速排序是选择一个基准值，然后把数组分成两部分，比基准值小的放左边，大的放右边\n助手：你说得对。那你觉得基准值的选择会影响排序的效率吗？为什么？\n用户：我觉得会影响，但是不太确定具体原因",
    "chosen": "你是一个专业的数据结构教师。学生已经理解了快速排序的基本思想，现在需要引导他思考基准值选择的重要性。\n请通过以下方式引导：\n1. 让学生思考极端情况（如已排序数组）下基准值的选择会带来什么问题\n2. 引导学生分析不同基准值选择对算法性能的影响\n3. 鼓励学生自己推导出最优的基准值选择策略\n记住使用费曼学习法，通过提问引导学生思考，而不是直接给出答案。",
    "rejected": "你是一个数据结构老师。学生需要了解快速排序中基准值的选择。\n讲解以下内容：\n1. 基准值选择的常用方法\n2. 不同选择方法的优缺点\n3. 最佳实践建议"
}
```

### 2.2 RLHF数据格式

### 2.2.1 SFT数据格式

数据分类：
- 用户回答部分正确，教师进一步引导
- 用户回答错误，教师引导用户思考
- 用户回答完全正确，教师引导用户继续学习其它相关知识点

```python
# 原始数据格式
{
    "question": str,              # 原始问题
    "dialogs": List[dict],         # 用户与教师智能体的对话
    "target_prompt": str         # 针对性的提示词
}

# 示例数据
{
    "question": "请解释快速排序的基本原理",
    "dialogs": [
        {"role": "user", "content": "快速排序是选择一个基准值，然后把数组分成两部分，比基准值小的放左边，大的放右边"},
        {"role": "assistant", "content": "非常好，你已经理解了快速排序的基本原理。但是，快速排序中基准值的选择对性能有很大影响，你知道常用的基准值选择方法吗？"},
        {"role": "user", "content": "我经常选择第一个元素作为基准值"},
    ],
    "target_prompt": """你是一个专业的数据结构教师。学生对快速排序有基本认识，但是不清楚在不同情况下的基准值选择方法。
请重点引导学生思考：
- 快速排序中基准值选择对性能的影响
- 不同情况下的基准值选择方法
保持鼓励性语气，通过启发式提问深化理解。"""
}

# 转换后的训练格式
{
  "input": """[{\"role\": \"system\", \"content\": \"你是一个提示词生成助手。请根据问题、用户与教师智能体的对话，生成进一步的教学指导提示词。\"},
{\"role\": \"user\", \"content\": \"问题：请解释快速排序的基本原理。\n学生回答：快速排序是选择一个基准值，然后把数组分成两部分，比基准值小的放左边，大的放右边"},
{\"role\": \"assistant\", \"content\": \"非常好，你已经理解了快速排序的基本原理。但是，快速排序中基准值的选择对性能有很大影响，你知道常用的基准值选择方法吗？\"},
{\"role\": \"user\", \"content\": \"我经常选择第一个元素作为基准值\"}
  ]""",
  "output": "{\"role\": \"assistant\", \"content\": \"现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\\n你是一个专业的数据结构教师。学生对快速排序有基本认识，但是不清楚在不同情况下的基准值选择方法。\\n请重点引导学生思考：\\n- 快速排序中基准值选择对性能的影响\\n- 不同情况下的基准值选择方法\\n保持鼓励性语气，通过启发式提问深化理解。\"}"
}
```

### 2.2.2 PPO数据格式
```python
# 原始数据格式
{
    "question": str,              # 原始问题
    "student_response": str,      # 学生回答
    "response_features": dict,    # 回答特征分析
    "generated_prompt": str,      # 模型生成的提示词
    "teacher_response": str,      # 使用该提示词后教师的回复
    "reward_metrics": {           # 多维度评分
        "guidance_effectiveness": float,  # 引导效果
        "relevance": float,              # 相关性
        "specificity": float,            # 具体程度
        "encouragement": float           # 鼓励程度
    }
}

# 转换后的训练格式
{
    "prompt": f"""<|im_start|>system
你是一个提示词生成器。根据学生回答的特征，生成能指导教师进行针对性引导的提示词。<|im_end|>
<|im_start|>user
问题：{question}
学生回答：{student_response}
回答特征分析：{response_features}<|im_end|>""",
    "response": generated_prompt,
    "reward": weighted_average(reward_metrics)  # 多维度评分的加权平均
}
```

#### 奖励设计
- 使用单一奖励分数替代多维度评分
- 分数范围0-1，便于模型学习
- 评分标准可以包含：
    - 回复的积极性
    - 引导的针对性
    - 问题的具体性
    - 教学策略的合理性

## 3. 数据处理流程

### 3.1 DPO数据处理
```python
class DPODataProcessor:
    def __init__(self):
        self.system_prompt = """你是一个提示词生成助手。你的任务是根据学生和教师的对话历史，生成能够帮助教师更好地引导学生思考的提示词。
要求：
1. 严格遵循费曼学习法
2. 通过提问引导学生思考
3. 避免直接给出答案
4. 保持积极鼓励的态度"""

    def process_conversation(self, data: dict) -> dict:
        """处理单条DPO训练数据"""
        # 构建对话历史
        dialog_history = self._format_dialog_history(data['dialogs'])
        
        # 构建prompt
        prompt = f"问题：{data['question']}\n对话历史：{dialog_history}"
        
        return {
            "prompt": prompt,
            "chosen": data["chosen"],
            "rejected": data["rejected"]
        }

    def _format_dialog_history(self, dialogs: List[dict]) -> str:
        """格式化对话历史"""
        formatted = []
        for dialog in dialogs:
            role = "用户" if dialog["role"] == "user" else "助手"
            formatted.append(f"{role}：{dialog['content']}")
        return "\n".join(formatted)

    def validate_data(self, data: dict) -> bool:
        """验证数据质量"""
        return (
            self._check_prompt_quality(data["chosen"]) and
            self._check_feynman_alignment(data["chosen"]) and
            self._verify_guidance_nature(data["chosen"])
        )
```

### 3.2 SFT数据处理
```python
class DataConverter:
    def __init__(self):
        self.system_prompt = """你是一个专业的教学助手。你的任务是分析学生的回答，并提供有针对性的引导。
要求：
1. 准确理解学生的回答要点
2. 识别回答中的不足之处
3. 使用启发式提问引导学生思考
4. 保持积极鼓励的态度"""

    def convert_to_training_format(self, data: dict) -> str:
        # 构建问题和回答上下文
        question_context = f"问题：{data['context']['question']}\n学生回答：{data['context']['student_response']}"
        
        # 构建助手回复
        assistant_response = f"""我来分析一下你的回答：
{data['response']['analysis']}

{data['response']['guidance']}"""

        # 组合完整对话
        return self._create_dialog_format(question_context, assistant_response)

    def _create_dialog_format(self, user_input: str, assistant_output: str) -> str:
        return f"""<|im_start|>system
{self.system_prompt}<|im_end|>
<|im_start|>user
{user_input}<|im_end|>
<|im_start|>assistant
{assistant_output}<|im_end|>"""
```


### 3.3 PPO数据处理

```python
class PPODataProcessor:
    def __init__(self):
        self.system_prompt = """你是一个教学助手。分析学生的回答，给出鼓励性反馈，并通过提问引导学生思考。"""
        
    def process_interaction(self, data: dict) -> dict:
        """处理单条PPO训练数据"""
        # 构建prompt
        prompt = f"""<|im_start|>system
{self.system_prompt}<|im_end|>
<|im_start|>user
问题：{data['question']}
学生回答：{data['student_response']}<|im_end|>"""

        return {
            "prompt": prompt,
            "response": data["model_response"],
            "reward": data["reward"]
        }

    def batch_process(self, data_list: List[dict]) -> List[dict]:
        """批量处理PPO训练数据"""
        return [self.process_interaction(item) for item in data_list]
```

### 3.4 特征分析器
```python
class ResponseAnalyzer:
    def analyze_response(self, question: str, response: str) -> dict:
        """分析学生回答的特征"""
        return {
            "knowledge_points": self._extract_knowledge_points(response),
            "understanding_level": self._assess_understanding(response),
            "misconceptions": self._identify_misconceptions(response, question),
            "missing_points": self._find_missing_points(response, question)
        }

class PromptGenerator:
    def generate_teaching_prompt(self, analysis: dict) -> str:
        """根据分析生成教学提示词"""
        prompt_template = """你是一个专业的{subject}教师。
学生对{topic}的理解水平为{level}。
需要重点关注：{focus_points}
教学策略：{strategies}
语气要求：{tone}"""
        
        return self._fill_template(prompt_template, analysis)
```

## 4. 数据质量控制

### 4.1 监控指标
1. **数据完整性**
   - 必要字段存在率
   - 字段值有效率

2. **数据质量**
   - 文本长度分布
   - 知识点覆盖率
   - 引导策略多样性

3. **转换质量**
   - 格式正确率
   - 对话完整性
   - token数量分布

### 4.2 质量报告生成
```python
class QualityReporter:
    def generate_report(self, raw_data: List[dict], processed_data: List[str]) -> dict:
        return {
            "total_samples": len(raw_data),
            "valid_samples": len(processed_data),
            "conversion_rate": len(processed_data) / len(raw_data),
            "avg_tokens": self._calculate_avg_tokens(processed_data),
            "knowledge_coverage": self._analyze_knowledge_coverage(raw_data),
            "strategy_distribution": self._analyze_teaching_strategies(raw_data)
        }
```

## 5. 数据增强策略

### 5.1 DPO数据增强
```python
class DPODataAugmenter:
    def augment_data(self, data: dict) -> List[dict]:
        """DPO数据增强方法"""
        augmented_data = []
        
        # 1. 变换对话历史表述
        augmented_data.extend(self._rephrase_dialogs(data))
        
        # 2. 生成不同程度的提示词对
        augmented_data.extend(self._generate_prompt_pairs(data))
        
        # 3. 调整引导深度
        augmented_data.extend(self._vary_guidance_depth(data))
        
        return augmented_data

    def _verify_pair_quality(self, chosen: str, rejected: str) -> bool:
        """验证生成的提示词对的质量差异"""
        chosen_score = self._evaluate_prompt(chosen)
        rejected_score = self._evaluate_prompt(rejected)
        return chosen_score > rejected_score + 0.3  # 确保足够的质量差异
```

### 5.2 通用数据增强
```python
class DataAugmenter:
    def augment_data(self, data: dict) -> List[dict]:
        """数据增强方法"""
        augmented_data = []
        
        # 1. 变换问题表述
        augmented_data.append(self._rephrase_question(data))
        
        # 2. 生成不同程度的学生回答
        augmented_data.extend(self._generate_response_variations(data))
        
        # 3. 调整引导方式
        augmented_data.extend(self._vary_guidance_style(data))
        
        return augmented_data
```

## 6. 使用示例
```python
# DPO数据处理示例
dpo_processor = DPODataProcessor()
dpo_data = [dpo_processor.process_conversation(conv) 
            for conv in raw_dpo_data]

# SFT数据处理示例
sft_pipeline = SFTDataPipeline()
sft_data = sft_pipeline.process_data(raw_sft_data)

# PPO数据处理示例
ppo_processor = PPODataProcessor()
ppo_data = [ppo_processor.process_interaction(interaction) 
            for interaction in raw_ppo_data]
``` 