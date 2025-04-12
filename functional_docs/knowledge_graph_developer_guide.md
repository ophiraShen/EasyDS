# 知识图谱构建指南

本文档详细说明了从PDF资料到RelationScore知识图谱的完整构建流程。

## 1. 项目概述

### 1.1 目标
构建基于RelationScore的数据结构知识图谱，为考研教学提供精准的知识关联服务。

### 1.2 数据来源
- 考研大纲PDF
- 数据结构教材PDF
- 考研真题PDF（近10年）

### 1.3 技术栈
- **Python**: 核心处理语言
- **Neo4j**: 图数据库
- **NLP库**: SpaCy, NLTK
- **向量模型**: Sentence-Transformers
- **图算法**: NetworkX

### 1.4 目录结构
```
EasyDS/
└── src/
    └── knowledge_graph/
        ├── extract/
        │   ├── __init__.py
        │   ├── pdf_extractor.py        # PDF文本提取
        │   ├── term_extractor.py       # 术语提取
        │   └── relation_extractor.py   # 关系提取
        ├── process/
        │   ├── __init__.py
        │   ├── knowledge_processor.py  # 知识点处理
        │   ├── question_processor.py   # 试题处理
        │   └── text_processor.py       # 文本清洗处理
        ├── score/
        │   ├── __init__.py
        │   ├── module_distance.py      # 模块距离计算
        │   ├── document_weight.py      # 真题共现权重
        │   ├── semantic_similarity.py  # 语义相似度
        │   └── relation_score.py       # 关系分数融合
        ├── database/
        │   ├── __init__.py
        │   ├── neo4j_connector.py      # Neo4j连接器
        │   └── graph_builder.py        # 图谱构建工具
        ├── models/
        │   ├── __init__.py
        │   ├── knowledge_point.py      # 知识点模型
        │   └── relation.py             # 关系模型
        ├── utils/
        │   ├── __init__.py
        │   ├── config.py               # 配置文件
        │   └── logger.py               # 日志工具
        ├── main.py                     # 主执行脚本
        └── config.yaml                 # 配置文件
```

## 2. 构建流程

### 2.1 数据预处理阶段

#### 2.1.1 PDF文本提取
从PDF文件中提取文本内容，包括大纲、教材和真题。

**执行脚本**: `src/knowledge_graph/extract/pdf_extractor.py`

**关键步骤**:
1. 安装必要的库：`pdfplumber`, `pytesseract`（用于OCR）
2. 提取PDF文本内容
3. 对扫描版PDF进行OCR处理
4. 保存提取的文本为结构化文件

**示例命令**:
```bash
python -m src.knowledge_graph.extract.pdf_extractor --input_dir ./data/pdf --output_dir ./data/text
```

#### 2.1.2 文本清洗与结构化
清洗提取的文本，去除噪声，并进行初步结构化。

**执行脚本**: `src/knowledge_graph/process/text_processor.py`

**关键步骤**:
1. 去除页眉页脚
2. 识别章节结构
3. 分割段落和句子
4. 识别真题中的题号、题目内容、选项和答案

**示例命令**:
```bash
python -m src.knowledge_graph.process.text_processor --input_dir ./data/text --output_dir ./data/processed
```

### 2.2 知识点提取阶段

#### 2.2.1 领域词典构建
从大纲和教材中提取关键术语，建立数据结构领域词典。

**执行脚本**: `src/knowledge_graph/extract/term_extractor.py`

**关键步骤**:
1. 使用正则表达式提取大纲中的术语
2. 使用NLP工具识别专业名词
3. 合并去重，生成领域词典

**示例命令**:
```bash
python -m src.knowledge_graph.extract.term_extractor --input_file ./data/processed/outline.txt --output_file ./data/dictionary/terms.json
```

#### 2.2.2 知识点识别与结构化
根据领域词典，从文本中识别知识点并进行结构化。

**执行脚本**: `src/knowledge_graph/process/knowledge_processor.py`

**关键步骤**:
1. 加载领域词典
2. 从文本中识别知识点
3. 提取知识点定义和属性
4. 确定知识点类别
5. 生成结构化知识点数据

**示例命令**:
```bash
python -m src.knowledge_graph.process.knowledge_processor --terms_file ./data/dictionary/terms.json --input_dir ./data/processed --output_file ./data/kg/knowledge_points.json
```

### 2.3 关系抽取阶段

#### 2.3.1 基于规则的关系提取
使用规则和模式识别知识点之间的关系。

**执行脚本**: `src/knowledge_graph/extract/relation_extractor.py`

**关键步骤**:
1. 加载知识点数据
2. 根据规则识别知识点间的关系（包含、前置、相似等）
3. 保存提取的关系

**示例命令**:
```bash
python -m src.knowledge_graph.extract.relation_extractor --knowledge_file ./data/kg/knowledge_points.json --text_dir ./data/processed --output_file ./data/kg/relations.json
```

#### 2.3.2 真题数据处理
处理真题数据，建立知识点与试题的关联。

**执行脚本**: `src/knowledge_graph/process/question_processor.py`

**关键步骤**:
1. 加载知识点数据和真题文本
2. 识别题目中涉及的知识点
3. 提取题目年份、类型等信息
4. 保存结构化的题目数据

**示例命令**:
```bash
python -m src.knowledge_graph.process.question_processor --knowledge_file ./data/kg/knowledge_points.json --questions_dir ./data/processed/questions --output_file ./data/kg/questions.json
```

### 2.4 RelationScore计算阶段

#### 2.4.1 模块距离(MD)计算
计算知识点在知识树中的结构相似性。

**执行脚本**: `src/knowledge_graph/score/module_distance.py`

**关键步骤**:
1. 构建知识树
2. 计算节点间最短路径距离
3. 归一化处理，生成MD分数

