#!/bin/bash

# 小红书创作快速启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  小红书自动创作系统${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 检查环境变量
echo -e "${YELLOW}检查配置...${NC}"

if [ -z "$GEMINI3PRO_API_KEY" ]; then
    echo -e "${RED}❌ 缺少 GEMINI3PRO_API_KEY 环境变量${NC}"
    echo "请在 .env 文件中配置"
    exit 1
fi

if [ -z "$TEXT_API_KEY" ] || [ -z "$TEXT_SECRET_KEY" ]; then
    echo -e "${YELLOW}⚠️  未配置百度审核 API，将跳过审核步骤${NC}"
fi

echo -e "${GREEN}✅ 配置检查完成${NC}"
echo ""

# 解析参数
THEME=""
TEXT_ONLY=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --theme)
            THEME="$2"
            shift 2
            ;;
        --text-only)
            TEXT_ONLY=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "未知参数：$1"
            echo "用法：$0 [--theme \"主题\"] [--text-only] [-v]"
            exit 1
            ;;
    esac
done

# 构建命令
CMD="python scripts/create_note.py"

if [ -n "$THEME" ]; then
    CMD="$CMD --theme \"$THEME\""
fi

if [ "$TEXT_ONLY" = true ]; then
    CMD="$CMD --text-only"
fi

if [ "$VERBOSE" = true ]; then
    CMD="$CMD --verbose"
fi

# 执行
echo -e "${YELLOW}开始创作...${NC}"
echo ""

eval $CMD

echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}  创作完成！${NC}"
echo -e "${GREEN}================================${NC}"
