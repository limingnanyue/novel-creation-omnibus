#!/bin/bash
# 小说创作全能工坊 安装脚本
# Usage: bash scripts/install.sh
set -e

echo "=== 小说创作全能工坊 安装脚本 ==="
echo ""

# 1. 检查 Node.js
if ! command -v node >/dev/null 2>&1; then
  echo "✗ 需要先安装 Node.js v18+"
  echo "  安装方法: https://nodejs.org/  或  brew install node"
  exit 1
fi

NODE_MAJOR=$(node -v | sed 's/v//' | cut -d. -f1)
if [ "$NODE_MAJOR" -lt 18 ]; then
  echo "✗ Node.js 版本过低 (当前 $(node -v)), 需要 v18+"
  exit 1
fi
echo "✓ Node.js $(node -v)"

# 2. 安装 skill
echo ""
echo "正在安装 novel-creation-omnibus ..."
if ! npx skills add limingnanyue/novel-creation-omnibus -g; then
  echo ""
  echo "✗ 安装失败。请检查网络连接,或手动执行:"
  echo "  npx skills add limingnanyue/novel-creation-omnibus -g"
  exit 1
fi

# 3. 验证脚本可用
echo ""
echo "=== 验证 ==="
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/novel-tools.py" ]; then
  if python3 "$SCRIPT_DIR/novel-tools.py" --outline 验证测试 >/dev/null 2>&1; then
    echo "✓ novel-tools.py 可运行"
  else
    echo "△ novel-tools.py 验证失败 (可能缺少 python3)"
  fi
fi

echo ""
echo "=== 安装完成 ==="
echo ""
echo "现在对 Agent 说:"
echo "  写小说"
echo ""
echo "或试试具体任务:"
echo "  帮我写个第一章开头，要抓人"
echo "  去AI味，我是用Claude写的"
echo ""
echo "文档: https://github.com/limingnanyue/novel-creation-omnibus"