**示例命令**:
```bash
python -m src.knowledge_graph.score.module_distance --knowledge_file ./data/kg/knowledge_points.json --relations_file ./data/kg/relations.json --output_file ./data/kg/md_scores.json
```

#### 2.4.2 真题共现权重(DW)计算
基于真题中知识点共现情况，计算PageRank权重。

**执行脚本**: `src/knowledge_graph/score/document_weight.py`

**关键步骤**:
1. 构建共现矩阵
2. 使用NetworkX计算PageRank值
3. Z-score标准化处理
4. 生成DW分数

**示例命令**:
```bash
python -m src.knowledge_graph.score.document_weight --knowledge_file ./data/kg/knowledge_points.json --questions_file ./data/kg/questions.json --output_file ./data/kg/dw_scores.json
```

#### 2.4.3 语义相似度(SS)计算
计算知识点文本的语义相似度。

**执行脚本**: `src/knowledge_graph/score/semantic_similarity.py`

**关键步骤**:
1. 使用预训练模型获取文本嵌入
2. 计算余弦相似度
3. 生成SS分数

**示例命令**:
```bash
python -m src.knowledge_graph.score.semantic_similarity --knowledge_file ./data/kg/knowledge_points.json --output_file ./data/kg/ss_scores.json
```

#### 2.4.4 RelationScore融合计算
融合三个维度的分数，计算最终的RelationScore。

**执行脚本**: `src/knowledge_graph/score/relation_score.py`

**关键步骤**:
1. 加载三个维度的分数
2. 设置权重参数
3. 加权融合计算
4. 归一化至0-10范围
5. 保存最终RelationScore

**示例命令**:
```bash
python -m src.knowledge_graph.score.relation_score --md_file ./data/kg/md_scores.json --dw_file ./data/kg/dw_scores.json --ss_file ./data/kg/ss_scores.json --output_file ./data/kg/relation_scores.json --weights 0.4 0.3 0.3
```

### 2.5 知识图谱构建阶段

#### 2.5.1 Neo4j环境设置
配置Neo4j数据库环境。

**前置条件**:
1. 下载并安装Neo4j Desktop
2. 创建新的数据库实例，设置密码
3. 安装APOC插件(可选)

**配置文件**: `src/knowledge_graph/config.yaml`

#### 2.5.2 导入数据到Neo4j
将处理好的数据导入Neo4j数据库。

**执行脚本**: `src/knowledge_graph/database/graph_builder.py`

**关键步骤**:
1. 连接Neo4j数据库
2. 创建索引
3. 导入知识点节点
4. 导入题目节点
5. 创建关系并设置RelationScore

**示例命令**:
```bash
python -m src.knowledge_graph.database.graph_builder --knowledge_file ./data/kg/knowledge_points.json --relations_file ./data/kg/relations.json --questions_file ./data/kg/questions.json --relation_scores_file ./data/kg/relation_scores.json
```

#### 2.5.3 验证和可视化
验证知识图谱的完整性和正确性，并进行可视化。

**操作步骤**:
1. 打开Neo4j Browser
2. 运行验证查询
3. 可视化核心知识点和关系

**示例查询**:
```cypher
// 查看所有知识点
MATCH (n:KnowledgePoint) RETURN n LIMIT 100;

// 查看特定知识点的关系
MATCH (n:KnowledgePoint {name: '二叉树'})-[r]->(m) RETURN n, r, m;

// 查看高RelationScore的关系
MATCH (n)-[r]->(m) WHERE r.relationScore > 8 RETURN n, r, m;
```

## 3. 执行流程

### 3.1 主脚本执行
使用main.py脚本执行完整的知识图谱构建流程。

**执行脚本**: `src/knowledge_graph/main.py`

**关键步骤**:
1. 配置参数
2. 顺序执行各个阶段的处理
3. 生成日志和报告

**示例命令**:
```bash
python -m src.knowledge_graph.main --config_file ./src/knowledge_graph/config.yaml
```

### 3.2 分阶段执行
可以分阶段执行各个模块，便于调试和优化。

**执行顺序**:
1. 数据预处理阶段
2. 知识点提取阶段  
3. 关系抽取阶段
4. RelationScore计算阶段
5. 知识图谱构建阶段

### 3.3 半自动化流程
结合自动处理和人工审核，提高知识图谱质量。

**推荐流程**:
1. 自动提取初步知识点和关系
2. 导出为CSV/JSON格式供专家审核
3. 导入审核后的数据
4. 继续自动化处理

## 4. 优化与扩展

### 4.1 数据质量优化
- 增加人工校验环节
- 使用反馈数据优化提取规则
- 定期更新和扩充知识点

### 4.2 性能优化
- 优化Neo4j查询
- 批量导入提高效率
- 缓存中间结果减少重复计算

### 4.3 功能扩展
- 集成RAG检索功能
- 开发图谱可视化界面
- 添加用户反馈机制

## 5. 实施建议

### 5.1 循序渐进
首次构建知识图谱建议采用以下渐进式方法：

1. **小规模测试**:
   - 选择"树"等单一子领域
   - 手动提取20-30个知识点
   - 完成基本图谱构建

2. **验证与优化**:
   - 验证RelationScore计算
   - 调整参数和权重
   - 优化算法和流程

3. **扩展规模**:
   - 扩展到完整数据结构领域
   - 逐步添加更多知识点和关系
   - 完善图谱结构

### 5.2 关键优化点
- **术语识别准确性**: 决定了知识点覆盖率
- **关系提取规则**: 影响图谱的连通性和准确性
- **RelationScore参数**: 决定路由决策的准确性

### 5.3 维护与更新
- 定期更新知识点（根据新版大纲）
- 添加新的真题数据
- 优化RelationScore计算方法 