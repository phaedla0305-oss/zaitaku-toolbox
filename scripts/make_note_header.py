"""note 見出し画像（1280x670）の A案・B案を作る。

元画像（ChatGPT作成の①案）の見出し文字と表を消し、文字と罫線を Pillow で正確に描き直して合成する。
- 見出し・表見出しのフォント：Yu Gothic Bold（Windows 標準フォントを参照するだけで、フォントファイルは配布・同梱しない）
- 手（表に重なる部分）は前景として残す
- 出力：output/note/ に PNG（A・B）、背景（文字・罫線なし）、手の前景、編集用 SVG
使い方：python scripts/make_note_header.py
"""
from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output/note/subscription-concept-1-1280x670.png"
OUT = ROOT / "output/note"
FONT = "C:/Windows/Fonts/YuGothB.ttc"  # index 0 = Yu Gothic Bold
FONT_NAME = "Yu Gothic"
W, H = 1280, 670
SS = 4  # 描画の超解像倍率（アンチエイリアス用）

HEADLINE = ["サブスク料金、", "見直す前に整理しよう"]
LABELS = ["サービス", "支払額", "更新日"]

INK = (52, 50, 44)
LABEL_INK = (56, 64, 50)
LINE = (120, 148, 116)
BAND = (208, 223, 192)


def lum(p):
    return 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]


def grain(img: Image.Image, amount: int = 3, seed: int = 7) -> Image.Image:
    rnd = random.Random(seed)
    n = Image.effect_noise(img.size, 12).convert("L")
    n = n.point(lambda v: 128 + (v - 128) * amount // 12)
    return ImageChops.add(ImageChops.subtract(img, Image.merge("RGB", [n] * 3).point(lambda v: max(0, 128 - v))),
                          Image.merge("RGB", [n] * 3).point(lambda v: max(0, v - 128)))


def erase(img: Image.Image, box, select, grow: int = 5, filt: int = 23) -> Image.Image:
    """box 内で select(p) が真の画素（文字や罫線）を、周りの紙・背景の色で埋める。"""
    x0, y0, x1, y1 = box
    region = img.crop(box)
    m = Image.new("L", region.size, 0)
    rp, mp = region.load(), m.load()
    for y in range(region.height):
        for x in range(region.width):
            if select(rp[x, y]):
                mp[x, y] = 255
    m = m.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    # 文字以外の画素だけで周りの色を平均する（正規化たたみ込み）。明るい跡が残らない
    keep = ImageChops.invert(m)
    masked = ImageChops.multiply(region, Image.merge("RGB", [keep] * 3))
    n = region.width * region.height
    done = [False] * n
    res = [(0, 0, 0)] * n
    for radius in (filt, filt * 2, filt * 4):  # 広い文字の内側まで埋まるよう段階的に広げる
        kw = list(keep.filter(ImageFilter.GaussianBlur(radius)).get_flattened_data())
        num = list(masked.filter(ImageFilter.GaussianBlur(radius)).get_flattened_data())
        for i in range(n):
            if not done[i] and kw[i] > 20:
                w = kw[i] / 255.0
                r_, g_, b_ = num[i]
                res[i] = (min(255, round(r_ / w)), min(255, round(g_ / w)), min(255, round(b_ / w)))
                done[i] = True
    bg = Image.new("RGB", region.size)
    bg.putdata(res)
    bg = grain(bg, 3)
    m = m.filter(ImageFilter.GaussianBlur(1.5))
    out = img.copy()
    out.paste(Image.composite(bg, region, m), (x0, y0))
    return out


def text_center(draw: ImageDraw.ImageDraw, cx: float, cy: float, s: str, font, fill):
    """文字のインク（実際に描かれる範囲）の中心を (cx, cy) に合わせる。"""
    # 字形の外枠ではなく、実際に濃く描かれる画素の範囲で中心を出す（「日」などの余白の偏りを補正）
    l, t, r, b = draw.textbbox((0, 0), s, font=font)
    tmp = Image.new("L", (int(r - l) + 40, int(b - t) + 40), 0)
    ImageDraw.Draw(tmp).text((20 - l, 20 - t), s, font=font, fill=255)
    il, it, ir, ib = tmp.point(lambda v: 255 if v > 110 else 0).getbbox()
    ink_cx = (il + ir) / 2 - 20 + l
    ink_cy = (it + ib) / 2 - 20 + t
    draw.text((cx - ink_cx, cy - ink_cy), s, font=font, fill=fill)


def paper_mask(src: Image.Image, box) -> Image.Image:
    """表の紙・罫線・見出し帯の画素は 255、手（肌色）・袖は 0。"""
    m = Image.new("L", (W, H), 0)
    sp, mp = src.load(), m.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = sp[x, y]
            skin = (r - b) > 52 and r > 150
            if not skin:
                mp[x, y] = 255
    # 手の輪郭を少し内側に（にじみ防止）
    return m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))


