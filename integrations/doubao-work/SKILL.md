---
name: 个人ip助手
description: 用于豆包工作的内容账号运营完整流程：初始化、学习对标、讨论选题、稿件评分、发布前预测、拍摄与发布登记、数据复盘、受众画像、规则校准和状态管理。调用随包原版15个子技能及采集适配器，独立模型通道负责隔离盲评和跨模型审核。
---

# 个人ip助手

原始完整规则位于本技能的 `assets/cheat-on-content/`。本文件只适配宿主工具；评分规则、预测格式、校准门槛、用户确认条件和全部业务流程以原版文件为准，不用摘要代替原流程。

## 开始执行

1. 确认**当前任务实际能访问**的技能安装目录 `SKILL_ROOT` 和账号内容目录 `ACCOUNT_ROOT`。文件工具的本地路径与命令工具的云端路径可能不同；通过实际列目录确认，不猜测、不沿用其他电脑路径。多个账号使用各自目录。
2. 读取 [宿主适配协议](references/host-adapter.md)。首次调用、初始化前或运行环境改变时执行：

   ```bash
   python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" doctor
   ```

3. 每次本技能开始工作时执行 `session`，显示原版状态报告与接入能力。它会检查并封存已有预测；失败则先解决完整性问题。

   ```bash
   python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" session
   ```

4. 读取 `assets/cheat-on-content/SKILL.md` 的总原则，再按下表读取目标子技能的**完整文件**。原版某处与较新的子技能/共享协议不同，使用具体子技能和状态协议。例如不再写已淘汰的 mode 字段，当前 schema 从迁移注册表读取。
5. 没有 `.cheat-state.json` 时，按原版 `cheat-init` 逐项了解账号后创建；安装技能不等于初始化账号，不跳过原版入门问题。

## 完整路由

下列路径均相对 `assets/cheat-on-content/`；读取目标文件引用的共享协议、模板及脚本。

| 用户任务 | 原版技能文件 |
|---|---|
| 初始化 | `skills/cheat-init/SKILL.md` |
| 学习对标 / 导入对标 | `skills/cheat-learn-from/SKILL.md` |
| 讨论选题 / 写初稿 / 批量选题 | `skills/cheat-seed/SKILL.md` |
| 抓热点 | `skills/cheat-trends/SKILL.md` |
| 从候选池推荐 | `skills/cheat-recommend/SKILL.md` |
| 稿件评分 | `skills/cheat-score/SKILL.md` |
| 发布前预测 / 拍后 v2 预测 | `skills/cheat-predict/SKILL.md` |
| 拍摄登记 | `skills/cheat-shoot/SKILL.md` |
| 发布登记 | `skills/cheat-publish/SKILL.md` |
| 数据回收与复盘 | `skills/cheat-retro/SKILL.md` |
| 受众画像 | `skills/cheat-persona/SKILL.md` |
| 完整规则升级 / 仅重校 bucket | `skills/cheat-bump/SKILL.md` |
| 状态看板 | `skills/cheat-status/SKILL.md` |
| 状态迁移 | `skills/cheat-migrate/SKILL.md` |
| 内部隔离打分（不是用户入口） | `skills/cheat-score-blind/SKILL.md` |

## 宿主工具映射

- 原版 `Read / Glob / Grep / Bash / WebFetch`：使用本次豆包任务真实提供的对应文件、命令、搜索及浏览器工具；不存在时明确说明缺项。
- 原版 `Skill` 和 `/cheat-*`：读取上表对应的完整技能文件执行，同一包内无需依赖斜杠菜单注册。
- 原版 `Task → cheat-score-blind`：使用桥接脚本的 `blind-score`，它发起只有原稿与通用评分规则的全新 API 请求。普通并行子代理可能继承主对话，不能据此宣称隔离。主对话不得代打分。
- 原版 `mcp__llm-chat__chat`：使用独立、不同模型的 `audit` API 通道。缺配置时告知配置方法，不自动关闭审核、不将自审写成跨模型 PASS。原版显式离线例外仍需由用户明确选择并如实标记。
- 原版 `.claude/settings.json` hooks：保留随包原始实现供 Claude Code 使用。豆包中所有预测文件写入使用 `write`，每次调用用 `session` 检查；不把 `hooks_installed` 伪标为 true。宿主没有全局 SessionStart/PreToolUse 的事实必须在状态中如实说明。
- 原版源码定位：统一使用 `SKILL_ROOT/assets/cheat-on-content`；不执行寻找 `~/.claude/skills` 的旧示例。
- 原版可选 `humanizer`、热点 MCP、转录引擎及平台登录态：按原流程检测、调用；随包保留全部接入文档，不把“未配置”说成“已完成”。

## 必须通过桥接执行的操作

隔离评分（维度来自当前 rubric，不修改模型输出以迎合预期）：

```bash
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" blind-score --script 'scripts/实际稿件.md'
```

原版 `non_blind_warning` 仍返回标记后的维度与 medium 置信度，由原主流程处理；不能将它报告为无污染盲评。日志中的模型身份按实际通道填写。

写预测、登记发布元数据、追加复盘、追加 v2 或 re-score：先将拟写入的**完整文件**放到临时文件，再受保护写入。原预测段必须逐字保留，新版本在新二级标题下追加。

```bash
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" write --path 'predictions/实际预测.md' --input '/实际临时目录/拟写入文件.md'
```

跨模型审核：完成原版规则升级中的全池隔离重评分和本地排序检验后，按宿主适配协议准备材料。审核返回 `REJECT`、网络失败或缺配置都不能进入 PASS 分支。原版落地确认步骤保留。

```bash
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" audit --input '/实际临时目录/审核材料.json'
```

运营数据采集：在账号目录安装相应依赖并登录后，通过 `collect` 调用原始 `run.sh`。保持原适配器的数据、评论和报告输出；登录失败时按原流程处理，不能生成伪数据。

```bash
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" collect --adapter douyin-session --id '实际作品ID' --folder 'videos/实际作品目录' --script 'scripts/实际稿件.md'
```

## 交付与能力边界

执行用户所选的完整原流程；完成后说明产物位置和本次真实验证结果。隔离评分只发送稿件和 `rubric_notes.md`；外部审核发送公式与校准池数据。调用前应让用户清楚数据流向已配置的模型服务，不要求在聊天中粘贴密钥。

缺少模型通道时，仍可以按原流程做不依赖它的任务，例如导入对标、选题、登记、人工数据复盘和画像；正式隔离打分及规则升级必须等依赖就绪。不能以“简化版”替代用户要求的完整功能，也不能将“保留了文件”表述为“所有功能已实测通过”。

配置说明见本技能 [README.md](README.md)。对本包的改动应由维护者重新构建；不要直接改动随包原版资源或删除预测保护账本。
