# 数据处理系统设计文档

## 1. 数据处理概述

EasyDS系统的数据处理模块主要负责两大类数据的处理：
1. **GRPO训练数据**：用于教师智能体的计算推理能力优化
2. **知识图谱数据**：用于构建RelationScore知识图谱

本文档详细描述了数据获取、预处理、转换和存储的完整流程，确保数据质量满足系统需求。

## 2. GRPO训练数据处理

### 2.1 数据需求

GRPO (Guided Reinforcement from Preference Optimization) 训练的目标是增强教师智能体在数据结构计算推理方面的能力，特别针对考研数据结构中的数值计算问题。

**数据特征需求**：
- 计算类题目（如时间复杂度、空间分析、性能评估等）
- 包含完整的推理步骤
- 具有明确的正确答案及评分标准

### 2.2 数据收集策略

#### 2.2.1 原始数据来源

1. **考研真题**：
   - 收集近10年全国统考数据结构真题
   - 筛选计算类题目（约100道）
   - 覆盖所有主要知识点和典型计算场景

2. **数据增强处理**：
   通过以下技术将原始100道题目扩展至300道高质量样本：
   - **变量替换**：修改问题中的数值条件
   - **问题重述**：保持核心计算不变，改变问题描述方式
   - **条件变更**：调整问题约束条件，形成变种问题

#### 2.2.2 数据标注流程

每道题目需标注以下内容：
1. **题目文本**：原始题目描述
2. **标准答案**：精确的计算结果
3. **解题步骤**：完整规范的推理过程
4. **双指标评分**：
   - 答案正确性（0-7分）：根据最终结果是否正确
   - 步骤合理性（0-3分）：由专业评审根据解题步骤评定

```python
# 数据标注示例
{
    "id": "DS2023-45",
    "question": "一棵完全二叉树有768个结点，求叶子节点的数量。",
    "standard_answer": "384",
    "solution_steps": [
        "完全二叉树的节点总数为n=768",
        "对于完全二叉树，若n为偶数，则叶子节点数为n/2",
        "因此，叶子节点数 = 768/2 = 384"
    ],
    "correctness_score": 7,  # 答案正确得7分
    "reasoning_score": 3,    # 推理步骤完全合理得3分
    "total_score": 10
}
```

### 2.3 数据预处理

#### 2.3.1 文本清洗

1. **格式统一化**：
   - 标准化数学符号和公式
   - 统一术语表达（如"时间复杂度"vs"时间效率"）
   - 移除无关文本和冗余信息

2. **数据结构化**：
   - 解析题目为结构化格式
   - 将解题步骤分解为逻辑连贯的步骤序列

#### 2.3.2 质量控制

1. **专家审核**：
   - 每道题目由至少两名数据结构专家审核
   - 确认答案和推理步骤的准确性
   - 验证评分的合理性

2. **异常检测**：
   - 识别并修正不一致数据
   - 确保评分标准的统一应用
   - 剔除低质量或有争议的样本

### 2.4 数据转换与划分

#### 2.4.1 训练数据格式

**GRPO训练数据格式**：
```json
{
    "conversations": [
        {
            "role": "user",
            "content": "请解答这道数据结构题目：{question}"
        },
        {
            "role": "assistant",
            "content": "{solution}"
        }
    ],
    "reward_score": {
        "correctness": 7,
        "reasoning": 3
    }
}
```

#### 2.4.2 数据集划分

- **训练集**：210道题目（70%）
- **验证集**：45道题目（15%）
- **测试集**：45道题目（15%）

划分原则：
1. 确保各集合中的题目难度分布相似
2. 各主要知识点在所有集合中均有覆盖
3. 随机分配同类型的增强变种题目到不同集合

### 2.5 数据扩充与优化

#### 2.5.1 难度均衡

**难度分布控制**：
- 简单题目（30%）：基本计算、单一知识点应用
- 中等题目（50%）：多步骤计算、多知识点关联
- 困难题目（20%）：复杂计算、综合应用、边界情况

#### 2.5.2 错误示例生成

为增强模型的纠错能力，创建带有典型错误的解答示例：
1. **计算错误**：常见的数值计算错误
2. **概念误用**：错误应用数据结构概念
3. **推理缺陷**：逻辑跳跃或步骤不完整
4. **结论错误**：推理正确但结论错误

这些错误示例将获得较低的评分，用于训练模型识别并避免常见错误。

### 2.6 实现流程

