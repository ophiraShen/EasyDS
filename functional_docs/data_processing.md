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

### 2.1 SFT数据格式
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
  "output": "{\"role\": \"assistant\", \"content\": \"你是一个专业的数据结构教师。学生对快速排序有基本认识，但是不清楚在不同情况下的基准值选择方法。\\n请重点引导学生思考：\\n- 快速排序中基准值选择对性能的影响\\n- 不同情况下的基准值选择方法\\n保持鼓励性语气，通过启发式提问深化理解。\"}"
}
```

### 2.2 PPO数据格式
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

### 3.1 SFT数据处理
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

### 3.2 PPO数据处理
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

### 3.1 特征分析器
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

### 5.1 数据增强方法
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
# SFT数据处理示例
sft_pipeline = SFTDataPipeline()
sft_data = sft_pipeline.process_data(raw_sft_data)

# PPO数据处理示例
ppo_processor = PPODataProcessor()
ppo_data = [ppo_processor.process_interaction(interaction) 
            for interaction in raw_ppo_data]
``` 