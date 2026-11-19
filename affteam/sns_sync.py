"""記事とまだ投稿していないX文面の照合（APIを使わない機械チェック）。

記事を直したときに、未投稿の文面（content/sns/<slug>.json のうち、まだ投稿していない分）が
いまの記事とずれていないかを洗い出す。指摘はすべて warn（公開は止めない）。直すかどうかは人か Claude Code が決める。

見るもの
- 数（「4つ」「5項目」「3点」など）：同じ数と単位が記事本文にない
- 書き手の実体験に読める言い回し（「失敗」「昨年」「作業が止まった」など）
- 使わない用語（「支給VPN」「IP制限に入れない」など）
- 条件を省く言い方・原因の決めつけ（「これだけでOK」「○選」「VPNがあれば解決」など）
"""
from __future__ import annotations

import json
import re

from .config import ARTICLES_DIR, ROOT, SNS_DIR, parse_front_matter

STATE = ROOT / "data" / "sns_posted.json"

COUNT = re.compile(r"([0-9０-９]+)\s*(つ|点|項目|案|個|ステップ|パターン|選|件|問)")
RULES = [
    (re.compile(r"失敗|昨年|去年|ピンチ|早合点|ロス…|作業(が)?(止ま|ストップ)|ぶっつけ本番"),
     "書き手の実体験に読める言い回し（一般化して「〜することがあります」と書く）"),
    (re.compile(r"支給VPN|IP制限に入(れ|る)"), "使わない用語（「会社のVPN」「社内ツールに入れない」）"),
    (re.compile(r"これだけで(OK|大丈夫|十分)|[0-9０-９]+選"), "条件を省く言い方（記事と数がずれやすい）"),
    (re.compile(r"(があれば|で)解決|なら回線(を)?変更|なら(乗り換え|契約)"), "原因を確かめずに契約や効果に結びつける言い方"),
    (re.compile(r"安心です.*安心です|しましょう.*しましょう"), "「安心です」「〜しましょう」の繰り返し"),
]


def _to_half(s: str) -> str:
    return s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def unposted(slug: str) -> list[tuple[int, str]]:
    """まだ投稿していない文面（番号, 本文）。"""
    path = SNS_DIR / f"{slug}.json"
    if not path.exists():
        return []
    posts = json.loads(path.read_text(encoding="utf-8")).get("x_posts", [])
    done = 0
    if STATE.exists():
        done = json.loads(STATE.read_text(encoding="utf-8")).get("posts", {}).get(slug, 0)
    return [(i, p) for i, p in enumerate(posts) if i >= done]


def review(slug: str) -> list[dict]:
    """未投稿の文面を記事と照合し、warn の指摘を返す。"""
    art = ARTICLES_DIR / f"{slug}.md"
    if not art.exists():
        return []
    meta, body = parse_front_matter(art.read_text(encoding="utf-8"))
    text = _to_half(str(meta.get("title", "")) + "\n" + body)
    issues: list[dict] = []
    for i, post in unposted(slug):
        where = f"X文面 v{i + 1}（未投稿）"
        for m in COUNT.finditer(post):
            n, unit = _to_half(m.group(1)), m.group(2)
            # 「4つ」は、記事に同じ数と単位があるか、丸数字の最後（チェック①〜④の「④」）があれば合っているとみなす
            circled = "①②③④⑤⑥⑦⑧⑨⑩"[int(n) - 1] if 1 <= int(n) <= 10 else None
            if not re.search(rf"{n}\s*{unit}", text) and not (circled and circled in text):
                issues.append({"severity": "warn", "quote": m.group(0), "where": where,
                               "reason": f"記事に「{n}{unit}」が見当たらない。記事の項目数と照合し、確かめられなければ数字を外す"})
        for pat, reason in RULES:
            m = pat.search(post)
            if m:
                issues.append({"severity": "warn", "quote": m.group(0), "where": where, "reason": reason})
    return issues


def listing(slug: str) -> list[str]:
    """レポートに載せる未投稿文面の一覧（Markdown の行）。"""
    rows = unposted(slug)
    if not rows:
        return ["- 未投稿の文面なし"]
    return [f"- v{i + 1}: {p}" for i, p in rows]
