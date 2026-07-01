# Hermes Public Skills

四个开源科研 skill，覆盖学术工作的完整链路——从"谁在做"到"发什么"到"怎么写"。

```
学术侦察              文献发现                文献管理              写作输出
academic-research ──→ literature-pipeline ──→ zotero-management
  -recon                    │                        │
                       wenxian-tuisong               │
                       （日常 cron 推送）              │
                                                      ▼
                                                researchwrite
                                                （proposal / 论文）
```

---

## 安装

```bash
# 全部五个
hermes skills install https://raw.githubusercontent.com/Jiahao8595/hermes-public-skills/main/academic-research-recon/SKILL.md
hermes skills install https://raw.githubusercontent.com/Jiahao8595/hermes-public-skills/main/literature-pipeline/SKILL.md
hermes skills install https://raw.githubusercontent.com/Jiahao8595/hermes-public-skills/main/wenxian-tuisong/SKILL.md
hermes skills install https://raw.githubusercontent.com/Jiahao8595/hermes-public-skills/main/zotero-management/SKILL.md
hermes skills install https://raw.githubusercontent.com/Jiahao8595/hermes-public-skills/main/researchwrite/SKILL.md
```

或克隆整个 repo 到 `~/.hermes/skills/research/`，然后 `/reload-skills`。

**建议同时安装的前置依赖：**

```bash
hermes skills install brainstorming      # researchwrite 入口追问
hermes skills install professor         # 动态专家审查
hermes skills install avoid-ai-writing  # 英文去 AI 味
hermes skills install arxiv             # arXiv 检索
hermes skills install pdf               # PDF 全文处理
hermes skills install docx              # Word 文档导出
hermes skills install obsidian          # 笔记管理
```

---

## 技能详解

### 1. academic-research-recon — 学术侦察

**定位：了解领域里谁在做、做了什么、跟谁合作、什么来头。**

基于 OpenAlex、ORCID、DOI 元数据、Crossref 等学术索引，生成研究者画像：机构轨迹、发表主题、合作网络、学术谱系。

**使用场景：**
- 查一个教授/导师/潜在合作者的背景
- 追踪某人的机构变迁（如"他是不是从 MIT 转到 Stanford 的"）
- 了解一个 lab 的研究方向和影响力
- 查审稿人/委员会成员

**示例：**
```
"帮我查一下 XXX 教授的研究背景和主要合作者"
"这个人是不是做钙钛矿的？他跟 Oxford/EPFL 什么关系"
```

---

### 2. literature-pipeline — 管线引擎

**定位：文献管线的底层框架。定义检索→筛选→评分→分类→归档的完整逻辑。**

wenxian-tuisong 的上层驱动引擎。包含六维评分体系、批量分类规则、笔记模板、gap analysis 方法论、推送格式规范。

**使用场景：**
- 搭建新的文献管线（任何领域）
- 定制评分权重和分类体系
- 设计文献笔记模板
- gap analysis：梳理领域研究空白

**核心文件：**
| 文件 | 内容 |
|------|------|
| `references/_index.md` | 管线总览 |
| `references/bulk-classification.md` | 批量分类策略 |
| `references/gap-analysis.md` | 文献 gap 分析方法 |
| `references/note-template.md` | 文献笔记标准模板 |
| `references/push-format.md` | 推送格式规范 |
| `references/review-compilation-workflow.md` | reviews文献汇编工作流 |

---

### 3. wenxian-tuisong — 每日文献推送

**定位：面向日常使用的文献推送应用层。配好关键词就能跑。**

基于 literature-pipeline 的完整管线实现。多源检索 → 六维粗筛 → 精选精读 → 飞书/Telegram 推送 → 归档。支持 cron 每日自动运行。

**管线架构：**
```
多源检索 (30 篇候选)
  OpenAlex / arXiv / Crossref / Semantic Scholar（自动降级）
       ↓
六维粗筛 (30 → 5 篇)
  方向匹配 35 + 方法价值 20 + 期刊质量 15 + 网络关联 10 + 工程价值 10 + 归档价值 10
       ↓
精选精读 (top 5)
  标注来源级别：Full-text / Abstract only / Metadata only
       ↓
推送
  🏅 排名 | 标题 | 期刊 | ⭐ 评分 | 💡 一句话 | 🔬 方法 | 📊 结果 | 🧭 点评
       ↓
归档
  DOI/arXiv 去重 → 笔记 → 索引
```

