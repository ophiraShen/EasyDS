# EasyDS/src/data/augmenter.py
from typing import List, Dict
import random
from copy import deepcopy

class PromptAugmenter:
    """提示词增强器：仅对提示词的表达方式进行变化，保持原意不变"""
    def __init__(self):
        self.template_variations = {
            "subject_templates": [
                "你是一个专业的{subject}教师",
                "作为{subject}领域的教学专家",
                "你是一位经验丰富的{subject}导师"
            ],
            "focus_templates": [
                "需要重点关注：{points}",
                "建议重点引导以下方面：{points}",
                "请着重引导这些要点：{points}"
            ],
            "tone_templates": [
                "请保持耐心和鼓励的语气",
                "使用循序渐进的引导方式",
                "通过启发式提问激发思考"
            ]
        }

    def augment_prompt(self, prompt: str, subject: str) -> List[str]:
        """增强提示词，仅改变表达方式，保持内容不变"""
        variations = []
        parts = self._parse_prompt(prompt)
        
        # 仅组合不同的表达模板
        for subj_temp in self.template_variations["subject_templates"]:
            for focus_temp in self.template_variations["focus_templates"]:
                for tone_temp in self.template_variations["tone_templates"]:
                    new_prompt = f"""{subj_temp.format(subject=subject)}。
学生的理解水平：{parts['level']}
{focus_temp.format(points=', '.join(parts['points']))}
{tone_temp}。"""
                    variations.append(new_prompt)
        
        return variations

    def _parse_prompt(self, prompt: str) -> Dict:
        """解析原始提示词，提取关键信息"""
        lines = prompt.split('\n')
        return {
            'level': self._extract_level(lines),
            'points': self._extract_points(lines)
        }

    def _extract_level(self, lines: List[str]) -> str:
        """提取理解水平描述"""
        for line in lines:
            if "理解水平" in line or "掌握程度" in line:
                return line.strip()
        return lines[1].strip()  # 默认取第二行作为理解水平描述

    def _extract_points(self, lines: List[str]) -> List[str]:
        """提取重点关注点，保持原有内容"""
        points = []
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '•')):
                point = line.split('.', 1)[-1].strip()
                points.append(point)
        return points

class DataAugmenter:
    """数据增强器：仅进行表达方式的变化，不改变原有语义"""
    def __init__(self):
        self.prompt_augmenter = PromptAugmenter()

    def augment_example(self, example: Dict) -> List[Dict]:
        """增强单个样例，仅改变提示词的表达方式"""
        augmented = []
        base_example = deepcopy(example)
        
        # 生成不同表达方式的提示词
        prompt_variations = self.prompt_augmenter.augment_prompt(
            base_example['target_prompt'],
            subject="数据结构"
        )
        
        # 为每个提示词变体创建新样例
        for prompt in prompt_variations:
            variation = deepcopy(base_example)
            variation['target_prompt'] = prompt
            augmented.append(variation)
        
        return augmented

    def augment_dataset(self, dataset: List[Dict]) -> List[Dict]:
        """增强整个数据集"""
        augmented_dataset = []
        for example in dataset:
            augmented_dataset.extend(self.augment_example(example))
        return augmented_dataset