def draw_table(layer: Image.Image, cols, rows, label_size: int, line_w: float, labels=LABELS):
    d = ImageDraw.Draw(layer)
    s = SS
    x0, x1 = cols[0], cols[-1]
    # 見出し帯（やわらかい緑。紙の質感を残すため不透明度を少し下げる）
    d.rectangle([x0 * s, rows[0] * s, x1 * s, rows[1] * s], fill=BAND + (250,))
    lw = round(line_w * s)
    for y in rows:
        d.line([(x0 * s, y * s), (x1 * s, y * s)], fill=LINE + (255,), width=lw)
    for x in cols:
        d.line([(x * s, rows[0] * s), (x * s, rows[-1] * s)], fill=LINE + (255,), width=lw)
    f = ImageFont.truetype(FONT, label_size * s, index=0)
    for i, lab in enumerate(labels):
        cx = (cols[i] + cols[i + 1]) / 2 * s
        cy = (rows[0] + rows[1]) / 2 * s
        text_center(d, cx, cy, lab, f, LABEL_INK + (255,))


def finalize(layer: Image.Image) -> Image.Image:
    return layer.resize((W, H), Image.LANCZOS)


def build():
    src = Image.open(SRC).convert("RGB")
    assert src.size == (W, H), src.size

    # 1) 見出し文字を消す（低彩度の濃い画素＝文字。葉・マグ・下線は残す）
    head_sel = lambda p: lum(p) < 205 and (max(p) - min(p)) < 45
    clean = erase(src, (255, 10, 1095, 200), head_sel, grow=5, filt=25)

    # 2) 表の文字と罫線を消す（紙の範囲だけ。手は残す）
    tbox = (300, 284, 1092, 670)
    tab_sel = lambda p: lum(p) < 236 and (p[0] - p[2]) < 52
    clean_t = erase(clean, tbox, tab_sel, grow=3, filt=17)
    pm = paper_mask(src, tbox)
    clean = Image.composite(clean_t, clean, pm)

    # 手の前景（表に重なる部分）を切り出して保存（SVG 用）
    hands = src.copy().convert("RGBA")
    inv = ImageChops.invert(pm)
    box_mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(box_mask).rectangle(tbox, fill=255)
    hands.putalpha(ImageChops.multiply(inv, box_mask))

    clean.save(OUT / "subscription-header-background-clean.png")
    hands.save(OUT / "subscription-header-hands-foreground.png")

    # B案は見出しを大きくして下線を描き直すため、元の下線（オレンジのにじみ）を消した背景を使う
    orange_sel = lambda p: (p[0] - p[2]) > 55 and lum(p) < 238
    clean_b = erase(clean, (330, 190, 965, 242), orange_sel, grow=4, filt=15)
    clean_b.save(OUT / "subscription-header-B-background-clean.png")

    results = {}
    for variant in ("A", "B"):
        base = (clean if variant == "A" else clean_b).copy().convert("RGBA")
        if variant == "A":
            cols = [322, 616, 839, 1062]
            rows = [298, 366, 433, 500, 568, 635]
            head_size, head_lines_y = 76, [76, 162]
            label_size, line_w = 30, 2.4
        else:
            cols = [322, 616, 839, 1062]
            rows = [300, 382, 476, 570, 664]
            head_size, head_lines_y = 86, [72, 168]
            label_size, line_w = 40, 3.0

        # 表（紙の上だけに描き、手は上に残す）
        tl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        draw_table(tl, cols, rows, label_size, line_w)
        tl = finalize(tl)
        a = ImageChops.multiply(tl.getchannel("A"), pm)
        tl.putalpha(a)
        base = Image.alpha_composite(base, tl)

        # 見出し
        hl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hl)
        if variant == "B":
            # 小さく表示しても読めるよう、見出しの後ろにクリーム色の紙を敷き、下線を描き直す
            panel = Image.new("L", (W, H), 0)
            ImageDraw.Draw(panel).rounded_rectangle([150, 14, 1130, 236], radius=28, fill=235)
            panel = panel.filter(ImageFilter.GaussianBlur(9)).resize((W * SS, H * SS))
            cream = Image.new("RGBA", (W * SS, H * SS), (252, 245, 230, 255))
            cream.putalpha(panel)
            hl = Image.alpha_composite(hl, cream)
            hd = ImageDraw.Draw(hl)
        f = ImageFont.truetype(FONT, head_size * SS, index=0)
        cx = 645 * SS
        if variant == "B":
            # 下線（やわらかいオレンジ）。2行目の下に、文字幅に合わせる
            l, t, r, b = hd.textbbox((0, 0), HEADLINE[1], font=f)
            wline = (r - l)
            y = (head_lines_y[1] * SS) + (b - t) / 2 + 14 * SS
            hd.rounded_rectangle([cx - wline / 2 + 30 * SS, y, cx + wline / 2 - 30 * SS, y + 9 * SS],
                                 radius=5 * SS, fill=(236, 150, 104, 150))
        for line, y in zip(HEADLINE, head_lines_y):
            text_center(hd, cx, y * SS, line, f, INK + (255,))
        hl = finalize(hl)
        base = Image.alpha_composite(base, hl)

        out = base.convert("RGB")
        path = OUT / f"subscription-header-{variant}-1280x670.png"
        out.save(path, optimize=True)
        results[variant] = dict(path=path, cols=cols, rows=rows, head_size=head_size, head_y=head_lines_y,
                                label_size=label_size, line_w=line_w)
        write_svg(variant, results[variant])
    return results


