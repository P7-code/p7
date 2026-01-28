# 招标文件智能分析系统

基于 LangGraph 工作流的智能招标文件分析工具，专为网络安全售前工程师设计。

## ✨ 核心功能

- ✅ **废标项检测** - 自动识别可能导致废标的致命问题
- ✅ **商务得分检查** - 评估商务部分得分，找出失分点
- ✅ **技术方案评估** - 检查技术方案的完整性、创新性、可行性
- ✅ **指标应答验证** - 逐条检查技术指标响应情况
- ✅ **技术得分点分析** - 深度分析技术得分覆盖情况
- ✅ **文件结构检查** - 检查目录完整性和排布合理性

## 🚀 快速开始

### 在线访问

- **GitHub 仓库**：https://github.com/P7-code/p7
- **在线应用**：https://p7-code-p7.streamlit.app

### 本地运行

#### 1. 克隆仓库

```bash
git clone https://github.com/P7-code/p7.git
cd p7
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 配置环境变量（可选）

如果要使用完整功能，需要配置 LLM API：

```bash
# Linux/Mac
export OPENAI_API_KEY="your-api-key"
export OPENAI_API_BASE="https://api.openai.com/v1"  # 可选

# Windows
set OPENAI_API_KEY=your-api-key
set OPENAI_API_BASE=https://api.openai.com/v1
```

#### 4. 运行应用

```bash
streamlit run app.py
```

浏览器会自动打开 http://localhost:8501

## 📦 部署到 Streamlit Cloud

### 1. 推送代码到 GitHub

```bash
git add .
git commit -m "your commit message"
git push origin main
```

### 2. 连接 Streamlit Cloud

1. 访问 https://share.streamlit.io
2. 点击 "New app"
3. 选择你的 GitHub 仓库
4. 配置：
   - Repository: `P7-code/p7`
   - Branch: `main`
   - Main file path: `app.py`
5. 点击 "Deploy"

### 3. 配置环境变量（推荐）

在 Streamlit Cloud 中添加环境变量：

1. 进入应用设置：Settings → Environment Variables
2. 添加以下变量：
   - `OPENAI_API_KEY`: 你的 API 密钥
   - `OPENAI_API_BASE`: API 基础URL（可选）

### 支持的 LLM 服务

本系统使用 OpenAI 兼容接口，支持以下服务：

- **OpenAI** - https://api.openai.com/v1
- **Azure OpenAI** - 你的 Azure endpoint
- **其他兼容服务** - 如 DeepSeek、Kimi 等

## 📁 项目结构

```
p7/
├── app.py                          # Streamlit Web 应用
├── requirements.txt                 # Python 依赖
├── README.md                       # 项目说明
├── .streamlit/config.toml          # Streamlit 配置
│
├── src/                            # 源代码
│   └── graphs/
│       ├── state.py               # 状态定义
│       ├── node.py                # 节点函数
│       └── graph.py               # 主图编排
│
├── src/                            # 工具
│   └── utils/
│       └── file/
│           └── file.py            # 文件处理
│
└── config/                         # LLM 配置
    ├── generate_checklist_cfg.json
    ├── invalid_items_check_cfg.json
    ├── commercial_score_check_cfg.json
    ├── technical_plan_check_cfg.json
    ├── indicator_response_check_cfg.json
    ├── technical_score_check_cfg.json
    ├── bid_structure_check_cfg.json
    └── modification_summary_cfg.json
```

## 🎯 使用流程

1. **上传招标文件**
   - 支持 PDF、Word、PPT 格式
   - 系统自动提取文件内容

2. **上传投标文件**
   - 支持 PDF、Word、PPT 格式
   - 系统自动提取文件内容

3. **点击"开始分析"**
   - 系统自动进行六维并行检测
   - 分析过程通常需要 1-3 分钟

4. **查看分析结果**
   - 废标项检测结果
   - 商务得分检查
   - 技术方案评估
   - 指标应答验证
   - 技术得分点分析
   - 文件结构检查

5. **下载分析报告**
   - 下载完整的 JSON 格式报告

## 🛠️ 技术栈

- **工作流引擎**: LangGraph
- **Web 框架**: Streamlit
- **LLM 接口**: LangChain + OpenAI API
- **文档处理**: PyPDF、python-docx、python-pptx
- **数据处理**: Pandas、OpenPyXL

## 📖 工作流架构

```
┌─────────────┐
│  文件解析   │
│ (串行)     │
└──────┬──────┘
       │
┌──────▼──────┐
│  生成清单   │
└──────┬──────┘
       │
   ┌───┴────────────────────┐
   │     六维并行检测       │
   ├─────────┬───────┬──────┤
   │         │       │      │
废标 商务 技术 指标 得分 结构
   │         │       │      │
   └─────────┴───────┴──────┘
            │
      ┌─────▼─────┐
      │  汇总建议  │
      └───────────┘
```

## ⚠️ 注意事项

1. **文件大小限制**
   - 单个文件不超过 100MB
   - 建议使用压缩后的 PDF

2. **API 配额**
   - 使用 LLM 服务会产生费用
   - 建议设置合理的配额限制

3. **隐私保护**
   - 上传的文件仅用于分析
   - 不会存储在服务器上

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

- GitHub: https://github.com/P7-code/p7
- Email: 18646133221@163.com

---

**AI应用创新激励计划参赛作品** 🚀
