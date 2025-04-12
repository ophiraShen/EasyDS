# 智能体系统设计文档

## 1. 系统概述

EasyDS 智能体系统采用费曼学习法设计三层智能体模型（路由、学生、教师），突破传统"问答式"AI辅导教学范式。系统通过"用户主动讲解题目 → 路由agent评估回答 → 动态选择学生agent（深度追问）或教师agent（纠错引导）"的流程，形成"讲解-反馈-修正-强化"的教学闭环。

## 2. 核心智能体

### 2.1 路由智能体（Router Agent）

**功能定位**：评估用户讲解并决策下一步教学路径

**核心能力**：
1. **回答评估**：分析用户讲解的正确性、完整性和清晰度
2. **知识关联**：通过RAG从RelationScore知识图谱获取相关知识点信息
3. **决策路由**：根据评估结果决定启用学生智能体（深度追问）或教师智能体（纠错引导）
4. **状态管理**：维护教学会话状态，追踪学习进度

**路由决策Prompt设计**：
```
你是一个专业的数据结构教学路由决策系统。请基于以下信息进行分析和决策：

用户讲解：{user_explanation}
相关知识点：{related_knowledge}
历史对话：{conversation_history}

评估维度：
1. 正确性（0-10分）：知识理解是否准确无误
2. 完整性（0-10分）：要点覆盖是否全面
3. 清晰度（0-10分）：表述是否清晰易懂

根据评估结果，决定下一步操作：
- 若总分≥24分：选择学生智能体，进行深度追问，引导用户更深入思考
- 若总分<24分：选择教师智能体，进行纠错引导，帮助用户改进理解

请输出：
- 各维度评分及理由
- 决策结果（学生智能体/教师智能体）
- 给下一个智能体的简要指导
```

**技术实现**：
- 基于LangGraph的状态流转管理
- RAG技术与知识图谱集成
- 评分模型与决策阈值调优

### 2.2 学生智能体（Student Agent）

**功能定位**：模拟学习者提出深度追问

**核心能力**：
1. **深度提问**：针对用户讲解中的关键点提出深入问题
2. **困惑模拟**：模拟学习过程中可能出现的困惑点
3. **引导阐述**：引导用户进行更清晰的知识阐述
4. **思维启发**：通过问题启发用户思考知识间的联系

**学生智能体Prompt设计**：
```
你是一位正在学习数据结构的学生。你刚刚听取了用户对{topic}的讲解：

用户讲解：{user_explanation}

路由评估：{router_assessment}

请你像一个真实的学生一样，提出1-2个有深度的问题。这些问题应该：
1. 针对用户讲解中的关键点或隐含假设
2. 探索知识点之间的联系或应用场景
3. 揭示可能被忽略的重要概念
4. 促使用户更深入地思考和解释

注意：问题要有针对性和思考深度，不要问过于基础或无关的问题。表现得像一个真实但较为聪明的学生。
```

**技术实现**：
- 基于上下文的问题生成
- 关键知识点识别
- 提问策略优化

### 2.3 教师智能体（Teacher Agent）

**功能定位**：提供专业纠错引导和知识强化

**核心能力**：
1. **错误纠正**：识别并纠正用户讲解中的概念性错误
2. **知识补充**：补充遗漏的重要知识点
3. **引导改进**：提供具体的改进建议
4. **计算推理**：针对数值计算问题提供准确解析

**教师智能体Prompt设计**：
```
你是一位专业的数据结构教师，擅长费曼学习法教学。请针对用户的讲解提供专业指导：

用户讲解：{user_explanation}
主题：{topic}
路由评估：{router_assessment}

请提供以下指导：
1. 概念纠正：指出并纠正讲解中的概念错误（如有）
2. 知识补充：补充遗漏的关键知识点
3. 推理分析：针对计算或算法分析提供规范步骤
4. 总结提炼：用简洁清晰的语言总结正确的理解

注意：回答应专业、准确，同时保持鼓励性，帮助用户形成正确的知识体系。对于计算问题，请展示完整的解题步骤。
```

**优化方案**：
- 基座模型：DeepSeek-R1-Distill-Qwen-14B
- 微调方法：GRPO（Guided Reinforcement from Preference Optimization）
- 双指标评估体系：
  * 答案正确性（7分）：数值精确匹配
  * 步骤合理性（3分）：解题过程评估

## 3. 智能体协同工作流

### 3.1 状态流转图

