#!/usr/bin/env python3
"""Novel Creation Toolset

Usage:
  python3 novel-tools.py --validate <path>    Validate chapter
  python3 novel-tools.py --outline <title>     Generate outline
  python3 novel-tools.py --count <path>        Count chars
"""
import sys, os

def validate(path):
    with open(path) as f:
        c = f.read()
    print(f"Lines: {c.count(chr(10))}")
    print(f"CJK: {sum(1 for ch in c if chr(0x4e00) <= ch <= chr(0x9fff))}")

def outline(title):
    print(f"# 《{title}》总大纲")
    print("| 卷 | 核心事件 |")
    print("|---|---------|")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
    elif sys.argv[1] == "--validate" and len(sys.argv) > 2:
        validate(sys.argv[2])
    elif sys.argv[1] == "--outline" and len(sys.argv) > 2:
        outline(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "--count" and len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            print(f"Chars: {len(f.read())}")
    else:
        print(__doc__)
