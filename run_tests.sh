#!/bin/bash
# テスト実行スクリプト

set -e  # エラーで終了

echo "🧪 Board Meeting Agent - テストスイート"
echo "=================================="
echo ""

# PYTHONPATHを設定
export PYTHONPATH=.

# 引数の確認
if [ "$1" = "coverage" ]; then
    echo "📊 カバレッジレポート付きでテストを実行"
    pytest tests/ \
        --cov=. \
        --cov-report=term-missing \
        --cov-report=html \
        -k "not test_run_board_meeting" \
        -v
    echo ""
    echo "✅ カバレッジレポートは htmlcov/index.html に生成されました"
elif [ "$1" = "quick" ]; then
    echo "⚡ クイックテスト（詳細出力なし）"
    pytest tests/ \
        --no-cov \
        -k "not test_run_board_meeting" \
        -q
elif [ "$1" = "verbose" ]; then
    echo "📝 詳細出力でテストを実行"
    pytest tests/ \
        --no-cov \
        -k "not test_run_board_meeting" \
        -vv
else
    echo "📋 標準テストを実行"
    pytest tests/ \
        --no-cov \
        -k "not test_run_board_meeting" \
        -v
fi

echo ""
echo "✅ テスト完了"
