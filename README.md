# 《钢铁共和国》
# Steel Republic

> 一个关于文明如何创造、承担和修复自己的科幻史诗。

## 项目简介

《钢铁共和国》是一部长篇科幻文明史诗。

故事从一台废弃机甲404开始，经过：

废铁营时代 → 拓荒者时代 → 工业智能时代 → 星海文明时代。

最终探索：文明为什么存在，以及文明如何在损坏之后继续前进。

## 核心主题

### 创造

谁有资格创造未来？

### 责任

谁承担创造后的影响？

### 修复

文明如何面对自己的错误？

### 连接

不同存在如何共同成长？

## 四卷结构

### Volume 01：《废铁营》

主题：创造力量。

### Volume 02：《守住北线》

主题：维护文明。

### Volume 03：《第一座工厂》

主题：定义未来。

### Volume 04：《星海拓荒》

主题：探索文明。

## 项目组成

- **Canon**：世界观、时间线、人物、科技、势力与术语数据库
- **Novel**：正式小说正文与卷级生产资料
- **Assets**：人物、机甲、星球、地图与封面视觉资产
- **Prompts**：章节写作、人物检查与世界观检查模板
- **Tools**：一致性、时间线与元数据校验工具
- **Docs**：项目计划、开发日志与流程文档

## 项目结构

```text
steel-republic-project/
├── README.md
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── canon/
│   ├── world/
│   ├── timeline/
│   ├── characters/
│   ├── technology/
│   ├── factions/
│   └── lore/
├── novel/
│   ├── volume01-waste-iron-camp/
│   ├── volume02-north-line/
│   ├── volume03-first-factory/
│   └── volume04-star-exploration/
├── assets/
│   ├── characters/
│   ├── mechs/
│   ├── planets/
│   ├── maps/
│   └── covers/
├── prompts/
├── tools/
│   ├── consistency-check/
│   └── timeline-check/
├── docs/
└── .github/
    └── ISSUE_TEMPLATE/
```

## AI协作

本项目面向 Codex、ChatGPT 与 GitHub Actions 设计，可用于：

- 世界观检查
- 人物一致性检查
- 时间线检查
- 章节规划与正文辅助
- 长篇创作状态追踪

所有AI修改都必须遵循 [AGENTS.md](AGENTS.md)，并以 `canon/` 中的正式设定为最高优先级。

## 当前状态

- Version：`SR-V1.0`
- 阶段：世界观数据库完成，GitHub/Codex 工程骨架初始化完成
- 正文状态：第一卷正文尚未迁移到本工程库
- GitHub远程仓库：尚未创建

### Canon入口

- [宇宙设定总纲](canon/world/universe.md)
- [百万年历史时间线](canon/timeline/master-timeline.md)
- [人物数据库](canon/characters/README.md)
- [科技数据库](canon/technology/README.md)
- [文明与势力档案](canon/factions/civilizations.md)
- [世界观名词百科](canon/lore/glossary.md)

### 开发入口

- [项目计划](docs/project-plan.md)
- [开发日志](docs/development-log.md)
- [章节写作模板](prompts/chapter-writing.md)
- [人物一致性检查模板](prompts/character-check.md)
- [世界观检查模板](prompts/lore-check.md)
- [第一卷生产数据库](novel/volume01-waste-iron-camp/README.md)

## 状态约定

- `CANON`：作者确认的正式设定
- `OUTLINE`：已确认的计划义务，不等于事件已经发生
- `DRAFT`：待审草案
- `PROPOSAL`：候选方案
- `TBD`：需要作者决策
- `ACCEPTED`：正文已验收，可回写状态台账