```python
# generate_grpo_data.py 核心流程
def process_raw_data(raw_data_path, output_path):
    """处理原始数据生成GRPO训练数据"""
    # 1. 加载原始题目数据
    raw_problems = load_json(raw_data_path)
    
    # 2. 数据增强
    enhanced_problems = enhance_problems(raw_problems)
    
    # 3. 结构化处理
    structured_data = []
    for problem in enhanced_problems:
        # 处理问题文本
        cleaned_text = clean_text(problem["question"])
        
        # 生成标准答案示例
        standard_solution = generate_solution(problem)
        
        # 生成错误示例(可选)
        incorrect_solutions = generate_incorrect_solutions(problem)
        
        # 创建训练样本
        sample = create_training_sample(cleaned_text, standard_solution)
        structured_data.append(sample)
        
        # 添加错误示例样本
        for solution in incorrect_solutions:
            incorrect_sample = create_training_sample(cleaned_text, solution)
            structured_data.append(incorrect_sample)
    
    # 4. 数据划分
    train, val, test = split_dataset(structured_data)
    
    # 5. 保存处理后的数据
    save_jsonl(train, output_path + "/train_data.jsonl")
    save_jsonl(val, output_path + "/eval_data.jsonl")
    save_jsonl(test, output_path + "/test_data.jsonl")
```

## 3. 知识图谱数据处理

### 3.1 数据需求

RelationScore知识图谱需要全面覆盖考研数据结构领域知识，并量化知识点之间的相关性。

**数据特征需求**：
- 完整的知识点体系
- 准确的知识点关系
- 量化的关联分数

### 3.2 数据收集策略

#### 3.2.1 知识点提取

1. **文本来源**：
   - 考研大纲和指定教材
   - 权威参考书籍
   - 往年真题和解析

2. **提取方法**：
   - 人工提取关键知识点
   - NLP辅助识别专业术语和概念
   - 概念层级关系分析

#### 3.2.2 关系标注

针对每对相关知识点，标注以下信息：
1. **关系类型**：包含、前置、相似、对比或应用
2. **关联原因**：描述两个知识点关联的具体原因
3. **RelationScore**：关联强度评分（0-10）

### 3.3 数据预处理

#### 3.3.1 知识点规范化

1. **概念统一**：
   - 消除同义概念（如"链表"和"链式存储结构"）
   - 标准化术语表达
   - 明确概念边界

2. **定义完善**：
   - 补充完整定义
   - 添加关键属性
   - 关联典型实例

#### 3.3.2 关系验证

1. **一致性检查**：
   - 检测并解决循环依赖
   - 验证关系的传递性
   - 确保关系网络的完整性

2. **专家审核**：
   - 由数据结构专家审核关系的正确性
   - 调整不合理的RelationScore
   - 补充遗漏的重要关系

### 3.4 RelationScore计算

RelationScore是一个0-10的浮点数，用于量化两个知识点之间关系的强度。

#### 3.4.1 计算因素

RelationScore基于以下因素计算：
1. **概念近似度**（w1=0.25）：基于文本嵌入的语义相似度
2. **共现频率**（w2=0.2）：在教材和试题中共同出现的频率
3. **学习路径距离**（w3=0.15）：在推荐学习路径中的距离倒数
4. **错误关联度**（w4=0.15）：错误理解时的相互关联频率
5. **专家评分**（w5=0.25）：领域专家对关联性的评分

#### 3.4.2 计算实现

```python
def calculate_relation_score(node1, node2, relation_type):
    """计算两个知识点之间的RelationScore"""
    # 1. 计算概念近似度
    embeddings = get_embeddings([node1["definition"], node2["definition"]])
    concept_similarity = cosine_similarity(embeddings[0], embeddings[1]) * 10
    
    # 2. 计算共现频率
    cooccurrence = get_cooccurrence_frequency(node1["name"], node2["name"])
    norm_cooccurrence = normalize_frequency(cooccurrence) * 10
    
    # 3. 计算学习路径距离
    path_distance = get_path_distance(node1["name"], node2["name"])
    if path_distance > 0:
        norm_distance = min(10, 10 / path_distance)
    else:
        norm_distance = 0
    
    # 4. 计算错误关联度
    misconception_corr = get_misconception_correlation(node1["name"], node2["name"])
    
    # 5. 获取专家评分
    expert_rating = get_expert_rating(node1["name"], node2["name"], relation_type)
    
    # 6. 计算加权得分
    weights = [0.25, 0.2, 0.15, 0.15, 0.25]
    factors = [concept_similarity, norm_cooccurrence, norm_distance, 
              misconception_corr, expert_rating]
    
    relation_score = sum(w * f for w, f in zip(weights, factors))
    
    # 7. 确保分数在0-10范围内
    return max(0, min(10, relation_score))
```

### 3.5 知识图谱构建

#### 3.5.1 数据结构

