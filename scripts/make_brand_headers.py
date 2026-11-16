"""X と note のヘッダー画像（共通アイコンと同じトーン：クリーム背景・紺の文字・オレンジは1か所だけ）。
- X：1500x500。左下はプロフィール画像が重なるので、文字とマークは右寄りの中央に置く
- note（クリエイターページ）：1920x1006。表示されるのは縦方向の中央 324px（note公式のお知らせ）。スマホでは左右も切れるため中央にまとめる
出力：output/brand/headers/ に PNG と、表示範囲を重ねた確認用画像
使い方：python scripts/make_brand_headers.py
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_brand_icon_B as icon  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/brand/headers"
OUT.mkdir(parents=True, exist_ok=True)
NAVY, ORANGE, CREAM = "#1F3A5F", "#F28C28", "#FAF6EE"
SUBTLE = "#55697F"  # 補足文字（紺を薄めた色。緑は小さな文字に使わない決まり）
FB = "C:/Windows/Fonts/YuGothB.ttc"
FM = "C:/Windows/Fonts/YuGothM.ttc"
K = 3
MARK = icon.CANDIDATES["B-1"]


def mark(d: ImageDraw.ImageDraw, cx, cy, size, f):
    """共通アイコンのマーク（背景なし）を、中心 (cx, cy)・一辺 size で描く。"""
    g = icon.geometry(MARK)
    s = size / 400
    T = lambda x, y: ((cx + (x - 200) * s) * f, (cy + (y - 200) * s) * f)
    w = g["w"] * s
    for (ax, ay), r in g["arcs"]:
        a0, a1 = 270 - math.degrees(g["half"]), 270 + math.degrees(g["half"])
        (x0, y0), (x1, y1) = T(ax - r, ay - r), T(ax + r, ay + r)
        d.arc([x0, y0, x1, y1], start=a0, end=a1, fill=NAVY, width=round(w * f))
        for ang in (a0, a1):
            a = math.radians(ang)
            ex, ey = T(ax + (r - g["w"] / 2) * math.cos(a), ay + (r - g["w"] / 2) * math.sin(a))
            rr = w / 2 * f
            d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=NAVY)
    bx0, by0, bx1, by1 = g["box"]
    d.rounded_rectangle([*T(bx0, by0), *T(bx1, by1)], radius=g["br"] * s * f, fill=NAVY)
    sx0, sy0, sx1, sy1 = g["seam"]
    d.rectangle([*T(sx0, sy0), *T(sx1, sy1)], fill=CREAM)
    cx0, cy0, cx1, cy1 = g["clasp"]
    d.rounded_rectangle([*T(cx0, cy0), *T(cx1, cy1)], radius=g["clasp_r"] * s * f, fill=ORANGE)


def ink_box(d, text, font):
    l, t, r, b = d.textbbox((0, 0), text, font=font)
    return l, t, r, b


def block(W, H, cx, cy, title, tagline, sub, title_px, f):
    """マーク＋ブランド名＋一言＋補足を1つのまとまりとして (cx, cy) を中心に描く。"""
    im = Image.new("RGB", (W * f, H * f), CREAM)
    d = ImageDraw.Draw(im)
    ft = ImageFont.truetype(FB, title_px * f, index=0)
    fg = ImageFont.truetype(FB, round(title_px * 0.42) * f, index=0)
    fs = ImageFont.truetype(FM, round(title_px * 0.34) * f, index=0)
    msize = title_px * 2.6  # マークの見た目の高さが、文字のまとまりの高さに近くなる大きさ
    gap = title_px * 0.35
    tl, tt, tr, tb = ink_box(d, title, ft)
    gl, gt, gr, gb = ink_box(d, tagline, fg)
    sl, st, sr, sb = ink_box(d, sub, fs)
    text_w = max(tr - tl, gr - gl, sr - sl) / f
    total_w = msize + gap + text_w
    x0 = cx - total_w / 2
    # 文字の行（ブランド名・下線・一言・補足）の高さ
    lines_h = (tb - tt) / f + title_px * 0.30 + 6 + title_px * 0.32 + (gb - gt) / f + title_px * 0.22 + (sb - st) / f
    y = cy - lines_h / 2
    mark(d, x0 + msize / 2, cy, msize, f)
    tx = x0 + msize + gap
    d.text(((tx * f) - tl, y * f - tt), title, font=ft, fill=NAVY)
    y += (tb - tt) / f + title_px * 0.30
    # オレンジの短い下線（強調はここ1か所）
    d.rounded_rectangle([tx * f, y * f, (tx + title_px * 1.4) * f, (y + 6) * f], radius=3 * f, fill=ORANGE)
    y += 6 + title_px * 0.32
    d.text(((tx * f) - gl, y * f - gt), tagline, font=fg, fill=NAVY)
    y += (gb - gt) / f + title_px * 0.22
    d.text(((tx * f) - sl, y * f - st), sub, font=fs, fill=SUBTLE)
    return im.resize((W, H), Image.LANCZOS)


def x_header():
    W, H = 1500, 500
    im = block(W, H, 905, 238, "在宅ワーク道具箱", "在宅で働く人の、道具と固定費を整える", "回線・VPN・作業環境と、契約・支払いの整理", 74, K)
    im.save(OUT / "x-header-1500x500.png")
    # 確認用：プロフィール画像が重なる位置（Xのパソコン表示の目安）と、スマホで上下が切れる目安
    chk = im.copy().convert("RGBA")
    ov = Image.new("RGBA", chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    av = Image.open(icon.OUT / "icon-B-1.png").resize((300, 300))
    m = Image.new("L", (300, 300), 0)
    ImageDraw.Draw(m).ellipse([0, 0, 299, 299], fill=255)
    od.rectangle([0, 0, W, 40], fill=(255, 0, 0, 40))
    od.rectangle([0, H - 40, W, H], fill=(255, 0, 0, 40))
    chk = Image.alpha_composite(chk, ov)
    ring = Image.new("RGBA", (312, 312), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse([0, 0, 311, 311], fill=(255, 255, 255, 255))
    chk.paste(ring, (44, 344), ring)
    chk.paste(av, (50, 350), m)
    chk.convert("RGB").save(OUT / "x-header-check.png")


def note_header():
    W, H = 1920, 1006
    im = block(W, H, 960, 503, "在宅ワーク道具箱", "在宅で働く人の、道具と固定費を整える", "契約と支払いを、払う前に整理するメモ", 64, K)
    im.save(OUT / "note-header-1920x1006.png")
    # 確認用：表示される中央324pxの帯と、スマホで左右が切れる目安（中央1100px）
    chk = im.copy().convert("RGBA")
    ov = Image.new("RGBA", chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    top = (H - 324) // 2
    od.rectangle([0, 0, W, top], fill=(0, 0, 0, 90))
    od.rectangle([0, top + 324, W, H], fill=(0, 0, 0, 90))
    od.rectangle([(W - 1100) // 2, top, (W + 1100) // 2, top + 324], outline=(255, 0, 0, 200), width=4)
    Image.alpha_composite(chk, ov).convert("RGB").save(OUT / "note-header-check.png")


if __name__ == "__main__":
    x_header()
    note_header()
    print("ok", [p.name for p in OUT.iterdir()])
