# 基于章节的结构化问题数据库设计

## 1. 设计概述

EasyDS 系统采用基于章节的结构化问题数据库，以支持费曼学习法的教学流程。该数据库组织考研数据结构知识点和问题，符合学习曲线，支持智能体系统进行精准的问题追问和扩展。

### 1.1 设计原则

- **符合学习曲线**：按照教材章节组织知识点和问题，确保学习过程符合难度递进
- **知识点关联**：建立知识点之间的关联关系，支持相关知识拓展
- **问题扩展**：每个问题关联多个可能的扩展问题，便于学生智能体进行深度追问
- **易于维护**：采用结构化设计，便于内容更新和扩展

### 1.2 数据库特点

- 以章节为主要组织结构
- 问题与知识点多对多关联
- 支持知识点间的前置、相关和扩展关系
- 可配置的问题难度级别
- 详细的参考答案和解析

## 2. 数据模型

### 2.1 实体关系图

```
+----------+      +------------+      +---------+
| 章节     |----->| 知识点     |<-----| 问题    |
+----------+      +------------+      +---------+
     |                  ^                  |
     |                  |                  |
     v                  |                  v
+----------+      +------------+      +---------+
| 子章节   |----->| 关联知识点 |<-----| 相关问题 |
+----------+      +------------+      +---------+
```

### 2.2 数据结构

#### 章节 (Chapter)

```json
{
  "id": "string",            // 章节唯一标识符
  "title": "string",         // 章节标题
  "parent_id": "string",     // 父章节ID（可选）
  "order": "integer",        // 排序顺序
  "description": "string",   // 章节描述
  "knowledge_points": [      // 包含的知识点ID列表
    "knowledge_point_id"
  ],
  "sub_chapters": [          // 子章节ID列表
    "chapter_id"
  ]
}
```

#### 知识点 (KnowledgePoint)

```json
{
  "id": "string",            // 知识点唯一标识符
  "title": "string",         // 知识点标题
  "chapter_id": "string",    // 所属章节ID
  "description": "string",   // 知识点详细描述
  "related_points": [        // 关联知识点
    {
      "id": "string",        // 关联知识点ID
      "relation_type": "string" // 关系类型: "prerequisite", "related", "extension"
    }
  ],
  "questions": [             // 相关问题ID列表
    "question_id"
  ]
}
```

#### 问题 (Question)

```json
{
  "id": "string",            // 问题唯一标识符
  "title": "string",         // 问题标题
  "content": "string",       // 问题内容
  "difficulty": "integer",   // 难度等级 (1-5)
  "type": "string",          // 问题类型 ("concept", "calculation", "application")
  "knowledge_points": [      // 相关知识点ID列表
    "knowledge_point_id"
  ],
  "related_questions": [     // 相关问题（用于扩展）
    {
      "id": "string",        // 相关问题ID
      "relation_type": "string" // 关系类型: "extension", "application", "contrast"
    }
  ],
  "reference_answer": {      // 参考答案
    "content": "string",     // 答案内容
    "key_points": [          // 关键点列表
      "string"
    ],
    "explanation": "string"  // 详细解释
  }
}
```

### 2.3 关系类型

#### 知识点关系

- **前置知识 (prerequisite)**: A是B的前置知识，学习B前应先掌握A
- **相关知识 (related)**: A与B有关联但无明确依赖关系
- **扩展知识 (extension)**: A是B的扩展或深入内容

#### 问题关系

- **扩展问题 (extension)**: 针对同一知识点的深入探讨
- **应用问题 (application)**: 知识点的实际应用场景
- **对比问题 (contrast)**: 涉及相似但有区别的概念

## 3. 数据库实现

### 3.1 存储选择

考虑到数据结构的复杂性和灵活性需求，推荐使用以下存储方案：

- **MongoDB**: 作为主要存储，适合存储结构灵活的文档数据
- **备选方案**: SQLite (适合轻量级部署)

### 3.2 文件组织

```
data/
└── questions/
    ├── chapters.json         # 章节数据
    ├── knowledge_points.json # 知识点数据
    ├── questions.json        # 问题数据
    └── chapter1/             # 按章节组织的问题详情文件
        ├── question_1_1.md   # 问题1-1详情
        ├── question_1_2.md   # 问题1-2详情
        └── ...
```

### 3.3 索引设计

为提高查询效率，需要在以下字段上建立索引：

- 章节ID
- 知识点ID
- 问题ID
- 知识点与章节的关联
- 问题与知识点的关联

## 4. 接口设计

### 4.1 查询接口

```python
# 获取章节列表
def get_chapters(parent_id=None):
    # 返回章节列表，可选按父章节筛选
    pass

# 获取知识点列表
def get_knowledge_points(chapter_id=None):
    # 返回知识点列表，可选按章节筛选
    pass

# 获取问题列表
def get_questions(knowledge_point_id=None, difficulty=None, type=None):
    # 返回问题列表，可按知识点、难度、类型筛选
    pass

# 获取关联知识点
def get_related_knowledge_points(knowledge_point_id, relation_type=None):
    # 返回与指定知识点关联的其他知识点
    pass

# 获取相关问题
def get_related_questions(question_id, relation_type=None):
    # 返回与指定问题相关的其他问题
    pass
```

### 4.2 智能体接口

```python
# 获取问题详情（用于初始展示给用户）
def get_question_details(question_id):
    # 返回问题详情，包括标题、内容、难度等
    pass

# 获取问题上下文（用于路由智能体决策）
def get_question_context(question_id):
    # 返回问题的完整上下文，包括所有关联知识点和关系
    pass

# 获取扩展问题（用于学生智能体追问）
def get_extension_questions(question_id, answered_questions=None):
    # 返回可用于追问的扩展问题，排除已回答过的问题
    pass

# 获取参考答案（用于路由智能体评估用户回答）
def get_reference_answer(question_id):
    # 返回问题的参考答案和关键点
    pass
```

## 5. 数据填充

### 5.1 数据来源

- 考研数据结构教材
- 历年考研真题
- 专家编写的概念解析
- 典型算法题目和解析

### 5.2 数据处理流程

1. 教材分析与章节提取
2. 知识点归纳与关联构建
3. 问题编写与分级
4. 答案编写与审核
5. 数据导入与验证

### 5.3 质量控制

- 专家审核知识点准确性
- 检查知识点关联合理性
- 验证问题难度分级
- 评估答案质量和完整性

## 6. 与智能体系统集成

### 6.1 路由智能体集成

- 提供问题上下文和参考答案
- 支持用户回答评估
- 提供知识点关联信息

### 6.2 学生智能体集成

- 提供相关扩展问题
- 支持追问策略生成
- 记录已追问内容

### 6.3 教师智能体集成

- 提供完整知识点解析
- 支持答案纠错和指导
- 提供知识总结材料

## 7. 扩展与维护

### 7.1 数据库扩展

- 新章节和知识点添加
- 问题库定期更新
- 用户反馈整合

### 7.2 数据库维护

- 定期检查数据一致性
- 更新过时内容
- 优化查询性能
- 数据备份策略

## 8. 管理工具

### 8.1 后台管理功能

- 章节管理（增删改查）
- 知识点管理（增删改查）
- 问题管理（增删改查）
- 关系管理（建立和修改关联）

### 8.2 数据导入导出

- JSON格式导入导出
- 批量更新工具
- 数据迁移支持 