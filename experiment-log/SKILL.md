---
name: experiment-log
description: "标准化实验日志记录——接收原始材料（图/语音/文字），产出带 YAML frontmatter 的标准日志到本地 vault。需配合飞书 CLI 使用。"
version: 1.0.0
author: 十五
license: MIT
metadata:
  hermes:
    tags: [research, experiment, logging, feishu, automation]
    related_skills: [feishu-cli-integration, obsidian]
---

# experiment-log — 实验日志标准化

## 触发条件

用户通过以下任一方式提交实验原始材料时自动加载：

- **路径 A** — CLI 直接提交（图片 / 语音转录 / 文字）
- **路径 B** — 发到飞书科研群，通过 `feishu-cli-integration` 扫描

## 前置依赖

需要配合 `feishu-cli-integration` skill 使用。确保：
- 飞书 bot 已添加到目标群
- bot 权限：`im:message` + `im:resource` + `im:message.group_msg`
- 群 ID 配置在 skill 上下文中

## 处理流程

1. 接收材料 → vision_analyze 读图 + 提取结构化信息
2. 生成实验 ID + 样品批次 ID
3. 写出标准日志到 `wiki/实验日志/{体系}/{类型}/{exp_id}.md`
4. 原始材料（图片等）归档到 `raw/experiments/YYYY.MM.DD_描述_EXPID/`
5. 日志末尾加「原始材料」段落，引用 raw 路径
6. 检查异常 → 有则追加 `异常记录.md`
7. 追加操作记录到日志索引
8. 告知用户写入位置

模糊信息（温度记不清、样品编号不明）主动询问，不猜测写入。

## 目录结构

```
/vault/
├── raw/experiments/                       ← 原始层（归档）
│   └── YYYY.MM.DD_描述_EXPID/
│       ├── 笔记.md
│       ├── 图片/
│       └── 语音/
│
wiki/实验日志/                              ← 标准层（产出）
├── 实验索引.md
├── 异常记录.md
├── {体系A}/
│   ├── 实验类型1/
│   ├── 实验类型2/
│   └── ...
├── {体系B}/
│   └── ...
└── 公共/
    └── 设备与试剂追踪.md
```

## 实验 ID 规则

```
{体系代码}-{设备代码}-YYMMDD-{序号}
  │        │       │       └─ 当日序号（001 起）
  │        │       └─ 日期
  │        └─ 设备代码（M=马弗炉, T=管式炉, E=电化学, G=手套箱, F=可控气氛炉, B=通用）
  └─ 体系代码（自定义，如 CL / NO / OX / HY 等）
```

## 样品批次 ID 规则

```
{体系代码}-{候选编号}-B{序号}
  │        │         └─ 配盐批次序号
  │        └─ 候选配方编号
  └─ 体系代码
```

同一批样品跨多个实验时 `sample_batch` 保持一致，便于 dataview 追踪。

## 设备代码

| 代码 | 设备 | 场景 |
|------|------|------|
| M | 马弗炉 | 热处理、浸泡腐蚀 |
| T | 管式炉 | 气氛控制、脱水、热稳定性 |
| E | 电化学工作站 | CV/SWV/EIS |
| G | 手套箱 | 配盐、称量、取样 |
| F | 可控气氛炉 | 精密气氛控制 |
| B | 通用 | 干燥、清洗、制样 |

按实际设备扩展。

## 标准日志模板

所有日志使用 YAML frontmatter + Markdown 正文。模板分两部分：

1. **YAML 头部** — 结构化数据，dataview 可查询
2. **正文** — 自由文本：实验目的、操作步骤、观察、结果、异常

具体模板见 `references/example-log.md`，包含一个通用腐蚀实验的完整示例。

## 飞书 CLI 操作要点

路径 B 使用 `feishu-cli-integration` skill：

- 拉消息：`lark-cli im +chat-messages-list --chat-id oc_*** --page-size 30 --sort asc`
- 下载图片：`lark-cli im +messages-resources-download --message-id *** --file-key *** --type image --output <相对路径>`
- ⚠️ `--output` 只接受相对路径，先 `cd` 到 `raw/experiments/` 归档目录

群 ID 和 bot 权限按 `feishu-cli-integration` skill 的配置获取。

## 自定义指南

- **体系代码**：按你的实验体系自定义（如 CL/NO/OR/PO）
- **实验类型**：在 `wiki/实验日志/{体系}/` 下按需创建子目录
- **YAML 字段**：模板是建议结构，可增删字段
- **设备代码**：按实际实验室设备扩展

## 相关文件

| 文件 | 用途 |
|------|------|
| `references/example-log.md` | 完整实验日志示例 |
| `wiki/实验日志/实验索引.md` | Dataview 仪表盘 |
| `wiki/实验日志/异常记录.md` | 异常记录格式 |
| `wiki/实验日志/公共/设备与试剂追踪.md` | 设备、试剂追踪 |
