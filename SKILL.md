---
name: text-to-illustrated-pdf
description: 智能文字配图 → PDF 生成工具。LLM 分析文本，Tavily 搜索作品图，Creaa AI 生成场景图
user-invocable: true
homepage: https://[skill homepage]
---
metadata: {"openclaw":{"requires":{"env":["CREAA_API_KEY","TAVILY_API_KEY"]},"primaryEnv":"CREAA_API_KEY"}}

# 智能文字配图 → PDF 生成工具

基于 LLM 的智能配图系统，通过语义分析自动为文本添加配图，生成图文并茂的 PDF 文档。

## ⚠️ 核心约束（必须遵守）

### 1. LLM扮演一位风光摄影大师，能感知文字所表达的图片信息，对"比例"，"情绪"，"色彩"，"氛围"等有敏锐的感知力

### 2. 配图数量要求【硬性标准】

#### A.目标要求
- 配图点定义：文本中适合插入图片的具体位置，通常是具有以下特征之一的内容：
   - 包含视觉描述元素（场景、物体、光影、构图等）
   - 能够通过图片增强读者理解或表达效果
   - 具备独立的叙事或说明价值
- 硬性要求：每个文字文件必须识别出不少于 17 个配图点
- 配图要求：每个配图点应插入1-2 张图片，最终图片总数不少于 20 张
- 判断示例：
   - ✓ 是配图点："海面上一根木桩，四周是雾蒙蒙的水和天"（有画面感）
   - ✓ 是配图点："蒙德里安的色块绘画"（有艺术家信息，可搜索）
   - ✗ 非配图点："色调其实是后期后期风格中最容易被识别的一部分"（纯理论）
- **以上对于配图点数量和图片数量的了求是最低硬性门槛，不是建议值，也不是参考值**

#### B.执行规则
- 在完成全文分析后，必须对当前文件进行配图点统计。
- 如果识别出的配图点 少于 15 个，不得进入下一步，必须继续重新审视全文，补充挖掘更多适合配图的位置。
- 重新分析时，应主动从以下角度继续寻找配图机会，包括但不限于：
   - 场景描写
   - 人物/角色出场
   - 动作或事件节点
   - 地点转换
   - 物品、工具、设备、食物、服饰等具象名词
   - 情绪变化或氛围强化点
   - 抽象概念可视化
   - 流程、步骤、结构、对比关系
   - 数据、案例、结果展示点

#### C.配图生成要求
- 每个已识别的配图点，都应对应多张候选图片，用于搜索、筛选或生成。
- 不允许出现"只为少数几个点配图，其余内容不处理"的情况。
- 配图工作必须覆盖已识别出的全部配图点。

#### D.过程控制要求
- 执行过程中必须实时计数当前已识别的配图点数量。
- 在配图点总数 未达到 17 个之前，持续分析，不得视为完成。
- 只有当配图点数量达到或超过 17 个后，才可进入后续图片搜索、生成、筛选或排版流程。

#### E.质量底线
- 不允许为了凑数而重复标记相邻、同质、无明显区别的内容作为多个配图点。
- 所有配图点都必须具有明确的配图价值，能够对应相对独立的视觉表达目标。
- 在满足数量要求的同时，必须保证配图点具备多样性、代表性和实际可用性。

### 3. 配图点识别范围
LLM 必须在以下所有类型的内容中识别配图需求：

#### A. 明确视觉内容（优先）
- 艺术家/摄影师姓名及其作品
- 具体的场景、物体、画面描述
- 构图、光影、色彩、角度等摄影技法描述

#### B. 视觉比喻和类比
- "像...一样"（如"像丝绸一样的水面"）
- 比喻性描述（如"时间像一个滤网"）
- 视觉化的抽象概念（如"视觉上的张力"）

#### C. 对比性内容
- 前后对比（"拍之前"vs"拍之后"）
- 正反对比（"极简"vs"繁杂"）
- 效果对比（"高饱和"vs"低饱和"）

