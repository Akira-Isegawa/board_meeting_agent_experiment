# Board Meeting (経営会議シミュレーション)

OpenAI Agents SDK を使って、企画書に対する経営会議の討論をシミュレーションします。
議事録・想定問答・改訂企画書を複数のMarkdownファイルで出力します。

## ✅ 前提
- Python 3.8+
- OPENAI_API_KEY を設定済み

## 🔧 実行方法

```bash
python main.py --input inputs/proposal.md
```

### オプション
- `--output-dir` : 出力ディレクトリ（デフォルト: `./outputs`）
- `--rounds` : 討論ラウンド数（デフォルト: 12）
- `--context-turns` : 直近発言の参照数（デフォルト: 6）

例:

```bash
python main.py --input inputs/proposal.md --output-dir outputs --rounds 14
```

## 📝 出力ファイル
出力ディレクトリに以下が生成されます:
- `minutes.md` : 会議の議事録
- `qa.md` : 想定問答集
- `refined_proposal.md` : ブラッシュアップ後の企画書
- `discussion_log.md` : 全ラウンドの対話履歴（詳細ログ）
- `evaluation.md` : **原版と改訂版の比較評価レポート（新機能）**

## 🆕 評価機能
改訂版では、原版企画書と改訂版企画書を比較し、以下の観点で詳細な評価レポートを自動生成します：
- 期待される売上規模と成長性
- 事業規模の拡大可能性
- コスト構造と削減効果
- リスクとリスクマネジメントの妥当性
- 既存事業とのシナジー
- 実現可能性（ブランド・ケイパビリティの観点）
- 経営判断に必要な情報の網羅性
- 情報の事実性と根拠の妥当性
- 次に取るべきアクションの明確性

評価レポートには総合評価、定量的スコアカード（100点満点）、Go/No-Go判断基準、推奨事項が含まれます。

## 👥 参加メンバー
- 社長
- 営業担当役員
- 企画・設計担当役員
- 製造担当役員
- バックオフィス担当役員
- 製造業のコンサルタント
- 知的財産権の専門家
- 法務の専門家
- 会計の専門家

## 📌 仕様メモ
- ファシリテーターが発言者を指名
- 発言回数が少ないメンバーは優先的に指名され、全員が最低1回は発言
- 出力はMarkdownで複数ファイル

## 🧪 テスト

### テスト環境のセットアップ

```bash
pip install -r requirements-dev.txt
```

### テストの実行

```bash
# 簡単な方法（推奨）
./run_tests.sh                 # 標準テスト
./run_tests.sh quick          # クイックテスト
./run_tests.sh coverage       # カバレッジレポート付き
./run_tests.sh verbose        # 詳細出力

# 手動実行
PYTHONPATH=. pytest tests/ -v --no-cov

# カバレッジレポート付き
PYTHONPATH=. pytest tests/ --cov=. --cov-report=html

# 特定のテストファイルを実行
PYTHONPATH=. pytest tests/test_models.py -v
```

### テストの内容
- **test_models.py**: Pydanticモデルのバリデーションテスト
- **test_meeting_agents.py**: エージェント作成関数のテスト
- **test_workflow.py**: ワークフローとヘルパー関数のテスト
- **test_main.py**: CLI機能とメイン関数のテスト

### テストカバレッジ
- 全体: 83%
- models.py: 100%
- meeting_agents.py: 100%
- main.py: 98%

詳細は [tests/README.md](tests/README.md) を参照してください。
