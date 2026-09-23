# Jev Scout

Jev Scout is an agent skill for finding and evaluating worthwhile uses of Jev, TypeSafe AI's decision model. It compares the current approach and simpler code changes, and can optionally prepare bounded API experiments or implement a selected candidate. A decision not to adopt Jev is a valid outcome.

This project is an independent, community-maintained distribution. It is not affiliated with, sponsored by, or endorsed by TypeSafe AI. Jev Scout does not include TypeSafe credentials, and it does not make API calls during discovery.

## Quick start

Install the tracked `skills/jev-scout/` directory in a Claude Code or Codex skill discovery location, then invoke it with a repository-specific question:

```text
/jev-scout assess whether this repository should adopt Jev
$jev-scout compare Jev with a deterministic implementation for this workflow
```

Discovery, candidate comparison, and the `status`/`preview` commands work without an API key or network access. Live measurements require an explicitly approved experiment policy, Node.js 22+, and an optional `TYPESAFE_API_KEY`; the key is read from the environment or a local ignored binding and is never part of this distribution. An API key alone does not authorize an experiment.

For Claude Code and Codex installation details, see the Japanese guidance below.

## Jev導入設計の論考

エージェント向けSkillとは別に、設計者が読める[**Jev導入の設計地図――意味判断を、どこに、どこまで置くか**](docs/jev-adoption-field-guide.md)を公開しています。Jevの基本操作ではなく、既存ソフトウェアのどの判断を切り出し、どこを通常コードに残すかを扱う技術的な検討です。Skillを使うための必読資料ではありません。

四段階の調査を横断し、次の問いを具体的なOSSのコード経路と対照例から掘り下げます。

- 正規表現、HTTP status、経過日数、XPathなどは、どの「意味」の代理になっているか。
- 置換だけでなく、意味条件の追加、競合時だけの判断、後段ゲート、検索停止やテスト選択のような制御系へ、どこに置けるか。
- 既存LLMの有限な操作選択と文章生成をどう分け、候補不足・不確実性・副作用をどう扱うか。
- 単純な規則改善と同じデータでどう比較し、**導入しない**結論をいつ出すか。

公開コードを手掛かりにした導入案は未検証の仮説であり、精度や費用の改善実績ではありません。調査原本はこの公開リポジトリに含めていません。

## 使う

- Claude Code: `/jev-scout このリポジトリでJevを導入する価値を調べて`
- Codex: `$jev-scout このリポジトリでJevを導入する価値を調べて`
- 実験: `この合成データで最大6リクエストまで比較して`
- 実装: `候補1を実装して。既存の失敗時動作は維持して`

キーなしでも探索・候補比較・評価案まで完結します。キーありでも対象データと実行上限が未設定なら実験案まで。設定済み条件内では同じ確認を繰り返しません。

## CC/Cdx共通配置

正本は `skills/jev-scout/`。このチェックアウトでは `.claude/skills/jev-scout` と `.agents/skills/jev-scout` が同じ正本を指します。新しいセッションで読み込んでください。

他のプロジェクトでも使う場合は固定チェックアウトを保ち、個人用の **両方** の発見場所へ `skills/jev-scout` の絶対パスをシンボリックリンクします。

| Host | Personal discovery directory | Invocation |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/jev-scout` | `/jev-scout` |
| Codex | `~/.agents/skills/jev-scout` | `$jev-scout` |

既存の同名Skillを上書きしないでください。個人用配置の代わりに対象リポジトリの `.claude/skills/` と `.agents/skills/` に置くこともできます。配布するときはGitのtracked内容だけを使い、`local.json` や秘密ファイルをコピーしないでください。独自インストーラー・専用MCP・別Skill依存はありません。

配置根拠: [Claude Code skills](https://code.claude.com/docs/en/skills)、[Codex skills](https://developers.openai.com/codex/skills)。クラウド実行には端末上のキーやリンクは引き継がれません。

## 専用APIキー

キーは配布物には含めません。標準は `TYPESAFE_API_KEY` 環境変数です。

端末共通の専用キーには、Skill直下のGit対象外 `local.json` に `{"key_file":"/absolute/private/path/credentials.env"}` を設定します。秘密ファイルは所有者だけが読み書きできる状態で `TYPESAFE_API_KEY=...` の一行にします。

ランナーの `--key-file` が最優先、次に専用キー設定、最後に環境変数です。無効な明示設定を黙って別キーへ切り替えません。CC/Cdxは同じ正本を参照するため同じ専用キー設定を使います。キーをチャットに貼る必要はありません。詳細は [実験手順](skills/jev-scout/references/experiments.md) を参照。

## 開発と検証

Python 3.10以上。APIを呼ぶ `run` にはNode.js 22以上も必要です。Python標準ライブラリとNode標準の `fetch` を使い、追加パッケージは不要です。キーなしの探索と `status` / `preview` はNode不要です。

```sh
python3 -m unittest discover -s tests -v
python3 skills/jev-scout/scripts/jev_scout.py status
python3 skills/jev-scout/scripts/jev_scout.py preview --experiment evals/support/experiment.json --policy evals/support/policy.example.json
```

`preview` は認証も通信も不要。`run` は承認済みポリシーと新しいGit対象外の出力先を必要とします。実験結果はAPI正常応答と正解率、本番反映を区別して解釈してください。

評価題材・採点基準は [evals](evals/README.md)、設計は [docs/design.md](docs/design.md)。ホスト間で文章が一致することではなく、根拠・非採用判断・検証可能な提案を評価します。

## 深い導入提案

置換だけでなく、既存ルールへの意味条件追加、差分後の重要度判定、未分類・競合時だけの呼び出し、助言型レビューを比較します。既存データから作る新機能も対象です。提案には挿入位置・呼出条件・価値・比較実験を含め、出典付き選択が必要な場合だけ根拠整合を要求します。

実験結果には任意の確率分布・対象版メタデータを残せます。既存CLI・入力形式は継続利用可能です。[組み込みパターン](skills/jev-scout/references/integration-patterns.md)と[評価題材](evals/placement/README.md)を参照してください。

## License

MIT. See [LICENSE](LICENSE).
