# Agent-for-generating-similar-questions

基于LangGraph框架的智能问题生成和解答系统，可以根据一道输入题目扩散性地生成多道同类问题，并提供详细的思维链解答。

## 🌟 主要功能

- **智能标签识别**: 自动为输入问题打上领域标签（数学、物理、编程等）
- **动态提示词优化**: 根据领域标签优化出题和解题提示词
- **相似问题生成**: 基于原问题生成5道同知识点的相似问题
- **思维链解答**: 使用DeepSeek-Reasoner模型生成详细的解题思路
- **数据持久化**: 所有问题和解答存储到SQLite数据库

## 🛠️ 技术架构

### 核心框架
- **LangGraph**: 工作流编排框架
- **deepseek-chat**: 主要推理模型
- **SQLite**: 数据存储
- **Pydantic**: 数据验证和模型

### 工作流设计
```
输入问题 → 标签识别 → 问题生成 → 问题解答 → 结果存储
```

## 📁 项目结构

```
src/
├── agents/                 # 工作流代理
│   ├── __init__.py
│   └── question_agents.py  # 标签识别、问题生成、解答代理
├── database/              # 数据库模块
│   ├── __init__.py
│   └── db_manager.py      # SQLite数据库管理
├── models/                # 数据模型
│   ├── __init__.py
│   └── schemas.py         # Pydantic数据模型
├── prompts/               # 提示词管理
│   ├── __init__.py
│   └── prompt_manager.py  # 提示词模板和优化
├── utils/                 # 工具函数
│   ├── __init__.py
│   └── llm_client.py      # LLM客户端封装
├── __init__.py
└── workflow.py            # LangGraph工作流定义
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd Agent-for-generating-similar-questions

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API密钥
# DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 3. 运行示例

```bash
# 运行主程序（包含示例）
python main.py

# 运行完整测试
python test_workflow.py
```

### 交互式运行（按用户输入生成）

项目支持从用户输入直接触发工作流（问题 → 答案 → 思维链）。推荐在开发或演示时使用交互模式：

```bash
# 交互式模式，会提示依次输入：问题、参考答案、思维链（支持多行，以空行结束）
python main.py --interactive

# 或直接运行无参数时也会提示输入（取决于 main.py 的行为）
python main.py
```

在交互模式下，输入会被直接传入 `QuestionGenerationWorkflow.run(question, thinking_chain, answer)` 并执行完整工作流。

## 💡 使用示例

### 基本用法

```python
from src.workflow import QuestionGenerationWorkflow

# 创建工作流
workflow = QuestionGenerationWorkflow()

# 输入问题数据
question = "一个圆的半径是5cm，求这个圆的面积。"
thinking_chain = "使用圆的面积公式 S = πr²..."
answer = "25π cm²"

# 运行工作流
result_state = workflow.run(question, thinking_chain, answer)

# 获取结果
results = workflow.get_results(result_state)
```

### 工作流输出示例

```json
{
  "original_question": {
    "question": "一个圆的半径是5cm，求这个圆的面积。",
    "tags": ["数学", "几何"]
  },
  "generated_questions": [
    {
      "id": 1,
      "question": "一个圆的直径是8cm，求这个圆的面积。",
      "tags": ["数学", "几何"],
      "solution": {
        "thinking_chain": "已知直径为8cm，则半径r=4cm...",
        "answer": "16π cm²"
      }
    }
  ]
}
```

## 🎯 工作流详解

### 1. 问题标签识别节点
- 分析输入问题的领域特征
- 支持多标签分类（数学、物理、编程等16个领域）
- 为后续节点提供领域上下文

### 2. 问题生成节点
- 根据领域标签优化生成提示词
- 调用专业角色prompt（如"数学教育专家"）
- 生成5道同知识点但不同情境的问题
- 保存到SQLite数据库

### 3. 问题解答节点
- 根据领域标签优化解题提示词
- 生成详细的思维链和最终答案
- 保存解答到数据库

> 注意：模型经常会在数学表达式中使用 LaTeX（例如 `\frac{1}{2}`）或未转义的反斜杠，这可能导致 JSON 解析失败（Invalid \escape）。见下方“故障排查”部分获取缓解措施。

## 🗄️ 数据库设计

### 表结构

```sql
-- 原始问题表
CREATE TABLE original_questions (
    id INTEGER PRIMARY KEY,
    question TEXT NOT NULL,
    thinking_chain TEXT NOT NULL,
    answer TEXT NOT NULL,
    domain_tags TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 生成问题表
CREATE TABLE generated_questions (
    id INTEGER PRIMARY KEY,
    original_question_id INTEGER,
    question TEXT NOT NULL,
    domain_tags TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 问题解答表
CREATE TABLE question_solutions (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL,
    thinking_chain TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 关联查询功能

通过表关联查询，问题解答表可以获取问题内容：

```python
# 获取解答时自动包含问题内容
solutions = db_manager.get_question_solutions(question_id)
for solution in solutions:
    print(f"问题: {solution.question}")
    print(f"解答: {solution.answer}")

# 获取解答的完整上下文
context = db_manager.get_solution_with_full_context(solution_id)
```

### 数据库工具

```bash
# 查看数据库统计
python db_viewer.py stats

# 查看所有解答（含问题内容）
python db_viewer.py solutions

# 查看特定解答的完整上下文
python db_viewer.py context <solution_id>

# 导出数据到JSON
python db_viewer.py export
```

### 快速查看 QA 总览（问题 / 思维链 / 答案）

```bash
python db_viewer.py qa 10   # 列出最近 10 条解答的 问题/思维链/答案
```

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | - |
| `OPENAI_API_KEY` | OpenAI API密钥（备用） | - |
| `OPENAI_BASE_URL` | API基础URL | `https://api.deepseek.com/v1` |

### 支持的领域标签

数据&聚类、深度学习、SVM、决策树、贝叶斯、集成学习

## 🤝 贡献指南

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

如有问题或建议，请通过Issue或邮件联系。