**首次配置：**
```
我的研究领域是骨代谢，关键词：bone metabolism, osteoblast,
osteoporosis, orthopedic implant, osseointegration,
文献推送到飞书群 oc_xxx，归档到 ~/research/literature/
```

**内置保护：** 评分校验防越界、三重去重、数据源自动降级、只写文献库不改知识库。

---

### 4. zotero-management — 文献库管理

**定位：Zotero 文献库的组织和维护。分类、移动、批处理。**

双层访问：MCP 做 item 级操作（搜索/元数据/全文），REST API 做 collection 级操作（创建/移动/批处理）。

**使用场景：**
- 把文献推送的精选论文自动导入 Zotero
- 按主题/项目重新组织文献库
- 批量标记和移动论文
- 清理重复条目

**与 literature-pipeline 的衔接：** 文献推送产出精选论文 → zotero-management 导入 Zotero → 长期文献库管理。

---

### 5. researchwrite — 科研写作 Pipeline

**定位：Proposal-first 写作状态机。从模糊想法到可投稿文本。**

三模式（compose / revise / hybrid）+ 四层 QA pipeline（专家审查 → 去 AI 味 → 格式校验 → 分维度打分）。强制执行论证架构，写完自动跑质量闸门。

**核心原则：**
| # | 原则 |
|---|------|
| 1 | 证据先于文字 — 先建 evidence_table 再写 |
| 2 | 论证先于章节 — 先画 argument_map 再落笔 |
| 3 | 契约先于段落 — 每节有 purpose / allowed / forbidden |
| 4 | 动态专家 — 按失败模式召唤对应审查专家 |
| 5 | 内容先于语言 — 科学逻辑诊断在语言打磨之前 |
| 6 | 删除胜于解释 — 不可行的主张直接删，不解释 |
| 7 | 该停就停 — 平台期/证据缺失是停止理由 |

**四层 QA Pipeline：**
```
Gate 2: professor 专家审查（方法论+领域/可行性+创新性）
  ↓
Gate 1: avoid-ai-writing 语言检查（仅英文）
  ↓
Gate 3: 自动校验（citation? 可复现? 编号连续?）
  ↓
Gate 4: 评分阈值（≥7.0 通过，<7.0 定向回退 ≤3 轮）
```

**四挡位：** `paper` / `proposal` / `internal` / `quick`

---

## 完整工作流

这四个 skill 不是孤立的——它们是一条链：

```
"这个领域谁在做？"
  academic-research-recon
       │  了解人物、机构、谱系
       ▼
"每天有什么新进展？"
  literature-pipeline（引擎）
  wenxian-tuisong（应用）
       │  每日检索→筛选→推送→归档
       ▼
"怎么管理这些论文？"
  zotero-management
       │  分类、导入、长期维护
       ▼
"怎么写出来？"
  researchwrite
       │  evidence_table 引用积累的锚点论文
       │  compose/revise/hybrid → QA pipeline
       ▼
    投稿 / 答辩
```

---

## 常见问题

**Q: 我的领域不是材料/化学，能用吗？**

全部通用。每个 skill 的关键词、分类规则、推送目标都可配置。医学、生物、CS、社科——换关键词就行。

**Q: 需要什么模型？**

推荐 DeepSeek V3/V4 或 Claude 3.5。每日文献推送 cron 可用 flash 模型降成本。

**Q: 和 Zotero 原生客户端冲突吗？**

不冲突。zotero-management 通过 API 操作同一份数据。

**Q: 四个必须全装吗？**

不需要。每个独立可用：
- 只要推送 → wenxian-tuisong（自动加载 literature-pipeline）
- 只要写作 → researchwrite
- 只查学者 → academic-research-recon

---

## 许可

Apache 2.0 License. PR welcome.

## 作者

十五 + JL，基于 Hermes Agent 生态构建。原创 skill，非第三方拉取。
