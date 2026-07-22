#!/usr/bin/env python3
"""Novel Creation Toolset

Usage:
  python3 novel-tools.py --validate <path>           Validate chapter (lines, CJK chars, paragraphs)
  python3 novel-tools.py --outline <title>            Generate outline template
  python3 novel-tools.py --count <path>               Count chars (excludes whitespace)
  python3 novel-tools.py --check-continuity <path>    Check chapter opening for forbidden time words
  python3 novel-tools.py --check-continuity <dir>     Batch check all .md/.txt chapters in a directory

The --check-continuity command enforces the core-writing.md rule:
  "章首禁用任何时间词" — chapter openings must NOT start with time words.
It scans the first sentence(s) of each chapter and reports violations.
"""
import sys
import re
from pathlib import Path

# Forbidden time words at chapter openings (from core-writing.md §连续性标准)
FORBIDDEN_TIME_WORDS = [
    # 显性时间词
    "第二天", "次日", "翌日", "隔天", "早上", "下午", "晚上", "清晨",
    "一小时后", "半天后", "片刻之后", "就在这时",
    # 隐性过渡短语
    "转眼之间", "过了一会儿", "不知过了多久",
]

# Water/filler words (反水文标准)
FILLER_WORDS = ["想了想", "叹了口气", "愣了一下", "不由得", "不知不觉"]


def read_file(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        sys.exit(f"File not found: {path}")
    except UnicodeDecodeError:
        sys.exit(f"Encoding error (not UTF-8): {path}")


def validate(path):
    c = read_file(path)
    cjk = sum(1 for ch in c if '\u4e00' <= ch <= '\u9fff')
    paragraphs = [p for p in c.split("\n\n") if p.strip()]
    print(f"Lines: {c.count(chr(10))}")
    print(f"CJK chars: {cjk}")
    print(f"Paragraphs: {len(paragraphs)}")


def outline(title):
    print(f"# 《{title}》总大纲\n")
    print("| 卷 | 核心事件 | 主角目标 | 反派动作 |")
    print("|---|---------|---------|---------|")
    print("| 一 |  |  |  |")
    print("| 二 |  |  |  |")
    print("| 三 |  |  |  |")
    print("\n## 单章细纲模板")
    print("- 章节号：")
    print("- 场景：")
    print("- 出场人物：")
    print("- 核心冲突：")
    print("- 爽点/钩子：")
    print("- 章末钩子：")


def count(path):
    c = read_file(path)
    # Count meaningful characters (exclude whitespace/newlines)
    chars = len(c.replace("\n", "").replace(" ", "").replace("\t", ""))
    cjk = sum(1 for ch in c if '\u4e00' <= ch <= '\u9fff')
    print(f"Chars (no whitespace): {chars}")
    print(f"CJK chars: {cjk}")


def get_opening(text, max_chars=120):
    """Extract the opening of a chapter (skip title, first real sentence)."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if not lines:
        return ""
    # Skip leading markdown headings (# 第X章) and pure-number lines
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("#"):
            continue
        # Skip chapter markers like "第一章" / "第1章" / pure title lines < 15 chars
        if re.match(r"^第[一二三四五六七八九十百零\d]+章", line) and len(line) < 30:
            continue
        body_start = i
        break
    opening = "".join(lines[body_start:body_start + 3])
    return opening[:max_chars]


def check_continuity_single(path):
    """Check a single chapter file. Returns list of violation dicts."""
    text = read_file(path)
    opening = get_opening(text)
    if not opening:
        return [], "empty"

    violations = []
    for word in FORBIDDEN_TIME_WORDS:
        idx = opening.find(word)
        if idx != -1:
            # context window around the hit
            start = max(0, idx - 10)
            end = min(len(opening), idx + len(word) + 10)
            violations.append({
                "word": word,
                "position": idx,
                "context": opening[start:end],
            })

    # Also flag filler words anywhere in opening
    for word in FILLER_WORDS:
        idx = opening.find(word)
        if idx != -1:
            start = max(0, idx - 10)
            end = min(len(opening), idx + len(word) + 10)
            violations.append({
                "word": word,
                "position": idx,
                "context": opening[start:end],
                "type": "filler",
            })

    return violations, opening


def check_continuity(path):
    target = Path(path)
    if target.is_dir():
        files = sorted(set(target.rglob("*.md")) | set(target.rglob("*.txt")))
    elif target.is_file():
        files = [target]
    else:
        sys.exit(f"Path not found: {path}")

    if not files:
        print(f"No .md/.txt files found in: {path}")
        return

    total_violations = 0
    checked = 0
    print(f"{'='*60}")
    print(f"🔗 章首连续性检查 — {path}")
    print(f"{'='*60}\n")

    for f in files:
        checked += 1
        violations, opening = check_continuity_single(str(f))
        status = "✅ PASS" if not violations else "❌ FAIL"
        print(f"{status}  {f.name}")
        if violations:
            total_violations += len(violations)
            for v in violations:
                tag = v.get("type", "time")
                print(f"        [{tag}] 「{v['word']}」 → …{v['context']}…")
        elif opening:
            preview = opening[:30].replace("\n", " ")
            print(f"        开头: {preview}…")

    print(f"\n{'='*60}")
    print(f"检查完成: {checked} 章, 违规 {total_violations} 处")
    if total_violations == 0:
        print("🎉 全部通过 — 章首无禁用时间词/填充词")
    else:
        print("⚠️ 请修正章首，改用「已完成的事」暗示时间流动")
        print("   示例: 「掐掉视频的时候天已经亮了」")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--validate" and len(sys.argv) > 2:
        validate(sys.argv[2])
    elif sys.argv[1] == "--outline" and len(sys.argv) > 2:
        outline(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "--count" and len(sys.argv) > 2:
        count(sys.argv[2])
    elif sys.argv[1] == "--check-continuity" and len(sys.argv) > 2:
        check_continuity(sys.argv[2])
    else:
        print(__doc__)