#### D. 情绪和氛围
- 明显的情绪描述（"孤独"、"宁静"、"压抑"）
- 氛围描述（"电影感"、"复古"、"现代"）
- 情绪密度相关描述

#### E. 视觉过程和路径
- 视觉观看路径描述（"先看到...再看到..."）
- 构图过程描述（"主体放在什么位置"）
- 观察方法描述

#### F. 练习和案例
- 练习方法中的场景描述
- 案例分析的配图机会
- 方法论中的可视化内容

### 4. 配图密度检查
- 在分析文本时：
   - 密度目标：每扫描 200-300 字，应至少识别出 1-2 个配图点
   - 强制重新分析：如果某段文字超过 200 字且无配图，必须重新审视
   - 例外情况：以下内容可以不配图，但配图不足时需重新评估：
      - 纯定义性内容（如"极简主义是指..."）
      - 代码或技术参数列表
      - 简短的过渡性语句（少于 50 字）

### 5. 实时计数要求
- 在执行过程中：
   1.初始化两个计数器：
      - 配图点计数器 = 0（跟踪识别的配图位置数量）
      - 图片计数器 = 0（跟踪已生成的图片数量）
   2.每识别一个配图点，配图点计数器 +1
   2.每生成/搜索一张图，图片计数器 +1
   2.配图点识别阶段：
      - 当 配图点计数器 < 17：继续分析文本
      - 当 配图点计数器 >= 17：进入图片生成阶段
      - 建议继续寻找，目标 17-20 个配图点
   4.图片生成阶段：
      - 每个配图点应生成 1-2 张图片
      - 确保 图片计数器 >= 20

### 6. 配图不足时的补救措施
- 如果配图点数量不足（<17）：
   - 回顾所有"不配图"的判断，重新评估
   - 对抽象概念进行视觉化处理
   - 对理论讲解添加示意图或案例图
   - 在关键概念处添加图示（用生成或搜索）
   - **绝对不能**以"文本没有画面感"为由跳过配图

## 系统架构

### 四层架构设计

```
┌─────────────────────────────────────────────────────────┐
│                        用户命令                         │
│              "大力，用 [模型] 处理配图Task"               │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                    LLM（大脑层）                          │
│  1. 调用 polling.py 获取待处理任务队列                   │
│  2. 【LLM 直接分析文本，识别配图需求】                     │
│     - 识别艺术家/摄影师 → Tavily 搜索                     │
│     - 识别场景描述 → Creaa AI 生成                       │
│     - 识别作品名称 → Tavily 搜索                         │
│  3. 组织 Markdown 文档，插入图片                          │
│  4. 调用 save.py 保存为 PDF                              │
│  5. 汇报处理结果，继续下一任务                            │
└─────────────────────────────────────────────────────────┘
                           ↓              ↓              ↓
                    ┌──────────┐    ┌──────────────┐    ┌─────────────┐
                    │polling.py│    │  save.py     │    │realtime_save│
                    └──────────┘    └──────────────┘    └─────────────┘
                    任务轮询器        结果保存器      实时图片保存器
```

### 核心组件

#### 1. polling.py（任务轮询器）

**功能**：
- 扫描 `Tasks/` 目录中的所有 `.txt` 文件
- 检查 `Results/` 目录中是否有同名的 `.pdf` 文件
- 返回所有未处理任务的队列

**输出格式**：
```json
{
  "status": "pending",
  "count": 9,
  "tasks": [
    {"filename": "任务1", "content": "文本内容..."},
    {"filename": "任务2", "content": "文本内容..."}
  ]
}
```

**调用方式**：
```bash
python3 polling.py
```

#### 2. save.py（结果保存器）

**功能**：
- 接收 Markdown 内容和文件名
- 保存中间 Markdown 到 `temp/` 目录
- 使用 `pandoc` 转换 Markdown → HTML
- 使用 `weasyprint` 生成 PDF
- 保存到 `Results/` 目录
- **注意**：不再负责图片下载、复制、批量保存、单张保存（这些工作由 realtime_save.py 完成）

