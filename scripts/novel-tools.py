#!/usr/bin/env python3
"""Novel Creation Toolset

Usage:
  python3 novel-tools.py --validate <path>    Validate chapter (lines, CJK chars, paragraphs)
  python3 novel-tools.py --outline <title>     Generate outline template
  python3 novel-tools.py --count <path>        Count chars (excludes whitespace)
"""
import sys


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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--validate" and len(sys.argv) > 2:
        validate(sys.argv[2])
    elif sys.argv[1] == "--outline" and len(sys.argv) > 2:
        outline(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "--count" and len(sys.argv) > 2:
        count(sys.argv[2])
    else:
        print(__doc__)
