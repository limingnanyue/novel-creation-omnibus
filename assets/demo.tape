# demo.tape — 可复现的 showcase 录制脚本
# 用途：用 vhs (https://github.com/charmbracelet/vhs) 录制一段终端 demo
# 展示 novel-tools.py 和 word-count-tool.py 的真实运行输出
#
# 录制方法：
#   1. 安装 vhs:  brew install vhs  (macOS) 或见 https://github.com/charmbracelet/vhs
#   2. 在仓库根目录运行:  vhs assets/demo.tape
#   3. 产物: assets/demo.gif
#
# 前置条件：仓库已克隆到本地，Python 3 已安装

Output "assets/demo.gif"

Set FontSize 16
Set Width 1200
Set Height 600
Set Padding 20

# 展示：章首连续性检查
Type@300ms "python3 scripts/novel-tools.py --check-continuity examples/"
Enter
Sleep 2s

# 展示：字数统计与AI味分析
Type@300ms "python3 scripts/word-count-tool.py examples/demo-output.md"
Enter
Sleep 2s

# 展示：JSON 结构化导出
Type@300ms "python3 scripts/word-count-tool.py --json examples/demo-output.md"
Enter
Sleep 2s

# 展示：大纲生成
Type@300ms "python3 scripts/novel-tools.py --outline 我的小说"
Enter
Sleep 2s

Type@200ms "echo '🎬 完整文档见 README.md'"
Enter
Sleep 1s
