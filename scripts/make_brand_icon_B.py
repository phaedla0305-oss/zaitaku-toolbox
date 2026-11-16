"""共通アイコン B「電波の持ち手」の仕上げ。
決定事項：紺の箱・オレンジの留め具・クリーム背景を維持。モチーフは追加しない。
調整するのは「電波の弧の間隔」「箱との余白」「縮小時の見やすさ」だけ。
出力：output/brand/B/icon-B-{1,2,3}.png（400x400）・.svg、比較シート icon-B-compare.png
使い方：python scripts/make_brand_icon_B.py
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/brand/B"
OUT.mkdir(parents=True, exist_ok=True)
NAVY, ORANGE, CREAM = "#1F3A5F", "#F28C28", "#FAF6EE"
K = 4

# 候補（400x400 の座標）
# w=線の太さ、ri/ro=内側・外側の弧の半径（線の中心）、gap=内側の弧の端と箱の上辺のすき間、
# span=弧の開き角度、box=(幅, 高さ, 角丸)、cy=全体の縦中心
CANDIDATES = {
    "B-1": dict(note="現状に近い（基準）", w=24, ri=52, ro=96, gap=16, span=110, box=(224, 136, 28), scale=1.00),
    "B-2": dict(note="線を太く・弧の間隔と箱との余白を広く・全体を少し大きく", w=28, ri=50, ro=104, gap=22, span=104, box=(232, 140, 30), scale=1.06),
    "B-3": dict(note="さらに太く・弧の開きを狭く（小さい表示を優先）", w=32, ri=48, ro=108, gap=24, span=96, box=(236, 140, 32), scale=1.08),
}


def geometry(c):
    """弧・箱・合わせ目・留め具の座標を、全体が縦横の中央に来るように計算する。"""
    w, ri, ro, gap, span = c["w"], c["ri"], c["ro"], c["gap"], c["span"]
    bw, bh, br = c["box"]
    half = math.radians(span / 2)
    # 弧の中心を (0, 0) とする。端点の高さ = -r*cos(half)。内側の弧の端（線の下端）と箱の上辺の間を gap にする
    inner_end_y = -ri * math.cos(half) + w / 2
    box_top = inner_end_y + gap
    top = -ro - w / 2
    bottom = box_top + bh
    h = bottom - top
    s = c["scale"]
    oy = 200 - (top + h / 2) * s  # 縦中心を 200 に
    ox = 200
    T = lambda x, y: (ox + x * s, oy + y * s)
    g = dict(scale=s, w=w * s, arcs=[(T(0, 0), r * s) for r in (ro, ri)], half=half,
             box=(*T(-bw / 2, box_top), *T(bw / 2, bottom)), br=br * s)
    seam_y = box_top + bh * 0.30
    g["seam"] = (*T(-bw / 2, seam_y), *T(bw / 2, seam_y + 16))
    g["clasp"] = (*T(-20, seam_y - 10), *T(20, seam_y + 26))
    g["clasp_r"] = 9 * s
    return g


def draw(c, size=400):
    g = geometry(c)
    f = size / 400 * K
    im = Image.new("RGB", (size * K, size * K), CREAM)
    d = ImageDraw.Draw(im)
    w = g["w"]
    for (cx, cy), r in g["arcs"]:
        a0, a1 = 270 - math.degrees(g["half"]), 270 + math.degrees(g["half"])
        d.arc([(cx - r) * f, (cy - r) * f, (cx + r) * f, (cy + r) * f], start=a0, end=a1, fill=NAVY, width=round(w * f))
        for ang in (a0, a1):  # 端を丸める
            a = math.radians(ang)
            ex, ey = cx + (r - w / 2) * math.cos(a), cy + (r - w / 2) * math.sin(a)
            # 線幅の中心に端の丸を置く（弧は外側から内側へ w の幅で描かれる）
            rr = w / 2
            d.ellipse([(ex - rr) * f, (ey - rr) * f, (ex + rr) * f, (ey + rr) * f], fill=NAVY)
    x0, y0, x1, y1 = g["box"]
    d.rounded_rectangle([x0 * f, y0 * f, x1 * f, y1 * f], radius=g["br"] * f, fill=NAVY)
    sx0, sy0, sx1, sy1 = g["seam"]
    d.rectangle([sx0 * f, sy0 * f, sx1 * f, sy1 * f], fill=CREAM)
    cx0, cy0, cx1, cy1 = g["clasp"]
    d.rounded_rectangle([cx0 * f, cy0 * f, cx1 * f, cy1 * f], radius=g["clasp_r"] * f, fill=ORANGE)
    return im.resize((size, size), Image.LANCZOS)


def svg(name, c):
    g = geometry(c)
    parts = [f'<rect width="400" height="400" fill="{CREAM}"/>']
    for (cx, cy), r in g["arcs"]:
        rc = r - g["w"] / 2  # 線の中心の半径
        x1, y1 = cx - rc * math.sin(g["half"]), cy - rc * math.cos(g["half"])
        x2, y2 = cx + rc * math.sin(g["half"]), y1
        parts.append(f'<path d="M{x1:.1f} {y1:.1f} A{rc:.1f} {rc:.1f} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" '
                     f'stroke="{NAVY}" stroke-width="{g["w"]:.1f}" stroke-linecap="round"/>')
    x0, y0, x1, y1 = g["box"]
    parts.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" rx="{g["br"]:.1f}" fill="{NAVY}"/>')
    sx0, sy0, sx1, sy1 = g["seam"]
    parts.append(f'<rect x="{sx0:.1f}" y="{sy0:.1f}" width="{sx1 - sx0:.1f}" height="{sy1 - sy0:.1f}" fill="{CREAM}"/>')
    cx0, cy0, cx1, cy1 = g["clasp"]
    parts.append(f'<rect x="{cx0:.1f}" y="{cy0:.1f}" width="{cx1 - cx0:.1f}" height="{cy1 - cy0:.1f}" rx="{g["clasp_r"]:.1f}" fill="{ORANGE}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">\n'
            f'  <!-- 共通アイコン {name}：{c["note"]}。正は PNG（scripts/make_brand_icon_B.py） -->\n  '
            + "\n  ".join(parts) + "\n</svg>\n")


def circle(im, size, bg="white"):
    im = im.resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    out = Image.new("RGB", (size, size), bg)
    out.paste(im, (0, 0), m.resize((size, size), Image.LANCZOS))
    return out


if __name__ == "__main__":
    fb = ImageFont.truetype("C:/Windows/Fonts/YuGothB.ttc", 17, index=0)
    fs = ImageFont.truetype("C:/Windows/Fonts/YuGothM.ttc", 12, index=0)
    sheet = Image.new("RGB", (3 * 340 + 30, 560), "white")
    d = ImageDraw.Draw(sheet)
    for i, (name, c) in enumerate(CANDIDATES.items()):
        im = draw(c)
        im.save(OUT / f"icon-{name}.png")
        (OUT / f"icon-{name}.svg").write_text(svg(name, c), encoding="utf-8")
        x = 15 + i * 340
        d.text((x, 8), name, font=fb, fill="#222")
        d.text((x, 32), c["note"], font=fs, fill="#555")
        sheet.paste(circle(im, 180), (x, 58))
        sheet.paste(circle(im, 48), (x, 250))
        sheet.paste(circle(im, 32), (x + 60, 258))
        sheet.paste(circle(im, 24), (x + 104, 262))
        # 32px・24px をそのまま4倍に拡大（実際に画面に出る画素の見え方）
        sheet.paste(circle(im, 32).resize((128, 128), Image.NEAREST), (x, 310))
        sheet.paste(circle(im, 24).resize((96, 96), Image.NEAREST), (x + 140, 326))
        d.text((x, 444), "下段：32px・24pxを画素のまま4倍に拡大", font=fs, fill="#555")
        dark = Image.new("RGB", (150, 70), "#15202B")
        dark.paste(circle(im, 48, "#15202B"), (10, 11))
        dark.paste(circle(im, 32, "#15202B"), (70, 19))
        sheet.paste(dark, (x, 470))
    sheet.save(OUT / "icon-B-compare.png")
    print("ok")
