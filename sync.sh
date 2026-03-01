#!/bin/bash

# Skill 同步脚本
# 用于在 my-skill-collection 和项目 workspace 之间同步技能

set -e

SKILL_COLLECTION_DIR="/home/ubuntu/my-skill-collection"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助
show_help() {
    echo -e "${GREEN}Skill 同步脚本${NC}"
    echo ""
    echo "用法:"
    echo "  $0 list                          # 列出所有技能"
    echo "  $0 <skill-name> <target-dir>     # 同步技能到目标目录"
    echo "  $0 <skill-name> <target-dir> --pull  # 从目标目录拉取更新"
    echo ""
    echo "示例:"
    echo "  $0 list"
    echo "  $0 image-generator /home/ubuntu/.openclaw/workspace-xiang_xiaohongshu/skills/"
    echo "  $0 image-generator-python /path/to/project/skills/ --pull"
    echo ""
}

# 列出所有技能
list_skills() {
    echo -e "${GREEN}可用的技能:${NC}"
    for dir in "$SKILL_COLLECTION_DIR"/*/; do
        if [ -d "$dir" ]; then
            skill_name=$(basename "$dir")
            if [ "$skill_name" != ".git" ]; then
                echo "  - $skill_name"
            fi
        fi
    done
}

# 同步技能（推送到项目）
push_skill() {
    local skill_name=$1
    local target_dir=$2
    local source_dir="$SKILL_COLLECTION_DIR/$skill_name"
    
    if [ ! -d "$source_dir" ]; then
        echo -e "${RED}错误：技能 '$skill_name' 不存在${NC}"
        echo "可用技能:"
        list_skills
        exit 1
    fi
    
    if [ ! -d "$target_dir" ]; then
        echo -e "${YELLOW}目标目录不存在，创建中...${NC}"
        mkdir -p "$target_dir"
    fi
    
    echo -e "${GREEN}同步技能 '$skill_name' 到 $target_dir${NC}"
    
    # 使用 rsync 同步（保留权限，删除多余文件）
    rsync -av --delete "$source_dir/" "$target_dir/$skill_name/"
    
    echo -e "${GREEN}✅ 同步完成${NC}"
}

# 拉取技能（从项目更新到 collection）
pull_skill() {
    local skill_name=$1
    local source_dir=$2
    local target_dir="$SKILL_COLLECTION_DIR/$skill_name"
    
    if [ ! -d "$source_dir/$skill_name" ]; then
        echo -e "${RED}错误：源目录 '$source_dir/$skill_name' 不存在${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}从 $source_dir 拉取技能 '$skill_name' 更新${NC}"
    
    # 使用 rsync 同步
    rsync -av "$source_dir/$skill_name/" "$target_dir/"
    
    echo -e "${GREEN}✅ 拉取完成${NC}"
}

# 创建软连接
create_symlink() {
    local skill_name=$1
    local target_dir=$2
    local source_dir="$SKILL_COLLECTION_DIR/$skill_name"
    local link_path="$target_dir/$skill_name"
    
    if [ ! -d "$source_dir" ]; then
        echo -e "${RED}错误：技能 '$skill_name' 不存在${NC}"
        exit 1
    fi
    
    if [ -L "$link_path" ]; then
        echo -e "${YELLOW}删除现有软连接：$link_path${NC}"
        rm "$link_path"
    elif [ -e "$link_path" ]; then
        echo -e "${RED}错误：目标已存在且不是软连接：$link_path${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}创建软连接：$link_path -> $source_dir${NC}"
    ln -s "$source_dir" "$link_path"
    
    echo -e "${GREEN}✅ 软连接创建完成${NC}"
}

# 主逻辑
if [ $# -lt 1 ]; then
    show_help
    exit 1
fi

case "$1" in
    "list")
        list_skills
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        skill_name=$1
        target_dir=$2
        pull_flag=$3
        
        if [ -z "$target_dir" ]; then
            echo -e "${RED}错误：请指定目标目录${NC}"
            show_help
            exit 1
        fi
        
        if [ "$pull_flag" = "--pull" ]; then
            pull_skill "$skill_name" "$target_dir"
        else
            # 询问使用软连接还是拷贝
            echo -e "${YELLOW}选择同步方式:${NC}"
            echo "  1) 软连接（推荐开发用，实时同步）"
            echo "  2) 拷贝（推荐生产用，独立版本）"
            echo ""
            read -p "请选择 [1/2]: " choice
            
            if [ "$choice" = "1" ]; then
                create_symlink "$skill_name" "$target_dir"
            else
                push_skill "$skill_name" "$target_dir"
            fi
        fi
        ;;
esac
