# 从零开始：安装 VS Code、连接 GitHub 并运行本项目（Windows）

本指南面向完全新手，手把手教你在 Windows 上安装 VS Code，登录 GitHub，克隆并运行本项目。全程使用系统自带的 PowerShell 和系统 Python（不使用虚拟环境）。

---

## 1. 准备工作（约 10~20 分钟）

- Windows 10/11 电脑，具备管理员权限
- 稳定的网络
- 一个 GitHub 账号（若没有，先到 https://github.com 注册）

---

## 2. 安装必备软件

### 2.1 安装 Git
- 下载地址：https://git-scm.com/download/win
- 一路“下一步”安装，默认选项即可。
- 验证安装：

```powershell
git --version
```

看到版本号（如 git version 2.x）表示成功。

### 2.2 安装 Python 3.11（可选安装conda）
- 下载地址：https://www.python.org/downloads/windows/
- 建议安装 Python 3.11.x。
- 安装界面务必勾选“Add python.exe to PATH”，然后“Install Now”。
- 验证安装：

```powershell
python --version
pip --version
```

看到版本号（如 Python 3.11.x）表示成功。

### 2.3 安装 Visual Studio Code（VS Code）
- 下载地址：https://code.visualstudio.com/
- 安装完成后启动 VS Code。

### 2.4 安装 VS Code 扩展（建议）
- Python（Microsoft）
- Pylance（Microsoft）
- GitHub Pull Requests and Issues（GitHub）
- GitLens（可选）

在 VS Code 左侧“扩展”面板搜索安装。

---

## 3. 登录 GitHub（VS Code 内）

1) 打开 VS Code，点击左下角“帐户（Accounts）”。
2) 选择“Sign in to GitHub”。
3) 按提示在浏览器完成授权，返回 VS Code 显示已登录即可。

（如只克隆公开仓库，也可直接使用 HTTPS 地址，不登录 VS Code 也行）

---

## 4. 获取项目代码

你可以用 VS Code 图形化“克隆仓库”，或用命令行。

### 方式 A：VS Code 图形化
1) 打开 VS Code → Ctrl+Shift+P → 输入并选择 “Git: Clone”。
2) 粘贴仓库地址：
   https://github.com/TTAWDTT/Agent-for-generating-similar-questions.git
3) 选择保存位置，克隆完成后选择“Open”打开项目。

### 方式 B：命令行（PowerShell）
```powershell
cd $HOME\Documents
git clone https://github.com/TTAWDTT/Agent-for-generating-similar-questions.git
cd Agent-for-generating-similar-questions
```

---

## 5. 安装项目依赖

在项目根目录执行：

```powershell
pip install -r requirements.txt
```

如遇权限或网络问题：
- 以管理员身份打开 PowerShell 后重试
- 使用镜像（可选）：

```powershell
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 6. 配置 API 密钥（必做）

本项目使用 DeepSeek 或 OpenAI 的 API。请准备任一平台的 API Key。

1) 复制环境变量模板（若不存在 .env.example，可直接创建 .env 文件）：

```powershell
# 有模板时
Copy-Item .env.example .env

# 没有模板时（直接创建空文件，由你手动填内容）
New-Item -ItemType File .env -Force | Out-Null
```

2) 用 VS Code 打开并编辑 `.env`，填入你的密钥：

```
DEEPSEEK_API_KEY=你的_DeepSeek_API_Key
# 或使用 OpenAI：
# OPENAI_API_KEY=你的_OpenAI_API_Key
# OPENAI_BASE_URL=https://api.deepseek.com/v1  # 使用 DeepSeek 的 OpenAI 兼容端点
```

提示：若出现 402 Insufficient Balance，请在控制台充值或更换可用 Key。

---

## 7. 运行项目（首次）

在项目根目录执行：

```powershell
python main.py
```

你应当看到终端按顺序打印：
- 工作流启动 → 标签识别 → 生成问题 → 生成解答 → 思维链检查
- 最终提示“🎉 工作流执行完成!”
- 结果会保存到 `results.json`，数据写入 `questions.db`

---

## 8. 常用工具与查看数据

- 查看数据库统计：

```powershell
python db_viewer.py stats
```

- 查看所有解答（含问题内容）：

```powershell
python db_viewer.py solutions
```

- 导出数据到 JSON：

```powershell
python db_viewer.py export
```

- 运行工作流测试（可选）：

```powershell
python test_workflow.py
```

---

## 9. 可视化工作流（可选）

仓库已内置 LangGraph 配置（`langgraph.json`）。如需在浏览器中查看图形化工作流：

```powershell
# 安装（若尚未安装）
pip install langgraph

# 启动本地可视化（开发面板）
langgraph dev

# 或快速检查配置
langgraph check
```

启动后按提示在浏览器打开本地地址，即可看到 `question_generation` 工作流图。

---

## 10. 常见问题排查（FAQ）

- pip/python 不是内部或外部命令
  - 重新安装 Python 时勾选 “Add python.exe to PATH”，或重启 PowerShell。

- 402 Insufficient Balance / 配额不足
  - 检查 `.env` 中的 API Key，确保余额充足或更换可用 Key。

- SSL/网络错误
  - 尝试换网络、使用镜像源安装依赖，或配置系统代理。

- 解析 JSON 出错
  - 本项目已对常见的 JSON 截断与转义问题做了容错；若仍失败，重试一次或更换模型/Key。

---

## 11. 下一步

- 在 `src/prompts/templates/` 中微调提示词模板，适配你的学科与题型
- 在 `main.py` 中替换示例题目，试运行不同输入
- 如需批量生成或接入 Web 界面，可在 Issues 提需求或自行扩展（可以做成Django框架的强耦合前后端）

祝你使用顺利！如在任一步卡住，欢迎到仓库提 Issue 寻求帮助。
