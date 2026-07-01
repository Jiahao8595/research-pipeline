# zotero-management

Zotero 文献库管理工具。双层访问：MCP 做 item 级操作，REST API 做 collection 级操作。

## 这是什么

用 Hermes Agent 管理 Zotero 文献库——创建/移动 collection、批量分类、导入文献。不需要打开 Zotero 客户端。

## 前置条件

- Zotero 运行中（本地或 Web）
- 在 Zotero 设置中生成 API key
- 配置 `~/.hermes/config.yaml` 中的 `mcp_servers.zotero.env`

## 安装

```bash
git clone https://github.com/Jiahao8595/research-pipeline.git
cp -r research-pipeline/zotero-management ~/.hermes/skills/
```

安装后 `/reload-skills`。

## 使用示例

```
"帮我把最近推送的 5 篇氯盐论文导入 Zotero，分类到 corrosion 子库"
"整理一下 Zotero 里的重复条目"
"列出我 Zotero 库中 2024 年以后发的论文"
```

## 与 literature-pipeline 的衔接

文献推送产出精选论文 → zotero-management 一键导入 → 长期文献库管理。

## 文件结构

```
zotero-management/
├── SKILL.md                   ← 技能入口
└── scripts/
    └── batch-classify.py      ← 批量分类脚本
```

## 作者

十五 (JL Lab)
