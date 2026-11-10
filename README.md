# 个人账号升级 · Cheat on Content

一套运行在 **Codex / Claude Code** 中的内容创作与账号运营技能包。通过持续记录选题、稿件评分、发布前预测和发布后数据，帮助创作者判断哪些内容有效，并逐步调整适合自己账号的评分规则。

豆包工作用户可下载 [可导入技能包](https://github.com/wangge666666/cheat-on-content-doubao/blob/main/packages/cheat-on-content-doubao.zip)，并按 [豆包工作接入说明](integrations/doubao-work/README.md) 配置。源码保留原版功能，新增的接入层位于 `integrations/doubao-work/`。

核心流程：

```text
了解账号 / 导入对标 → 讨论选题 → 写稿与评分 → 发布前预测
                                              ↓
调整评分规则 / 更新受众画像 ← 对照数据复盘 ← 拍摄与发布登记
```

本目录保存的是技能说明、安装脚本、模板和数据采集适配器。日常使用时，由 AI 助手读取这些规则，在单独的内容项目中维护你的账号资料和创作记录。当前目录尚未包含初始化后的账号状态文件 `.cheat-state.json`。

## 适合做什么

- **建立账号资料**：记录内容形态、发布节奏、历史内容和对标账号。
- **讨论选题与起草**：围绕你的主题、经历或观察提炼角度，默认一次讨论一个选题；也可以显式要求批量处理。
- **评估稿件**：按当前 rubric（评分规则）逐项打分，并说明依据。
- **留下发布前判断**：记录预期表现、判断依据和风险，等数据出来后对照。
- **管理创作节奏**：区分“已拍未发”和“已发布”，查看库存、候选选题和待复盘内容。
- **复盘与积累经验**：结合运营数据和评论，分析预测偏差，沉淀写作结构与受众画像。
- **校准评分规则**：用历史样本检验新规则，也可以只调整表现区间（bucket）的边界。

流程可用于视频、长文、短文、播客和教程等内容。仓库提供相应的起始评分模板；其中多数是未经你本人账号数据验证的初始规则，需要通过实际发布和复盘校准。

## 快速开始

**豆包工作接入**：新增独立接入包，完整保留原有 15 个子技能与配套资源。构建、导入、模型通道配置及运行限制见 [豆包工作接入说明](integrations/doubao-work/README.md)。豆包版通过专用脚本保护预测写入，不能将其等同于 Claude Code 的全局 hooks；模型 API 和平台登录仍需在实际运行环境配置。

### 1. 安装技能

在本项目根目录运行与你使用的助手对应的命令：

```bash
# Codex
bash install.sh --codex

# Claude Code（默认目标）
bash install.sh

# 两个助手都安装
bash install.sh --all
```

安装脚本包含 **15 个子技能**，其中 `cheat-score-blind` 是内部隔离评分技能。Claude Code 安装到 `~/.claude/skills/`；Codex 安装到 `~/.codex/skills/`，并额外安装总入口 `cheat-on-content`。

默认采用软链接，源码目录需要保留在原位置；更新源码后，链接所指向的技能内容随之更新。如果希望使用安装时的固定副本：

```bash
bash install.sh --codex --copy
# 或 bash install.sh --all --copy
```

副本模式需要重新执行安装命令才能同步后续修改。安装技能不会自动安装平台采集依赖，也不会自动创建你的账号内容项目。Codex 当前会话未识别到新技能时，重新打开会话。

### 2. 创建账号内容目录

建议每个账号使用独立目录，保存各自的稿件、评分规则、登录态和复盘数据。例如：

```bash
mkdir -p "$HOME/Documents/我的内容账号"
cd "$HOME/Documents/我的内容账号"
```

在这个目录中打开 Codex 或 Claude Code，然后发送：

```text
初始化 cheat-on-content
```

助手会逐项了解内容类型、历史发布情况、发布节奏、数据收集方式和对标账号，并创建工作文件。已有历史作品时，可以按引导导入；还未发布过内容，也可以从初始规则开始。

### 3. 完成第一条内容的闭环

以下内容是发给 AI 助手的消息，示例路径应替换为你实际生成的文件路径：

```text
我想做一条关于「第一次用 AI 做客户项目踩过的坑」的内容
打分这篇 scripts/你的稿件.md
启动预测 scripts/你的稿件.md
拍了 scripts/你的稿件.md
已发布，链接是：你的作品链接
复盘 videos/对应作品目录/
状态
```

先确认最终稿并写预测，再拍摄、发布，最后到约定时间复盘。默认复盘窗口为发布后 **3 天**；教程等依赖长尾流量的内容，应按内容特点调整观察窗口。

`已发布` 用于登记你已经发布的作品。实际拍摄、剪辑和向平台发布由你完成。

## 日常指令

Codex 中可以直接使用自然语言触发；Claude Code 中也可以使用对应的 `/cheat-*` 命令。具体参数见各技能文件。

| 你可以说 | 对应技能 | 用途 |
|---|---|---|
| 初始化 cheat-on-content | `cheat-init` | 创建账号工作目录与初始配置 |
| 学这个账号 / 导入对标账号 | `cheat-learn-from` | 整理对标稿件、数据与可借鉴的结构 |
| 我想做一条关于……的内容 / 找选题 | `cheat-seed` | 讨论角度并起草，默认一次一个 |
| 打分这篇 scripts/稿件.md | `cheat-score` | 查看评分，不写预测日志 |
| 启动预测 scripts/稿件.md | `cheat-predict` | 保存发布前预测与决策依据 |
| 拍了 scripts/稿件.md | `cheat-shoot` | 登记拍摄，记录实际稿与草稿的差异，增加待发库存 |
| 已发布，链接是…… | `cheat-publish` | 登记链接、平台 ID 和时间，更新待发库存 |
| 复盘 videos/作品目录/ | `cheat-retro` | 收集数据，对照预测并记录观察 |
| 我的观众是谁 / 更新受众画像 | `cheat-persona` | 从复盘评论整理受众特征 |
| 升级 rubric / 调整权重 | `cheat-bump` | 提议并检验评分规则变更 |
| 重校桶 / cheat-bump --bucket-only | `cheat-bump` | 仅重新校准表现区间边界 |
| 推荐选题 | `cheat-recommend` | 对已有候选池排序并解释推荐依据 |
| 抓热点 / 今天有什么可做的 | `cheat-trends` | 从已配置的数据源补充候选选题 |
| 状态 / 看板 | `cheat-status` | 查看库存、校准进度和待复盘事项 |
| 迁移 / 升级 state | `cheat-migrate` | 将旧内容项目升级到当前状态结构 |

`cheat-score-blind` 由评分、预测和规则升级流程内部调用，不作为日常聊天入口。

## 账号资料如何保存

初始化后的内容项目与本技能源码目录分开。以下是主要文件及其用途，部分文件会在使用对应功能后创建：

```text
我的内容账号/
├── .cheat-state.json       # 配置、计数、发布记录和待办状态
├── .gitignore             # 排除登录态、凭证与缓存
├── rubric_notes.md        # 当前评分公式和通用维度定义
├── rubric-memo.md         # 规则升级记录、实绩证据与派生依据
├── script_patterns.md     # 可复用的写作结构
├── benchmark.md           # 对标账号资料（启用对标时）
├── audience.md            # 受众画像
├── candidates.md          # 候选选题池
├── WORKFLOW.md            # 工作流程
├── STATUS.md              # 状态看板
├── scripts/               # 草稿与发布前稿件
├── predictions/           # 预测日志，复盘追加在对应文件中
├── videos/                # 每条作品的实际稿件与数据报告
│   └── 日期_ID_短标题/
│       ├── script.md
│       └── report.md
├── samples/               # 对标账号的转录和资料
├── .cheat-hooks/           # 启用 Claude Code hooks 时复制的脚本
├── .claude/settings.json  # Claude Code hook 注册配置
├── .cheat-cache/           # 缓存与部分适配器的调试产物
└── content.db             # 可选 SQLite 数据文件
```

稿件、预测和作品目录使用同一组“日期、ID、短标题”关联。即使内容形式是文章，当前流程也沿用 `videos/` 这个目录名。

`rubric_notes.md` 只保存用于评分的通用规则；包含具体实绩的证据放在 `rubric-memo.md`。受众画像保存在 `audience.md`，可用于选题和写作，隔离评分流程禁止读取它，以降低事后数据对评分的影响。

## 数据采集与可选依赖

可以先用人工录入数据完成闭环，再按需启用适配器。各适配器有自己的依赖文件和说明，安装技能时不会自动安装这些依赖。

| 平台 / 功能 | 实现目录与说明 | 当前实现方式 |
|---|---|---|
| 抖音 | [douyin-session](adapters/perf-data/douyin-session/README.md) | Playwright 登录态，采集作品数据和评论 |
| 小红书 | [xhs-explore](adapters/perf-data/xhs-explore/README.md) | 创作者中心数据与前台采集；提供公开页补全、正文图片归档和账号汇总 |
| B站 | [bilibili-stat](adapters/perf-data/bilibili-stat/README.md) | 通过公开接口读取视频统计和热门评论，使用 `httpx` |
| LinkedIn | [linkedin-session](adapters/perf-data/linkedin-session/README.md) | 通过登录后的浏览器页面读取本人单帖分析数据 |
| 微信视频号 | [wechat-channels](adapters/perf-data/wechat-channels/README.md) | 从本人视频号助手后台采集作品指标和评论 |
| 视频 / 音频转录 | [whisper](adapters/script-extraction/whisper/README.md) | 本地 `whisper-cpp` 或 `openai-whisper`，配合 FFmpeg |

浏览器采集通常需要 **Python 3.10+、Playwright、Chromium 和有效登录态**。以抖音为例，先在内容项目中创建环境，再安装对应依赖；`CHEAT_SOURCE` 应指向保留的完整技能源码目录：

```bash
# 此示例对应当前本地项目位置；移动源码后需修改
CHEAT_SOURCE="/Users/wang/Desktop/个人账号升级"

cd "$HOME/Documents/我的内容账号"
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r "$CHEAT_SOURCE/adapters/perf-data/douyin-session/requirements.txt"
python -m playwright install chromium
python "$CHEAT_SOURCE/adapters/perf-data/douyin-session/crawler.py" login
```

热点数据源的接入说明位于 [adapters/trend-sources/](adapters/trend-sources/)，包括 aihot、TrendRadar MCP、微博和知乎。实际调用取决于内容项目启用的数据源及外部服务是否已配置；无法使用时可以粘贴链接或标题作为素材。

`humanizer` 是起草流程可选的外部技能，本仓库未打包；未安装时会跳过对应润色步骤。

## 预测与复盘的约定

1. **先预测，再看本条作品的数据。** 已经看过播放、互动或评论的作品，应标记为历史重建分析，不能当作新的盲预测样本。
2. **保留原判断。** 已写入的预测段不事后改成“更准确”的版本；实绩、偏差和修正说明追加在复盘部分。需要重做时保留原记录，按协议另建版本。
3. **新规则要经过历史样本检验。** 完整评分规则升级需要对校准池重新隔离评分、检查排序一致性，并默认进行跨模型审核；通过后由用户确认落地。只调整 bucket 边界走单独的轻量流程。
4. **把观察转成可用规则。** 已被推翻或已吸收进正式规则的临时观察应及时清理，历史过程保存在版本记录和升级档案中。

Claude Code 启用 hooks 后，可在指定的 `Edit` / `Write` 工具调用中拦截预测段修改，并在会话开始时报告状态。相关脚本依赖 Bash、`jq` 等工具。这些 Claude Code hooks 在 Codex 中不会自动运行；使用 Codex 时主动发送 `状态` 查看进度，并遵守相同的记录约定。

完整约定见 [盲预测协议](shared-references/blind-prediction-protocol.md)、[规则升级验证协议](shared-references/bump-validation-protocol.md) 和 [状态管理](shared-references/state-management.md)。

## 源码目录

```text
个人账号升级/
├── SKILL.md                # 总协议与技能路由
├── README.md               # 本文档
├── CHANGELOG.md            # 变更记录
├── install.sh              # 技能安装与 hook 脚本刷新
├── uninstall.sh            # 卸载全局技能
├── skills/                 # 15 个子技能的工作流说明
├── shared-references/      # 评分、预测、节奏与状态等共享协议
├── starter-rubrics/        # 各内容形态的初始评分规则
├── templates/              # 内容项目的文件模板与 SQLite schema
├── adapters/               # 运营数据、热点和转录适配器
├── hooks/                  # Claude Code 钩子配置与脚本
├── migrations/             # 状态结构版本与迁移步骤
├── tools/                  # 稿件差异计算、误差曲线等工具
├── examples/               # 写作结构示例
└── docs/                   # 原有中文介绍与图片资源
```

扩展时，新增工作流修改 `skills/`；新增评分形态修改 `starter-rubrics/`；新增数据源修改 `adapters/` 并更新路由约定。涉及状态结构的变更，需要同步初始化逻辑、迁移注册表、迁移文件和变更记录。

已有的辅助工具包括：

- [diff_pct.py](tools/diff_pct.py)：计算规范化后的稿件差异，辅助判断实际拍摄稿是否需要重新预测。
- [score-curve.py](tools/score-curve.py)：读取预测与复盘记录，输出误差表；安装 `matplotlib` 后可生成曲线图。当前解析依赖指定的 Markdown 格式和以 `w` 表示的播放单位，其他指标需要适配。
- [content.db.schema.sql](templates/content.db.schema.sql)：可选 SQLite 表结构；当前目录未提供 Markdown 到数据库的一键迁移脚本。

## 更新与卸载

当前状态结构版本为 **`1.4`**，以 [迁移注册表](migrations/registry.md) 为准。它是内容项目的 schema 版本，不等同于软件发布版本。

替换或拉取新版源码后，软链接安装会使用更新后的技能；副本安装需要重新执行安装命令。已有内容项目在助手中发送 `迁移`，按注册表依次升级。尤其是 `1.3 → 1.4`，需要将通用评分规则与包含实绩的升级证据分开保存。

如果更新涉及 hook 脚本，在源码根目录执行：

```bash
bash install.sh --reinstall-hooks "$HOME/Documents/我的内容账号"
```

该命令仅刷新内容项目 `.cheat-hooks/` 中的脚本，不负责重新注册 hooks，也不代替状态迁移。

卸载全局技能：

```bash
bash uninstall.sh --codex
# 或 bash uninstall.sh --all
```

卸载不会删除内容项目中的稿件、预测、评分规则和账号数据。

## 当前使用边界

- 本项目通过支持技能的 AI 助手运行，当前目录没有独立的网页界面、后端服务或一键视频生产系统。
- 初始评分和表现预测用于记录、比较和校准，效果需要用你自己的数据验证；样本数量本身不保证预测精度。
- 平台采集依赖页面、接口、登录态和可访问权限；字段完整性及实时可用性需要在实际账号上确认。失败时可以改为手动录入。
- 隔离评分需要助手支持独立子代理上下文；完整规则升级默认还需要外部模型审核能力。安装脚本不会替你配置这些运行能力。
- 登录态保存在内容项目的 `.auth/`、`.auth-xhs/`、`.auth-linkedin/`、`.auth-wechat-channels/` 等目录，应按项目模板排除版本控制。运营报告、评论和调试文件也可能包含账号资料。

进一步阅读：[总协议与路由](SKILL.md) · [初始化流程](skills/cheat-init/SKILL.md) · [变更记录](CHANGELOG.md) · [原有中文介绍](docs/README_CN.md)。部分旧介绍与当前文件存在差异，具体行为以安装脚本、对应子技能和共享协议为准。

## 来源与许可证

本项目基于 [XBuilderLAB/cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content) 修改，保留原作者的版权与 MIT 许可声明。许可证全文见 [LICENSE](LICENSE)。
