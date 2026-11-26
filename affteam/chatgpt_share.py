"""ChatGPT との共有の自動化（チームの自走化 段階1、2026-11-26 運営者承認）。

運営者がチャットに手で貼っていた共有プロンプト（docs/chatgpt-briefing-*.md の最初のコード枠）を、
OpenAI API（ChatGPT）に送り、返ってきた回答を GitHub の Issue「ChatGPTとの共有（自動）」にコメントで残す。
回答は reports/chatgpt/ にも保存し、Claude Code が次の作業で読めるようにする。

- システムの指示には、ChatGPT のプロジェクトの指示（docs/chatgpt-project-prompt.md の【プロジェクトの指示】）を使う
- 送る前に個人情報・秘密情報の検出（llm.guard）を通す。見つかったら送らずに止める
- 決める・公開する・支出するのは今までどおり運営者。ここでは回答を記録するだけ
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import gh
from .config import ROOT, REPORTS_DIR, today, write_text
from .llm import chatgpt, extract_json

ISSUE_TITLE = "ChatGPTとの共有（自動）"
LABEL = "chatgpt"
STUB = '{"stub": "ドライランのため送信していません"}'


def _first_block(md: str) -> str:
    m = re.search(r"```[^\n]*\n(.*?)```", md, re.S)
    if not m:
        raise ValueError("共有プロンプトのコード枠（```）が見つかりません")
    return m.group(1).strip()


def _project_instructions() -> str:
    p = ROOT / "docs" / "chatgpt-project-prompt.md"
    md = p.read_text(encoding="utf-8")
    i = md.find("## 【プロジェクトの指示】")
    return _first_block(md[i:] if i >= 0 else md)


def _issue_number() -> str:
    """共有用のIssue（なければ作る）の番号。"""
    out = gh._run(["issue", "list", "--label", LABEL, "--state", "open", "--json", "number,title", "--limit", "20"])
    for it in json.loads(out or "[]"):
        if it.get("title") == ISSUE_TITLE:
            return str(it["number"])
    url = gh.create_issue(ISSUE_TITLE,
                          "共有プロンプト（docs/chatgpt-briefing-*.md）をChatGPT（API）に自動で送り、回答をここに残します。\n"
                          "決定・公開・支出は今までどおり運営者が行います。", [LABEL])
    return url.rstrip("/").split("/")[-1] if url else ""


def run(file: str) -> int:
    path = (ROOT / file) if not Path(file).is_absolute() else Path(file)
    prompt = _first_block(path.read_text(encoding="utf-8"))
    system = _project_instructions()
    answer = chatgpt(system, prompt, stub=STUB)
    try:
        parsed = extract_json(answer)
    except Exception:
        parsed = None
    name = path.stem
    out_dir = REPORTS_DIR / "chatgpt"
    write_text(out_dir / f"{name}.md",
               f"# ChatGPTの回答：{name}\n\n- 送った日：{today()}\n- 共有プロンプト：{file}\n\n```\n{answer.strip()}\n```\n")
    if parsed is not None:
        write_text(out_dir / f"{name}.json", json.dumps(parsed, ensure_ascii=False, indent=2) + "\n")
    num = _issue_number()
    body = (f"### {name}\n共有プロンプト：`{file}`（{today()} 自動送信）\n\n"
            f"<details open><summary>ChatGPTの回答</summary>\n\n```json\n{answer.strip()}\n```\n</details>\n\n"
            "※この回答はChatGPTの意見です。採用するかは Claude Code が照合し、運営者が決めます。")
    if num:
        gh._run(["issue", "comment", num, "--body", body])
    print(f"[ChatGPT共有] {name} → Issue #{num or '(dry)'} ／ 保存 reports/chatgpt/{name}.md")
    return 0
