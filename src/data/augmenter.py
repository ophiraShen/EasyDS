# EasyDS/src/data/augmenter.py
from typing import List, Dict
import random
from copy import deepcopy

class PromptAugmenter:
    """提示词增强器"""
    def __init__(self):
        self.template_variations = {
            "subject_templates": [
                "你是一个专业的{subject}教师",
                "作为{subject}领域的教学专家",
                "你是一位经验丰富的{subject}导师"
            ],
            "understanding_templates": [
                "学生对{topic}的理解水平为{level}",
                "学生在{topic}方面展现出{level}的理解",
                "学生对{topic}的掌握程度为{level}"
            ],
            "focus_templates": [
                "需要重点关注：{points}",
                "建议重点引导以下方面：{points}",
                "请着重引导这些要点：{points}"
            ]
        }

    def augment_prompt(self, prompt: str, subject: str, topic: str) -> List[str]:
        """增强提示词"""
        variations = []
        
        # 解析原始提示词的结构
        parts = self._parse_prompt(prompt)
        
        # 生成不同的组合
        for subj_temp in self.template_variations["subject_templates"]:
            for und_temp in self.template_variations["understanding_templates"]:
                for focus_temp in self.template_variations["focus_templates"]:
                    new_prompt = self._combine_templates(
                        subj_temp, und_temp, focus_temp,
                        parts, subject, topic
                    )
                    variations.append(new_prompt)
        
        return variations

    def _parse_prompt(self, prompt: str) -> Dict:
        """解析提示词结构"""
        lines = prompt.split('\n')
        return {
            'level': self._extract_level(lines),
            'points': self._extract_points(lines),
            'strategies': self._extract_strategies(lines),
            'tone': self._extract_tone(lines)
        }

    def _combine_templates(self, subj_temp: str, und_temp: str, 
                         focus_temp: str, parts: Dict, 
                         subject: str, topic: str) -> str:
        """组合模板生成新的提示词"""
        return f"""{subj_temp.format(subject=subject)}。
{und_temp.format(topic=topic, level=parts['level'])}。
{focus_temp.format(points=', '.join(parts['points']))}
教学策略：{parts['strategies']}
语气要求：{parts['tone']}"""

class DataAugmenter:
    """数据增强器"""
    def __init__(self):
        self.prompt_augmenter = PromptAugmenter()
        self.feature_variations = {
            "understanding_levels": [
                "基础理解", "部分理解", "深入理解", "完全掌握"
            ],
            "misconception_types": [
                "概念混淆", "应用错误", "逻辑谬误", "过度简化"
            ]
        }

    def augment_example(self, example: Dict) -> List[Dict]:
        """增强单个样例"""
        augmented = []
        base_example = deepcopy(example)
        
        # 生成不同的特征分析变体
        feature_variations = self._generate_feature_variations(
            base_example['response_analysis']
        )
        
        # 对每个特征变体生成对应的提示词变体
        for features in feature_variations:
            new_example = deepcopy(base_example)
            new_example['response_analysis'] = features
            
            # 生成对应的提示词变体
            prompt_variations = self.prompt_augmenter.augment_prompt(
                base_example['target_prompt'],
                subject="数据结构",
                topic=self._extract_topic(base_example['question'])
            )
            
            # 组合特征和提示词变体
            for prompt in prompt_variations:
                variation = deepcopy(new_example)
                variation['target_prompt'] = prompt
                augmented.append(variation)
        
        return augmented

    def _generate_feature_variations(self, analysis: Dict) -> List[Dict]:
        """生成特征分析的变体"""
        variations = []
        base_analysis = deepcopy(analysis)
        
        # 变换理解程度
        for level in self.feature_variations["understanding_levels"]:
            if level != base_analysis["understanding_level"]:
                variation = deepcopy(base_analysis)
                variation["understanding_level"] = level
                variations.append(variation)
        
        # 添加或移除误解
        if base_analysis["misconceptions"]:
            # 移除一个误解
            variation = deepcopy(base_analysis)
            variation["misconceptions"].pop()
            variations.append(variation)
        else:
            # 添加一个误解
            variation = deepcopy(base_analysis)
            variation["misconceptions"].append(
                random.choice(self.feature_variations["misconception_types"])
            )
            variations.append(variation)
        
        return variations

    def _extract_topic(self, question: str) -> str:
        """从问题中提取主题"""
        # 简单实现，实际应用中可能需要更复杂的逻辑
        keywords = ["排序", "树", "图", "栈", "队列", "链表"]
        for keyword in keywords:
            if keyword in question:
                return keyword
        return "数据结构"

    def augment_dataset(self, dataset: List[Dict]) -> List[Dict]:
        """增强整个数据集"""
        augmented_dataset = []
        for example in dataset:
            augmented_dataset.extend(self.augment_example(example))
        return augmented_dataset 