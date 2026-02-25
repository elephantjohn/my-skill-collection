# LESSONS.md - 经验教训库

> 每次犯错或踩坑后，记录到这里并提交。换机器也不会再犯同样的错。

---

## 2026-02-25: OpenClaw 插件安装配置

**问题**：安装 memory-lancedb-pro 插件时反复报错，重启 3 次才成功。

**根因**：
1. `plugins.load.paths` 用了相对路径，但 gateway 工作目录不是 workspace，导致路径解析错误
2. `rerank` 配置放在了顶层（和 `embedding` 并列），但插件 schema 要求在 `retrieval` 下面
3. 分多次写入配置，每次重启 gateway 的 doctor 会清掉无效项，导致前面写入的内容丢失

**正确做法**：
- `plugins.load.paths` **必须使用绝对路径**
- 写配置前**先读插件的 `openclaw.plugin.json`**，了解 schema 结构
- **一次性写入所有配置**（paths + entries + slots），不要分步
- 写完后立即验证，再重启

**正确配置示例**：
```json
{
  "plugins": {
    "load": {
      "paths": ["/absolute/path/to/plugin"]
    },
    "entries": {
      "plugin-name": {
        "enabled": true,
        "config": { "...按 configSchema 填写..." }
      }
    },
    "slots": {
      "memory": "plugin-name"
    }
  }
}
```

---

## 2026-02-22: Telegram 多 Bot 重复回复

**问题**：国资预算 bot 回复后会再回复一次（重复回复）。

**根因**：
- 单一 `botToken` 模式下添加了多条 `bindings`
- 同一消息被多个 agent 同时处理

**正确做法**：
- 多 bot 必须用 `channels.telegram.accounts` 多账户模式
- 每个 account 对应独立的 `botToken`
- `bindings.match` 必须用 `accountId` 区分

---

## 2026-02-21: bindings.match 字段名

**问题**：`add-project.py` 生成的 bindings 用了 `match.account`（已废弃）。

**根因**：脚本写错了字段名。

**正确做法**：必须用 `match.accountId`，不是 `match.account`。

---

## 规则

1. 每次犯错后，在此文件追加一条记录
2. 同时更新相关的 SKILL.md（如适用）
3. 提交并推送到仓库
4. 新 session 启动时可参考此文件避免重复犯错