**调用方式**：
```bash
python3 save.py --filename "任务名" --stdin < markdown.md
```

**输出格式**：
```json
{
  "success": true,
  "message": "PDF已成功保存到 ...",
  "pdf_path": "/path/to/file.pdf",
  "markdown_path": "temp/任务名.md"
}
```

#### 3. realtime_save.py（实时图片保存包装器）

**功能**：
- 在每次获取图片URL后，立即下载并保存到本地
- 在 `Results/` 目录下创建与原文字文件同名的文件夹
- 支持单张图片保存（按序号命名）
- 由 LLM 在每张图片获取后立即调用

**调用方式**：
```bash
python3 realtime_save.py --filename "任务名" --image-url "图片URL" --image-index 0
```

**可选参数**：
- `--image-index`：图片序号（用于生成文件名，如 `image_0.jpg`）
- `--timeout`：超时时间（默认120秒）

**输出格式**：
```json
{
  "success": true,
  "message": "图片已保存到 ...",
  "local_path": "Results/任务名/image_0.jpg",
  "url": "https://..."
}
```

**保存位置**：`Results/[任务名]/image_0.jpg, image_1.jpg, ...`

#### 4. tavily_search.py（Tavily 搜索模块）

**功能**：
- 使用 Tavily API 搜索图片
- 支持关键词查询
- 返回图片 URL、标题、来源

**调用方式**：
```bash
python3 tavily_search.py <搜索关键词>
```

**输出格式**：
```json
{
  "url": "https://...",
  "title": "图片描述",
  "source": "tavily"
}
```

#### 5. creaa_ai.py（Creaa AI 生图模块）

**功能**：
- 使用 Creaa Open API 生成图片
- 支持自定义提示词与模型
- 支持轮询任务状态并返回结果图片 URL
- 可选将生成结果下载到本地

**调用方式**：
```bash
python3 creaa_ai.py <提示词> --model <模型名>
```

**输出格式**：
```json
{
   "success": true,
   "model": "seedream-5.0",
   "prompt": "...",
   "task_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
   "status": "completed",
   "result_url": "https://...",
   "download": {
      "success": true,
      "path": "temp/cat.jpg"
   }
}
```

#### 6. LLM（智能分析层）【核心】

**职责**：
- **文本语义分析**：识别需要配图的文字
- **配图决策**：判断是搜索还是生成
- **API 调用**：协调 Tavily 和 Creaa AI
- **文档组织**：将图片插入到正确的位置
- **流程控制**：循环处理所有任务

**💡 重要说明**：
- **配图分析完全由 Agent LLM 完成**
- **不使用任何子脚本进行文本分析**
- **LLM 通过语义理解判断配图需求**
- **避免硬编码关键词匹配的局限性**

## 配图分析逻辑

### LLM 分析原则

当分析文本时，LLM 需要判断以下情况：

#### 1. 搜索模式（Tavily）

**触发条件**：
1. 文中明确提及艺术家/摄影师姓名
   - 例如："Saul Leiter"、"Michael Kenna"、"William Eggleston"、"何藩"、"Gregory Crewdson"

2. 文中提及具体作品名称
   - 例如："《红色天花板》"、"《春树奇峰》"、"Pier, Calais, France"


**搜索策略**：
- 关键词：艺术家姓名 + 作品名称（如有）
- 搜索数量：2-3 张
- 图片选择：优先选择权威来源

#### 2. 生成模式（Creaa AI）

**触发条件**：
1. 纯场景描述
   - 例如："海面上一根木桩，四周是雾蒙蒙的水和天"

2. 视觉画面描述
   - 例如："瀑布、水流、草地以及远处的山坡"

3. 提及抽象氛围或情绪
   - 例如："宁静的午后"、"孤独的背影"、"电影氛围"

4. 光影/构图/色彩描述
   - 例如："强烈的光影对比"、"色彩非常柔和"、"视觉中心不够明确"

