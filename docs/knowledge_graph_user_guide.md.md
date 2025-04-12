# 知识图谱构建指南

本文档详细介绍了使用EasyDS框架构建知识图谱的过程、方法和相关配置。

## 1. 概述

知识图谱构建是将非结构化的文本数据转换为结构化的知识网络的过程。在EasyDS框架中，知识图谱构建分为以下几个阶段：

1. **提取阶段**：从PDF文档中提取文本内容，并构建领域词典
2. **处理阶段**：清洗和标准化文本，提取知识点
3. **关系阶段**：识别知识点之间的关系，处理考试题目信息
4. **评分阶段**：计算和评估知识点之间关系的强度和可信度
5. **构建阶段**：将处理后的数据导入图数据库，构建最终的知识图谱

## 2. 环境准备

### 2.1 基础环境

确保已安装以下依赖：

```bash
pip install pdfplumber pytesseract jieba textrank4zh numpy pandas scikit-learn sentence-transformers neo4j pyyaml tqdm
```

### 2.2 数据库设置

本框架使用Neo4j作为图数据库。在开始前请确保：

1. 已安装Neo4j数据库服务（可以使用Docker容器方式）
2. 已创建专用数据库账户
3. 在配置文件中正确设置数据库连接信息

在Autodl环境中，可以使用以下命令启动Neo4j容器：

```bash
docker run \
    --name neo4j \
    -p 7474:7474 -p 7687:7687 \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/password \
    neo4j:latest
```

### 2.3 文件结构准备

确保以下目录已创建：

```
/root/autodl-tmp/EasyDS/
├── config/
│   └── kg_config.yaml       # 知识图谱配置文件
├── data/
│   ├── pdfs/                # 存放原始PDF文档
│   ├── questions/           # 存放试题文档
│   ├── kg_temp/             # 临时数据存放目录
│   ├── kg_cache/            # 缓存数据存放目录
│   ├── kg_output/           # 输出数据存放目录
│   └── resources/           # 资源文件目录
│       ├── stopwords.txt    # 停用词表
│       ├── domain_dict.txt  # 领域词典
│       └── relation_prompt.txt # 关系提取提示模板
└── src/
    └── knowledge_graph/     # 知识图谱相关代码
        ├── __init__.py
        ├── main.py          # 主执行脚本
        ├── extractors/      # 提取器模块
        ├── processors/      # 处理器模块
        ├── calculators/     # 计算器模块
        └── builders/        # 构建器模块
```

## 3. 配置文件

知识图谱构建的配置文件位于`/root/autodl-tmp/EasyDS/config/kg_config.yaml`，包含以下主要部分：

- **基本配置**：项目名称、版本、日志级别等
- **资源文件配置**：各类资源文件路径
- **文本提取配置**：PDF提取和术语提取参数
- **文本处理配置**：文本清洗和知识点提取参数
- **关系提取配置**：关系类型和大语言模型参数
- **分数计算配置**：关系评分方法和权重设置
- **数据库配置**：Neo4j数据库连接和索引设置

详细配置项说明请参考注释和文档。

## 4. 执行流程

### 4.1 阶段划分

知识图谱构建分为多个阶段，可以单独执行或按顺序依次执行：

1. **extract**: 提取文本内容与术语
2. **process**: 处理文本并提取知识点
3. **relation**: 提取知识点之间的关系
4. **score**: 计算关系评分
5. **build**: 构建图数据库
6. **all**: 执行所有阶段

### 4.2 命令行执行

使用以下命令执行知识图谱构建：

```bash
# 执行所有阶段
python -m src.knowledge_graph.main --config config/kg_config.yaml --phase all

# 仅执行某一阶段
python -m src.knowledge_graph.main --config config/kg_config.yaml --phase extract

# 启用调试模式
python -m src.knowledge_graph.main --config config/kg_config.yaml --phase process --debug
```

### 4.3 执行参数说明

- `--config`: 配置文件路径
- `--phase`: 执行阶段，可选值为extract, process, relation, score, build, all
- `--debug`: 启用调试模式，输出更多详细信息

## 5. 具体阶段实现

### 5.1 提取阶段 (Extract)

该阶段完成两项主要任务：

1. **PDF文本提取**：从PDF文档中提取文本内容，可选择是否使用OCR技术
2. **术语提取**：从文本中识别领域专业术语，构建领域词典

主要流程：
- 读取PDF目录下所有文件
- 使用PDFExtractor提取文本内容
- 使用TermExtractor识别专业术语
- 保存提取结果到临时目录

