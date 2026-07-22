#!/usr/bin/env python3
"""生成 demo.gif: 用 PIL 渲染终端输出,展示 novel-tools 与 word-count-tool 的真实运行。
Usage: python3 scripts/gen-demo-gif.py
产物: assets/demo.gif
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
ASSETS.mkdir(exist_ok=True)
OUT = ASSETS / "demo.gif"

# 字体: 优先等宽中文兼容字体,回退默认
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
]
CN_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
]


def load_font(size):
    for p in CN_FONT_CANDIDATES + FONT_CANDIDATES:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def capture(cmd):
    """运行命令,返回输出文本。"""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15, cwd=ROOT)
        return r.stdout + (r.stderr if r.returncode else "")
    except Exception as e:
        return f"(error: {e})\n"


def render_frame(lines, font, w, h, pad=24, bg=(30, 30, 36), fg=(220, 220, 220),
                 title_fg=(120, 200, 255)):
    img = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(img)
    # 标题栏
    d.rectangle([0, 0, w, 32], fill=(50, 50, 58))
    d.ellipse([10, 11, 22, 23], fill=(255, 95, 86))
    d.ellipse([28, 11, 40, 23], fill=(255, 189, 46))
    d.ellipse([46, 11, 58, 23], fill=(39, 201, 63))
    d.text((w // 2 - 90, 8), "novel-creation-omnibus", font=load_font(14),
           fill=(170, 170, 170))
    # 正文
    y = 32 + pad
    for ln in lines:
        d.text((pad, y), ln, font=font, fill=fg)
        y += 22
    return img


def main():
    font = load_font(16)
    W, H = 1100, 620

    # 采集真实输出(各取头部若干行,避免过长)
    frames_data = []

    out1 = capture(["python3", "scripts/novel-tools.py",
                    "--check-continuity", "examples/sample-chapter.md"])
    frames_data.append((
        "$ python3 scripts/novel-tools.py --check-continuity examples/sample-chapter.md",
        out1.strip().split("\n")[:22],
    ))

    out2 = capture(["python3", "scripts/word-count-tool.py",
                    "examples/sample-chapter.md"])
    frames_data.append((
        "$ python3 scripts/word-count-tool.py examples/sample-chapter.md",
        out2.strip().split("\n")[:22],
    ))

    out3 = capture(["python3", "scripts/word-count-tool.py", "--json",
                    "examples/sample-chapter.md"])
    frames_data.append((
        "$ python3 scripts/word-count-tool.py --json examples/sample-chapter.md",
        out3.strip().split("\n")[:22],
    ))

    frames = []
    for title, body in frames_data:
        lines = [title, ""] + body
        frames.append(render_frame(lines, font, W, H))

    # 每帧停留 2 秒,循环
    frames[0].save(
        OUT, format="GIF", save_all=True, append_images=frames[1:],
        duration=2000, loop=0, optimize=True,
    )
    print(f"✓ 生成 {OUT} ({OUT.stat().st_size // 1024} KB, {len(frames)} 帧)")


if __name__ == "__main__":
    main()
