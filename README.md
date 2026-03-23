# text-to-illustrated-pdf

智能文字配图 → PDF 生成工具。LLM 分析文本，Tavily 搜索作品图，Creaa AI 生成场景图，生成图文并茂的 PDF 文档。

---

## ⚠️ 前置依赖

本技能依赖以下 OpenClaw Skills，请先安装：

### 1. Tavily Search Skill

用于搜索图片（艺术家、作品等）。

- **安装地址**：https://clawhub.ai/Jacky1n7/openclaw-tavily-search
- **作用**：搜索网络图片，识别摄影作品、艺术家作品

### 2. Creaa AI Skill

用于 AI 生成图片（场景、氛围等）。

- **安装地址**：请查看 [Creaa AI 使用指南](https://creaa.ai/blog/openclaw-skill)
- **作用**：调用 Creaa 平台生成图片
- **注意**：Creaa 是第三方平台，需要**充值积分**才能使用生图功能
- **更多信息**：https://creaa.ai/blog/openclaw-skill 包含：
  - Creaa AI Skill 安装地址
  - API Key 获取方式
  - 充值入口
  - 收费标准说明

---

## 环境配置

### 1. 安装系统依赖

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install -y weasyprint pandoc

# macOS
brew install weasyprint pandoc
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

```bash
# Creaa AI API 密钥（必需）
# 获取方式：https://creaa.ai 注册账号并充值积分
export CREAA_API_KEY=your_creaa_api_key

# Tavily API 密钥（必需）
# 获取方式：在 tavily-search skill 中配置
export TAVILY_API_KEY=your_tavily_api_key

# 可选：自定义工作目录（默认使用脚本所在目录）
export TEXT_TO_PDF_DIR=/path/to/workspace
```

---

## 快速开始

### 基本用法

```bash
# 轮询任务
python3 scripts/polling.py

# 保存 PDF（从 stdin 读取 Markdown）
python3 scripts/save.py --filename "任务名" < input.md

# 实时保存图片
python3 scripts/realtime_save.py --filename "任务名" --image-url "https://example.com/image.jpg" --image-index 0

# 搜索图片
python3 scripts/tavily_search.py "搜索关键词"

# AI 生成图片
python3 scripts/creaa_ai.py "生成提示词" --model seedream-5.0
```

---

## 目录结构

```
text-to-illustrated-pdf/
├── Tasks/              # 待处理任务（.txt 文件）
├── Results/            # 生成的 PDF 和图片
├── temp/               # 中间 Markdown 文件
├── scripts/            # 核心脚本
│   ├── polling.py      # 任务轮询器
│   ├── save.py         # PDF 保存器
│   ├── realtime_save.py # 实时图片保存
│   ├── tavily_search.py # 图片搜索
│   └── creaa_ai.py     # AI 生图
├── error_log.txt       # 错误日志
├── requirements.txt    # Python 依赖
└── README.md
```

---

## 使用流程

1. 将待处理的文本文件（.txt）放入 `Tasks/` 目录
2. 运行 `python3 scripts/polling.py` 获取任务队列
3. LLM 分析文本，识别配图需求
4. 根据需求调用 Tavily 搜索或 Creaa AI 生成
5. 调用 `save.py` 生成 PDF

---

## 生图模型（Creaa 平台）

| 模型 | 说明 | 免费额度 |
|------|------|----------|
| `z-image-turbo` | 免费，最快 | 无限制 |
| `seedream-5.0` | 高质量 | 每天10张 |
| `nano-banana-2` | 多图编辑 | 每天5张 |
| `nano-banana-pro` | 专业级 | 每天1张 |

> ⚠️ 以上免费额度基于 Creaa 平台活动，可能有变化。请以 [Creaa 官网](https://creaa.ai) 实时数据为准。

---

## 配图分析逻辑

### 搜索模式（ Tavily）

触发条件：
- 文中明确提及艺术家/摄影师姓名（如 Saul Leiter、Michael Kenna）
- 文中提及具体作品名称

### 生成模式（Creaa AI）

触发条件：
- 纯场景描述（如"海面上一根木桩，四周是雾蒙蒙的水和天"）
- 视觉画面描述
- 抽象氛围或情绪描述
- 光影/构图/色彩描述

### 降级机制

如果 Tavily 搜索失败，自动降级为 Creaa AI 生成。

---

## 示例

### 搜索图片
```bash
python3 scripts/tavily_search.py "Saul Leiter photography"
```

### 生成图片
```bash
python3 scripts/creaa_ai.py "瀑布、水流、草地以及远处的山坡，风光摄影" --model seedream-5.0
```

### 保存 PDF
```bash
python3 scripts/save.py --filename "极简" < temp/极简.md
```

---

## 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `CREAA_API_KEY` | Creaa AI API 密钥 | ✅ 是 |
| `TAVILY_API_KEY` | Tavily API 密钥 | ✅ 是 |
| `TEXT_TO_PDF_DIR` | 工作目录 | ❌ 否 |

---

## 错误处理

所有错误会记录到 `error_log.txt`，包括：
- 任务轮询失败
- 图片搜索/生成失败
- PDF 转换失败

---

## 相关链接

- **Tavily Search Skill**: https://clawhub.ai/Jacky1n7/openclaw-tavily-search
- **Creaa AI 官网**: https://creaa.ai
- **Creaa AI 完整指南**（含安装地址、充值入口、收费标准）: https://creaa.ai/blog/openclaw-skill
