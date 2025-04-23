# EasyDS - 基于费曼学习法的考研数据结构教学系统


## 简介

EasyDS是一款创新型AI教育系统，专为考研数据结构学习设计。系统采用费曼学习法，通过多智能体协同教学模式，实现深度交互式学习体验。不同于传统"问答式"AI辅导，EasyDS引导学生主动讲解题目，智能体根据学生表现动态调整教学策略，形成"讲解-反馈-修正-强化"的学习闭环，有效提升学习效果。

## 系统架构

EasyDS采用三层智能体模型设计：

- **路由Agent**：评估用户回答，动态选择合适的下一步智能体
- **学生Agent**：针对回答正确但不完整的情况，进行知识点追问，促进深度理解
- **教师Agent**：分为三种工作模式：
  - 纠错引导（回答不正确时）
  - 知识点追问（回答不完整时）
  - 总结加强（回答正确且完整时）

## 技术特点

- **基于LangGraph构建**：灵活的智能体协作框架
- **双模型支持**：DeepSeek-V3 和 Qwen2.5-7B-Instruct
- **动态教学路径**：根据学习者表现实时调整教学策略
- **知识范围限定**：严格遵循考研数据结构大纲
- **RAG增强**：整合权威资料，提供精准知识点讲解

## 快速开始

### 在线演示

您可以直接访问我们的在线系统：[EasyDS](http://117.72.84.121:3003/)

### 环境要求

- Python 3.11
- 依赖包：详见`requirements.txt`

### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/EasyDS.git
cd EasyDS

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，添加必要的API密钥
```

### 运行

```bash
# 启动Web服务
bash run_web.sh

# 或直接运行
python -m uvicorn web.main:app --host 0.0.0.0 --port 3003 --workers 1
```

访问 `http://localhost:3003` 开始使用EasyDS。

## 使用指南

1. **题目讲解**：用户向系统提供数据结构题目，并尝试自己讲解解题思路
2. **智能评估**：系统评估讲解的正确性和完整性
3. **互动反馈**：
   - 回答正确但不完整：学生Agent提出追问
   - 回答不正确：教师Agent提供纠错指导
   - 回答正确且完整：教师Agent进行总结强化
4. **知识巩固**：系统根据学习进度推荐相关练习题

## 项目结构
```
EasyDS/
├── src/ # 核心源代码
│ ├── agents/ # 智能体实现
│ │ ├── prompts/ # 系统提示词
│ ├── models/ # 模型相关代码
│ ├── database/ # 知识库和数据存储
│ └── knowledge_qa_system.py # 主系统实现
├── web/ # Web界面
├── docs/ # 文档
├── data/ # 数据集和资源
├── config/ # 配置文件
├── requirements.txt # 依赖包列表
├── run_web.sh # 启动脚本
└── README.md # 项目说明
```


## 设计理念

EasyDS基于费曼学习法（"通过教授来学习"），通过引导学习者主动讲解知识点，发现知识盲点，实现更深层次的理解。系统的多智能体协同模式模拟了理想的学习环境，既有提问引导的"同学"，又有纠错点拨的"老师"，帮助学习者建立完整、准确的知识体系。

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 代码优化和bug修复
- 文档改进
- 新功能建议和实现
- 知识库扩充

请参阅[贡献指南](docs/CONTRIBUTING.md)了解更多信息。

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。

## 联系方式

- 项目维护者：OphiraShen
- 电子邮件：ophira.shenyige@outlook.com
- 项目仓库：https://github.com/yourusername/EasyDS