**降级机制**：
- 如果 Tavily 搜索失败（找不到图片）
- 自动降级为 Creaa AI 生成
- 在结果中记录降级次数

#### 3. 慎重判断（非强制不配图）
**以下情况可以先标记为"不配图"，但在配图不足时需重新评估**：

1. 纯理论讲解
   - 首选：尝试视觉化表达（概念图、示意图）
   - 备选：搜索相关艺术作品作为类比
   - 例外：如果是纯粹的列表或定义，可以不配图

2. 逻辑分析/步骤说明
   - 首选：为每个步骤配一张示意图
   - 备选：使用对比图展示"前后变化"
   - 示例："建立光影关系"可以配"光线对比图"

3. 标题和小标题
   - 一般不配图，避免杂乱
   - 例外：如果标题本身就是视觉概念（"极简"、"留白"），可以考虑配图

4. **配图不足的强制措施**：
   - 当配图总数 < 15 时，**必须重新审查所有"不配图"的标记**
   - 将可视觉化的理论、步骤配图
   - 添加概念图、对比图、示意图

## 工作流程

### 完整处理流程

```
1. 用户发送命令
   "大力，用 seedream-5.0 处理配图Task"

2. LLM 调用 polling.py
   → 获取待处理任务队列

3. 循环处理每个任务：
   ├─ 读取文本内容
   ├─ 【LLM 智能分析】识别配图需求
   │   ├─ 分语句处理文本
   │   ├─ 对每语句进行语义判断
   │   └─ 决定配图策略（搜索/生成/无配图）
   ├─ 对每个需要配图的语句：
   │   ├─ 搜索模式 → 调用 tavily_search.py
   │   ├─ 生成模式 → 调用 creaa_ai.py
   │   ├─ 搜索失败则降级为生成
   │   └─ **获取图片URL后，立即调用 realtime_save.py 保存**
   ├─ 组织完整 Markdown 文档
   │   └─ **中间文件保存**：Markdown 文件保存到 `temp/` 目录
   ├─ 调用 save.py 转换 Markdown 为 PDF
   └─ 汇报处理结果：
       ├─ 总配图数
       ├─ 搜索获取数
       ├─ AI 生成数
       └─ 搜索降级为生成数

4. 继续处理下一个任务，直到全部完成
```

### LLM 分析示例

**输入文本**：
```
Saul Leiter（索尔·莱特）的摄影作品有一个非常明显的特征：色彩非常柔和，而且经常带有一种偏暖的复古色调。
```

**LLM 分析过程**：
1. 检测到艺术家：Saul Leiter
2. 检测到风格描述：色彩柔和、复古色调
3. 决策：搜索模式（搜索 Saul Leiter 的典型作品）
4. 搜索关键词："Saul Leiter photography retro color"
5. **执行搜索**：`python3 tavily_search.py "Saul Leiter photography retro color"`
6. **立即保存图片**：`python3 realtime_save.py --filename "任务名" --image-url "图片URL" --image-index 0`

**Markdown 输出**：
```markdown
Saul Leiter（索尔·莱特）的摄影作品有一个非常明显的特征：色彩非常柔和，而且经常带有一种偏暖的复古色调。

![Saul Leiter 作品](https://.../image1.jpg)
![Saul Leiter 作品](https://.../image2.jpg)
```

---

**输入文本**：
```
这是一张风光照片，画面里有瀑布、水流、草地以及远处的山坡。
```

**LLM 分析过程**：
1. 检测到场景描述：瀑布、水流、草地、山坡
2.无艺术家/作品信息
3. 决策：生成模式
4. 生成提示词："瀑布、水流、草地以及远处的山坡，风光摄影"
5. **执行生成**：`python3 creaa_ai.py "瀑布、水流、草地以及远处的山坡，风光摄影" --model seedream-5.0`
6. **立即保存图片**：`python3 realtime_save.py --filename "任务名" --image-url "图片URL" --image-index 1`

**Markdown 输出**：
```markdown
这是一张风光照片，画面里有瀑布、水流、草地以及远处的山坡。

![瀑布风光](https://.../generated.jpg)
```

