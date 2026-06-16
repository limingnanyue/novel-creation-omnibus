#!/usr/bin/env python3
"""
小说字数统计与分析工具 (Novel Word Count Analyzer)
Usage:
  python3 word-count-tool.py <chapter-file-or-directory>
  python3 word-count-tool.py --watch          # watch mode: monitor word count trends
  python3 word-count-tool.py --compare A.md B.md  # compare two chapters

Features:
  - Per-file word/char stats
  - Directory batch analysis
  - Dialog-to-narrative ratio
  - AI-smell keyword density
  - Chapter length distribution
  - Estimated reading time
  - Daily/weekly output tracking
"""

import sys, os, re, json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# AI-smell keyword sets
AI_SMELL = {
    "情态": ["仿佛", "好像", "犹如", "宛若", "一丝", "一抹", "些许", "隐约"],
    "动作模板": ["深吸一口气", "缓缓", "不禁", "微微", "轻轻", "淡淡"],
    "表情模板": ["眼中闪过", "嘴角勾起", "眉头微皱", "眉眼低垂"],
    "心理模板": ["心中一动", "心头一震", "心下了然", "心底泛起", "不由得"],
    "过渡词": ["突然", "瞬间", "不由自主", "情不自禁", "自然而然地"],
}

# Dialog indicators
DIALOG_MARKS = {"“", "”", '"', "「", "」", "『", "』"}

def count_chapter(text: str) -> dict:
    lines = text.split("\n")
    total_chars = len(text.replace("\n", "").replace(" ", ""))
    total_words_est = total_chars  # Chinese: chars ≈ words
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    sentences = [s for s in re.split(r"[。！？\n]", text) if s.strip()]

    # Dialog lines
    dialog_lines = 0
    for line in lines:
        stripped = line.strip()
        if any(m in stripped for m in DIALOG_MARKS):
            dialog_lines += 1

    # AI-smell keyword density
    ai_hits = {}
    for category, words in AI_SMELL.items():
        hits = [w for w in words if w in text]
        if hits:
            ai_hits[category] = len(hits)

    # Paragraph length distribution
    para_lens = [len(p.replace("\n", "")) for p in paragraphs]
    avg_para_len = sum(para_lens) / len(para_lens) if para_lens else 0
    short_paras = sum(1 for l in para_lens if l < 50)
    long_paras = sum(1 for l in para_lens if l > 200)

    return {
        "total_chars": total_chars,
        "total_lines": len(lines),
        "total_paragraphs": len(paragraphs),
        "total_sentences": len(sentences),
        "avg_para_len": round(avg_para_len, 1),
        "short_paras": short_paras,
        "long_paras": long_paras,
        "dialog_lines": dialog_lines,
        "dialog_ratio": round(dialog_lines / len(lines) * 100, 1) if lines else 0,
        "ai_smell_hits": ai_hits,
        "ai_smell_total": sum(ai_hits.values()),
        "ai_smell_density": round(sum(ai_hits.values()) / max(total_chars, 1) * 1000, 2),
        "estimated_read_time_min": round(total_chars / 400, 1),  # 400 chars/min avg
    }

def analyze_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    result = count_chapter(text)
    result["file"] = path
    result["filename"] = Path(path).name
    result["size_kb"] = round(os.path.getsize(path) / 1024, 1)
    return result

def analyze_dir(path: str):
    files = sorted(Path(path).glob("*.md")) + sorted(Path(path).glob("*.txt"))
    if not files:
        files = sorted(Path(path).rglob("*.[mdt][dx]*t"))  # .md, .txt
    results = []
    for f in files:
        try:
            r = analyze_file(str(f))
            results.append(r)
        except:
            pass

    # Summary
    print(f"\n{'='*60}")
    print(f"📊 字数统计报告 — {path}")
    print(f"{'='*60}\n")

    # Per-file
    print(f"{'文件':<30} {'字数':>8} {'段落':>6} {'对话%':>8} {'AI味':>8} {'阅读时间':>10}")
    print("-"*70)
    total_chars = 0
    for r in results:
        total_chars += r["total_chars"]
        print(f"{r['filename']:<30} {r['total_chars']:>8} {r['total_paragraphs']:>6} "
              f"{r['dialog_ratio']:>7}% {r['ai_smell_total']:>5}/kw "
              f"{r['estimated_read_time_min']:>7}min")
    print("-"*70)
    print(f"{'总计':<30} {total_chars:>8} ({len(results)} files)")

    if results:
        avg_dialog = sum(r["dialog_ratio"] for r in results) / len(results)
        avg_ai = sum(r["ai_smell_total"] for r in results) / len(results)
        avg_len = total_chars / len(results)
        print(f"\n📈 平均数据：")
        print(f"  每章字数: {avg_len:.0f}")
        print(f"  对话占比: {avg_dialog:.1f}%")
        print(f"  AI味关键词: {avg_ai:.1f} 处/章")
        print(f"  估计总阅读时间: {total_chars/400:.0f} 分钟")

        # Grade
        print(f"\n🏆 综合评级：")
        if avg_dialog >= 40:
            print(f"  ✅ 对话密度: 优秀 (≥40%)")
        elif avg_dialog >= 30:
            print(f"  ⚠️ 对话密度: 及格 (30-40%)")
        else:
            print(f"  ❌ 对话密度: 不足 (<30%) — 建议增加对话")

        if avg_ai <= 5:
            print(f"  ✅ AI味控制: 优秀 (≤5处/章)")
        elif avg_ai <= 10:
            print(f"  ⚠️ AI味控制: 中等 (5-10处/章) — 建议去AI味处理")
        else:
            print(f"  ❌ AI味控制: 严重 (>10处/章) — 必须去AI味处理")

        if 1500 <= avg_len <= 3500:
            print(f"  ✅ 章节字数: 合适 (1500-3500)")
        elif avg_len < 1500:
            print(f"  ⚠️ 章节字数: 偏短 (<1500) — 建议扩写")
        else:
            print(f"  ⚠️ 章节字数: 偏长 (>3500) — 番茄文建议减到2000以内")

    return results

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    target = sys.argv[1]

    if target == "--watch":
        print("📡 Watch mode — run regularly to track word count trends")
        print("   Recommended: cronjob every 24h")
        print("   hermes cronjob create --schedule '0 9 * * *' --prompt 'run word count'")
        sys.exit(0)

    if target == "--compare":
        if len(sys.argv) < 4:
            print("Usage: word-count-tool.py --compare A.md B.md")
            sys.exit(1)
        a = analyze_file(sys.argv[2])
        b = analyze_file(sys.argv[3])
        print(f"\n📊 对比: {a['filename']} vs {b['filename']}\n")
        print(f"{'指标':<20} {a['filename']:<20} {b['filename']:<20}")
        print("-"*60)
        for k in ["total_chars", "total_paragraphs", "dialog_ratio", "ai_smell_total", "avg_para_len"]:
            va = a.get(k, 0)
            vb = b.get(k, 0)
            u = "%" if k == "dialog_ratio" else (" 处" if k == "ai_smell_total" else "")
            print(f"{k:<20} {va:<20} {vb:<20}")
        sys.exit(0)

    if os.path.isdir(target):
        analyze_dir(target)
    elif os.path.isfile(target):
        r = analyze_file(target)
        print(f"\n📄 {r['filename']}")
        print(f"{'='*40}")
        for k, v in r.items():
            if k in ["file", "filename"]:
                continue
            print(f"  {k}: {v}")
    else:
        print(f"File not found: {target}")
        sys.exit(1)

if __name__ == "__main__":
    main()
