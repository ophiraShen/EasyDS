# 数据处理设计文档

## 1. 数据结构设计

### 1.1 SFT数据格式
```python
# 原始数据格式
{
    "context": {
        "question": str,              # 原始问题
        "student_response": str,      # 用户回答
        "knowledge_points": list,     # 相关知识点列表
    },
    "response": {
        "analysis": str,             # 回答分析
        "guidance": str,             # 引导性建议
        "teaching_strategy": str     # 教学策略
    }
}

# 转换后的训练格式
"""
<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{question_and_response}<|im_end|>
<|im_start|>assistant
{analysis_and_guidance}<|im_end|>
"""
```

### 1.2 PPO数据格式
```python
# 原始数据格式
{
    "context": {
        "question": str,
        "student_response": str,
        "history": List[Dict]        # 对话历史
    },
    "model_response": {
        "guidance": str,             # 模型生成的引导
        "reward_metrics": {
            "relevance": float,      # 相关性分数
            "guidance_quality": float,# 引导质量分数
            "engagement": float      # 参与度分数
        }
    }
}

# 转换后的训练格式
{
    "prompt": str,          # 包含历史对话的完整提示
    "response": str,        # 模型回复
    "reward": float,        # 综合奖励分数
    "metadata": {
        "metrics": dict,    # 详细评分指标
        "strategy": str     # 使用的教学策略
    }
}
```

## 2. 数据处理流程

### 2.1 SFT数据处理
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

### 2.2 PPO数据处理
```python
class PPODataProcessor:
    def __init__(self):
        self.reward_weights = {
            "relevance": 0.4,
            "guidance_quality": 0.4,
            "engagement": 0.2
        }

    def process_interaction(self, data: dict) -> dict:
        # 构建训练样本
        prompt = self._build_prompt(data["context"])
        response = data["model_response"]["guidance"]
        reward = self._calculate_reward(data["model_response"]["reward_metrics"])
        
        return {
            "prompt": prompt,
            "response": response,
            "reward": reward,
            "metadata": {
                "metrics": data["model_response"]["reward_metrics"],
                "strategy": self._identify_strategy(response)
            }
        }

    def _calculate_reward(self, metrics: dict) -> float:
        return sum(score * self.reward_weights[metric]
                  for metric, score in metrics.items())

    def _build_prompt(self, context: dict) -> str:
        # 构建包含历史对话的提示
        history = self._format_history(context["history"])
        current = f"问题：{context['question']}\n学生回答：{context['student_response']}"
        return f"{history}\n{current}"
```

## 3. 数据质量控制

### 3.1 监控指标
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

### 3.2 质量报告生成
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

## 4. 数据增强策略

### 4.1 数据增强方法
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

## 5. 使用示例
```python
# SFT数据处理示例
sft_pipeline = SFTDataPipeline()
sft_data = sft_pipeline.process_data(raw_sft_data)

# PPO数据处理示例
ppo_processor = PPODataProcessor()
ppo_data = [ppo_processor.process_interaction(interaction) 
            for interaction in raw_ppo_data]
``` 