```
[用户] --> [输入讲解] --> [路由智能体] --评分≥24--> [学生智能体] --> [用户回应] --> [路由智能体]
                                      \
                                       --评分<24--> [教师智能体] --> [用户回应] --> [路由智能体]
```

### 3.2 会话流程

1. **初始化阶段**
   - 获取用户学习目标和背景
   - 加载相关知识图谱信息
   - 初始化会话状态

2. **讲解阶段**
   - 用户主动讲解数据结构知识点或解题思路
   - 系统记录讲解内容

3. **评估与路由阶段**
   - 路由智能体评估讲解质量
   - 决策启动学生智能体或教师智能体

4. **反馈阶段**
   - 学生智能体：提出深度追问，促进思考
   - 教师智能体：提供纠错引导，强化正确概念

5. **修正与强化阶段**
   - 用户回应智能体反馈
   - 路由智能体重新评估，决定下一步

6. **总结阶段**
   - 教师智能体总结学习要点
   - 强化关键知识点
   - 生成学习报告

### 3.3 状态管理

**会话状态结构**：
```python
{
    "session_id": "unique_id",
    "user_info": {
        "background": "...",
        "learning_goals": "..."
    },
    "current_topic": "topic_name",
    "knowledge_graph": {
        "related_nodes": [...],
        "relation_scores": {...}
    },
    "conversation_history": [...],
    "assessment_history": [...],
    "learning_progress": {
        "mastered_points": [...],
        "weak_points": [...],
        "recommended_path": [...]
    },
    "current_state": "routing/student/teacher",
    "feedback_counter": 0
}
```

## 4. 技术实现

### 4.1 技术栈

- LangGraph：智能体工作流管理
- LangChain：智能体框架与组件
- DeepSeek-R1-Distill-Qwen-14B：教师智能体基座模型
- Neo4j：RelationScore知识图谱存储
- FastAPI：后端服务
- MongoDB：会话状态管理

### 4.2 系统架构

```
[前端UI] <--> [FastAPI后端]
                |
    +-----------+------------+
    |           |            |
[智能体管理器] [知识图谱API] [会话管理]
    |           |
    |           V
[LangGraph流] [Neo4j数据库]
    |
+---+---+-------+
|       |       |
[路由] [学生] [教师]
        |       |
        +-------+
            |
        [模型服务]
            |
    [DeepSeek-R1-Distill-Qwen-14B]
```

### 4.3 代码结构

```python
# agent_workflow.py - 智能体工作流定义
from langchain.agents import Tool
from langgraph.graph import StateGraph

# 定义状态类型
class AgentState(TypedDict):
    user_input: str
    conversation_history: list
    current_assessment: dict
    next_agent: str
    output: str

# 构建工作流图
def create_agent_workflow():
    # 创建工作流图
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("router", router_agent)
    workflow.add_node("student", student_agent)
    workflow.add_node("teacher", teacher_agent)
    
    # 定义状态转移
    workflow.add_edge("router", condition_function)
    workflow.add_conditional_edges(
        "router",
        lambda state: state["next_agent"],
        {
            "student": "student",
            "teacher": "teacher"
        }
    )
    workflow.add_edge("student", "router")
    workflow.add_edge("teacher", "router")
    
    # 设置入口节点
    workflow.set_entry_point("router")
    
    return workflow.compile()
```

## 5. 评估与优化

### 5.1 评估指标

1. **路由准确性**：路由决策与专家判断的一致率
2. **提问质量**：学生智能体提问的深度与相关性
3. **教学效果**：用户知识点掌握程度提升
4. **用户体验**：交互满意度与学习投入度

### 5.2 优化策略

1. **Prompt优化**：通过A/B测试迭代改进各智能体提示词
2. **阈值调整**：优化路由决策阈值以提高准确性
3. **知识图谱强化**：丰富RelationScore知识图谱的节点与关系
4. **教师智能体GRPO微调**：针对计算推理能力持续优化

## 6. 实施计划

1. **阶段一**：基础框架搭建（2周）
   - 实现基本智能体结构
   - 设计初始Prompt
   - 构建状态管理机制

2. **阶段二**：功能完善（3周）
   - 实现RAG检索集成
   - 细化路由决策逻辑
   - 优化智能体交互流程

3. **阶段三**：GRPO优化（4周）
   - 数据集构建与标注
   - 教师智能体微调
   - 性能评估与迭代

4. **阶段四**：系统测试与部署（2周）
   - 综合功能测试
   - 用户体验评估
   - 系统部署与文档完善
