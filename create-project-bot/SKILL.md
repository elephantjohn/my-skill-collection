---
name: create-project-bot
description: 这个技能应在用户要求“创建项目bot”、“新增项目bot”、“创建 Telegram 项目 bot”、“自动生成 SOUL.md/AGENTS.md”、“把新 bot 接入 OpenClaw”时使用。它把创建流程挂在主 bot（盘古）上，通过 add-project.py 自动完成账号、Agent、路由与部署。
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    emoji: "🤖"
    os: [darwin, linux, win32]
    requires:
      bins: [python3, git, curl]
---

# 创建项目 Bot（挂在盘古主 Bot）

将“创建新项目 Bot”作为一个管理技能运行在主 Bot（盘古）里，不创建额外管理 Bot。

## 目标

- 接收项目描述，自动生成 `SOUL.md` 与 `AGENTS.md`
- 调用 `~/openclaw-server-config/scripts/add-project.py` 创建：
  - Telegram `channels.telegram.accounts.<project>`
  - `agents.list` 新 Agent
  - `bindings` 路由规则
  - `workspaces/<project>/SOUL.md` 与 `AGENTS.md`
- 可先 dry-run 预览，再确认部署

## 前置检查

1. 校验仓库路径存在：`~/openclaw-server-config/scripts/add-project.py`
2. 校验项目名格式：仅字母/数字/`-`/`_`
3. 默认使用 `accounts.main` 对话入口（盘古），仅创建新的项目 account，不新建管理 bot
4. 若仓库不在默认路径，先设置环境变量：`export OPENCLAW_SERVER_CONFIG_REPO="<repo_dir>"`

## 必收集信息

- `project_name`：项目标识（英文）
- `bot_token`：BotFather token
- `description`：项目简介（一句话）
- `tech_stack` / `repo_url` / `deploy_env`（用于 AGENTS.md）
- `server`（默认 `ubuntu@VM-16-15-ubuntu`）

## 执行流程

### Step 1: 先做 Token 体检（避免 429）

先做格式和可用性检查；对话中仅展示脱敏 token（前 6 + 后 4）。

```bash
curl -s "https://api.telegram.org/bot<BOT_TOKEN>/getMe"
```

若返回 `"ok":false` 或出现 `429 invalid tokens multiple times`，停止创建并要求用户更新 token；按返回提示等待冷却时间后重试。

### Step 2: 生成 SOUL.md 与 AGENTS.md（由模型生成）

根据用户提供的项目上下文生成两份文件，写入临时路径：

- `/tmp/<project>.SOUL.md`
- `/tmp/<project>.AGENTS.md`

生成要求：
- `SOUL.md` 聚焦人格、价值观、沟通风格
- `AGENTS.md` 聚焦技术栈、仓库、部署、工作规则
- 内容具体，避免空模板

### Step 3: 先 dry-run

优先执行 dry-run，先看变更，不直接部署：

```bash
bash <SKILL_DIR>/scripts/run_add_project.sh \
  --name "<project_name>" \
  --token "<bot_token>" \
  --description "<description>" \
  --soul-file "/tmp/<project_name>.SOUL.md" \
  --agents-file "/tmp/<project_name>.AGENTS.md" \
  --server "<server>" \
  --dry-run
```

向用户汇报将修改的文件与路由结果，等待明确确认。

### Step 4: 用户确认后正式执行

```bash
bash <SKILL_DIR>/scripts/run_add_project.sh \
  --name "<project_name>" \
  --token "<bot_token>" \
  --description "<description>" \
  --soul-file "/tmp/<project_name>.SOUL.md" \
  --agents-file "/tmp/<project_name>.AGENTS.md" \
  --server "<server>"
```

### Step 5: 收尾与验收

执行后给出验收步骤：

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <配对码>
openclaw agents list --bindings
```

## 安全规则（必须遵守）

- 未经明确同意，不执行破坏性命令（如 `rm -rf`、`git checkout --`）
- 回滚优先使用可审计方式：
  - `git restore -- openclaw.json`
  - 删除 `workspaces/<project>` 前必须二次确认
- 任何失败先保留现场并汇报，不自动“清空重来”

## 常见坑

- `bindings.match` 必须使用 `accountId`
- Telegram 多账户模式必须配置 `channels.telegram.accounts`
- 单一 `botToken` + 多条 `bindings` 会导致同一消息被多次处理（重复回复）

## 常见失败处理

- `Telegram account already exists`：更换 `project_name` 或先清理旧配置
- `Agent already exists`：同上
- `ssh deploy failed`：先 `--dry-run` 保留本地变更，待网络恢复后重试
- `429 invalid tokens multiple times`：更换正确 token + 等待冷却时间
