---
name: qingyun-proxy-setup
description: 一键配置青云(Qingyun)第三方中转站，支持 Claude、Gemini、GPT/Codex 三个模型通过青云 API 代理接入 OpenClaw。包含完整配置模板、踩坑记录和故障排查指南。
user-invocable: true
disable-model-invocation: false
metadata:
  openclaw:
    emoji: "☁️"
    os: [darwin, linux, win32]
    requires:
      bins: [curl]
---

# 青云 (Qingyun) 中转站一键配置

你是一个 OpenClaw 配置助手。当用户触发此技能时，引导他们完成青云第三方中转站的完整配置。

## 青云平台信息

- 平台地址: https://api.qingyuntop.top
- 三种 API 协议，三个不同端点：

| 模型类型 | Provider ID | Base URL | API 协议 |
|---------|------------|----------|---------|
| Claude | `api-proxy-claude` | `https://api.qingyuntop.top` | `anthropic-messages` |
| Gemini | `api-proxy-google` | `https://api.qingyuntop.top/v1beta` | `google-generative-ai` |
| GPT/Codex | `api-proxy-gpt` | `https://api.qingyuntop.top/v1` | `openai-completions` |

## 配置流程

### 第一步：收集用户信息

询问用户以下信息：
1. 服务器操作系统（Linux/macOS/Windows）和运行 OpenClaw 的用户名（决定 home 目录路径）
2. 青云 API Key（最多三个：Claude、Gemini、GPT/Codex）
3. 每个 Key 对应的具体模型名称（如 `claude-opus-4-6-thinking`、`gemini-3-pro-preview`、`gpt-5.3-codex-xhigh`）
4. 模型分工策略：哪个做主模型(primary)、哪个做图像模型(imageModel)、哪个做备选

### 第二步：生成 openclaw.json

根据用户信息生成配置，注意以下模板中的 `<PLACEHOLDER>` 需要替换：

```json
{
  "agents": {
    "defaults": {
      "workspace": "<HOME_DIR>/.openclaw/workspace",
      "models": {
        "api-proxy-claude/<CLAUDE_MODEL_ID>": { "alias": "<CLAUDE_ALIAS>" },
        "api-proxy-google/<GEMINI_MODEL_ID>": { "alias": "<GEMINI_ALIAS>" },
        "api-proxy-gpt/<GPT_MODEL_ID>": { "alias": "<GPT_ALIAS>" }
      },
      "model": {
        "primary": "api-proxy-claude/<CLAUDE_MODEL_ID>"
      },
      "imageModel": {
        "primary": "api-proxy-google/<GEMINI_MODEL_ID>"
      }
    }
  },
  "auth": {
    "profiles": {
      "api-proxy-claude:default": { "provider": "api-proxy-claude", "mode": "api_key" },
      "api-proxy-google:default": { "provider": "api-proxy-google", "mode": "api_key" },
      "api-proxy-gpt:default": { "provider": "api-proxy-gpt", "mode": "api_key" }
    }
  },
  "models": {
    "mode": "merge",
    "providers": {
      "api-proxy-claude": {
        "baseUrl": "https://api.qingyuntop.top",
        "api": "anthropic-messages",
        "models": [
          {
            "id": "<CLAUDE_MODEL_ID>",
            "name": "<CLAUDE_ALIAS>",
            "reasoning": true,
            "contextWindow": 200000,
            "maxTokens": 128000
          }
        ]
      },
      "api-proxy-google": {
        "baseUrl": "https://api.qingyuntop.top/v1beta",
        "api": "google-generative-ai",
        "models": [
          {
            "id": "<GEMINI_MODEL_ID>",
            "name": "<GEMINI_ALIAS>",
            "contextWindow": 1000000,
            "maxTokens": 64000
          }
        ]
      },
      "api-proxy-gpt": {
        "baseUrl": "https://api.qingyuntop.top/v1",
        "api": "openai-completions",
        "models": [
          {
            "id": "<GPT_MODEL_ID>",
            "name": "<GPT_ALIAS>",
            "reasoning": true,
            "contextWindow": 400000,
            "maxTokens": 128000
          }
        ]
      }
    }
  }
}
```

**重要**: 生成配置时必须保留用户原有的 `gateway`、`channels`、`plugins`、`skills`、`hooks`、`wizard`、`meta`、`messages` 等配置段落不变，只替换 `agents.defaults.models`、`agents.defaults.model`、`agents.defaults.imageModel`、`auth.profiles`、`models` 这几个部分。

### 第三步：生成 auth-profiles.json

```json
{
  "version": 1,
  "profiles": {
    "api-proxy-claude:default": {
      "type": "api_key",
      "provider": "api-proxy-claude",
      "key": "<CLAUDE_API_KEY>"
    },
    "api-proxy-google:default": {
      "type": "api_key",
      "provider": "api-proxy-google",
      "key": "<GEMINI_API_KEY>"
    },
    "api-proxy-gpt:default": {
      "type": "api_key",
      "provider": "api-proxy-gpt",
      "key": "<GPT_API_KEY>"
    }
  },
  "lastGood": {
    "api-proxy-claude": "api-proxy-claude:default",
    "api-proxy-google": "api-proxy-google:default",
    "api-proxy-gpt": "api-proxy-gpt:default"
  }
}
```

