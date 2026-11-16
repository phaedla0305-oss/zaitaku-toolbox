"""ブランドアイコン 第2弾：道具箱を土台に、視認性と独自性を足した3案。
- 箱は塗りつぶし（細い線より小さく表示しても形が残る）
- 何を整える道具箱かを、持ち手や中身の形で表す
出力：output/brand/v2/icon-{A,B,C}.png・.svg、比較シート icons-v2-compare.png
使い方：python scripts/make_brand_icons_v2.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/brand/v2"
OUT.mkdir(parents=True, exist_ok=True)
NAVY, ORANGE, CREAM = "#1F3A5F", "#F28C28", "#FAF6EE"
S, K = 400, 4

# 共通の箱（塗り）：x 88〜312、y 176〜312、角丸28。ふたの合わせ目はクリームの帯
BOX = (88, 176, 312, 312, 28)
SEAM = (88, 214, 312, 230)
CLASP = (180, 204, 220, 240, 9)

VARIANTS = {
    "A": "屋根の持ち手（在宅）",
    "B": "電波の持ち手（回線）",
    "C": "カードが入った道具箱（契約の整理）",
}


def svg_parts(v):
    x0, y0, x1, y1, r = BOX
    p = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{NAVY}"/>',
         f'<rect x="{SEAM[0]}" y="{SEAM[1]}" width="{SEAM[2] - SEAM[0]}" height="{SEAM[3] - SEAM[1]}" fill="{CREAM}"/>',
         f'<rect x="{CLASP[0]}" y="{CLASP[1]}" width="{CLASP[2] - CLASP[0]}" height="{CLASP[3] - CLASP[1]}" rx="{CLASP[4]}" fill="{ORANGE}"/>']
    if v == "A":
        # 屋根の形の持ち手（家の輪郭）
        p.insert(0, f'<path d="M126 182 L200 104 L274 182" fill="none" stroke="{NAVY}" stroke-width="26" stroke-linejoin="round" stroke-linecap="round"/>')
    elif v == "B":
        # 電波（2本の弧）と点
        p.insert(0, f'<path d="M123 124 A84 84 0 0 1 277 124" fill="none" stroke="{NAVY}" stroke-width="24" stroke-linecap="round"/>')
        p.insert(0, f'<path d="M168 147 A40 40 0 0 1 232 147" fill="none" stroke="{NAVY}" stroke-width="24" stroke-linecap="round"/>')
    elif v == "C":
        # 箱から3枚のカードがのぞく（1枚だけオレンジ）。持ち手はなし
        for x, h, c in ((118, 92, NAVY), (176, 112, ORANGE), (234, 80, NAVY)):
            p.insert(0, f'<rect x="{x}" y="{196 - h}" width="48" height="{h + 20}" rx="10" fill="{c}"/>')
    return p


def draw(v, size=S):
    f = size / 400 * K
    im = Image.new("RGB", (size * K, size * K), CREAM)
    d = ImageDraw.Draw(im)
    if v == "A":
        pts = [(126, 182), (200, 104), (274, 182)]
        w = 26
        d.line([(x * f, y * f) for x, y in pts], fill=NAVY, width=round(w * f), joint="curve")
        for x, y in pts:
            rr = w / 2 * f
            d.ellipse([x * f - rr, y * f - rr, x * f + rr, y * f + rr], fill=NAVY)
    elif v == "B":
        for cx, cy, r in ((200, 214, 92), (200, 202, 50)):
            pass
        # 外側の弧：中心(200,232) 半径100、内側：中心(200,232) 半径58（箱の上に乗る電波）
        for r, w in ((96, 24), (52, 24)):
            box = [(200 - r) * f, (178 - r) * f, (200 + r) * f, (178 + r) * f]
            d.arc(box, start=215, end=325, fill=NAVY, width=round(w * f))
            import math
            for ang in (215, 325):  # 弧の端を丸める
                a = math.radians(ang)
                ex, ey = 200 + (r - w / 2) * math.cos(a), 178 + (r - w / 2) * math.sin(a)
                rr = w / 2 * f
                d.ellipse([ex * f - rr, ey * f - rr, ex * f + rr, ey * f + rr], fill=NAVY)
    elif v == "C":
        for x, h, c in ((118, 92, NAVY), (176, 112, ORANGE), (234, 80, NAVY)):
            d.rounded_rectangle([x * f, (196 - h) * f, (x + 48) * f, 216 * f], radius=10 * f, fill=c)
            # カードと箱の間に細いすき間（クリーム）を入れて形を分ける
    x0, y0, x1, y1, r = BOX
    if v == "C":
        d.rounded_rectangle([(x0 - 6) * f, (y0 - 6) * f, (x1 + 6) * f, (y1 + 6) * f], radius=(r + 6) * f, fill=CREAM)
    d.rounded_rectangle([x0 * f, y0 * f, x1 * f, y1 * f], radius=r * f, fill=NAVY)
    d.rectangle([SEAM[0] * f, SEAM[1] * f, SEAM[2] * f, SEAM[3] * f], fill=CREAM)
    d.rounded_rectangle([CLASP[0] * f, CLASP[1] * f, CLASP[2] * f, CLASP[3] * f], radius=CLASP[4] * f, fill=ORANGE)
    return im.resize((size, size), Image.LANCZOS)


def circle(im, size, bg="white"):
    im = im.resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    out = Image.new("RGB", (size, size), bg)
    out.paste(im, (0, 0), m.resize((size, size), Image.LANCZOS))
    return out


if __name__ == "__main__":
    fb = ImageFont.truetype("C:/Windows/Fonts/YuGothB.ttc", 18, index=0)
    fs = ImageFont.truetype("C:/Windows/Fonts/YuGothM.ttc", 13, index=0)
    sheet = Image.new("RGB", (3 * 330 + 40, 470), "white")
    d = ImageDraw.Draw(sheet)
    for i, (v, name) in enumerate(VARIANTS.items()):
        im = draw(v)
        im.save(OUT / f"icon-{v}.png")
        (OUT / f"icon-{v}.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">\n'
            f'  <!-- 案{v}：{name}（試作）。PNG は scripts/make_brand_icons_v2.py の描画が正。SVG は編集用 -->\n'
            f'  <rect width="400" height="400" fill="{CREAM}"/>\n  ' + "\n  ".join(svg_parts(v)) + "\n</svg>\n",
            encoding="utf-8")
        x = 20 + i * 330
        d.text((x, 10), f"案{v}：{name}", font=fb, fill="#222")
        sheet.paste(circle(im, 200), (x, 45))
        sheet.paste(circle(im, 48), (x, 270))
        sheet.paste(circle(im, 32), (x + 60, 278))
        sheet.paste(circle(im, 24), (x + 105, 282))
        d.text((x, 330), "200px／48px／32px／24px（丸く切り抜き）", font=fs, fill="#555")
        dark = Image.new("RGB", (150, 70), "#15202B")
        dark.paste(circle(im, 48, "#15202B"), (10, 11))
        sheet.paste(dark, (x, 360))
    sheet.save(OUT / "icons-v2-compare.png")
    print("ok")
