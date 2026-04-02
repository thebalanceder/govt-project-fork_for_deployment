# 🇲🇾 CSPOPS - Citizen Sentiment & Public Opinion Perception System

## 🤖 Multi-Agent AI Discussion System for Malaysia

**English** | [中文](#中文版本)

---

## 📋 Overview / 概述

CSPOPS is an advanced AI-powered public opinion monitoring system that combines:
- **Real-time data collection** from 170+ sources (news, APIs, web crawlers)
- **NLP sentiment analysis** with emotion detection
- **6 Expert AI Agents** that discuss and analyze issues using MiroFish methodology
- **Interactive dashboard** for visualization and decision-making

CSPOPS 是一个先进的人工智能舆论监测系统，结合了：
- **实时数据采集** 来自 170+ 来源（新闻、API、网络爬虫）
- **NLP 情感分析** 与情绪检测
- **6 个专家 AI 智能体** 使用 MiroFish 方法讨论和分析问题
- **交互式仪表板** 用于可视化和决策

---

## 🚀 Quick Start / 快速开始

### Prerequisites / 前置条件

```bash
# Python 3.10+ required
python3 --version

# Install dependencies (choose one)
pip install -e .
# or install from your own requirements workflow
```

### Run the Application / 运行应用

```bash
# Start Flask server
python3 -m opinion_sim_system.flask_app

# Open browser to
# 打开浏览器访问：http://localhost:5000
```

### Phase2B Briefing UI (MVP) / Phase2B 简报前端（MVP）

- The current MVP briefing flow is driven by `POST /api/briefing-run`, which returns:
  - `semantic_evidence` (Stage 2)
  - `simulation_result` (Stage 4)
  - `report` / `report_text` (Stage 5, DeepSeek live or fallback)
- To enable DeepSeek live mode, set `DEEPSEEK_API_KEY` in `.env` and restart the server.
- **Security**: keep `.env` local and never commit API keys to git.

### Collect Data & Run Agents / 采集数据并运行智能体

1. Click **"Data Collection"** tab / 点击 **"数据采集"** 标签
2. Click **"Collect Real-Time Data"** / 点击 **"采集实时数据"** 按钮
3. Wait 60-90 seconds for collection + NLP + agent discussions
4. Click **"AI Panel"** tab to see 6 agents' analysis / 点击 **"AI 面板"** 标签查看 6 个智能体的分析

---

## 🤖 MiroFish 6-Agent System / MiroFish 六智能体系统

### System Architecture / 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              Data Collection (170+ items)               │
│   Economic | Political | Cultural | Social Media        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           NLP Analysis (Sentiment + Emotions)           │
│   • Sentiment: Positive/Negative/Neutral                │
│   • Emotions: Joy, Anger, Fear, Sadness, Surprise       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         MiroFish Multi-Agent Discussion Engine          │
│   6 Expert Agents → Independent Analysis → Debate       │
│   → Opinion Evolution → Consensus Building              │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Dashboard Display (AI Panel)               │
│   Agent Cards | Consensus | Forecasts | Insights        │
└─────────────────────────────────────────────────────────┘
```

### The 6 Expert Agents / 六个专家智能体

| # | Agent Name | Role | Expertise | Model |
|---|------------|------|-----------|-------|
| 1 | **Dr. Lim Wei Chen**<br>林伟晨博士 | Chief Economist<br>首席经济学家 | Economic growth, inflation, GDP<br>经济增长、通胀、GDP | FinBERT |
| 2 | **Datin Sri Aisha**<br>艾莎拿汀 | Policy Advisor<br>政策顾问 | Governance, public welfare<br>治理、公共福利 | BERT Go Emotions |
| 3 | **Encik Razak**<br>拉扎克先生 | Business Leader<br>商业领袖 | Investment, industry, competitiveness<br>投资、产业、竞争力 | FinBERT |
| 4 | **Dr. Muthu**<br>穆图博士 | Sociologist<br>社会学家 | Social cohesion, cultural identity<br>社会凝聚力、文化认同 | RoBERTa Sentiment |
| 5 | **Ms. Wong Li Ming**<br>黄丽明女士 | IR Expert<br>国际关系专家 | Geopolitics, trade relations<br>地缘政治、贸易关系 | XLM-RoBERTa |
| 6 | **Ahmad bin Hassan**<br>艾哈迈德 | Public Representative<br>公众代表 | Citizen concerns, cost of living<br>民生关切、生活成本 | DistilBERT |

### How the Agents Work / 智能体工作原理

#### Step 1: Independent Analysis / 独立分析

Each agent analyzes the collected data from their expert perspective:
- **Economist**: Examines GDP, exchange rates, KLCI, oil prices
- **Policy Agent**: Reviews government policies and their effectiveness
- **Business Agent**: Assesses investment climate and business confidence
- **Sociologist**: Analyzes social cohesion and cultural factors
- **IR Agent**: Evaluates regional stability and international relations
- **Public Agent**: Represents citizen concerns and ground-level issues

每个智能体从各自专家角度分析采集的数据：
- **经济学家**: 检查 GDP、汇率、KLCI 股指、油价
- **政策智能体**: 审查政府政策及其有效性
- **商业智能体**: 评估投资环境和商业信心
- **社会学家智能体**: 分析社会凝聚力和文化因素
- **国际关系智能体**: 评估区域稳定和国际关系
- **公众智能体**: 代表公民关切和基层问题

#### Step 2: Initial Position Formation / 初始立场形成

Each agent produces:
- **Sentiment Score**: -1.0 (very negative) to +1.0 (very positive)
- **Confidence Level**: 0.0 to 1.0
- **Key Factors**: 3-5 main considerations
- **7-day & 30-day Forecasts**

每个智能体产生：
- **情感得分**: -1.0（非常负面）到 +1.0（非常正面）
- **置信度**: 0.0 到 1.0
- **关键因素**: 3-5 个主要考虑因素
- **7 天和 30 天预测**

#### Step 3: Multi-Round Discussion / 多轮讨论

**MiroFish Opinion Evolution Process:**

1. **Round 1**: Agents share initial positions
2. **Round 2-3**: Agents respond to each other, update opinions
3. **Round 4**: Final consensus building

**Opinion Update Formula:**
```
new_opinion = current_opinion + influence_factor × other_agents_opinions
```

Where `influence_factor = 0.15` (15% influence from other agents per round)

**MiroFish 意见演化过程：**

1. **第 1 轮**: 智能体分享初始立场
2. **第 2-3 轮**: 智能体相互回应，更新观点
3. **第 4 轮**: 最终共识建立

**观点更新公式：**
```
新观点 = 当前观点 + 影响因子 × 其他智能体观点
```

其中 `影响因子 = 0.15`（每轮 15% 来自其他智能体的影响）

#### Step 4: Consensus & Convergence / 共识与收敛

**Consensus Score**: Average of all agents' final sentiments
- **Positive**: > +0.1
- **Neutral**: -0.1 to +0.1
- **Negative**: < -0.1

**Convergence Rate**: How much agents agree (0% to 100%)
- **High (>70%)**: Agents largely agree
- **Medium (40-70%)**: Some disagreement
- **Low (<40%)**: Diverse views

**共识得分**: 所有智能体最终情感的平均值
- **正面**: > +0.1
- **中性**: -0.1 到 +0.1
- **负面**: < -0.1

**收敛率**: 智能体达成一致的程度（0% 到 100%）
- **高 (>70%)**: 智能体基本一致
- **中 (40-70%)**: 存在分歧
- **低 (<40%)**: 观点多样

---

## 📊 Data Sources / 数据来源

### Collection Summary / 采集汇总

| Category | Items | Sources |
|----------|-------|---------|
| 📈 Economic / 经济 | 43 | Exchange rates, KLCI, Oil, World Bank, FRED, News APIs |
| 🏛️ Political / 政治 | 61 | Crawled news, NewsAPI, GNews, RSS |
| 🎭 Cultural / 文化 | 80 | Crawled news, NewsAPI, GNews, RSS |
| **Total / 总计** | **184** | **8+ sources** |

### Malaysian News Crawler / 马来西亚新闻爬虫

**15+ Economic News Sources:**
- The Star Business, NST Business, The Edge Markets
- Free Malaysia Today, Malaysiakini Economy
- Malay Mail Business, Borneo Post Business

**8+ Political News Sources:**
- The Star Politics, NST Politics, Malaysiakini Politics
- Free Malaysia Today Nation, Malay Mail Politics

**7+ Cultural News Sources:**
- The Star Lifestyle, NST Life, Prestige Online
- ExpatGo Malaysia, Malaysian Digest

---

## 🎨 Dashboard Features / 仪表板功能

### 8 Main Tabs / 8 个主要标签

1. **Dashboard** 📊 - Overall sentiment, emotion breakdown, alerts
2. **Economy** 📈 - Economic indicators + business news
3. **Politics** 🏛️ - Political news & analysis
4. **Culture** 🎭 - Cultural news & events
5. **AI Panel** 🤖 - **NEW** 6-agent discussion results
6. **Graph** 🔗 - AI cause-effect relationship map
7. **Chat** 💬 - AI chatbot Q&A
8. **Collection** 📥 - Manual data collection

### AI Panel Tab Features / AI 面板标签功能

- **6 Agent Cards**: Show each agent's sentiment, forecasts, confidence
- **Consensus Visualization**: Display consensus for all 3 topics
- **Convergence Tracking**: Visual progress bars showing agent agreement
- **AI Insights**: Natural language explanation of analysis

**AI 面板标签功能：**
- **6 个智能体卡片**: 显示每个智能体的情感、预测、置信度
- **共识可视化**: 显示 3 个主题的共识
- **收敛追踪**: 可视化进度条显示智能体一致性
- **AI 洞察**: 分析的自然语言解释

---

## 🔧 Technical Details / 技术细节

### System Architecture / 系统架构

```
opinion_sim_system/
├── data_collection/
│   ├── unified_collector.py      # Main data collector
│   ├── malaysia_collector.py     # Malaysian-specific data
│   ├── enhanced_collector.py     # Enhanced APIs
│   └── collector.py              # Standard collectors
├── integration/
│   └── data_adapter.py           # MiroFish integration
├── mirofish/
│   └── discussion.py             # Multi-agent discussion engine
├── agents/
│   └── six_agents.py             # 6 expert agents
├── nlp/
│   └── advanced_analyzer.py      # Sentiment & emotion analysis
├── flask_app.py                  # Main Flask application
└── flask_app/
    ├── templates/
    │   └── index.html            # Dashboard UI
    └── static/
        ├── js/app.js             # Frontend logic
        └── css/style.css         # Styling
```

### API Endpoints / API 端点

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/collect` | POST | Collect data + run NLP + run agents |
| `/api/data` | GET | Get collected data |
| `/api/agents` | GET | Get MiroFish agent results |
| `/api/sentiment` | GET | Get NLP sentiment analysis |
| `/api/graph` | GET | Get cause-effect graph |
| `/api/chat` | POST | Chat with AI |

### Configuration / 配置

Create `.env` file in `opinion_sim_system/`:

```bash
# API Keys (optional)
NEWSAPI_KEY=your_newsapi_key
GNEWS_KEY=your_gnews_key
REDDIT_CLIENT_ID=your_reddit_id
REDDIT_CLIENT_SECRET=your_reddit_secret

# Model Settings
USE_GPU=false
MAX_ITEMS_PER_CATEGORY=100
```

---

## 📈 Sample Output / 示例输出

### Agent Discussion Results / 智能体讨论结果

```
📈 Economic Analysis:
  Final Consensus: +0.42 (Positive / 正面)
  Convergence: 78% (agents largely agree / 智能体基本一致)
  
  Agent Positions / 智能体立场:
  ┌─────────────────────────────────────────────────┐
  │ 👨‍💼 Dr. Lim (Economist)      +0.65  📈 Optimistic │
  │ 👩‍💼 Datin Aisha (Policy)     +0.42  👍 Positive  │
  │ 👨‍💼 Encik Razak (Business)   +0.38  👍 Positive  │
  │ 👨‍🔬 Dr. Muthu (Sociology)    +0.25  🙂 Slight +  │
  │ 👩‍💼 Ms. Wong (IR)            +0.18  🙂 Slight +  │
  │ 👤 Ahmad (Public)             -0.12  😐 Neutral   │
  └─────────────────────────────────────────────────┘
  
  Key Insights / 关键洞察:
  ✓ Economic fundamentals remain strong
  ✓ Inflation concerns moderate
  ✓ Public cost-of-living worries persist
  
  Forecasts / 预测:
  - 7-day:  +0.48 (Improving / 改善)
  - 30-day: +0.55 (Sustained Growth / 持续增长)
```

---

## 🚀 Feature Roadmap / 功能路线图

| Phase | Features | Timeline |
|-------|----------|----------|
| **Phase 1** ✅ | Data Collection, NLP, Dashboard | Complete |
| **Phase 2** ✅ | MiroFish 6-Agent Integration | Complete |
| **Phase 3** 🔄 | Real-Time Alerts, Trend Forecasting | 2-3 weeks |
| **Phase 4** 📋 | Topic Modeling, Report Generator | 3-4 weeks |
| **Phase 5** 💡 | Mobile App, Demographic Analysis | 4-6 weeks |

---

## 📚 Documentation / 文档

- `INTEGRATION_COMPLETE.md` - Data source integration details
- `MIROFISH_INTEGRATION_COMPLETE.md` - MiroFish integration guide
- `FEATURE_SUGGESTIONS_AND_MIROFISH_INTEGRATION.md` - Future features

---

## 👥 Authors / 作者

**CSPOPS Development Team**

- Multi-Agent AI System
- Real-Time Data Collection
- NLP Sentiment Analysis
- Interactive Dashboard

---

## 📄 License / 许可证

**OFFICIAL USE ONLY** - Government Project

---

## 🙏 Acknowledgments / 致谢

- MiroFish opinion evolution methodology
- HuggingFace transformer models
- Malaysian news sources
- Various data APIs

---

## 📞 Support / 支持

For issues or questions:
1. Check documentation files
2. Review error messages
3. Verify API keys in `.env`

---

**Last Updated / 最后更新**: March 2026

**Version / 版本**: 2.0.0

---

---

# 中文版本

## 🇲🇾 CSPOPS - 公民情感与公众舆论感知系统

## 🤖 马来西亚多智能体 AI 讨论系统

---

## 📋 概述

CSPOPS 是一个先进的人工智能舆论监测系统，结合了：
- **实时数据采集** 来自 170+ 来源（新闻、API、网络爬虫）
- **NLP 情感分析** 与情绪检测
- **6 个专家 AI 智能体** 使用 MiroFish 方法讨论和分析问题
- **交互式仪表板** 用于可视化和决策

---

## 🚀 快速开始

### 前置条件

```bash
# 需要 Python 3.10+
python3 --version

# 安装依赖
pip install -r opinion_sim_system/pyproject.toml
```

### 运行应用

```bash
# 启动 Flask 服务器
python3 -m opinion_sim_system.flask_app

# 打开浏览器访问：http://localhost:5000
```

### 采集数据并运行智能体

1. 点击 **"数据采集"** 标签
2. 点击 **"采集实时数据"** 按钮
3. 等待 60-90 秒完成采集 + NLP 分析 + 智能体讨论
4. 点击 **"AI 面板"** 标签查看 6 个智能体的分析结果

---

## 🤖 MiroFish 六智能体系统

### 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              数据采集 (170+ 条数据)                       │
│   经济 | 政治 | 文化 | 社交媒体                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│           NLP 分析 (情感 + 情绪)                          │
│   • 情感：正面/负面/中性                                 │
│   • 情绪：喜悦、愤怒、恐惧、悲伤、惊讶                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         MiroFish 多智能体讨论引擎                         │
│   6 个专家智能体 → 独立分析 → 辩论                       │
│   → 意见演化 → 共识建立                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              仪表板显示 (AI 面板)                          │
│   智能体卡片 | 共识 | 预测 | 洞察                        │
└─────────────────────────────────────────────────────────┘
```

### 六个专家智能体

| # | 智能体名称 | 角色 | 专业领域 | 模型 |
|---|------------|------|-----------|-------|
| 1 | **林伟晨博士** | 首席经济学家 | 经济增长、通胀、GDP | FinBERT |
| 2 | **艾莎拿汀** | 政策顾问 | 治理、公共福利 | BERT 情绪 |
| 3 | **拉扎克先生** | 商业领袖 | 投资、产业、竞争力 | FinBERT |
| 4 | **穆图博士** | 社会学家 | 社会凝聚力、文化认同 | RoBERTa |
| 5 | **黄丽明女士** | 国际关系专家 | 地缘政治、贸易关系 | XLM-RoBERTa |
| 6 | **艾哈迈德** | 公众代表 | 民生关切、生活成本 | DistilBERT |

### 智能体工作原理

#### 第一步：独立分析

每个智能体从各自专家角度分析采集的数据：
- **经济学家**: 检查 GDP、汇率、KLCI 股指、油价
- **政策智能体**: 审查政府政策及其有效性
- **商业智能体**: 评估投资环境和商业信心
- **社会学家智能体**: 分析社会凝聚力和文化因素
- **国际关系智能体**: 评估区域稳定和国际关系
- **公众智能体**: 代表公民关切和基层问题

#### 第二步：初始立场形成

每个智能体产生：
- **情感得分**: -1.0（非常负面）到 +1.0（非常正面）
- **置信度**: 0.0 到 1.0
- **关键因素**: 3-5 个主要考虑因素
- **7 天和 30 天预测**

#### 第三步：多轮讨论

**MiroFish 意见演化过程：**

1. **第 1 轮**: 智能体分享初始立场
2. **第 2-3 轮**: 智能体相互回应，更新观点
3. **第 4 轮**: 最终共识建立

**观点更新公式：**
```
新观点 = 当前观点 + 影响因子 × 其他智能体观点
```

其中 `影响因子 = 0.15`（每轮 15% 来自其他智能体的影响）

#### 第四步：共识与收敛

**共识得分**: 所有智能体最终情感的平均值
- **正面**: > +0.1
- **中性**: -0.1 到 +0.1
- **负面**: < -0.1

**收敛率**: 智能体达成一致的程度（0% 到 100%）
- **高 (>70%)**: 智能体基本一致
- **中 (40-70%)**: 存在分歧
- **低 (<40%)**: 观点多样

---

## 📊 数据来源

### 采集汇总

| 类别 | 项目数 | 来源 |
|------|--------|------|
| 📈 经济 | 43 | 汇率、KLCI、石油、世界银行、FRED、新闻 API |
| 🏛️ 政治 | 61 | 爬取新闻、NewsAPI、GNews、RSS |
| 🎭 文化 | 80 | 爬取新闻、NewsAPI、GNews、RSS |
| **总计** | **184** | **8+ 来源** |

### 马来西亚新闻爬虫

**15+ 经济新闻来源:**
- 星报商业、新海峡时报商业、边缘市场
- 自由马来西亚今日、当今大马经济
- 马来邮报商业、婆罗洲邮报商业

**8+ 政治新闻来源:**
- 星报政治、新海峡时报政治、当今大马政治
- 自由马来西亚今日国民、马来邮报政治

**7+ 文化新闻来源:**
- 星报生活、新海峡时报生活、Prestige Online
- ExpatGo 马来西亚、马来西亚摘要

---

## 🎨 仪表板功能

### 8 个主要标签

1. **仪表板** 📊 - 整体情感、情绪分解、警报
2. **经济** 📈 - 经济指标 + 商业新闻
3. **政治** 🏛️ - 政治新闻与分析
4. **文化** 🎭 - 文化新闻与活动
5. **AI 面板** 🤖 - **新增** 6 智能体讨论结果
6. **图谱** 🔗 - AI 因果关系图谱
7. **聊天** 💬 - AI 聊天机器人问答
8. **采集** 📥 - 手动数据采集

### AI 面板标签功能

- **6 个智能体卡片**: 显示每个智能体的情感、预测、置信度
- **共识可视化**: 显示 3 个主题的共识
- **收敛追踪**: 可视化进度条显示智能体一致性
- **AI 洞察**: 分析的自然语言解释

---

## 🔧 技术细节

### 系统架构

```
opinion_sim_system/
├── data_collection/
│   ├── unified_collector.py      # 主数据采集器
│   ├── malaysia_collector.py     # 马来西亚特定数据
│   ├── enhanced_collector.py     # 增强 API
│   └── collector.py              # 标准采集器
├── integration/
│   └── data_adapter.py           # MiroFish 集成
├── mirofish/
│   └── discussion.py             # 多智能体讨论引擎
├── agents/
│   └── six_agents.py             # 6 个专家智能体
├── nlp/
│   └── advanced_analyzer.py      # 情感与情绪分析
├── flask_app.py                  # 主 Flask 应用
└── flask_app/
    ├── templates/
    │   └── index.html            # 仪表板 UI
    └── static/
        ├── js/app.js             # 前端逻辑
        └── css/style.css         # 样式
```

### API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/collect` | POST | 采集数据 + 运行 NLP + 运行智能体 |
| `/api/data` | GET | 获取采集的数据 |
| `/api/agents` | GET | 获取 MiroFish 智能体结果 |
| `/api/sentiment` | GET | 获取 NLP 情感分析 |
| `/api/graph` | GET | 获取因果图谱 |
| `/api/chat` | POST | 与 AI 聊天 |

### 配置

在 `opinion_sim_system/` 中创建 `.env` 文件：

```bash
# API 密钥（可选）
NEWSAPI_KEY=你的 newsapi 密钥
GNEWS_KEY=你的 gnews 密钥
REDDIT_CLIENT_ID=你的 reddit ID
REDDIT_CLIENT_SECRET=你的 reddit 密钥

# 模型设置
USE_GPU=false
MAX_ITEMS_PER_CATEGORY=100
```

---

## 📈 示例输出

### 智能体讨论结果

```
📈 经济分析:
  最终共识：+0.42 (正面)
  收敛率：78% (智能体基本一致)
  
  智能体立场:
  ┌─────────────────────────────────────────────────┐
  │ 👨‍💼 林博士 (经济学家)      +0.65  📈 乐观      │
  │ 👩‍💼 艾莎 (政策顾问)       +0.42  👍 正面      │
  │ 👨‍💼 拉扎克 (商业领袖)     +0.38  👍 正面      │
  │ 👨‍🔬 穆图 (社会学家)       +0.25  🙂 略正面    │
  │ 👩‍💼 黄女士 (国际关系)     +0.18  🙂 略正面    │
  │ 👤 艾哈迈德 (公众代表)     -0.12  😐 中性      │
  └─────────────────────────────────────────────────┘
  
  关键洞察:
  ✓ 经济基本面保持强劲
  ✓ 通胀担忧缓和
  ✓ 公众生活成本担忧持续
  
  预测:
  - 7 天：  +0.48 (改善)
  - 30 天： +0.55 (持续增长)
```

---

## 🚀 功能路线图

| 阶段 | 功能 | 时间线 |
|------|------|--------|
| **第一阶段** ✅ | 数据采集、NLP、仪表板 | 完成 |
| **第二阶段** ✅ | MiroFish 六智能体集成 | 完成 |
| **第三阶段** 🔄 | 实时警报、趋势预测 | 2-3 周 |
| **第四阶段** 📋 | 主题建模、报告生成器 | 3-4 周 |
| **第五阶段** 💡 | 移动应用、人口统计分析 | 4-6 周 |

---

## 📚 文档

- `INTEGRATION_COMPLETE.md` - 数据源集成详情
- `MIROFISH_INTEGRATION_COMPLETE.md` - MiroFish 集成指南
- `FEATURE_SUGGESTIONS_AND_MIROFISH_INTEGRATION.md` - 未来功能

---

## 👥 作者

**CSPOPS 开发团队**

- 多智能体 AI 系统
- 实时数据采集
- NLP 情感分析
- 交互式仪表板

---

## 📄 许可证

**仅供官方使用** - 政府项目

---

## 🙏 致谢

- MiroFish 意见演化方法
- HuggingFace 变换器模型
- 马来西亚新闻来源
- 各种数据 API

---

## 📞 支持

如有问题或疑问：
1. 查看文档文件
2. 检查错误消息
3. 验证 `.env` 中的 API 密钥

---

**最后更新**: 2026 年 3 月

**版本**: 2.0.0
