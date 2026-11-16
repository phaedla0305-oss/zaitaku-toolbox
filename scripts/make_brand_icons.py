"""ブランドアイコンの試作（3案）。AI画像を使わず、図形を数値で描く。
出力：output/brand/icon-{1,2,3}.png（400x400）と icon-{1,2,3}.svg、比較シート icons-compare.png
使い方：python scripts/make_brand_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/brand"
OUT.mkdir(parents=True, exist_ok=True)
NAVY, ORANGE, CREAM = "#1F3A5F", "#F28C28", "#FAF6EE"
S, SS = 400, 4  # 出力サイズ、超解像倍率

# 各案の図形（400x400 の座標）。("rrect", x0,y0,x1,y1, r, stroke, fill?) / ("line", x0,y0,x1,y1, w) / ("rect", x0,y0,x1,y1, r, fillcolor)
ICONS = {
    1: {  # 角丸の道具箱：太い輪郭＋持ち手＋留め具
        "name": "角丸の道具箱",
        "shapes": [
            ("rrect", 150, 92, 250, 150, 18, 22, None),        # 持ち手
            ("rect", 140, 140, 260, 160, 0, CREAM),             # 持ち手の下側を箱の上辺で隠す
            ("rrect", 92, 140, 308, 300, 30, 22, None),        # 箱
            ("bar", 103, 185, 297, 207),                        # ふたの合わせ目（箱の内側だけ）
            ("rect", 182, 182, 218, 222, 8, ORANGE),            # 留め具（オレンジ）
        ],
    },
    2: {  # 整理カード：大小のカードを重ね、手前の角だけオレンジ
        "name": "整理カード",
        "shapes": [
            ("rrect", 96, 104, 276, 248, 24, 20, None),        # 奥のカード
            ("rrect", 142, 168, 310, 300, 24, 20, CREAM),      # 手前のカード（背景色で塗って奥を隠す）
            ("line", 172, 214, 262, 214, 18),                   # 手前のカードの行
            ("line", 172, 254, 232, 254, 18),
            ("corner", 310, 300, 24, 20, ORANGE),              # 手前のカードの右下の角だけオレンジ
        ],
    },
    3: {  # 仕切りトレー：角丸の外枠を縦線で区切り、片側に小さなオレンジの四角
        "name": "仕切りトレー",
        "shapes": [
            ("rrect", 84, 120, 316, 284, 28, 22, None),        # 外枠
            ("line", 162, 131, 162, 273, 18),                   # 仕切り
            ("line", 239, 131, 239, 273, 18),
            ("rect", 260, 182, 296, 218, 8, ORANGE),            # 片側の小さな四角
        ],
    },
}


def draw_icon(spec, size=S):
    k = SS
    im = Image.new("RGB", (size * k, size * k), CREAM)
    d = ImageDraw.Draw(im)
    f = size / 400 * k
    for sh in spec["shapes"]:
        t = sh[0]
        if t == "rrect":
            _, x0, y0, x1, y1, r, w, fill = sh
            d.rounded_rectangle([x0 * f, y0 * f, x1 * f, y1 * f], radius=r * f, outline=NAVY, width=round(w * f),
                                fill=fill)
        elif t == "rect":
            _, x0, y0, x1, y1, r, color = sh
            d.rounded_rectangle([x0 * f, y0 * f, x1 * f, y1 * f], radius=r * f, fill=color)
        elif t == "line":
            _, x0, y0, x1, y1, w = sh
            d.line([x0 * f, y0 * f, x1 * f, y1 * f], fill=NAVY, width=round(w * f))
            for x, y in ((x0, y0), (x1, y1)):  # 線の端を丸める
                rr = w / 2 * f
                d.ellipse([x * f - rr, y * f - rr, x * f + rr, y * f + rr], fill=NAVY)
        elif t == "bar":
            _, x0, y0, x1, y1 = sh
            d.rectangle([x0 * f, y0 * f, x1 * f, y1 * f], fill=NAVY)
        elif t == "corner":
            _, x1, y1, r, w, color = sh
            # 角の部分の輪郭線だけをオレンジで塗り直す（四分円の弧）
            box = [(x1 - 2 * r) * f, (y1 - 2 * r) * f, x1 * f, y1 * f]
            d.arc(box, start=0, end=90, fill=color, width=round(w * f))
            d.line([(x1 - w / 2) * f, (y1 - r) * f, (x1 - w / 2) * f, (y1 - r - 26) * f], fill=color, width=round(w * f))
            d.line([(x1 - r) * f, (y1 - w / 2) * f, (x1 - r - 26) * f, (y1 - w / 2) * f], fill=color, width=round(w * f))
    return im.resize((size, size), Image.LANCZOS)


def to_svg(spec):
    parts = []
    for sh in spec["shapes"]:
        t = sh[0]
        if t == "rrect":
            _, x0, y0, x1, y1, r, w, fill = sh
            parts.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{fill or "none"}" '
                         f'stroke="{NAVY}" stroke-width="{w}"/>')
        elif t == "rect":
            _, x0, y0, x1, y1, r, color = sh
            parts.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{r}" fill="{color}"/>')
        elif t == "line":
            _, x0, y0, x1, y1, w = sh
            parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{NAVY}" stroke-width="{w}" stroke-linecap="round"/>')
        elif t == "bar":
            _, x0, y0, x1, y1 = sh
            parts.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{NAVY}"/>')
        elif t == "corner":
            _, x1, y1, r, w, color = sh
            parts.append(f'<path d="M{x1 - w / 2} {y1 - r - 26} V{y1 - r} A{r - w / 2} {r - w / 2} 0 0 1 {x1 - r} {y1 - w / 2} H{x1 - r - 26}" '
                         f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
    body = "\n  ".join(parts)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">\n'
            f'  <!-- {spec["name"]}（試作）。色：紺{NAVY}・オレンジ{ORANGE}・背景{CREAM} -->\n'
            f'  <rect width="400" height="400" fill="{CREAM}"/>\n  {body}\n</svg>\n')


def circle(im, size, bg="white"):
    im = im.resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    out = Image.new("RGB", (size, size), bg)
    out.paste(im, (0, 0), m.resize((size, size), Image.LANCZOS))
    return out


def compare(imgs):
    font = ImageFont.truetype("C:/Windows/Fonts/YuGothB.ttc", 18, index=0)
    W = 3 * 330 + 40
    sheet = Image.new("RGB", (W, 470), "white")
    d = ImageDraw.Draw(sheet)
    for i, (n, im) in enumerate(imgs):
        x = 20 + i * 330
        d.text((x, 10), f"案{n}：{ICONS[n]['name']}", font=font, fill="#222")
        sheet.paste(circle(im, 200), (x, 45))
        # 小さく表示したとき（Xのタイムライン・noteの記事一覧相当）
        sheet.paste(circle(im, 48), (x, 270))
        sheet.paste(circle(im, 32), (x + 60, 278))
        sheet.paste(circle(im, 24), (x + 105, 282))
        d.text((x, 330), "200px／48px／32px／24px（丸く切り抜き）", font=ImageFont.truetype("C:/Windows/Fonts/YuGothM.ttc", 13, index=0), fill="#555")
        # 暗い背景（Xのダークモード）
        dark = Image.new("RGB", (150, 70), "#15202B")
        dark.paste(circle(im, 48, "#15202B"), (10, 11))
        sheet.paste(dark, (x, 360))
    return sheet


if __name__ == "__main__":
    imgs = []
    for n, spec in ICONS.items():
        im = draw_icon(spec)
        im.save(OUT / f"icon-{n}.png")
        (OUT / f"icon-{n}.svg").write_text(to_svg(spec), encoding="utf-8")
        imgs.append((n, im))
    compare(imgs).save(OUT / "icons-compare.png")
    print("ok", [p.name for p in sorted(OUT.iterdir())])
