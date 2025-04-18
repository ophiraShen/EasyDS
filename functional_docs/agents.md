# 智能体系统设计文档

## 1. 系统概述

c

## 2. 核心智能体

### 2.1 路由智能体（Router Agent）

**功能定位**：评估用户讲解并决策下一步教学路径

**核心能力**：
1. **回答评估**：分析用户讲解的正确性、完整性和清晰度
2. **决策路由**：根据评估结果决定启用学生智能体（深度追问）或教师智能体（纠错引导）
3. **状态管理**：维护教学会话状态，追踪学习进度

**路由决策策略**：
- 如果用户回复内容错误：直接转向 Teacher Agent
- 如果用户回复内容正确：
  - 回复错误，转向 Teacher Agent 进行纠正
  - 回复正确且完整，转向 Teacher Agent 进行总结
  - 回复正确但不完整，转向 Student Agent 进行追问
  - 回复不完整，转向 Student Agent 进行进一步的追问
- 对于选择题仅有答案无讲解的情况：
  - 如果答案正确：转向 Student Agent 引导讲解
  - 如果答案错误：转向 Teacher Agent 解释正确答案
- 对于用户的直接提问：始终转向 Teacher Agent 进行解答

**提示词设计路径**：`src/agents/prompts/router_agent_prompt.txt`

### 2.2 学生智能体（Student Agent）

**功能定位**：模拟学习者提出深度追问

**核心能力**：
1. **深度提问**：针对用户讲解中的关键点提出深入问题
2. **困惑模拟**：模拟学习过程中可能出现的困惑点
3. **引导阐述**：引导用户进行更清晰的知识阐述
4. **思维启发**：通过问题启发用户思考知识间的联系

**提问策略**：
- 当用户仅提供选择题答案但尚未详细解释时：
  - 对用户的正确选择表示认同
  - 请用户解释答案背后的原理
- 当用户已经进行了讲解但有深入空间时：
  - 针对核心知识点提问
  - 寻求更深入的解释或证明
  - 探讨与其他数据结构概念的关联
- 当解释不完整时，引导用户展开更详细的说明
- 当基本完整但缺少重要延伸点时，适当拓展提问

**提示词设计路径**：`src/agents/prompts/student_agent_prompt2.txt`

### 2.3 教师智能体（Teacher Agent）

**功能定位**：提供专业纠错引导和知识强化

**核心能力**：
1. **错误纠正**：识别并纠正用户讲解中的概念性错误
2. **知识补充**：补充遗漏的重要知识点
3. **引导改进**：提供具体的改进建议
4. **计算推理**：针对数值计算问题提供准确解析

**响应策略**：
- 用户讲解错误时：明确指出错误并温和纠正
- 用户讲解正确且完整时：给予肯定并总结核心知识点
- 用户直接提问时：提供专业、准确的回答

**工具集成**：
- 知识点检索工具：根据题目相关知识点列表提供详细概述信息

**提示词设计路径**：`src/agents/prompts/teacher_agent_prompt.txt`

**优化方案**：
- 基座模型：DeepSeek-R1-Distill-Qwen-14B
- 微调方法：GRPO（Guided Reinforcement from Preference Optimization）
- 双指标评估体系：
  * 答案正确性（7分）：数值精确匹配
  * 步骤合理性（3分）：解题过程评估

## 3. 智能体协同工作流

### 3.1 状态流转图

```
          +----------+
          |   开始   |
          +----------+
               |
               v
       +---------------+
       | 路由智能体    |----+
       | (router_agent)|    |
       +---------------+    |
          /          \      |
         /            \     |
        v              v    |
+---------------+ +---------------+
| 学生智能体    | | 教师智能体    |<---+
| (student_agent)| | (teacher_agent)|    |
+---------------+ +---------------+    |
        |                |             |
        |                |             |
        |                v             |
        |        +---------------+     |
        |        |    工具节点   |-----+
        |        |   (tool_node) |
        |        +---------------+
        |                
        |                
        v                
  +----------+          
  |   结束   |          
  +----------+          
```

