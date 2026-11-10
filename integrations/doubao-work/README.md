# 豆包工作完整流程接入包

本接入保留原版总协议、15 个子技能及其完整配套资源，通过单一豆包技能入口路由。原始功能文件不改动；`source-manifest.json` 可逐文件核对 SHA-256。

包内增加两类执行桥接：独立 API 请求负责隔离评分与跨模型审核，专用预测写入脚本负责在写入前检查不可变段落。它们保留原有业务约束，但不能伪称豆包支持 Claude Code 的全局 hooks。

## 当前接入情况

| 项目 | 验证方式 / 依赖 |
|---|---|
| 总入口与全部 15 子技能 | 打包清单逐文件校验 |
| 模板、迁移、5 平台适配器、转录、热点、工具 | 原文件随包保留 |
| 预测保护 | 本地行为测试；豆包中必须经 `write` 修改预测 |
| 独立盲评分 | 需要配置评分 API；不使用继承主历史的并行代理 |
| 跨模型审核 | 需要另一个模型 API；不是主对话自审 |
| 自动采集 | 需要在实际执行环境中安装依赖并登录各平台 |
| 会话状态报告 | 技能每次调用时执行 `session`，不是全局 SessionStart |

因此，“成功导入”与“全功能运行验收完成”要分开检查。未配置 API 前，正式盲评分与完整规则升级会明确停止，不会自动降级为自评。

## 构建

在原项目根目录执行：

```bash
python3 integrations/doubao-work/build.py
```

生成 `dist/cheat-on-content-doubao.zip` 和同名解压目录。构建只读取明确列出的源码目录和文件，跳过隐藏目录、凭证、登录态、账号数据与 Python 缓存。

## 导入豆包工作

进入“技能 · 连接器 · 伙伴”，选择添加/新建，再选择“上传技能”，上传 `cheat-on-content-doubao.zip`。名称应识别为 `cheat-on-content-doubao`。等待检测完成后，在工作任务中选择该技能。

首次可发送：

```text
使用 cheat-on-content-doubao。先定位你当前环境实际可访问的技能目录，
读取完整入口和宿主适配协议，检查包内15个技能及原版资源哈希，
运行 doctor，只报告真实结果。先不要初始化账号，不要创建或索取密钥。
```

随后为每个账号选择独立且可持久保存的内容目录。执行环境必须能访问该目录；豆包云端 Linux 不能直接使用 Mac 的 `/Users/wang/...` 路径。初始化时按原版提问，已有内容项目先备份并运行迁移，不另建空项目替代旧数据。

## 模型服务配置指引

豆包工作聊天账号与模型 API 是不同入口。要补齐独立评分和审核，需要你自行开通相应模型服务并确认费用，接入包不会代为购买或开通付费项目。

建议组合：

1. **盲评分：火山方舟的豆包文本模型。** 在控制台创建 API Key，并取得你实际可用的模型 ID / 推理接入点 ID。使用支持非流式 Chat Completions 文本响应的模型。
2. **跨模型审核：阿里云百炼的通义千问文本模型。** 在百炼控制台取得对应区域的 API Key、模型 ID 和完整 Chat Completions 地址。选择与评分不同的模型；API Key 与地域、套餐及 endpoint 必须相符。

官方文档：[火山方舟地址与鉴权](https://docs.volcengine.com/docs/ark/base-url-and-authentication?lang=zh)、[方舟文本生成](https://docs.volcengine.com/docs/ark/text-generation?lang=zh)、[百炼接口说明](https://help.aliyun.com/zh/model-studio/compatibility-of-openai-with-dashscope)、[百炼 Base URL](https://docs.modelstudio.console.alibabacloud.com/en/model-studio/base-url)。具体 model 值以你控制台实际显示的可用值为准，包内不填写猜测的模型 ID。

配置放在**实际运行脚本的环境**中的账号内容目录 `.cheat-secrets.json`，结构参照 `references/model-config.example.json`。与已有文件合并 `doubao_bridge` 字段，不覆盖其他凭证。

每个通道填写：

- `endpoint`：完整的 `https://.../chat/completions` 地址。
- `model`：控制台提供的实际值。
- `api_key_env`：保存密钥的环境变量名；优先从该环境变量读取。
- `api_key`：没有安全环境变量入口时，可在你自行控制的配置文件内填写；不要通过聊天发送。

在你控制的交互终端运行以下命令，脚本会逐项询问地址和模型 ID，并隐藏输入密钥，合并保存到权限为 `600` 的配置文件，自动补齐 `.gitignore`。不要把真实 Key 放进终端命令历史。

```bash
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" configure
```

豆包云端与本机配置不共享；上面的配置必须发生在实际执行环境。没有云端安全配置入口时，先停在待配置状态，不能声称本机配置已经在云端生效。

模型数据流向：盲评分服务接收原稿与通用评分规则；审核服务接收新旧公式、校准池维度与实绩、排序结果。主对话、登录 cookie 和密钥不会加入模型请求正文。

配置后执行 `doctor` 检查配置是否齐全，再用**合成稿件**测试 `blind-score` 和一份合成校准池测试 `audit`。`doctor` 不会联网，也不会把“配置齐全”标为“接口已验证”。

## 运行命令

`SKILL_ROOT` 是实际技能目录，`ACCOUNT_ROOT` 是实际账号目录。以下命令由豆包按你选择的任务调用，也可在同一环境的终端执行：

```bash
# 环境、资源与依赖检查
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" doctor

# 调用时状态报告，并检查/建立预测保护基线
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" session

# 检查既有预测是否被其他工具改动
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" verify

# 隔离盲评分
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" blind-score --script 'scripts/实际稿件.md'

# 预测文件受保护写入；input 是包含修改后完整文件内容的临时文件
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" write --path 'predictions/实际预测.md' --input '/实际路径/临时完整文件.md'

# 独立模型审核；材料结构见宿主适配协议
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" audit --input '/实际路径/审核材料.json'

# 调用原版数据采集适配器
python3 "$SKILL_ROOT/scripts/runtime.py" --project "$ACCOUNT_ROOT" collect --adapter bilibili-stat --id '实际BV号' --folder 'videos/实际作品目录'
```

`.cheat-guard/predictions.json` 保存保护基线，需要与预测文件一起备份。跨模型 `REJECT` 的退出码是 4；其他失败是 2。任何失败均不能解释为已成功。

## 本地验证

```bash
python3 -m unittest discover -s integrations/doubao-work/tests -v
python3 integrations/doubao-work/build.py
```

行为测试覆盖已保存预测不可修改、复盘与 v2 追加、删除/改序/符号链接绕过、盲评分输入隔离、模型返回校验及审核失败处理。没有真实密钥的测试不验证外部模型或平台采集服务；这些需要配置后在豆包实际环境中另行验收。

公开能力依据：[豆包工作官方功能介绍](https://www.feishu.cn/content/article/7677519271848610746)。本包是客户端自用技能导入包，不是开放平台商店上架申请。
