"""Xの現行ヘッダー（output/x-profile/header-2.png）と統一感のある note のクリエイターページ用ヘッダー（1920x1006）。
- 同じイラスト（机・窓・観葉植物・ノートPC・ルーター）を使い、背景色もXと同じにする
- note で表示されるのは縦方向の中央 324px。スマホでは左右も切れるので、絵は中央約1100pxの範囲に収める
- N1：イラストのみ（Xと同じ構成）／N2：左にブランド名とカテゴリ（L1と同じ文字組み）
出力：output/brand/headers/note-header-N1/N2-1920x1006.png、確認用 -check.png、比較 note-N1-N2-compare.png
使い方：python scripts/make_note_header_from_x.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "output/x-profile/header-2.png"
OUT = ROOT / "output/brand/headers"
W, H, BAND = 1920, 1006, 324
TOP = (H - BAND) // 2
NAVY, ORANGE = "#1F3A5F", "#F28C28"
SUBTLE = "#55697F"
FB, FM = "C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/YuGothM.ttc"
K = 3


def base():
    src = Image.open(SRC).convert("RGB")
    bg = src.getpixel((10, 10))
    canvas = Image.new("RGB", (W, H), bg)
    return src, bg, canvas


def place_scene(canvas, src, scene_center_x, height=BAND, top=None):
    """Xヘッダーの絵の部分（x 900〜右端）を、表示される帯の高さに合わせて縮小し、帯の中に置く。"""
    sx0 = 860  # 机の左端（x≈924）より手前から切り出し、縁をぼかしても机にかからないようにする
    scene = src.crop((sx0, 0, src.width, src.height))
    s = height / src.height
    scene = scene.resize((round(scene.width * s), height), Image.LANCZOS)
    x = round(scene_center_x - scene.width / 2)
    # 左端は背景色へなめらかにつなぐ（絵の左側は元から背景色だけ）
    mask = Image.new("L", scene.size, 255)
    md = ImageDraw.Draw(mask)
    fade = 14
    for i in range(fade):
        md.line([(i, 0), (i, scene.height)], fill=round(255 * i / fade))
    canvas.paste(scene, (x, TOP + BAND - height if top is None else top), mask)
    return x, x + scene.width


def text_block(canvas, cx, cy, px=84):
    big = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    title, line = "在宅ワーク道具箱", "回線｜VPN｜作業環境｜サブスク"
    ft = ImageFont.truetype(FB, px * K, index=0)
    fl = ImageFont.truetype(FM, round(px * 0.46) * K, index=0)
    tl, tt, tr, tb = d.textbbox((0, 0), title, font=ft)
    ll, lt, lr, lb = d.textbbox((0, 0), line, font=fl)
    th, lh = (tb - tt) / K, (lb - lt) / K
    g1, bar, g2 = px * 0.30, 7, px * 0.34
    y = cy - (th + g1 + bar + g2 + lh) / 2
    d.text((cx * K - (tl + tr) / 2, y * K - tt), title, font=ft, fill=NAVY)
    y += th + g1
    bw = px * 1.3
    d.rounded_rectangle([(cx - bw / 2) * K, y * K, (cx + bw / 2) * K, (y + bar) * K], radius=3.5 * K, fill=ORANGE)
    y += bar + g2
    d.text((cx * K - (ll + lr) / 2, y * K - lt), line, font=fl, fill=SUBTLE)
    small = big.resize((W, H), Image.LANCZOS)
    canvas.paste(small, (0, 0), small)


def check(im):
    chk = im.copy().convert("RGBA")
    ov = Image.new("RGBA", chk.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([0, 0, W, TOP], fill=(0, 0, 0, 90))
    od.rectangle([0, TOP + BAND, W, H], fill=(0, 0, 0, 90))
    od.rectangle([(W - 1100) // 2, TOP, (W + 1100) // 2, TOP + BAND], outline=(255, 0, 0, 200), width=4)
    return Image.alpha_composite(chk, ov).convert("RGB")


if __name__ == "__main__":
    out = {}
    # N1：イラストのみ。帯の中央より少し右に置く（Xと同じく右側に絵、左は余白）
    src, bg, c1 = base()
    place_scene(c1, src, 1180)
    out["N1"] = c1
    # N2：左にブランド名とカテゴリ、右にイラスト（どちらもスマホの目安の範囲内）
    src, bg, c2 = base()
    place_scene(c2, src, 1250, height=290)  # 帯の下端にそろえて少し小さく
    text_block(c2, 690, TOP + BAND / 2, px=70)
    out["N2"] = c2
    fs = ImageFont.truetype(FB, 22, index=0)
    sheet = Image.new("RGB", (980, 2 * (int(BAND * 960 / W) + 50) + 10), "white")
    sd = ImageDraw.Draw(sheet)
    y = 8
    for k, im in out.items():
        im.save(OUT / f"note-header-{k}-1920x1006.png")
        check(im).save(OUT / f"note-header-{k}-check.png")
        sd.text((10, y), f"{k}（noteで表示される帯）", font=fs, fill="#222")
        band = im.crop((0, TOP, W, TOP + BAND)).resize((960, round(BAND * 960 / W)), Image.LANCZOS)
        sheet.paste(band, (10, y + 32))
        y += 32 + band.height + 18
    sheet.save(OUT / "note-N1-N2-compare.png")
    print("ok")
