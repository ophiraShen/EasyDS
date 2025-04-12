#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
知识图谱构建主程序
"""

import os
import sys
import yaml
import argparse
import logging
from datetime import datetime
from tqdm import tqdm

# 导入各个模块的处理器
from extractors.pdf_extractor import PDFExtractor
from extractors.term_extractor import TermExtractor
from processors.text_processor import TextProcessor
from processors.knowledge_processor import KnowledgeProcessor
from processors.question_processor import QuestionProcessor
from extractors.relation_extractor import RelationExtractor
from calculators.distance_calculator import ModuleDistanceCalculator
from calculators.weight_calculator import DocumentWeightCalculator
from calculators.similarity_calculator import SemanticSimilarityCalculator
from calculators.score_calculator import RelationScoreCalculator
from builders.graph_builder import KnowledgeGraphBuilder


class KnowledgeGraphConstruction:
    """知识图谱构建类"""

    def __init__(self, config_path, debug=False):
        """
        初始化
        
        Args:
            config_path: 配置文件路径
            debug: 是否启用调试模式
        """
        self.config_path = config_path
        self.debug = debug
        self.config = self._load_config()
        self._setup_logging()
        self._create_dirs()
        self.logger.info("知识图谱构建初始化完成")
    
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            print(f"加载配置文件失败: {str(e)}")
            sys.exit(1)
    
    def _setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config['basic']['log_level'].upper())
        if self.debug:
            log_level = logging.DEBUG
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = f"knowledge_graph_{timestamp}.log"
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("KnowledgeGraph")
    
    def _create_dirs(self):
        """创建必要的目录"""
        dirs = [
            self.config['basic']['temp_dir'],
            self.config['basic']['cache_dir'],
            self.config['basic']['output_dir']
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
            self.logger.debug(f"目录创建成功: {d}")
    
    def run_extract_phase(self):
        """执行提取阶段"""
        self.logger.info("开始执行提取阶段")
        
        # PDF文本提取
        pdf_extractor = PDFExtractor(
            pdf_dir=self.config['resource_files']['pdf_dir'],
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'extracted_texts'),
            use_ocr=self.config['text_extraction']['use_ocr'],
            ocr_lang=self.config['text_extraction']['ocr_language']
        )
        pdf_extractor.extract_all()
        self.logger.info("PDF文本提取完成")
        
        # 术语提取
        term_extractor = TermExtractor(
            text_dir=os.path.join(self.config['basic']['temp_dir'], 'extracted_texts'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'extracted_terms'),
            stopwords_file=self.config['resource_files']['stopwords_file'],
            domain_dict_file=self.config['resource_files']['domain_dict_file'],
            min_term_freq=self.config['text_extraction']['min_term_frequency'],
            max_term_len=self.config['text_extraction']['max_term_length']
        )
        term_extractor.extract_all()
        self.logger.info("术语提取完成")
        
        self.logger.info("提取阶段执行完成")
        return True
    
    def run_process_phase(self):
        """执行处理阶段"""
        self.logger.info("开始执行处理阶段")
        
        # 文本处理
        text_processor = TextProcessor(
            text_dir=os.path.join(self.config['basic']['temp_dir'], 'extracted_texts'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'processed_texts'),
            cleaning_rules=self.config['text_processing']['cleaning_rules']
        )
        text_processor.process_all()
        self.logger.info("文本处理完成")
        
        # 知识点提取
        knowledge_processor = KnowledgeProcessor(
            text_dir=os.path.join(self.config['basic']['temp_dir'], 'processed_texts'),
            term_dir=os.path.join(self.config['basic']['temp_dir'], 'extracted_terms'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'knowledge_points'),
            min_sentence_len=self.config['text_processing']['min_sentence_length'],
            max_sentence_len=self.config['text_processing']['max_sentence_length']
        )
        knowledge_processor.process_all()
        self.logger.info("知识点提取完成")
        
        self.logger.info("处理阶段执行完成")
        return True
    
    def run_relation_phase(self):
        """执行关系阶段"""
        self.logger.info("开始执行关系阶段")
        
        # 关系提取
        relation_extractor = RelationExtractor(
            knowledge_dir=os.path.join(self.config['basic']['temp_dir'], 'knowledge_points'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'relations'),
            relation_types=self.config['relation_extraction']['relation_types'],
            max_distance=self.config['relation_extraction']['max_distance'],
            llm_config=self.config['relation_extraction']['llm_config']
        )
        relation_extractor.extract_all()
        self.logger.info("关系提取完成")
        
        # 试题处理
        if os.path.exists(self.config['resource_files']['question_dir']):
            question_processor = QuestionProcessor(
                question_dir=self.config['resource_files']['question_dir'],
                knowledge_dir=os.path.join(self.config['basic']['temp_dir'], 'knowledge_points'),
                relation_dir=os.path.join(self.config['basic']['temp_dir'], 'relations'),
                output_dir=os.path.join(self.config['basic']['temp_dir'], 'question_relations')
            )
            question_processor.process_all()
            self.logger.info("试题处理完成")
        else:
            self.logger.warning("试题目录不存在，跳过试题处理")
        
        self.logger.info("关系阶段执行完成")
        return True
    
    def run_score_phase(self):
        """执行评分阶段"""
        self.logger.info("开始执行评分阶段")
        
        # 模块距离计算
        distance_calculator = ModuleDistanceCalculator(
            relation_dir=os.path.join(self.config['basic']['temp_dir'], 'relations'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'distance_scores'),
            weight=self.config['scoring']['module_distance_weight']
        )
        distance_calculator.calculate_all()
        self.logger.info("模块距离计算完成")
        
        # 文档权重计算
        weight_calculator = DocumentWeightCalculator(
            relation_dir=os.path.join(self.config['basic']['temp_dir'], 'relations'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'weight_scores'),
            weight=self.config['scoring']['document_importance_weight']
        )
        weight_calculator.calculate_all()
        self.logger.info("文档权重计算完成")
        
        # 语义相似度计算
        similarity_calculator = SemanticSimilarityCalculator(
            knowledge_dir=os.path.join(self.config['basic']['temp_dir'], 'knowledge_points'),
            relation_dir=os.path.join(self.config['basic']['temp_dir'], 'relations'),
            output_dir=os.path.join(self.config['basic']['temp_dir'], 'similarity_scores'),
            weight=self.config['scoring']['semantic_similarity_weight'],
            model_name=self.config['scoring']['similarity_model'],
            device=self.config['scoring']['device']
        )
        similarity_calculator.calculate_all()
        self.logger.info("语义相似度计算完成")
        
        # 最终评分计算
        score_calculator = RelationScoreCalculator(
            distance_dir=os.path.join(self.config['basic']['temp_dir'], 'distance_scores'),
            weight_dir=os.path.join(self.config['basic']['temp_dir'], 'weight_scores'),
            similarity_dir=os.path.join(self.config['basic']['temp_dir'], 'similarity_scores'),
            relation_dir=os.path.join(self.config['basic']['temp_dir'], 'relations'),
            question_relation_dir=os.path.join(self.config['basic']['temp_dir'], 'question_relations'),
            output_dir=os.path.join(self.config['basic']['output_dir'], 'final_relations')
        )
        score_calculator.calculate_all()
        self.logger.info("最终评分计算完成")
        
        self.logger.info("评分阶段执行完成")
        return True
    
    def run_build_phase(self):
        """执行构建阶段"""
        self.logger.info("开始执行构建阶段")
        
        # 图数据库构建
        graph_builder = KnowledgeGraphBuilder(
            knowledge_dir=os.path.join(self.config['basic']['temp_dir'], 'knowledge_points'),
            relation_dir=os.path.join(self.config['basic']['output_dir'], 'final_relations'),
            db_config=self.config['database'],
            validation_rules=self.config['database']['validation_rules']
        )
        
        # 连接数据库
        graph_builder.connect()
        self.logger.info("数据库连接成功")
        
        # 清理数据库
        graph_builder.clear_database()
        self.logger.info("数据库清理完成")
        
        # 创建约束和索引
        graph_builder.create_constraints()
        self.logger.info("约束和索引创建完成")
        
        # 导入知识点
        graph_builder.import_knowledge_points()
        self.logger.info("知识点导入完成")
        
        # 导入关系
        graph_builder.import_relations()
        self.logger.info("关系导入完成")
        
        # 验证数据
        validation_result = graph_builder.validate_data()
        if validation_result:
            self.logger.info("数据验证通过")
        else:
            self.logger.warning("数据验证未通过，请检查日志")
        
        # 断开连接
        graph_builder.disconnect()
        
        # 生成报告
        graph_builder.generate_report(os.path.join(self.config['basic']['output_dir'], 'build_report.json'))
        self.logger.info("构建报告生成完成")
        
        self.logger.info("构建阶段执行完成")
        return True
    
    def run_all_phases(self):
        """执行所有阶段"""
        self.logger.info("开始执行所有阶段")
        
        phases = [
            self.run_extract_phase,
            self.run_process_phase,
            self.run_relation_phase,
            self.run_score_phase,
            self.run_build_phase
        ]
        
        for phase_func in phases:
            result = phase_func()
            if not result:
                self.logger.error(f"阶段 {phase_func.__name__} 执行失败，终止后续阶段")
                return False
        
        self.logger.info("所有阶段执行完成")
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="知识图谱构建工具")
    parser.add_argument("--config", required=True, help="配置文件路径")
    parser.add_argument("--phase", default="all", choices=["extract", "process", "relation", "score", "build", "all"],
                        help="执行阶段")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    args = parser.parse_args()
    
    # 创建知识图谱构建实例
    kg_construction = KnowledgeGraphConstruction(args.config, args.debug)
    
    # 根据选择的阶段执行相应的操作
    if args.phase == "extract":
        kg_construction.run_extract_phase()
    elif args.phase == "process":
        kg_construction.run_process_phase()
    elif args.phase == "relation":
        kg_construction.run_relation_phase()
    elif args.phase == "score":
        kg_construction.run_score_phase()
    elif args.phase == "build":
        kg_construction.run_build_phase()
    elif args.phase == "all":
        kg_construction.run_all_phases()
    else:
        print(f"未知阶段: {args.phase}")
        sys.exit(1)


if __name__ == "__main__":
    main() 