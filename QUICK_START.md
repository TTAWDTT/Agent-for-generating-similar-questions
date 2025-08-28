# 快速开始指南

## 🚀 快速安装和运行

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 配置API密钥
cp .env.example .env
# 编辑.env文件，填入你的DeepSeek API密钥
```

### 2. 基础使用

#### 方式一：运行示例程序
```bash
python main.py
```

#### 方式二：交互式运行
```bash
python cli.py -i
```

#### 方式三：从文件运行
```bash
# 创建示例文件
python cli.py --create-sample

# 从文件运行
python cli.py -f sample_input.json
```

### 3. 测试系统
```bash
python test_workflow.py
```

## 📝 输入格式

### JSON文件格式
```json
{
  "question": "你的问题",
  "thinking_chain": "详细的思维链",
  "answer": "答案"
}
```

### 交互模式
程序会依次提示你输入：
1. 问题（多行，空行结束）
2. 思维链（多行，空行结束）
3. 答案（单行）

## 🎯 预期输出

系统会为每个输入问题：
1. ✅ 识别领域标签
2. 🔄 生成5道相似问题
3. 🧠 为每道问题提供思维链解答
4. 💾 保存到SQLite数据库

## ⚙️ 环境变量配置

在`.env`文件中设置：
```
DEEPSEEK_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

## 🔧 故障排除

### 常见问题

1. **API密钥错误**
   - 检查`.env`文件是否存在
   - 确认API密钥正确

2. **网络连接问题**
   - 检查网络连接
   - 确认API基础URL正确

3. **依赖包问题**
   - 运行 `pip install -r requirements.txt`
   - 确保Python版本 >= 3.8

### 调试模式
如需调试，可以在代码中添加详细日志输出。

## 📚 更多功能

- 查看数据库：直接打开生成的`questions.db`文件
- 自定义提示词：修改`src/prompts/prompt_manager.py`
- 添加新领域：在`DOMAIN_EXPERTS`字典中添加

## 💡 使用建议

1. **质量最佳实践**：提供详细、准确的思维链
2. **领域覆盖**：支持数学、物理、编程等16个领域
3. **批量处理**：可以编写脚本批量处理多个问题

开始使用吧！🎉