## 使用方法

### 批量处理（推荐）

**命令格式**：
```
大力，用 [模型] 处理配图Task
大力，用 seedream-5.0 处理配图Task
大力，用 nano-banana-2 处理配图Task
```

**示例**：
```
大力，用 seedream-5.0 处理配图Task
```

**处理过程**：
```
扫描到 9 个待处理任务

[1/9] 处理: 小品摄影.txt
✓ 成功 | 搜索 2 张，生成 1 张，降级 1 张
→ Results/小品摄影.pdf

[2/9] 处理: 极简.txt
✓ 成功 | 搜索 3 张，生成 0 张，降级 1 张
→ Results/极简.pdf
注意：第 1 张图因搜索失败而降级为 AI 生成

[3/9] 处理: 画意.txt
✓ 成功 | 搜索 1 张，生成 2 张，降级 0 张
→ Results/画意.pdf

... (继续处理剩余任务)

全部完成！共处理 9 个文件
```

### 文件结构

```
text-to-illustrated-pdf/
├── Tasks/              # 待处理任务（放入 .txt 文件）
├── Results/            # 生成的 PDF 和图片
│   ├── [文件名].pdf
│   └── [文件名]/      # 同名文件夹，保存所有配图
├── temp/               # 中间 Markdown 文件
└── scripts/            # 核心脚本
    ├── polling.py
    ├── save.py
    ├── realtime_save.py
    ├── tavily_search.py
    └── creaa_ai.py
│   └── ...
├── temp/               # 中间文件
│   ├── 小品摄影.md     # Markdown 格式的中间文件
│   ├── 极简.md
│   └── ...
└── error_log.txt        # 错误日志
```

## 图片生成模型

| 模型 | 说明 | 免费额度 | 推荐场景 |
|------|------|----------|----------|
| `z-image-turbo` | 免费，最快 | 无限制 | 快速预览、测试 |
| `seedream-5.0` | 高质量 | 每天10张 | 封面、重要配图 |
| `nano-banana-2` | 多图编辑 | 每天5张 | 复杂场景 |
| `nano-banana-pro` | 专业级 | 每天1张 | 最高质量输出 |

## 处理结果反馈

每个文件处理完成后，LLM 会口头汇报：

```
✓ [文件名] 处理完成

插入图片：5 张
  - 搜索获取：3 张
  - AI 生成：1 张
  - 搜索降级为生成：1 张

PDF 路径：Results/[文件名].pdf
中间文件：temp/[文件名].md
图片文件夹：Results/[文件名]/
```

如果有降级情况，会特别提示：
```
注意：第 1、3 张图因搜索失败而降级为 AI 生成
```

### 输出文件说明

| 文件类型 | 保存位置 | 说明 |
|---------|----------|------|
| PDF 文件 | `Results/[文件名].pdf` | 最终图文并茂的 PDF 文档 |
| 中间 Markdown | `temp/[文件名].md` | 包含配图 URL 的 Markdown 源码 |
| 配图文件夹 | `Results/[文件名]/` | 所有配图的本地副本 |
| 错误日志 | `error_log.txt` | 记录所有操作错误信息 |

## Markdown 组织规则

### 文本保留

- 保持原文的原始格式
- 标题、段落、列表结构不变
- 不对原文进行修改

### 中间文件保存

**重要说明：**
- 技能处理过程中生成的 Markdown 格式文件会自动保存到 `temp/` 目录
- 文件名与原始任务文件名一致（例如：`极简.md`）
- 这些中间文件可用于调试、复用或查看 Markdown 源码
- Markdown 文件包含完整的文本内容和配图 URL

**保存位置：** `temp/`（技能根目录下）

**示例：**
```
temp/
├── 极简.md
├── 小品摄影.md
└── 画意.md
```

### 图片插入

- 插入位置：对应场景描述文字的下方
- 插入格式：标准 Markdown 图片语法
- 多张图片：按顺序排列