### 第四步：部署指引

告诉用户将文件放到以下路径（根据操作系统调整）：

| 文件 | Linux/macOS 路径 | Windows 路径 |
|------|-----------------|-------------|
| openclaw.json | `~/.openclaw/openclaw.json` | `C:\Users\<用户名>\.openclaw\openclaw.json`（或 `.clawdbot\clawdbot.json`）|
| auth-profiles.json | `~/.openclaw/agents/main/agent/auth-profiles.json` | `C:\Users\<用户名>\.openclaw\agents\main\agent\auth-profiles.json`（或对应 `.clawdbot` 路径）|

部署命令：
```bash
# 备份
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
cp ~/.openclaw/agents/main/agent/auth-profiles.json ~/.openclaw/agents/main/agent/auth-profiles.json.bak

# 替换文件后
openclaw doctor
openclaw gateway restart
openclaw models list
openclaw models status
```

### 第五步：验证

1. `openclaw models list` 应显示三个青云模型
2. `openclaw models status` 应显示三个 api-proxy provider 都有 profiles=1, api_key=1
3. 在消息渠道中发送消息测试回复
4. 用 `/model` 命令切换模型测试

## 踩坑记录（必读）

### 坑 1: imageModel 必须是对象，不能是字符串

```json
// 错误 — 会导致 "Invalid input: expected object, received string"
"imageModel": "api-proxy-google/gemini-3-pro-preview"

// 正确
"imageModel": {
  "primary": "api-proxy-google/gemini-3-pro-preview"
}
```

`model` 和 `imageModel` 都必须使用 `{ "primary": "..." }` 对象格式。

### 坑 2: 配置文件被外部脚本覆盖

如果用户之前设置了配置监控/健康检查脚本（如 crontab 中的 `cron-health-check.sh`），修改 openclaw.json 后可能被自动回滚。

**排查方法：**
```bash
crontab -l | grep -i openclaw
ps aux | grep -E "inotify|watch|monitor" | grep -v grep
```

**解决：** 在修改配置前，先停止或重命名监控脚本。

### 坑 3: 切换模型后 Context Overflow

从一个模型切换到另一个模型时，如果当前会话历史很长，可能报 "Context overflow: prompt too large for the model"。

**解决：** 切换模型后先发 `/new` 重置会话，再开始对话。

### 坑 4: 429 余额不足

收到 `429 Insufficient balance or no resource package` 表示青云账户对应模型的余额不足。

**解决：** 到青云平台充值对应模型的资源包。可以用 `/model` 先切到有余额的模型继续使用。

### 坑 5: API 请求无响应（静默超时）

青云 API 偶尔不稳定，请求发出后无响应。日志中表现为 `embedded run start` 之后无后续输出。

**排查方法：**
```bash
# 直接 curl 测试 API 连通性
# Claude:
curl -s https://api.qingyuntop.top/v1/messages \
  -H "x-api-key: <YOUR_CLAUDE_KEY>" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","max_tokens":50,"messages":[{"role":"user","content":"hi"}]}'

# GPT/Codex:
curl -s https://api.qingyuntop.top/v1/chat/completions \
  -H "Authorization: Bearer <YOUR_GPT_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"hi"}],"max_tokens":50}'

# Gemini:
curl -s https://api.qingyuntop.top/v1beta/chat/completions \
  -H "Authorization: Bearer <YOUR_GEMINI_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"hi"}],"max_tokens":50}'
```

### 坑 6: Linux 服务器上 iMessage 报错

`imsg rpc not ready after 10129ms (imsg not found (imsg))` — iMessage 仅支持 macOS，Linux 上无法使用。

**解决：** 在 openclaw.json 中禁用：
```json
"channels": {
  "imessage": { "enabled": false }
}
```

### 坑 7: reasoning 模型需要标记

Claude Thinking、GPT Codex XHigh 等推理模型需要在 provider 模型定义中设置 `"reasoning": true`，否则 OpenClaw 不会正确处理思考输出流。

### 坑 8: maxTokens 应匹配模型官方上限

不要随意设置 maxTokens，应查询各模型官方文档：

| 模型系列 | 官方 maxTokens 参考 |
|---------|-------------------|
| Claude Opus 4.6 | 128,000 |
| Gemini 3 Pro | 64,000 |
| GPT-5.3 Codex | 128,000 |

设置过低会限制模型输出能力，设置过高可能导致 API 拒绝请求。

## 日常使用速查

| 操作 | 命令 |
|------|------|
| 查看当前模型 | `/model` |
| 切换到 Claude | `/model api-proxy-claude/<MODEL_ID>` |
| 切换到 Gemini | `/model api-proxy-google/<MODEL_ID>` |
| 切换到 Codex | `/model api-proxy-gpt/<MODEL_ID>` |
| 重置会话 | `/new` |
| 查看模型状态 | `/model status` |

## 故障排查流程

1. `openclaw doctor` — 检查配置有效性
2. `openclaw models status` — 检查模型和认证状态
3. `openclaw logs --follow` — 实时查看日志
4. `tail -500 /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log | grep -i error` — 搜索错误日志
5. `curl` 直接测试青云 API — 排除 OpenClaw 本身的问题
6. 检查 crontab/systemd 是否有脚本覆盖配置
