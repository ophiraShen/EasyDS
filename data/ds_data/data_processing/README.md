# 知识点索引系统

这个系统用于快速查询知识点和相关题目，支持以下功能：
- 根据知识点ID快速获取知识点信息
- 根据知识点ID获取相关的所有题目
- 根据题目ID获取题目详情

## 系统结构

系统包含两个主要文件：
- `index_builder.py`: 用于构建和管理索引的核心类
- `demo_usage.py`: 演示如何使用索引系统的交互式脚本

## 使用方法

### 1. 构建索引

首次使用时，需要构建索引。可以通过以下命令运行：

```bash
cd autodl-tmp/EasyDS/data/ds_data/data_processing
python index_builder.py
```

这将读取所有章节、知识点和题目数据，构建索引并保存为`ds_indices.pkl`文件。

### 2. 使用索引

有两种方式使用索引：

#### 方式一：交互式界面

运行演示脚本：

```bash
python demo_usage.py
```

按照界面提示操作，可以：
- 通过知识点ID查询知识点详情
- 查询知识点对应的题目
- 通过题目ID查询题目详情

#### 方式二：在代码中使用

在您的Python代码中，可以这样使用索引系统：

```python
from index_builder import KnowledgeIndexSystem

# 从已保存的索引文件加载（推荐方式，速度快）
system = KnowledgeIndexSystem.load_indices('ds_indices.pkl')

# 或者重新构建索引
# system = KnowledgeIndexSystem()
# system.build_indices()

# 1. 查询知识点
knowledge_point = system.get_knowledge_point('kc0111')
print(f"知识点标题: {knowledge_point['title']}")

# 2. 获取知识点相关的题目
questions = system.get_questions_by_knowledge('kc0111')
print(f"该知识点下有 {len(questions)} 个题目")

# 3. 获取指定题目
question = system.get_question('q011002')
print(f"题目内容: {question['content']}")
```

## 索引结构

系统创建了以下索引：

1. `knowledge_index`: 知识点索引，格式为 `{knowledge_id: knowledge_point_object}`
2. `knowledge_question_index`: 知识点对应题目索引，格式为 `{knowledge_id: [question_ids]}`
3. `question_index`: 题目索引，格式为 `{question_id: question_object}`
4. `chapter_index`: 章节索引，格式为 `{chapter_id: chapter_object}`

这些索引一次构建，多次使用，提高了查询效率。

## 数据目录结构

系统假设数据目录结构如下：

```
data/ds_data/
├── chapters.json
├── knowledgepoints/
│   ├── all_knowledgepoints.json  (可选的全量文件)
│   ├── chapter_1.json
│   ├── chapter_2.json
│   └── ...
├── questions/
│   ├── chapter_1.json
│   ├── chapter_2.json
│   └── ...
```

## 注意事项

1. 第一次运行会较慢，因为需要构建索引。之后通过加载已保存的索引文件，启动速度会显著提升。
2. 如果原始数据文件发生变化，需要重新构建索引以保持数据一致性。 