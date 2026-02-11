# Board Meeting Agent Experiment - テストスイート

このディレクトリには、プロジェクトの単体テストが含まれています。

## テストの構成

- `conftest.py`: 共通のpytestフィクスチャとテストデータ
- `test_models.py`: Pydanticモデルのバリデーションテスト
- `test_meeting_agents.py`: エージェント作成関数のテスト
- `test_workflow.py`: ワークフローとヘルパー関数のテスト
- `test_main.py`: CLI機能とメイン関数のテスト

## テストの実行方法

### 開発用依存関係のインストール

```bash
pip install -r requirements-dev.txt
```

### すべてのテストを実行

```bash
# 簡単な方法（推奨）
./run_tests.sh

# または手動で実行
PYTHONPATH=. pytest tests/ -v --no-cov
```

### 特定のテストファイルを実行

```bash
PYTHONPATH=. pytest tests/test_models.py -v
```

### 特定のテストクラスを実行

```bash
PYTHONPATH=. pytest tests/test_models.py::TestFacilitatorDecision -v
```

### 特定のテスト関数を実行

```bash
PYTHONPATH=. pytest tests/test_models.py::TestFacilitatorDecision::test_valid_creation -v
```

### カバレッジレポート付きで実行

```bash
./run_tests.sh coverage

# または
PYTHONPATH=. pytest tests/ --cov=. --cov-report=html -k "not test_run_board_meeting"
```

カバレッジレポートは`htmlcov/index.html`に生成されます。

### 詳細な出力で実行

```bash
./run_tests.sh verbose
```

### クイックテスト

```bash
./run_tests.sh quick
```

### 失敗したテストのみ再実行

```bash
PYTHONPATH=. pytest --lf -v
```

## テストの特徴

- **Pydanticモデルのテスト**: バリデーション、必須フィールド、デフォルト値の確認
- **エージェント作成のテスト**: 適切なインスタンス生成、出力型、インストラクションの確認
- **ワークフローのテスト**: データフォーマット、ターン管理、統合テスト（モック使用）
- **CLIのテスト**: 引数パース、ファイル処理、エラーハンドリング

## カバレッジ目標

- 全体: 80%以上
- models.py: 95%以上
- meeting_agents.py: 90%以上
- workflow.py: 70%以上（OpenAI API呼び出し部分は除く）
- main.py: 85%以上

## 注意事項

- OpenAI APIの実際の呼び出しはテストではモック化されています
- 非同期関数のテストには`pytest-asyncio`を使用しています
- ファイルI/Oのテストには`tmp_path`フィクスチャを使用しています
