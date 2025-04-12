# EasyDS - 基于多智能体的智能教学系统

## 1. 系统概述

EasyDS 是一个基于大语言模型的多智能体协同教学系统，专注于考研数据结构教育。系统采用费曼学习法的教学理念，通过路由、学生和教师三层智能体模型，突破传统"问答式"AI辅导教学范式，构建"讲解-反馈-修正-强化"的教学闭环。

### 1.1 核心特点

- 基于费曼学习法的引导式教学
- 三层智能体模型（路由、学生、教师）
- RelationScore知识图谱驱动的学习评估
- GRPO优化的教师智能体
- 自适应学习路径生成

## 2. 系统架构
```
EasyDS/
|—— functional_docs/
|   ├── main_plans.md      # 主计划文档
|   ├── data_processing.md # 数据处理文档
|   ├── agent.md           # 智能体系统文档
|   ├── knowledge_graph.md # 知识图谱系统文档
|—— data/
│   ├── grpo_data/         # GRPO训练数据
│   │   ├── raw_data.jsonl
│   │   ├── train_data.jsonl
│   │   ├── eval_data.jsonl
│   │   └── test_data.jsonl
│   ├── knowledge_graph/   # 知识图谱数据
│   │   ├── nodes.json     # 知识点节点
│   │   ├── relations.json # 关系数据
│   │   └── metadata.json  # 元数据
│   ├── pdfs/              # 原始PDF资料
│   ├── resources/         # 资源文件
│   │   ├── stopwords.txt  # 停用词表
│   │   └── domain_dict.txt # 领域词典
│   ├── kg_temp/           # 知识图谱处理临时文件
│   └── kg_output/         # 知识图谱输出文件
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   ├── processor.py
|   |   ├── generate_grpo_data.py
│   │   └── knowledge_graph_builder.py
│   ├── knowledge_graph/
│   │   ├── main.py        # 知识图谱构建主程序
│   │   ├── extractors/
│   │   │   ├── pdf_extractor.py     # PDF文本提取器
│   │   │   ├── term_extractor.py    # 术语提取器
│   │   │   └── relation_extractor.py # 关系提取器
│   │   ├── processors/
│   │   │   ├── text_processor.py    # 文本处理器
│   │   │   ├── knowledge_processor.py # 知识点处理器
│   │   │   └── question_processor.py # 试题处理器
│   │   ├── calculators/
│   │   │   ├── distance_calculator.py  # 距离计算器
│   │   │   ├── weight_calculator.py    # 权重计算器
│   │   │   ├── similarity_calculator.py # 相似度计算器
│   │   │   └── score_calculator.py      # 评分计算器
│   │   └── builders/
│   │       └── graph_builder.py     # 图谱构建器
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── router_agent.py
│   │   ├── student_agent.py
│   │   ├── teacher_agent.py
│   │   └── agent_workflow.py
│   └── models/
|       └── grpo/
|           ├── config.yaml
|           ├── train.py
|           └── evaluate.py
├── openrlhf_workspace/
│   └── scripts/
│       └── train_grpo.sh
│   
└── configs/
    ├── agent_config.yaml   # 智能体配置
    ├── kg_config.yaml      # 知识图谱配置
    └── grpo_config.yaml    # GRPO训练配置
```

### 2.1 智能体组成

1. **路由智能体**
   - 评估用户讲解回答的正确性与完整性
   - 基于RelationScore知识图谱分析知识关联度
   - 决策选择学生智能体或教师智能体
   - 动态调整教学路径

2. **学生智能体**
   - 针对用户讲解提出深度追问
   - 模拟学习者困惑点
   - 引导用户进行更清晰的阐述

3. **教师智能体**
   - 实现费曼学习法的引导式教学
   - 纠错与方向性指导
   - 总结反馈与知识点强化
   - 通过GRPO优化的计算推理能力

### 2.2 核心模块

1. **多智能体协同框架**
   - 基于LangGraph/LangChain的智能体通信
   - 教学流程状态管理
   - 智能体角色定义与转换

2. **RelationScore知识图谱系统**
   - 考研数据结构知识点图谱
   - 知识点关联度量化（RelationScore）
   - RAG技术支持的路由决策
   - 自适应学习路径生成

3. **教师智能体优化系统**
   - 基于DeepSeek-R1-Distill-Qwen-14B
   - GRPO奖励机制设计
   - 双指标评估体系：答案正确性+步骤合理性
   - 计算推理能力增强

## 3. 实现计划

### 3.1 第一阶段：多智能体系统搭建

1. **基础框架搭建**
   - LangGraph/LangChain环境配置
   - 智能体通信协议设计
   - 会话流程实现

2. **智能体开发**
   - 路由智能体实现
     * 路由决策Prompt设计
     * RAG检索模块集成
     * 状态转换逻辑实现
   - 学生智能体实现
     * 追问策略设计
     * 上下文理解能力
   - 教师智能体实现
     * 纠错引导机制
     * 知识点讲解模板
   - 智能体协同调试

