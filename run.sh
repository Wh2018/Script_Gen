#!/bin/bash
# 政策宣传微短剧剧本生成系统 - 快速启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================================"
echo "政策宣传微短剧剧本生成系统"
echo "============================================================"
echo ""

# 检查conda环境
if ! command -v conda &> /dev/null; then
    echo -e "${RED}错误: 未找到conda命令${NC}"
    exit 1
fi

# 激活环境
echo -e "${YELLOW}激活jvben环境...${NC}"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate jvben

# 检查.env配置文件
if [ ! -f ".env" ]; then
    echo -e "${RED}错误: 未找到.env配置文件${NC}"
    echo ""
    echo "请按以下步骤配置："
    echo "  1. cp .env.example .env"
    echo "  2. 编辑.env文件，填入API密钥"
    echo ""
    exit 1
fi

# 创建输出目录
mkdir -p output

echo -e "${GREEN}环境检查通过！${NC}"
echo ""
echo "开始运行..."
echo ""

# 运行主程序（将所有参数传递给main.py）
python main.py "$@"

# 检查运行结果
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}✓ 运行成功！${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo "生成的文件位于 output/ 目录："
    ls -lht output/ | head -5
else
    echo ""
    echo -e "${RED}✗ 运行失败，请查看上方错误信息${NC}"
    exit 1
fi