**示例**：
```markdown
## 一、极简主义作品

Michael Kenna 的作品以简洁著称，他拍摄的《Pier, Calais, France》展示了海面上一根孤零零的木桩，四周是雾蒙蒙的水和天。

![Michael Kenna《Pier, Calais, France》](images/pier-1.jpg)
![Michael Kenna《Pier, Calais, France》](images/pier-2.jpg)

### 1. 结构与比例

海面上一根木桩，四周是雾蒙蒙的水和天，远处隐约可见山影。

![极简风光](images/minimal-1.jpg)
```

## PDF 转换

### 转换流程

```
Markdown → Pandoc → HTML → WeasyPrint → PDF
```

### 样式设计

- **`字体`**：Microsoft YaHei / SimHei / Arial
- **页面宽度**：最大 800px，居中
- **图片样式**：
  - 最大宽度：100%
  - 自动高度
  - 圆角：5px
  - 阴影效果
  - 上下边距：20px
- **标题样式**：
  - H1：底部 2px 边框，内边距 10px
  - H2-H6：上边距 30px，下边距 15px
- **段落样式**：
  - 行高：1.6
  - 文本对齐：justify
- **代码样式**：
  - 背景色：#f4f4f4
  - 内边距：2px 5px
  - 圆角：3px
  - 等宽字体

## 错误处理

### 错误类型

1. **配图失败**
   - 记录错误日志
   - 继续处理下一任务
   - 在结果中说明失败原因

2. **PDF 转换失败**
   - 记录错误日志
   - 继续处理下一任务
   - 保留生成的 Markdown 文件供排查

3. **API 调用失败**
   - 搜索失败：自动降级为生成
   - 生成失败：跳过该图片，继续处理
   - 记录错误日志

### 错误日志

日志位置：`error_log.txt`（技能根目录下）

日志格式：
```
[2026-03-18 23:15:30] 任务 小品摄影: Tavily 搜索失败 - The Red Ceiling
[2026-03-18 23:16:45] 任务 极简: PDF 转换失败 - weasyprint error
```

## 依赖安装

系统依赖：
```bash
sudo apt-get install weasyprint pandoc
```

Python 依赖：
```bash
# weasyprint 已通过系统包管理器安装
# 如果需要 Python 版本：
pip install markdown
```

## 环境变量配置

```bash
export CREAA_API_KEY=your_creaa_api_key
export TAVILY_API_KEY=your_tavily_api_key
```

## 注意事项

1. **API 密钥**：确保两个 API 密钥都已正确配置
2. **网络连接**：搜索和生图都需要稳定的网络连接
3. **中文编码**：输入文本应为 UTF-8 编码
4. **磁盘空间**：确保有足够的磁盘空间存储 PDF

## 技术细节

### polling.py 关键逻辑

```python
def get_pending_tasks():
    # 获取已完成的任务（Results中的pdf文件名）
    completed_files = set(pdf_filename in RESULTS_DIR)

    # 扫描Tasks目录
    pending_tasks = []
    for file in os.listdir(TASKS_DIR):
        if file.endswith('.txt'):
            filename = file[:-4]  # 去掉.txt
            if filename not in completed_files:
                # 读取文件内容
                content = read_file(file)
                pending_tasks.append({
                    "filename": filename,
                    "content": content
                })

    return pending_tasks
```

### save.py 关键逻辑

```python
def save_pdf(filename, markdown_content):
    # 转换为HTML
    html_content = pandoc_convert(markdown_content)

    # 生成PDF
    pdf_path = os.path.join(RESULTS_DIR, f"{filename}.pdf")
    weasyprint.HTML(string=html_content).write_pdf(pdf_path)

    return {"success": True, "pdf_path": pdf_path}
```

### realtime_save.py 关键逻辑

```python
def save_image_immediately(filename, image_url, index=None):
    # 在 Results/ 下创建同名文件夹
    image_dir = os.path.join(RESULTS_DIR, filename)
    os.makedirs(image_dir, exist_ok=True)

    # 下载图片并按序号命名
    local_filename = f"image_{index}.jpg" if index is not None else "image.jpg"
    local_path = os.path.join(image_dir, local_filename)

    # 下载图片
    download_image(image_url, local_path)

    return {"success": True, "local_path": local_path}
```