### 5.2 处理阶段 (Process)

该阶段对提取的文本进行处理，提取知识点：

1. **文本处理**：清洗、标准化文本，去除不必要的内容
2. **知识点提取**：将长文本分割成具有独立语义的知识点片段

主要流程：
- 读取提取阶段的输出
- 使用TextProcessor清洗和规范化文本
- 使用KnowledgeProcessor提取和分割知识点
- 保存处理结果到临时目录

### 5.3 关系阶段 (Relation)

该阶段识别知识点之间的关系：

1. **关系提取**：使用规则或大语言模型识别知识点间的关系
2. **题目处理**：分析考试题目，提取题目中的知识点和关系

主要流程：
- 读取处理阶段的输出和题目文件
- 使用RelationExtractor识别知识点间的关系
- 使用QuestionProcessor处理考试题目
- 保存关系数据到临时目录

### 5.4 评分阶段 (Score)

该阶段计算关系的强度和可信度：

1. **模块距离计算**：基于知识点在文档结构中的距离计算关系强度
2. **文档权重计算**：考虑文档的重要性和质量对关系的影响
3. **语义相似度计算**：使用语言模型计算知识点间的语义相似度
4. **最终评分**：综合以上因素计算最终关系评分

主要流程：
- 读取关系阶段的输出
- 使用ModuleDistanceCalculator计算模块距离分数
- 使用DocumentWeightCalculator计算文档权重分数
- 使用SemanticSimilarityCalculator计算语义相似度分数
- 使用RelationScoreCalculator计算最终关系评分
- 保存评分结果到临时目录

### 5.5 构建阶段 (Build)

该阶段将处理后的数据导入Neo4j数据库，构建知识图谱：

1. **数据库连接**：连接Neo4j数据库
2. **数据库清理**：清除已有数据
3. **约束和索引创建**：创建必要的约束和索引
4. **数据导入**：导入知识点和关系数据
5. **数据验证**：验证导入的数据完整性和一致性

主要流程：
- 读取评分阶段的输出
- 使用KnowledgeGraphBuilder连接数据库
- 清除已有数据，创建约束和索引
- 导入知识点和关系数据
- 验证导入的数据
- 生成构建报告

## 6. 可视化与应用

### 6.1 Neo4j Browser

构建完成后，可以通过Neo4j Browser进行可视化和查询：

1. 访问`http://<服务器IP>:7474`
2. 使用配置的用户名和密码登录
3. 使用Cypher查询语言进行数据探索

### 6.2 常用查询示例

```cypher
// 查询所有知识点
MATCH (k:KnowledgePoint) RETURN k LIMIT 100;

// 查询特定知识点及其关系
MATCH (k:KnowledgePoint {title: '知识点名称'})-[r]-(related) 
RETURN k, r, related;

// 查询两个知识点之间的路径
MATCH path = shortestPath(
  (k1:KnowledgePoint {title: '起始知识点'})-[*..5]-(k2:KnowledgePoint {title: '目标知识点'})
)
RETURN path;
```

### 6.3 导出数据

可以将构建的知识图谱导出为其他格式：

```bash
# 导出为图形格式(GML)
python -m src.knowledge_graph.export --config config/kg_config.yaml --format gml

# 导出为JSON格式
python -m src.knowledge_graph.export --config config/kg_config.yaml --format json
```

## 7. 故障排除

### 7.1 常见问题

1. **数据库连接失败**：检查Neo4j服务是否正常运行，以及配置文件中的连接信息是否正确
2. **内存不足**：大规模数据处理可能需要增加内存限制，可以调整JVM和Python的内存设置
3. **处理时间过长**：可以尝试调整批处理大小，或使用增量构建方法

### 7.2 日志分析

日志文件位于程序执行目录，根据日志级别记录了不同详细程度的信息。可以通过以下命令查看日志：

```bash
tail -f knowledge_graph_<日期>.log
```

## 8. 后续开发

### 8.1 扩展方向

1. **多语言支持**：增加对英语等其他语言的支持
2. **增量更新**：实现知识图谱的增量构建和更新
3. **高级推理**：基于知识图谱实现复杂的推理和问答功能
4. **用户界面**：开发友好的图形用户界面，方便非技术用户使用

### 8.2 性能优化

1. **并行处理**：引入多进程/多线程处理，提高构建速度
2. **分布式计算**：对于大规模数据，引入分布式计算框架
3. **索引优化**：优化Neo4j的索引策略，提高查询性能 