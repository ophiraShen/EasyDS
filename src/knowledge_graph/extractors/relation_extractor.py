#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从文本中提取实体关系的工具
"""

import os
import re
import json
import logging
import spacy
import jieba
import numpy as np
from tqdm import tqdm
from collections import defaultdict

try:
    import hanlp
    HANLP_AVAILABLE = True
except ImportError:
    HANLP_AVAILABLE = False


class RelationExtractor:
    """关系提取器
    
    用于从文本中提取实体之间的关系，支持规则、统计和神经网络方法。
    """
    
    def __init__(self, input_dir, output_dir, terms_file=None, method="rule"):
        """
        初始化关系提取器
        
        Args:
            input_dir: 输入文本目录
            output_dir: 输出目录
            terms_file: 术语文件路径
            method: 提取方法，可选 'rule', 'statistical', 'neural'
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.method = method
        self.terms = []
        self.term_dict = {}
        self.logger = logging.getLogger("KnowledgeGraph.RelationExtractor")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载术语
        if terms_file and os.path.exists(terms_file):
            try:
                with open(terms_file, 'r', encoding='utf-8') as f:
                    terms_data = json.load(f)
                    if 'terms' in terms_data and isinstance(terms_data['terms'], list):
                        self.terms = [item['term'] for item in terms_data['terms']]
                        self.term_dict = {item['term']: item.get('frequency', 1) for item in terms_data['terms']}
                self.logger.info(f"已加载 {len(self.terms)} 个术语")
            except Exception as e:
                self.logger.error(f"加载术语文件时出错: {str(e)}")
        
        # 初始化NLP工具
        self._init_nlp_tools()
    
    def _init_nlp_tools(self):
        """初始化NLP工具"""
        self.nlp_tools = {}
        
        # 加载英文模型
        try:
            self.nlp_tools['en'] = spacy.load("en_core_web_sm")
            self.logger.info("已加载英文NLP模型")
        except Exception as e:
            self.logger.warning(f"加载英文NLP模型失败: {str(e)}")
        
        # 加载中文模型
        if HANLP_AVAILABLE:
            try:
                self.nlp_tools['zh'] = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
                self.logger.info("已加载中文NLP模型")
            except Exception as e:
                self.logger.warning(f"加载中文NLP模型失败: {str(e)}")
    
    def extract_all(self):
        """从所有文本文件中提取关系"""
        json_files = [f for f in os.listdir(self.input_dir) if f.endswith('.json')]
        self.logger.info(f"找到 {len(json_files)} 个JSON文件需要处理")
        
        all_relations = []
        
        for filename in tqdm(json_files, desc="提取关系"):
            try:
                filepath = os.path.join(self.input_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 合并所有页面的文本
                if 'content' in data and isinstance(data['content'], list):
                    text = ' '.join([page['text'] for page in data['content'] if 'text' in page])
                else:
                    self.logger.warning(f"文件格式不正确: {filename}")
                    continue
                
                # 提取关系
                relations = self.extract_from_text(text)
                if relations:
                    source = data.get('filename', filename)
                    for relation in relations:
                        relation['source'] = source
                    all_relations.extend(relations)
            
            except Exception as e:
                self.logger.error(f"处理文件 {filename} 时出错: {str(e)}")
        
        # 保存关系
        relations_output = os.path.join(self.output_dir, 'relations.json')
        with open(relations_output, 'w', encoding='utf-8') as f:
            json.dump({
                'relations': all_relations
            }, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"共提取 {len(all_relations)} 个关系")
        return all_relations
    
    def extract_from_text(self, text):
        """
        从文本中提取关系
        
        Args:
            text: 输入文本
            
        Returns:
            提取的关系列表，每个关系为dict，包含head, relation, tail
        """
        if self.method == "rule":
            return self._extract_by_rule(text)
        elif self.method == "statistical":
            return self._extract_by_statistical(text)
        elif self.method == "neural":
            return self._extract_by_neural(text)
        else:
            self.logger.warning(f"不支持的方法: {self.method}，使用规则方法")
            return self._extract_by_rule(text)
    
    def _extract_by_rule(self, text):
        """使用规则方法提取关系"""
        relations = []
        
        # 将文本按句子切分
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            # 找到句子中包含的术语
            found_terms = self._find_terms_in_text(sentence)
            
            if len(found_terms) >= 2:
                # 基本规则：同一个句子中的术语可能有关系
                for i in range(len(found_terms)):
                    for j in range(i+1, len(found_terms)):
                        head = found_terms[i]
                        tail = found_terms[j]
                        
                        # 提取关系词
                        relation = self._extract_relation_between(sentence, head, tail)
                        
                        if relation:
                            relations.append({
                                'head': head,
                                'relation': relation,
                                'tail': tail,
                                'sentence': sentence
                            })
        
        return relations
    
    def _extract_by_statistical(self, text):
        """使用统计方法提取关系"""
        # 计算术语共现矩阵
        sentences = self._split_sentences(text)
        co_occurrence = defaultdict(lambda: defaultdict(int))
        
        for sentence in sentences:
            found_terms = self._find_terms_in_text(sentence)
            
            # 统计共现
            for i in range(len(found_terms)):
                for j in range(i+1, len(found_terms)):
                    head = found_terms[i]
                    tail = found_terms[j]
                    co_occurrence[head][tail] += 1
                    co_occurrence[tail][head] += 1
        
        # 转换为关系
        relations = []
        for head in co_occurrence:
            for tail in co_occurrence[head]:
                count = co_occurrence[head][tail]
                if count > 1:  # 仅保留出现次数大于阈值的共现关系
                    relations.append({
                        'head': head,
                        'relation': 'co_occurrence',
                        'tail': tail,
                        'weight': count
                    })
        
        return relations
    
    def _extract_by_neural(self, text):
        """使用神经网络方法提取关系"""
        relations = []
        
        # 检查是否有可用的NLP工具
        if not self.nlp_tools:
            self.logger.warning("没有可用的NLP工具，无法使用神经网络方法")
            return self._extract_by_rule(text)
        
        # 分离中英文
        zh_text, en_text = self._separate_languages(text)
        
        # 处理中文
        if 'zh' in self.nlp_tools and zh_text:
            zh_relations = self._extract_relations_hanlp(zh_text)
            relations.extend(zh_relations)
        
        # 处理英文
        if 'en' in self.nlp_tools and en_text:
            en_relations = self._extract_relations_spacy(en_text)
            relations.extend(en_relations)
        
        return relations
    
    def _extract_relations_spacy(self, text):
        """使用spaCy提取英文关系"""
        relations = []
        doc = self.nlp_tools['en'](text)
        
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in ("nsubj", "nsubjpass") and token.head.pos_ == "VERB":
                    subj = token.text
                    verb = token.head.text
                    
                    for child in token.head.children:
                        if child.dep_ in ("dobj", "pobj"):
                            obj = child.text
                            
                            # 检查主语和宾语是否在术语列表中
                            if self.terms and (subj in self.terms or obj in self.terms):
                                relations.append({
                                    'head': subj,
                                    'relation': verb,
                                    'tail': obj,
                                    'sentence': sent.text
                                })
        
        return relations
    
    def _extract_relations_hanlp(self, text):
        """使用HanLP提取中文关系"""
        relations = []
        
        # 使用HanLP进行句法分析
        doc = self.nlp_tools['zh'](text)
        
        # 依存关系提取
        for sent_idx, tree in enumerate(doc['dep']):
            for token_idx, (word, pos, head, dep) in enumerate(tree):
                # 检查主谓宾关系
                if dep == 'nsubj' and 0 <= head < len(tree):
                    subj = word
                    pred_idx = head
                    pred = tree[pred_idx][0]
                    
                    # 查找宾语
                    for obj_idx, (obj_word, obj_pos, obj_head, obj_dep) in enumerate(tree):
                        if obj_dep == 'dobj' and obj_head == pred_idx:
                            obj = obj_word
                            
                            # 检查主语和宾语是否在术语列表中
                            if self.terms and (subj in self.terms or obj in self.terms):
                                relations.append({
                                    'head': subj,
                                    'relation': pred,
                                    'tail': obj,
                                    'sentence': text
                                })
        
        return relations
    
    def _split_sentences(self, text):
        """将文本切分为句子"""
        # 简单的句子切分规则
        pattern = r'([。！？\.!?])'
        text = re.sub(pattern, r'\1\n', text)
        sentences = [s.strip() for s in text.split('\n') if s.strip()]
        return sentences
    
    def _find_terms_in_text(self, text):
        """在文本中查找术语"""
        found_terms = []
        
        # 如果没有预定义术语，使用简单的分词
        if not self.terms:
            words = jieba.lcut(text)
            return [w for w in words if len(w) >= 2]
        
        # 查找预定义术语
        for term in self.terms:
            if term in text:
                found_terms.append(term)
        
        return found_terms
    
    def _extract_relation_between(self, sentence, head, tail):
        """提取两个术语之间的关系词"""
        # 简单方法：提取两个术语之间的文本
        pattern = re.escape(head) + r'(.*?)' + re.escape(tail)
        match = re.search(pattern, sentence)
        
        if match:
            relation = match.group(1).strip()
            # 清理关系词
            relation = re.sub(r'[,，、的是]', '', relation).strip()
            return relation if relation else "相关"
        
        # 如果第一个模式没匹配到，尝试反向匹配
        pattern = re.escape(tail) + r'(.*?)' + re.escape(head)
        match = re.search(pattern, sentence)
        
        if match:
            relation = match.group(1).strip()
            # 清理关系词
            relation = re.sub(r'[,，、的是]', '', relation).strip()
            return relation if relation else "相关"
        
        # 默认关系
        return "相关"
    
    def _separate_languages(self, text):
        """将文本分离为中文和英文部分"""
        zh_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        en_pattern = re.compile(r'[a-zA-Z][a-zA-Z0-9_\-\']*[a-zA-Z0-9]')
        
        zh_text = ' '.join(zh_pattern.findall(text))
        en_text = ' '.join(en_pattern.findall(text))
        
        return zh_text, en_text


if __name__ == "__main__":
    # 简单测试代码
    logging.basicConfig(level=logging.DEBUG)
    extractor = RelationExtractor(
        input_dir="./extracted_texts",
        output_dir="./extracted_relations",
        terms_file="./extracted_terms/terms.json",
        method="rule"
    )
    extractor.extract_all()