# My Skill Collection

个人技能集合 - 统一管理、版本控制、按需同步

## 目录结构

```
my-skill-collection/
├── image-generator/          # JS 版本
├── image-generator-python/   # Python 版本
└── .git/                     # Git 版本控制
```

## 使用方式

### 1. 添加到项目（软连接方式）

```bash
# 软连接到 OpenClaw workspace
ln -s /home/ubuntu/my-skill-collection/image-generator \
      /home/ubuntu/.openclaw/workspace-xiang_xiaohongshu/skills/image-generator
```

### 2. 添加到项目（拷贝方式）

```bash
# 使用同步脚本
./sync.sh image-generator /home/ubuntu/.openclaw/workspace-xiang_xiaohongshu/skills/
```

### 3. Git 提交更新

```bash
cd /home/ubuntu/my-skill-collection
git add .
git commit -m "feat: add image-generator skill"
git push origin main
```

## 同步脚本

```bash
# 查看所有技能
./sync.sh list

# 同步到项目
./sync.sh image-generator /path/to/project/skills/

# 从项目拉取更新
./sync.sh image-generator /path/to/project/skills/ --pull
```

## 技能列表

| 技能 | 语言 | 说明 |
|------|------|------|
| image-generator | JS + Python | 通用图片生成（智能选择 API） |

## 添加新技能

1. 在 `my-skill-collection/` 创建技能文件夹
2. 开发测试完成后提交 git
3. 需要同步时使用 `sync.sh` 脚本

## 注意事项

- ✅ 所有技能统一版本控制
- ✅ 支持多项目共享
- ✅ 软连接适合开发（实时同步）
- ✅ 拷贝适合生产（独立版本）