### 3.2 会话流程

1. **初始化阶段**
   - 获取题目信息（标题、内容、参考答案、解释、相关知识点）
   - 初始化会话状态（消息记录、评估结果）

2. **讲解阶段**
   - 用户主动讲解数据结构知识点或解题思路
   - 系统记录讲解内容

3. **评估与路由阶段**
   - 路由智能体评估用户回复类型（讲解、选择题答案、直接提问）
   - 评估讲解的正确性和完整性
   - 根据评估结果决定下一步路由方向

4. **反馈阶段**
   - 学生智能体：提出深度追问，促进思考
   - 教师智能体：提供纠错引导或知识总结，必要时调用知识检索工具

5. **工具调用阶段（按需）**
   - 教师智能体可调用知识点检索工具获取详细概述
   - 工具处理完成后返回结果给教师智能体继续回复

6. **循环流程**
   - 用户继续讲解或回应反馈
   - 路由智能体重新评估，决定下一步路由

### 3.3 状态管理

**会话状态结构**：
```python
class State(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list, title="对话列表")
    question: list = Field(default=[], title="当前题目信息")
    evaluation: dict = Field(default={}, title="用户回复评估")
    log: str = Field(default="", title="节点执行日志")
```

**评估结果结构**：
```python
class Evaluation(TypedDict):
    is_right: bool = Field(default=None, title="用户回复是否正确")
    is_complete: bool = Field(default=None, title="用户回复是否完整")
    reason: str = Field(default="", title="用户回复评估原因")
    next_agent: Literal["teacher", "student"]
```

## 4. 技术实现

### 4.1 技术栈

- LangGraph：智能体工作流管理和状态转换
- LangChain：智能体框架、组件和工具集成
- DeepSeek-Chat：大语言模型API（当前实现）
- KnowledgeIndexSystem：知识点检索系统
- MemorySaver：状态保存与恢复

### 4.2 系统架构

```
[用户界面] <--> [MainGraph工作流]
                  |
       +----------+------------+
       |          |            |
[路由智能体]  [学生智能体]  [教师智能体]
       |                       |
       |                       v
       |               [知识检索工具节点]
       |                       |
       |                       v
       |               [KnowledgeIndexSystem]
       |                       
       v                       
[MemorySaver状态管理]
```

### 4.3 主要组件实现

**1. 路由智能体**：
```python
async def router_agent(state: State, config) -> Command[Literal["teacher_agent", "student_agent"]]:
    """根据当前状态进行路由"""
    try:
        curr_question = state.question[0]
        with open("/root/autodl-tmp/EasyDS/src/agents/prompts/router_agent_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt = ChatPromptTemplate([
            ("system", prompt),
            MessagesPlaceholder(variable_name="messages")
        ])
        system_prompt = prompt.partial(title=curr_question['title'],content=curr_question['content'],answer=curr_question['reference_answer']['content'],explanation=curr_question['reference_answer']['explanation'])
        chain = system_prompt | llm.with_structured_output(Evaluation, method="function_calling")
        router_result = await chain.ainvoke({"messages": state.messages}, config)
        if router_result['next_agent'] == 'teacher':
            goto = "teacher_agent"
        else:
            goto = "student_agent"
        return Command(
            update={
                "evaluation": router_result,
            },
            goto=goto
        )
    except Exception as e:
        return Command(
            update={
                "log": str(e)
            },
            goto="teacher_agent"                           
        )
```

