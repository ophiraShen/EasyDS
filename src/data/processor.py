# EasyDS/src/data/processor.py
import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TrainingExample:
    """训练数据样例类"""
    question: str
    dialogues: List[Dict]
    target_prompt: str

@dataclass
class RewardMetrics:
    """奖励指标类"""
    guidance_effectiveness: float
    relevance: float
    specificity: float
    encouragement: float

@dataclass
class PPOExample:
    """PPO训练数据样例类"""
    question: str
    student_response: str
    response_features: Dict
    generated_prompt: str
    teacher_response: str
    reward_metrics: RewardMetrics

class DataProcessor:
    """数据处理基类"""
    def __init__(self, system_prompt: Optional[str] = None):
        self.system_prompt = system_prompt or """你是一个提示词生成器。分析学生的回答特征，生成能够指导教师智能体进行针对性引导的提示词。"""

    def load_json(self, file_path: str) -> List[Dict]:
        """加载JSON格式的数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_json(self, data: List[Dict], file_path: str):
        """保存数据为JSON格式"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_jsonl(self, file_path: str) -> List[Dict]:
        """加载JSONL格式的数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f]
    
    def save_jsonl(self, data: List[Dict], file_path: str):
        """保存数据为JSONL格式"""
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')

class SFTDataProcessor(DataProcessor):
    """SFT数据处理器"""
    def convert_to_training_format(self, example: Dict) -> str:
        """转换为训练格式"""
        question = example['question']
        dialogues = example['dialogues']
        target_prompt = example['target_prompt']

        input_data = []
        input_data.append({"role": "system", "content": "你是一个提示词生成助手。请根据问题、用户与教师智能体的对话，生成进一步的教学指导提示词。"})
        first_response = dialogues[0]['content']
        input_data.append({"role": "user", "content": f"问题：{question}\n学生回答：{first_response}"})
        for dialogue in dialogues[1:]:
            input_data.append({"role": dialogue['role'], "content": dialogue['content']})

        output_data = {
            "role": "assistant",
            "content": f"现在在采用费曼学习法，帮助用户学习数据结构知识，尽可能的引导用户思考，非必要情况下不要直接给出答案。\n{target_prompt}"
        }

        return {
            "input": json.dumps(input_data, ensure_ascii=False),
            "output": json.dumps(output_data, ensure_ascii=False)
        }

        # return {
        #     "input": input_data,
        #     "output": output_data
        # }

    def process_file(self, input_file: str, output_file: str):
        """处理整个数据文件"""
        raw_data = self.load_json(input_file)
        processed_data = []
        
        for item in raw_data:
            analysis = ResponseAnalysis(
                knowledge_points=item['response_analysis']['knowledge_points'],
                understanding_level=item['response_analysis']['understanding_level'],
                misconceptions=item['response_analysis']['misconceptions'],
                missing_points=item['response_analysis']['missing_points']
            )
            
            example = TrainingExample(
                question=item['question'],
                student_response=item['student_response'],
                response_analysis=analysis,
                target_prompt=item['target_prompt']
            )
            processed_data.append(self.convert_to_training_format(example))
            
        self.save_json(processed_data, output_file)

class PPODataProcessor(DataProcessor):
    """PPO数据处理器"""
    def convert_to_training_format(self, example: PPOExample) -> Dict:
        """转换为PPO训练格式"""
        prompt = f"""<|im_start|>system
{self.system_prompt}<|im_end|>
<|im_start|>user
问题：{example.question}
学生回答：{example.student_response}
回答特征分析：{self._format_features(example.response_features)}<|im_end|>"""

        return {
            "prompt": prompt,
            "response": example.generated_prompt,
            "reward": self._calculate_weighted_reward(example.reward_metrics)
        }

    def _format_features(self, features: Dict) -> str:
        """格式化特征分析"""
        return json.dumps(features, ensure_ascii=False, indent=2)

    def _calculate_weighted_reward(self, metrics: RewardMetrics) -> float:
        """计算加权奖励分数"""
        weights = {
            'guidance_effectiveness': 0.4,
            'relevance': 0.3,
            'specificity': 0.2,
            'encouragement': 0.1
        }
        
        return (
            weights['guidance_effectiveness'] * metrics.guidance_effectiveness +
            weights['relevance'] * metrics.relevance +
            weights['specificity'] * metrics.specificity +
            weights['encouragement'] * metrics.encouragement
        )

    def process_file(self, input_file: str, output_file: str):
        """处理整个数据文件"""
        raw_data = self.load_json(input_file)
        processed_data = []
        
        for item in raw_data:
            metrics = RewardMetrics(
                guidance_effectiveness=item['reward_metrics']['guidance_effectiveness'],
                relevance=item['reward_metrics']['relevance'],
                specificity=item['reward_metrics']['specificity'],
                encouragement=item['reward_metrics']['encouragement']
            )
            
            example = PPOExample(
                question=item['question'],
                student_response=item['student_response'],
                response_features=item['response_features'],
                generated_prompt=item['generated_prompt'],
                teacher_response=item['teacher_response'],
                reward_metrics=metrics
            )
            processed_data.append(self.convert_to_training_format(example))
            
        self.save_json(processed_data, output_file)


