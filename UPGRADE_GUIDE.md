# 更新说明 - 扩展标签系统与思维链检查

## 🆕 新功能

### 1. 扩展标签系统
- **领域标签**（可多选）：数学、物理、化学、生物、历史、地理、语文、英语、编程、算法、机器学习、深度学习、经济学、心理学、哲学、逻辑推理、统计学、概率论、线性代数、微积分、离散数学、数据结构、操作系统、网络技术、数据库、人工智能
- **题型标签**（单选）：计算题、证明题、简答题

### 2. 新增思维链检查节点
- 自动检查每个生成问题的解答质量
- 评分标准：90-100分(优秀)、80-89分(良好)、70-79分(一般)、60-69分(较差)、<60分(不合格)
- 自动重试：分数低于80分会自动重新生成解答（最多2次）
- 检查维度：逻辑正确性、完整性、清晰度、准确性、符合题型

### 3. 分离式提示词管理
- 提示词按功能分离到 `src/prompts/templates/` 目录
- 便于独立调整和版本管理
- 包括：标签识别、问题生成、解答生成、思维链检查

## 🔄 工作流更新

新的工作流包含4个节点：
1. **tag_question** - 问题标签识别
2. **generate_questions** - 相似问题生成  
3. **solve_questions** - 问题解答
4. **verify_solutions** - 思维链检查（新增）

## 📊 数据库表结构变化

### original_questions
- 新增：`question_type` (TEXT) - 题型标签

### generated_questions  
- 新增：`question_type` (TEXT) - 题型标签

### question_solutions
- 新增：`verification_score` (INTEGER) - 验证得分
- 新增：`verification_passed` (BOOLEAN) - 是否通过验证
- 新增：`verification_feedback` (TEXT) - 验证反馈

## 🎯 输入格式更新

交互模式和文件模式的输入保持不变，但系统会自动识别：
- 领域标签：基于问题内容自动识别相关学科领域
- 题型标签：基于问题特征自动分类为计算题/证明题/简答题

## 📈 输出格式增强

结果中新增：
- 每题的领域标签和题型标签
- 思维链检查得分和通过状态
- 检查反馈和改进建议
- 整体验证摘要（通过率、平均分）

## 🛠️ 如何调整提示词

### 1. 标签识别提示词
文件：`src/prompts/templates/tagging_prompt.py`
- 调整领域标签列表
- 修改题型分类标准
- 调整输出格式

### 2. 问题生成提示词  
文件：`src/prompts/templates/generation_prompt.py`
- 调整生成问题数量
- 修改难度要求
- 调整多样性标准

### 3. 解答生成提示词
文件：`src/prompts/templates/solution_prompt.py`  
- 按题型调整解答格式
- 修改思维链要求
- 调整专业程度

### 4. 思维链检查提示词
文件：`src/prompts/templates/verification_prompt.py`
- 调整评分标准
- 修改检查维度
- 调整通过门槛

## 🚀 启动LangGraph Studio

```powershell
# 确保依赖已安装
python -m pip install -r requirements.txt
python -m pip install -e .

# 运行数据库迁移（如果有旧数据）
python migrate_database.py

# 启动Studio
langgraph dev
```

在浏览器中选择 `question_generation` 图，即可看到包含4个节点的完整工作流可视化界面。

## 🧪 测试建议

可以用不同类型的问题测试：
- **计算题示例**："计算函数f(x)=x²+2x+1的导数"
- **证明题示例**："证明勾股定理"  
- **简答题示例**："简述机器学习中监督学习和无监督学习的区别"

系统会自动识别题型并生成对应格式的相似问题和解答。