**2. 学生智能体**：
```python
async def student_agent(state: State, config) -> State:
    try:
        curr_question = state.question[0]
        evaluation = state.evaluation
        with open("/root/autodl-tmp/EasyDS/src/agents/prompts/student_agent_prompt2.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt = ChatPromptTemplate([
            ("system", prompt),
            ("human", "{messages}")
        ])
        system_prompt = prompt.partial(
            title=curr_question['title'],
            content=curr_question['content'],
            answer=curr_question['reference_answer']['content'],
            explanation=curr_question['reference_answer']['explanation'],
            is_right=evaluation['is_right'],
            is_complete=evaluation['is_complete'],
            reason=evaluation['reason']
        )
        chain = system_prompt | llm
        stu_feedback = await chain.ainvoke({"messages": state.messages}, config)
        return {"messages": stu_feedback}
    except Exception as e:
        return {"log": str(e)}
```

**3. 教师智能体**：
```python
async def teacher_agent(state: State, config) -> Command[Literal["tool_node", "__end__"]]:
    """根据当前状态进行回复"""
    try:
        curr_question = state.question[0]
        evaluation = state.evaluation
        with open("/root/autodl-tmp/EasyDS/src/agents/prompts/teacher_agent_prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        prompt = ChatPromptTemplate([
            ("system", prompt),
            ("human", "{messages}")
        ])
        system_prompt = prompt.partial(
            title=curr_question['title'],
            content=curr_question['content'],
            answer=curr_question['reference_answer']['content'],
            knowledge_points=curr_question['knowledge_points'],
            explanation=curr_question['reference_answer']['explanation'],
            is_right=evaluation['is_right'],
            is_complete=evaluation['is_complete'],
            reason=evaluation['reason']
        )
        chain = system_prompt | llm.bind_tools(tools)
        teacher_feedback = await chain.ainvoke({"messages": state.messages}, config)
        if teacher_feedback.tool_calls:
            goto = "tool_node"
        else:
            goto = "__end__"
        return Command(
            update={
                "messages": teacher_feedback
            },
            goto=goto
        )
    except Exception as e:
        return Command(
            update={
                "log": str(e)
            },
            goto="__end__"
        )
```

**4. 知识检索工具**：
```python
async def knowledge_summry_search(knowledge_points: list):
    """根据知识点列表查询知识点概述"""
    try:
        system = await KnowledgeIndexSystem.load_indices_async('/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl')
        knowledge_summry = []
        for kp in knowledge_points:
            knowledge_point_info = await system.get_knowledge_point_async(kp)
            if knowledge_point_info:    
                knowledge_summry.append({
                    "knowledge_point": knowledge_point_info['title'],
                    "summry": knowledge_point_info['summry']
                })
        if knowledge_summry:
            knowledge_summry_str = "\n".join([f"{kp['knowledge_point']}: {kp['summry']}" for kp in knowledge_summry])
            return knowledge_summry_str
        else:
            return "未找到对应知识点"
    except Exception as e:
        return str(e)
```

**5. 工作流程图配置**：
```python
workflow = StateGraph(State)

workflow.add_node("router_agent", router_agent)
workflow.add_node("student_agent", student_agent)
workflow.add_node("teacher_agent", teacher_agent)
workflow.add_node("tool_node", ToolNode(tools))
workflow.add_edge(START, "router_agent")
workflow.add_edge("tool_node", "teacher_agent")
workflow.add_edge("student_agent", "__end__")

memory = MemorySaver()

graph = workflow.compile(checkpointer=memory)
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
3. **知识图谱强化**：丰富KnowledgeIndexSystem中的知识点信息
4. **教师智能体GRPO微调**：针对计算推理能力持续优化

## 6. 实施计划

1. **阶段一**：基础框架搭建（已完成）
   - 实现基本智能体结构
   - 设计初始Prompt
   - 构建状态管理机制

2. **阶段二**：功能完善（进行中）
   - 知识检索工具集成（已完成）
   - 细化路由决策逻辑（已完成）
   - 优化智能体交互流程（进行中）

3. **阶段三**：模型优化（计划中）
   - 数据集构建与标注
   - 教师智能体微调
   - 性能评估与迭代

4. **阶段四**：系统测试与部署（计划中）
   - 综合功能测试
   - 用户体验评估
   - 系统部署与文档完善