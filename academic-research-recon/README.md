# academic-research-recon

学者与机构背景调查工具。基于 OpenAlex、ORCID、DOI 元数据、Crossref 等学术索引，追踪研究者、导师、实验室和学术谱系。

## 这是什么

不是简单的"搜这个人发了什么论文"——它构建研究者的完整画像：机构轨迹、发表主题、合作网络、学术谱系。

## 安装

```bash
git clone https://github.com/Jiahao8595/research-pipeline.git
cp -r research-pipeline/academic-research-recon ~/.hermes/skills/
```

安装后 `/reload-skills`。

## 使用示例

```
"帮我查一下 XXX 教授的研究背景和主要合作者"
"这个人是不是做钙钛矿的？他跟 Oxford/EPFL 什么关系"
"追踪一下这个 lab 的发表轨迹，过去五年方向有没有变化"
```

## 数据源

- OpenAlex — 期刊论文、引用数、作者机构
- ORCID — 研究者身份确认
- Crossref — DOI 元数据
- 中文搜索配合百度学术/CNKI

## 文件结构

```
academic-research-recon/
├── SKILL.md                                          ← 技能入口
└── references/
    └── chinese-institutional-collaboration-search.md ← 中文机构合作搜索方法
```

## 作者

十五 (JL Lab)
