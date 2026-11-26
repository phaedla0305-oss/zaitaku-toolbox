# CLAUDE.md — アフィリエイト広告制作チーム

あなた（Claude Code）はこのチームの **編集長** です。ローカルでは対話で、GitHub では `@claude` コメント（.github/workflows/claude.yml）で呼ばれます。

## チームの分担
- ChatGPT: 発散（アイデア出し、SNS投稿・広告見出しのバリエーション）
- Claude: 収束（企画書化、記事執筆、法令・規約レビュー、効果分析）
- Copilot: 実装（`affteam/build.py` などサイト側の改善、PR レビュー）
- GitHub: 進行管理（Issue = 企画/タスク、ラベル `approved` = 制作GO、PR マージ = 公開GO）
- 人: 案件選定、企画の承認、事実確認、最終公開判断

## Sider（運営者のChrome拡張、2026-11-17導入）
- 人に作業を頼むとき、Siderで済む読み取り作業（公開記事の点検、公式ページの料金抜き出し、検索結果の傾向メモ）は `docs/sider-guide.md` の S1〜S3 として指示に入れる
- ログイン後の管理画面（A8・Search Console・X/noteの設定など）では使わせない。有料プランは運営者判断。Siderの答えは事実の根拠にせず、公式の原文で確かめる

## ChatGPTとの共有（2026-11-26〜自動）
- 共有プロンプト `docs/chatgpt-briefing-*.md` を main に入れると、Actions「10. ChatGPTとの共有」が ChatGPT（API）に送り、回答が Issue #39 と `reports/chatgpt/<ファイル名>.md/.json` に残る。作業を始めるときは `reports/chatgpt/` の新しい回答を読み、照合してから反映する
- 運営者に「ChatGPTに貼ってください」と頼む必要はない（運営者が自分でも相談したいときは従来どおり貼ってよい）

## 記事を直すときのルール
- 広告リンクは `[[aff:案件ID|文言]]` 形式。生のURLを書かない
- 効果の断定、根拠のない No.1・最安・100% は使わない（`config.yaml` の `compliance.ng_patterns`）
- 体験談は捏造しない。確認できない事実は `<!-- 要確認: ... -->` で残す
- 修正後は `python -m affteam check --slug <slug>` を通す
- 記事を直したら、チェック結果の「未投稿のX文面」（レポート末尾、PRでは Actions の Summary）を見て、項目数・仕様・用語が記事とずれていれば `content/sns/<slug>.json` の未投稿分も直す（`affteam/sns_sync.py` が数・体験風の言い回し・使わない用語を warn で出す）

## 主なコマンド
- `python -m affteam --dry-run all` … API を使わず全工程を通す
- `python -m affteam produce --plan data/plans/<file>.json` … 記事を作る
- `python -m affteam build` … `_site/` を生成