3. **教学流程优化**
   - 状态流转逻辑完善
   - 边界情况处理
   - 用户体验优化

### 3.2 第二阶段：RelationScore知识图谱构建

1. **知识图谱设计**
   - 数据结构考点分析
   - 关系类型定义（包含、先决条件、相关、应用、实例）
   - RelationScore计算方法设计

2. **知识提取与处理流程**
   - PDF文本提取
     * 基于PyMuPDF的文本提取
     * 扫描文档OCR识别（Tesseract支持）
     * 多语言文本处理（中英文）
   - 术语提取
     * 基于词频和TF-IDF的术语识别
     * 领域术语字典匹配
     * 停用词过滤
   - 关系提取
     * 规则方法：基于句法模式和关键词提取实体间关系
     * 统计方法：分析术语共现计算关联度
     * 神经网络方法：基于spaCy和HanLP的句法依存分析
   - 知识点处理
     * 文本清洗和标准化
     * 句子分割与结构化
     * 知识点聚合

3. **评分计算系统**
   - 模块距离计算
     * 基于知识点所属模块的结构距离
     * 模块内与模块间关系权重差异化
   - 文档权重计算
     * 基于文档重要性的权重分配
     * 教材与真题的差异化处理
   - 语义相似度计算
     * 基于预训练模型的语义向量表示
     * 多语言支持（中英文）
   - RelationScore评分机制
     * 综合距离、权重和相似度的多维评分
     * 考虑试题关联的附加权重

4. **知识图谱构建**
   - Neo4j数据库设计
   - 节点与关系导入
   - 约束和索引优化
   - 查询接口实现

5. **RAG检索系统集成**
   - 向量数据库构建
   - 检索策略优化
   - 路由智能体集成

### 3.3 第三阶段：教师智能体GRPO优化

1. **数据准备**
   - 计算类题目收集
     * 近10年考研真题精选
     * 数据增强扩展
   - 数据标注与处理
     * 双指标评估标准建立
     * 训练集划分

2. **GRPO训练框架搭建**
   - 基座模型准备（DeepSeek-R1-Distill-Qwen-14B）
   - 奖励模型设计
     * 答案正确性评估（7分）
     * 步骤合理性评估（3分）
   - 训练流程实现

3. **模型训练与评估**
   - 参数优化
   - 性能评估
   - 模型集成

### 3.4 第四阶段：系统集成与测试

1. **模块整合**
   - 多智能体系统部署
   - 知识图谱系统接入
   - 优化后教师智能体集成

2. **系统测试**
   - 功能测试
   - 性能测试
   - 用户体验测试

3. **系统优化**
   - 性能优化
   - 交互优化
   - 教学效果评估

## 4. 技术栈

- LangGraph/LangChain: 智能体框架
- PyTorch: 模型训练框架
- Neo4j: 知识图谱存储
- FastAPI: 后端服务
- Vue.js: 前端界面
- DeepSeek-R1-Distill-Qwen-14B: 基座模型
- PyMuPDF: PDF文档处理
- Spacy/HanLP: 自然语言处理
- Tesseract: OCR文本识别
- Sentence-Transformers: 语义相似度计算

## 5. 评估指标

1. **教学效果**
   - 知识点掌握度
   - 学习进度达成率
   - 错误修正效率
   - 知识迁移能力

2. **系统性能**
   - 路由决策准确率
   - 教师智能体计算推理准确率
   - 响应时间
   - 资源利用率

3. **用户体验**
   - 学习投入度
   - 引导准确性
   - 交互流畅度
   - 满意度评分

4. **知识图谱评估**
   - 知识点覆盖率
   - 关系提取准确率
   - 知识连通性分析
   - RelationScore一致性

## 6. 创新特色

1. **三层智能体模型**
   - 突破传统"问答式"教学范式
   - "讲解-反馈-修正-强化"教学闭环
   - 动态路由决策机制

2. **RelationScore知识图谱**
   - 知识点关联度量化
   - 考点间关联性分析
   - 多维度评分机制（模块距离、文档权重、语义相似度）
   - 精准路由智能体决策支持

3. **教师智能体GRPO优化**
   - 双指标评估体系
   - 针对计算推理能力增强
   - 专业领域知识优化

4. **费曼学习法实践**
   - 主动讲解机制
   - 深度追问策略
   - 纠错引导闭环

## 7. 后续扩展

1. **课程扩展**
   - 考研其他学科
   - 本科专业课程
   - 专业认证考试

2. **功能增强**
   - 多模态交互
   - 个性化学习分析
   - 智能助教系统
   - 学习进度预测

3. **知识图谱增强**
   - 多源数据集成
   - 交互式知识编辑
   - 动态知识更新
   - 知识推理能力