### LLM 配图分析逻辑（Agent 内置）

```
1. 分段处理文本
2. 对每段进行语义分析：
   ├─ 提取关键实体（艺术家、作品）
   ├─ 识别场景描述（画面、光影、构图）
   ├─ 判断是否为纯理论/步骤说明
   └─ 决定配图策略：
       ├─ 有艺术家/作品 → Tavily 搜索
       ├─ 有场景描述 → Creaa AI 生成
       └─ 无画面感 → 不配图
3. 执行配图，获取图片URL
4. **立即调用 realtime_save.py 保存图片**
5. 插入到对应段落下方
```

## 示例输出

### 示例 1：搜索模式

**输入文本**：
```
Saul Leiter 的作品以色彩柔和著称，他的摄影作品经常带有一种偏暖的复古色调。
```

**LLM 分析**：
- 检测到艺术家：Saul Leiter
- 检测到风格特征：色彩柔和、复古色调
- 决策：Tavily 搜索

**执行配图**：
```bash
# 1. 搜索图片
python3 tavily_search.py "Saul Leiter photography retro color soft"

# 2. 立即保存图片（假设搜索返回了2张图片URL）
python3 realtime_save.py --filename "任务名" --image-url "https://.../image1.jpg" --image-index 0
python3 realtime_save.py --filename "任务名" --image-url "https://.../image2.jpg" --image-index 1
```

**Markdown 输出**：
```markdown
Saul Leiter 的作品以色彩柔和著称，他的摄影作品经常带有一种偏暖的复古色调。

![Saul Leiter 作品](https://.../image1.jpg)
![Saul Leiter 作品](https://.../image2.jpg)
```

### 示例 2：生成模式

**输入文本**：
```
这是一张风光照片，画面里有瀑布、水流、草地以及远处的山坡。
```

**LLM 分析**：
- 检测到场景描述：瀑布、水流、草地、山坡
- 无艺术家/作品信息
- 决策：Creaa AI 生成

**执行配图**：
```bash
# 1. 生成图片
python3 creaa_ai.py "瀑布、水流、草地以及远处的山坡，风光摄影" --model seedream-5.0

# 2. 立即保存图片
python3 realtime_save.py --filename "任务名" --image-url "https://.../generated.jpg" --image-index 2
```

**Markdown 输出**：
```markdown
这是一张风光照片，画面里有瀑布、水流、草地以及远处的山坡。

![瀑布风光](https://.../generated.jpg)
```

### 示例 3：无配图

**输入文本**：
```
色调其实是后期后期风格中最容易被识别的一部分。
```

**LLM 分析**：
- 纯理论讲解
- 无画面感
- 决策：不配图

**Markdown 输出**：
```markdown
色调其实是后期后期风格中最容易被识别的一部分。
```

## 版本历史

### v4.0（当前版本）
- **新增 realtime_save.py**：实时图片保存包装器
- **重构图片保存逻辑**：从 save.py 分离，每张图片获取后立即保存
- **save.py 简化**：只负责 Markdown → PDF 转换，不再处理图片
- **优化工作流**：LLM 在每张图片获取后立即调用 realtime_save.py

### v3.0
- **移除 image_analyzer.py**（硬编码规则引擎）
- **移除 llm_analyzer.py**（子脚本调用）
- **LLM 配图分析完全由 Agent 内置完成**
- 提升语义理解能力，支持任意艺术家和场景描述

### v2.0
- 重构架构：三层设计（polling.py + save.py + LLM）
- 改进配图决策：基于语义分析
- 新增降级机制：搜索失败自动降级为生成
- 优化文件结构：独立 Tasks/ 和 Results/ 目录

### v1.0（已废弃）
- 单脚本处理
- 规则引擎匹配
- 文件输出到工作空间根目录
