# 完了・保留・未確認の現状一覧（2026-11-20 確認）

過去の記録は消さず、ここで現在の状態を区別する。各記録ファイルには、この一覧への参照つきで訂正・追記を入れた。

## 1. 公開済み・マージ済み
| 項目 | 現在の状態（11/20） | 根拠 |
|---|---|---|
| 記事 | 6本すべて公開中（新規0本・更新6本）。11/20に公開ページ6本・中継ページ3件・サイトマップの応答200を確認 | https://phaedla0305-oss.github.io/zaitaku-toolbox/ |
| PR | #20〜#28 はすべてマージ済み。オープンPRは0件 | `gh pr list` |
| 記事④の自宅回線の測定例 | **公開本文は3回分**（11/11 12:00、11/13 17:30、11/15 20:00）。PR #22 はタイトルが「2回分」だが、マージされた内容（92fc75b、11/15マージ）に3回目の行が入っている | [PR #22](https://github.com/phaedla0305-oss/zaitaku-toolbox/pull/22)、公開ページ |
| 記事④のGMOとくとくBB光の広告 | 掲載中（11/13提携、PR #20 で記事④に1か所） | [PR #20](https://github.com/phaedla0305-oss/zaitaku-toolbox/pull/20) |
| X投稿の予定文面の修正 | 11/19に実施。#26で7件、#27で10件 | [PR #26](https://github.com/phaedla0305-oss/zaitaku-toolbox/pull/26)、[PR #27](https://github.com/phaedla0305-oss/zaitaku-toolbox/pull/27) |
| 記事と未投稿X文面の照合の自動化 | 11/19にマージ。法令チェックで動作中 | [PR #28](https://github.com/phaedla0305-oss/zaitaku-toolbox/pull/28) |

## 2. 記録と現状の違い（訂正・追記したもの）
| 記録 | 記録の内容 | 現状 | 対応 |
|---|---|---|---|
| data/drafts/home-line-measurement.json の status | 「2回分で記事④の原稿を作成（公開は運営者の判断待ち）」 | 3回分で公開済み | `status_2026-11-20` を追記（元の文は残す） |
| reports/ops_2026-11-19.md 5章 #1 | 「X投稿の予定文面4件を書き換えるか」（判断待ち） | 11/19に運営者の指示で実施済み（#26・#27）、照合も自動化（#28） | 訂正を追記 |
| docs/policy_2026-11-15.md 4章 | 「設定のままだと12/1 9:17 から週4本で動く」 | 12/1は火曜で定時枠がない。解除後の最初の定時枠は12/3（木）9:17（予算判定あり） | 訂正を追記。詳細は docs/decision-december-cadence_2026-11-20.md |
| docs/program-candidates_2026-11-13.md・Issue #12 | 光回線が「採用候補」、運営者の確認待ちに「UQ WiMAXの審査結果」 | 光回線（GMOとくとくBB光）は採用・掲載済み。ほかの5分野は保留のまま。UQ WiMAXの状態は未確認 | 追記。Issue #12 はクローズしない |

## 3. 保留（12/16の振り返りまで、または別の時期まで）
| 項目 | 状態 | 根拠 |
|---|---|---|
| 案件候補のうち5分野（転職・リモート求人、クラウド会計、セキュリティソフト、家具・周辺機器、コワーキング予約） | 保留（クラウド会計は1月に再検討） | docs/program-candidates_2026-11-13.md |
| 楽天アフィリエイト・楽天ROOM・noteの広告とサイトリンク・Siderの継続 | 12/16の議題 | docs/policy_2026-11-15.md 8章 |
| 週次編集デスクの追加開発・接続 | 凍結 | docs/policy_2026-11-15.md 1章 |
| 定時企画 | 12/1まで休止 | config.yaml `schedule` |

## 4. 運営者の判断待ち
| 項目 | 期限 | 材料 |
|---|---|---|
| 12月の本数（週2本／週4本） | 11/30 | docs/decision-december-cadence_2026-11-20.md |
| needs-review の停止ルールの採否と仕様 | 11/30 | 同上 3章 |

## 5. 未確認（推測で埋めない）
| 項目 | 状態 | 次の確認 |
|---|---|---|
| UQ WiMAXの提携状態 | 未確認（11/13の確認依頼以降、記録なし） | 次回A8ログイン時に「参加中」「申込中」の一覧で見る |
| A8の案件別SNS条件・Xアカウントのサイト登録・広告掲載URLの提出 | 未確認 | docs/a8-sns-check_2026-11-20.md の表を本人が埋める |
| Anthropic のクレジット残高・実請求、ChatGPT API・X API の実請求 | 未取得 | 運営者が各コンソールで確認 |
| 記事②のCisco参照URL（下記）の到達 | **未確認**。11/20の直接取得は HTTP 403。リンク切れとは断定せず、差し替えない | 11/25開始のS1点検で、運営者がブラウザで表示を確かめる（docs/sider-guide.md） |
| 記事①③の検索登録 | 次の確認は11/30（登録リクエストは繰り返さない） | docs/policy_2026-11-15.md 2-3 |
| 11/16〜11/22の計測 | 未取得 | 11/23（月）7:00の週次計測 |

Cisco参照URL：https://www.cisco.com/c/ja_jp/td/docs/rt/wanaggregationinternetedgert/asr1000aggregationservsrt/cg/024/nat-xe-3s-asr1k-book/nat-xe-3s-asr1k-book_chapter_010.html