**节点数据格式**：
```json
{
    "id": "KP001",
    "name": "平衡二叉树",
    "definition": "平衡二叉树是一种二叉排序树，其中每个节点的左子树和右子树的高度差不超过1。",
    "difficulty": 7,
    "importance": 9,
    "category": "树形结构",
    "properties": ["自平衡", "查找效率高"]
}
```

**关系数据格式**：
```json
{
    "source": "KP001",
    "target": "KP042",
    "type": "PREREQUISITE_FOR",
    "relationScore": 8.5,
    "description": "平衡二叉树是红黑树的理论基础，需要先理解平衡二叉树才能更好地学习红黑树。"
}
```

#### 3.5.2 数据导入流程

```python
def build_knowledge_graph(nodes_path, relations_path, neo4j_config):
    """构建RelationScore知识图谱"""
    # 1. 连接Neo4j数据库
    graph = Graph(**neo4j_config)
    
    # 2. 导入节点
    nodes = load_json(nodes_path)
    for node in nodes:
        if node["category"] == "KnowledgePoint":
            # 创建知识点节点
            graph.run("""
                CREATE (k:KnowledgePoint {
                    id: $id, 
                    name: $name, 
                    definition: $definition,
                    difficulty: $difficulty,
                    importance: $importance
                })
            """, **node)
        elif node["category"] == "Problem":
            # 创建题目节点
            graph.run("""
                CREATE (p:Problem {
                    id: $id, 
                    content: $content, 
                    type: $type,
                    year: $year,
                    chapter: $chapter
                })
            """, **node)
        # 处理其他类型节点...
    
    # 3. 导入关系
    relations = load_json(relations_path)
    for relation in relations:
        # 创建带有RelationScore的关系
        graph.run("""
            MATCH (a {id: $source}), (b {id: $target})
            CREATE (a)-[r:%s {relationScore: $relationScore, description: $description}]->(b)
        """ % relation["type"], **relation)
    
    # 4. 创建索引
    graph.run("CREATE INDEX FOR (n:KnowledgePoint) ON (n.name)")
    graph.run("CREATE INDEX FOR (n:Problem) ON (n.id)")
    # 创建其他索引...
```

## 4. 评估与优化

### 4.1 数据质量评估

#### 4.1.1 GRPO训练数据评估

1. **覆盖度评估**：
   - 知识点覆盖率：确保所有重要知识点均有相关题目
   - 难度分布：验证简单/中等/困难题目比例符合设计要求
   - 题型多样性：检查不同类型计算题的分布情况

2. **质量评估**：
   - 人工抽样审核：随机抽取样本进行人工检查
   - 一致性检验：确保相似题目的评分标准一致
   - 准确性验证：确认答案和解题步骤的准确性

#### 4.1.2 知识图谱数据评估

1. **完整性评估**：
   - 知识点覆盖率：与考研大纲比对，确保完整覆盖
   - 关系完整性：检查预期关系是否全部建立
   - 属性完整性：确保节点关键属性齐全

2. **准确性评估**：
   - 关系正确率：抽样验证关系的正确性
   - RelationScore合理性：检查分数分布是否符合预期
   - 专家验证：由领域专家评估图谱质量

### 4.2 持续优化策略

#### 4.2.1 GRPO数据优化

1. **数据扩充**：
   - 针对薄弱知识点增加更多题目
   - 添加更多边界情况和特殊情况测试
   - 根据模型表现增加难点题目

2. **评分细化**：
   - 优化双指标评分体系
   - 细化步骤合理性评分标准
   - 增加中间步骤的评分依据

#### 4.2.2 知识图谱优化

1. **数据丰富**：
   - 添加更多专业属性和细节
   - 扩充题目节点和应用关系
   - 增加常见误解关联

2. **RelationScore调优**：
   - 基于用户反馈调整权重参数
   - 优化计算公式
   - 定期更新专家评分

## 5. 实施计划

### 5.1 阶段一：数据准备（3周）

1. **第1周**：
   - 收集考研真题和教材资料
   - 设计数据结构和存储格式
   - 搭建预处理环境

2. **第2-3周**：
   - 提取知识点和题目
   - 初步标注关系和RelationScore
   - 生成GRPO基础训练数据

### 5.2 阶段二：数据处理（4周）

1. **第4-5周**：
   - 实现数据清洗和预处理
   - 开发GRPO数据增强模块
   - 实现RelationScore计算

2. **第6-7周**：
   - 完成知识图谱数据导入
   - 优化GRPO训练数据格式
   - 初步评估数据质量

### 5.3 阶段三：评估与优化（2周）

1. **第8周**：
   - 全面评估数据质量
   - 识别问题和优化机会

2. **第9周**：
   - 实施数据优化措施
   - 准备最终训练与部署数据 