def write_svg(variant: str, r: dict):
    cols, rows = r["cols"], r["rows"]
    lines = []
    for y in rows:
        lines.append(f'<line x1="{cols[0]}" y1="{y}" x2="{cols[-1]}" y2="{y}"/>')
    for x in cols:
        lines.append(f'<line x1="{x}" y1="{rows[0]}" x2="{x}" y2="{rows[-1]}"/>')
    labels = "\n".join(
        f'  <text x="{(cols[i] + cols[i + 1]) / 2}" y="{(rows[0] + rows[1]) / 2}" class="label">{s}</text>'
        for i, s in enumerate(LABELS))
    heads = "\n".join(
        f'  <text x="645" y="{y}" class="head">{s}</text>' for s, y in zip(HEADLINE, r["head_y"]))
    panel = ('<rect x="150" y="14" width="980" height="222" rx="28" fill="#FCF5E6" opacity="0.92" filter="url(#soft)"/>'
             if variant == "B" else "")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <!-- 編集用データ（{variant}案）。文字は <text> を直接書き換えられる。フォント：{FONT_NAME} Bold（利用者の環境のフォントを参照。ファイルは同梱しない） -->
  <!-- 正式な出力は scripts/make_note_header.py で作る PNG。SVG は表示ソフトによって文字の位置が少しずれることがある -->
  <defs><filter id="soft"><feGaussianBlur stdDeviation="6"/></filter>
  <style>
    .head {{ font-family: "{FONT_NAME}", "Noto Sans JP", sans-serif; font-weight: 700; font-size: {r["head_size"]}px; fill: rgb{INK}; text-anchor: middle; dominant-baseline: central; }}
    .label {{ font-family: "{FONT_NAME}", "Noto Sans JP", sans-serif; font-weight: 700; font-size: {r["label_size"]}px; fill: rgb{LABEL_INK}; text-anchor: middle; dominant-baseline: central; }}
    .grid line {{ stroke: rgb{LINE}; stroke-width: {r["line_w"]}; stroke-linecap: square; }}
  </style></defs>
  <image href="{"subscription-header-background-clean.png" if variant == "A" else "subscription-header-B-background-clean.png"}" x="0" y="0" width="{W}" height="{H}"/>
  <rect x="{cols[0]}" y="{rows[0]}" width="{cols[-1] - cols[0]}" height="{rows[1] - rows[0]}" fill="rgb{BAND}" opacity="0.92"/>
  <g class="grid">
    {"".join(lines)}
  </g>
{labels}
  <image href="subscription-header-hands-foreground.png" x="0" y="0" width="{W}" height="{H}"/>
  {panel}
{heads}
</svg>
'''
    (OUT / f"subscription-header-{variant}-editable.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    for k, v in build().items():
        print(k, v["path"].name, round(v["path"].stat().st_size / 1e6, 2), "MB")
