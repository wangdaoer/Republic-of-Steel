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
- 独立文学复审、作者验收与后续影响追踪

所有AI修改都必须遵循 [AGENTS.md](AGENTS.md)，并以 `canon/` 中的正式设定为最高优先级。
已接入的小说创作运行层见 [小说创作接入说明](docs/novel-skill-integration.md)，逐章复审可从 [文学审稿模板](prompts/literary-review.md) 开始。

## 当前状态

- Version：`SR-V1.4`
- 阶段：四卷正文与全部240章首轮文学精修已完成，Canon与卷级台账已同步。
- 正文规模：240章（第一卷120章、第二卷40章、第三卷40章、第四卷40章）。
- 第一卷《废铁营》：001—120，`DRAFT / POLISH_PASS_1 / FINAL_REVIEW_REQUIRED`。
- 第二卷《守住北线》：001—040，`DRAFT / POLISH_PASS_1 / FINAL_REVIEW_REQUIRED`。
- 第三卷《第一座工厂》：001—040，`DRAFT / POLISH_PASS_1 / FINAL_REVIEW_REQUIRED`。
- 第四卷《星海拓荒》：001—040，`COMPLETE / STRUCTURAL_REVIEW / POLISH_PASS_1 / FINAL_REVIEW_REQUIRED`。
- 总体状态：`COMPLETE / POLISH_PASS_1 / FINAL_REVIEW_REQUIRED`；全书结构验收通过，下一阶段为卷级独立回读、全书终稿复审与发布前校验。
- GitHub远程仓库：[wangdaoer/Republic-of-Steel](https://github.com/wangdaoer/Republic-of-Steel)，默认分支 `main`

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
- [文学审稿模板](prompts/literary-review.md)
- [小说创作接入说明](docs/novel-skill-integration.md)
- [第一卷生产数据库](novel/volume01-waste-iron-camp/README.md)
- [第二卷生产数据库](novel/volume02-north-line/README.md)
- [第三卷生产数据库](novel/volume03-first-factory/README.md)
- [第四卷生产数据库](novel/volume04-star-exploration/README.md)

## 状态约定

- `CANON`：作者确认的正式设定
- `OUTLINE`：已确认的计划义务，不等于事件已经发生
- `DRAFT`：待审草案
- `PROPOSAL`：候选方案
- `TBD`：需要作者决策
- `ACCEPTED`：正文已验收，可回写状态台账
- `COMPLETE`：规划范围内的正文与结构资产已完成
