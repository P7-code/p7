## 项目概述
- **名称**: 安天投标文件智能分析系统
- **功能**: 基于LangGraph工作流的智能招标文件分析工具，自动检测废标项、商务得分、技术方案等六个维度，生成详细的修改建议。

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|---------|---------|---------|
| tender_doc_parse | `src/graphs/node.py` | task | 解析招标文件内容 | - | - |
| bid_doc_parse | `src/graphs/node.py` | task | 解析投标文件内容 | - | - |
| invalid_items_check | `src/graphs/node.py` | agent | 废标项检查 | - | `config/invalid_items_check_cfg.json` |
| commercial_score_check | `src/graphs/node.py` | agent | 商务得分点检查 | - | `config/commercial_score_check_cfg.json` |
| technical_plan_check | `src/graphs/node.py` | agent | 技术方案检查 | - | `config/technical_plan_check_cfg.json` |
| indicator_response_check | `src/graphs/node.py` | agent | 指标与应答检查 | - | `config/indicator_response_check_cfg.json` |
| technical_score_check | `src/graphs/node.py` | agent | 技术得分点检查 | - | `config/technical_score_check_cfg.json` |
| bid_structure_check | `src/graphs/node.py` | agent | 投标文件结构检查 | - | `config/bid_structure_check_cfg.json` |
| modification_summary | `src/graphs/node.py` | agent | 汇总修改建议 | - | `config/modification_summary_cfg.json` |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 子图清单
| 子图名 | 文件位置 | 功能描述 | 被调用节点 |
|-------|---------|------|---------|-----------|
| 无 | - | 本项目为简单DAG结构，无子图 | - |

## 集成使用
- 所有 agent 节点使用 `大语言模型` 集成 (integration-doubao-seed)
- 节点函数通过 `langchain-openai` 接口调用 OpenAI 兼容的 API
- 支持的 API 服务：DeepSeek、Kimi、OpenAI、智谱 AI 等

## 工作流架构

```
┌─────────────┐
│tender_doc_  │
│  parse      │ 串行
└──────┬──────┘
       │
┌──────▼──────┐
│bid_doc_     │
│  parse      │ 串行
└──────┬──────┘
       │
  ┌────┴──────────────────────────────────────────┐
  │                六维并行检测                     │
  ├──────────┬──────────┬──────────┬──────────────┤
  │          │          │          │              │
  │invalid_  │commercial│technical │indicator_    │
  │ items    │ _score   │ _plan    │ response     │
  │ _check   │ _check   │ _check   │ _check       │
  │          │          │          │              │
  ├──────────┴──────────┴──────────┴──────────────┤
  │          │          │          │              │
  │technical │bid_      │          │              │
  │_score    │ structure│          │              │
  │_check    │_check    │          │              │
  │          │          │          │              │
  └──────────┴──────────┴──────────┴──────────────┘
                          │
                  ┌───────▼────────┐
                  │modification_   │
                  │   summary      │ 串行
                  └────────────────┘
```

## 数据流说明

### 输入阶段
1. **tender_file**: 招标文件（PDF/Word/PPT）
2. **bid_file**: 投标文件（PDF/Word/PPT）

### 串行阶段
1. **tender_doc_parse**: 解析招标文件 → 提取文本内容
2. **bid_doc_parse**: 解析投标文件 → 提取文本内容

### 并行阶段
1. **invalid_items_check**: 招标文件内容 + 投标内容 → 废标项检测结果
2. **commercial_score_check**: 招标文件内容 + 投标内容 → 商务得分结果
3. **technical_plan_check**: 招标文件内容 + 投标内容 → 技术方案评估
4. **indicator_response_check**: 招标文件内容 + 投标内容 → 指标应答验证
5. **technical_score_check**: 招标文件内容 + 投标内容 + indicator_response_check → 技术得分分析
6. **bid_structure_check**: 招标文件内容 + 投标内容 → 文件结构检查

### 输出阶段
1. **modification_summary**: 汇总所有检查结果 → 生成修改建议

## 配置文件清单

| 配置文件 | 用途 |
|---------|------|
| `config/invalid_items_check_cfg.json` | 废标项检查的 LLM 配置 |
| `config/commercial_score_check_cfg.json` | 商务得分检查的 LLM 配置 |
| `config/technical_plan_check_cfg.json` | 技术方案检查的 LLM 配置 |
| `config/indicator_response_check_cfg.json` | 指标应答检查的 LLM 配置 |
| `config/technical_score_check_cfg.json` | 技术得分检查的 LLM 配置 |
| `config/bid_structure_check_cfg.json` | 文件结构检查的 LLM 配置 |
| `config/modification_summary_cfg.json` | 汇总修改建议的 LLM 配置 |

## 关键文件说明

### `src/graphs/state.py`
- 定义全局状态 `GlobalState`
- 定义工作流输入 `GraphInput` 和输出 `GraphOutput`
- 定义每个节点的独立输入输出类

### `src/graphs/node.py`
- 实现所有节点函数
- 包含文件解析、LLM 调用等核心逻辑
- 使用 `get_config_file_path` 辅助函数读取配置文件

### `src/graphs/graph.py`
- 定义主图结构
- 采用清晰的串行+并行结构
- 无循环，纯 DAG 结构

### `src/utils/file/file.py`
- 文件处理工具类
- 支持 PDF、Word、PPT 等格式
- 提供文本提取功能

### `app.py`
- Streamlit Web 应用主文件
- 提供文件上传和结果展示界面
- 支持演示模式和完整模式

## 部署配置

### 环境变量
- `OPENAI_API_KEY`: API 密钥（必需）
- `OPENAI_API_BASE`: API 基础URL（必需）

### 配置文件
- `.streamlit/config.toml`: Streamlit 界面配置
- `.streamlit/secrets.toml`: API Key 配置（本地，不提交到 Git）
- `.streamlit/secrets.toml.example`: API Key 配置示例（提交到 Git）

### 依赖管理
- `requirements.txt`: Python 依赖列表
- 仅包含公开可用的包，无私有依赖

## 测试与验证

### 本地测试
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export OPENAI_API_KEY="your-key"
export OPENAI_API_BASE="https://api.deepseek.com"

# 运行应用
streamlit run app.py
```

### 线上部署
- Streamlit Cloud: https://p7-code-p7.streamlit.app
- GitHub 仓库: https://github.com/P7-code/p7
- 部署文档: [DEPLOYMENT.md](./DEPLOYMENT.md)

## 常见问题

### Q1: 如何修改 LLM 配置？
A: 编辑 `config/` 目录下的对应 JSON 文件，修改 `config.model` 字段。

### Q2: 如何添加新的检查维度？
A: 
1. 在 `src/graphs/state.py` 中添加新的节点输入输出类
2. 在 `src/graphs/node.py` 中实现节点函数
3. 在 `config/` 目录下创建对应的 LLM 配置文件
4. 在 `src/graphs/graph.py` 中添加节点和边

### Q3: 如何切换到其他 LLM 服务？
A: 修改 `.streamlit/secrets.toml` 中的 `OPENAI_API_KEY` 和 `OPENAI_API_BASE`。

### Q4: 为什么运行时显示"演示模式"？
A: 未配置 API Key，系统返回模拟结果。请按照部署文档配置环境变量。
