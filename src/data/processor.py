# EasyDS/src/data/processor.py
import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class ResponseAnalysis:
    """回答分析结果类"""
    knowledge_points: List[str]
    understanding_level: str
    misconceptions: List[str]
    missing_points: List[str]

@dataclass
class TrainingExample:
    """训练数据样例类"""
    question: str
    student_response: str
    response_analysis: ResponseAnalysis
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
    def convert_to_training_format(self, example: TrainingExample) -> str:
        """转换为训练格式"""
        return f"""<|im_start|>system
{self.system_prompt}<|im_end|>
<|im_start|>user
问题：{example.question}
学生回答：{example.student_response}
回答分析：{self._format_analysis(example.response_analysis)}<|im_end|>
<|im_start|>assistant
{example.target_prompt}<|im_end|>"""

    def _format_analysis(self, analysis: ResponseAnalysis) -> str:
        """格式化分析结果"""
        return f"""知识点：{', '.join(analysis.knowledge_points)}
理解程度：{analysis.understanding_level}
存在误解：{', '.join(analysis.misconceptions) if analysis.misconceptions else '无'}
缺失要点：{', '.join(analysis.missing_points)}"""

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


