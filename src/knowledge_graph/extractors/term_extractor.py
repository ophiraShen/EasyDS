 #!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
从文本中提取关键术语的工具
"""

import os
import re
import json
import logging
import nltk
import jieba
import jieba.posseg as pseg
from tqdm import tqdm
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer


class TermExtractor:
    """术语提取器
    
    用于从文本中提取关键术语，支持中英文混合处理。
    """
    
    def __init__(self, input_dir, output_dir, stopwords_path=None, custom_dict_path=None):
        """
        初始化术语提取器
        
        Args:
            input_dir: 输入文本目录
            output_dir: 输出目录
            stopwords_path: 停用词文件路径
            custom_dict_path: 自定义词典路径
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.logger = logging.getLogger("KnowledgeGraph.TermExtractor")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 加载停用词
        self.stopwords = set()
        if stopwords_path and os.path.exists(stopwords_path):
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                self.stopwords = set([line.strip() for line in f])
            self.logger.info(f"已加载 {len(self.stopwords)} 个停用词")
        
        # 加载自定义词典
        if custom_dict_path and os.path.exists(custom_dict_path):
            jieba.load_userdict(custom_dict_path)
            self.logger.info(f"已加载自定义词典: {custom_dict_path}")
        
        # 确保nltk数据已下载
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        try:
            nltk.data.find('taggers/averaged_perceptron_tagger')
        except LookupError:
            nltk.download('averaged_perceptron_tagger')
    
    def extract_all(self, min_term_freq=2, min_term_length=2):
        """从所有文本文件中提取术语"""
        json_files = [f for f in os.listdir(self.input_dir) if f.endswith('.json')]
        self.logger.info(f"找到 {len(json_files)} 个JSON文件需要处理")
        
        all_terms = []
        file_terms = {}
        
        for filename in tqdm(json_files, desc="提取术语"):
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
                
                # 提取术语
                terms = self.extract_from_text(text)
                if terms:
                    file_terms[data.get('filename', filename)] = terms
                    all_terms.extend(terms)
            
            except Exception as e:
                self.logger.error(f"处理文件 {filename} 时出错: {str(e)}")
        
        # 术语频率统计
        term_counter = Counter(all_terms)
        
        # 过滤低频和短术语
        filtered_terms = {term: count for term, count in term_counter.items() 
                         if count >= min_term_freq and len(term) >= min_term_length}
        
        # 保存全局术语
        terms_output = os.path.join(self.output_dir, 'terms.json')
        with open(terms_output, 'w', encoding='utf-8') as f:
            json.dump({
                'terms': [{'term': term, 'frequency': count} 
                         for term, count in sorted(filtered_terms.items(), key=lambda x: x[1], reverse=True)]
            }, f, ensure_ascii=False, indent=2)
        
        # 保存每个文件的术语
        file_terms_output = os.path.join(self.output_dir, 'file_terms.json')
        with open(file_terms_output, 'w', encoding='utf-8') as f:
            json.dump(file_terms, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"共提取 {len(all_terms)} 个术语，过滤后保留 {len(filtered_terms)} 个")
        return filtered_terms
    
    def extract_from_text(self, text):
        """
        从文本中提取术语
        
        Args:
            text: 输入文本
            
        Returns:
            提取的术语列表
        """
        # 分离中英文
        zh_text, en_text = self._separate_languages(text)
        
        # 提取中文术语
        zh_terms = self._extract_chinese_terms(zh_text)
        
        # 提取英文术语
        en_terms = self._extract_english_terms(en_text)
        
        # 合并结果
        return zh_terms + en_terms
    
    def _separate_languages(self, text):
        """将文本分离为中文和英文部分"""
        zh_pattern = re.compile(r'[\u4e00-\u9fa5]+')
        en_pattern = re.compile(r'[a-zA-Z][a-zA-Z0-9_\-\']*[a-zA-Z0-9]')
        
        zh_text = ' '.join(zh_pattern.findall(text))
        en_text = ' '.join(en_pattern.findall(text))
        
        return zh_text, en_text
    
    def _extract_chinese_terms(self, text):
        """提取中文术语"""
        if not text:
            return []
        
        # 使用结巴分词并标注词性
        words = pseg.cut(text)
        
        # 过滤词性，保留名词、动词等实意词
        valid_pos = {'n', 'nr', 'ns', 'nt', 'nz', 'v', 'vn', 'eng'}
        filtered_words = [word for word, flag in words 
                         if word not in self.stopwords and flag in valid_pos]
        
        return filtered_words
    
    def _extract_english_terms(self, text):
        """提取英文术语"""
        if not text:
            return []
        
        # 分词
        tokens = nltk.word_tokenize(text.lower())
        
        # 词性标注
        tagged_tokens = nltk.pos_tag(tokens)
        
        # 过滤词性，保留名词、动词等
        valid_pos = {'NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'}
        filtered_words = [word for word, pos in tagged_tokens 
                         if word not in self.stopwords and pos in valid_pos]
        
        return filtered_words


if __name__ == "__main__":
    # 简单测试代码
    logging.basicConfig(level=logging.DEBUG)
    extractor = TermExtractor(
        input_dir="./extracted_texts",
        output_dir="./extracted_terms",
        stopwords_path="./stopwords.txt"
    )
    extractor.extract_all(min_term_freq=3, min_term_length=2)