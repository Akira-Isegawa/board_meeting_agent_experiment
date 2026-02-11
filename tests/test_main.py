"""main.pyのCLI機能の単体テスト."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from main import parse_args, main


class TestParseArgs:
    """parse_args関数のテスト."""

    def test_parse_args_with_required_only(self):
        """必須引数のみ指定した場合のテスト."""
        test_args = ["--input", "inputs/proposal.md"]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            args = parse_args()
            assert args.input == "inputs/proposal.md"
            assert args.output_dir == "./outputs"
            assert args.rounds == 12
            assert args.context_turns == 6

    def test_parse_args_with_all_options(self):
        """すべてのオプションを指定した場合のテスト."""
        test_args = [
            "--input",
            "custom/path.md",
            "--output-dir",
            "custom_output",
            "--rounds",
            "20",
            "--context-turns",
            "10",
        ]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            args = parse_args()
            assert args.input == "custom/path.md"
            assert args.output_dir == "custom_output"
            assert args.rounds == 20
            assert args.context_turns == 10

    def test_parse_args_missing_required(self):
        """必須引数が欠けている場合のエラーテスト."""
        test_args = ["--output-dir", "outputs"]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_invalid_rounds(self):
        """不正なrounds値のテスト."""
        test_args = ["--input", "test.md", "--rounds", "invalid"]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            with pytest.raises(SystemExit):
                parse_args()

    def test_parse_args_negative_rounds(self):
        """負のrounds値が指定された場合（parse自体は成功）."""
        test_args = ["--input", "test.md", "--rounds", "-5"]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            args = parse_args()
            assert args.rounds == -5  # パースは成功するがmain()でエラーになる


class TestMain:
    """main関数のテスト."""

    def test_main_missing_api_key(self, tmp_path, capsys):
        """OPENAI_API_KEYが設定されていない場合のテスト."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書")

        test_args = ["--input", str(input_file)]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {}, clear=True):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "OPENAI_API_KEY" in captured.out

    def test_main_input_file_not_found(self, capsys):
        """入力ファイルが存在しない場合のテスト."""
        test_args = ["--input", "/nonexistent/file.md"]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "見つかりません" in captured.out

    def test_main_invalid_rounds(self, tmp_path, capsys):
        """rounds が1未満の場合のテスト."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書")

        test_args = ["--input", str(input_file), "--rounds", "0"]
        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "rounds は1以上" in captured.out

    def test_main_successful_execution(self, tmp_path):
        """正常実行のテスト（run_board_meetingをモック）."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書\n\nテスト内容")
        output_dir = tmp_path / "outputs"

        # run_board_meetingをモック
        mock_return = (
            "# 議事録",
            "# Q&A",
            "# 改訂企画書",
            "# 対話履歴",
            "# 評価",
        )

        test_args = [
            "--input",
            str(input_file),
            "--output-dir",
            str(output_dir),
            "--rounds",
            "2",
        ]

        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with patch("main.run_board_meeting", return_value=mock_return):
                    main()

        # 出力ファイルが作成されたことを確認
        assert (output_dir / "minutes.md").exists()
        assert (output_dir / "qa.md").exists()
        assert (output_dir / "refined_proposal.md").exists()
        assert (output_dir / "discussion_log.md").exists()
        assert (output_dir / "evaluation.md").exists()

        # ファイルの内容を確認
        assert (output_dir / "minutes.md").read_text() == "# 議事録"
        assert (output_dir / "qa.md").read_text() == "# Q&A"
        assert (output_dir / "refined_proposal.md").read_text() == "# 改訂企画書"
        assert (output_dir / "discussion_log.md").read_text() == "# 対話履歴"
        assert (output_dir / "evaluation.md").read_text() == "# 評価"

    def test_main_creates_output_directory(self, tmp_path):
        """出力ディレクトリが存在しない場合に自動作成されることをテスト."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書")
        output_dir = tmp_path / "new_output_dir"

        assert not output_dir.exists()

        mock_return = ("# 議事録", "# Q&A", "# 改訂", "# ログ", "# 評価")

        test_args = [
            "--input",
            str(input_file),
            "--output-dir",
            str(output_dir),
        ]

        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with patch("main.run_board_meeting", return_value=mock_return):
                    main()

        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_main_keyboard_interrupt(self, tmp_path, capsys):
        """キーボード割り込みのテスト."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書")

        test_args = ["--input", str(input_file)]

        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with patch(
                    "main.run_board_meeting", side_effect=KeyboardInterrupt()
                ):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "中断" in captured.out

    def test_main_exception_handling(self, tmp_path, capsys):
        """例外処理のテスト."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書")

        test_args = ["--input", str(input_file)]

        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with patch(
                    "main.run_board_meeting",
                    side_effect=Exception("テストエラー"),
                ):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "エラーが発生しました" in captured.out
        assert "テストエラー" in captured.out

    def test_main_with_custom_context_turns(self, tmp_path):
        """カスタムcontext_turnsでの実行テスト."""
        input_file = tmp_path / "proposal.md"
        input_file.write_text("# テスト企画書")
        output_dir = tmp_path / "outputs"

        mock_return = ("# 議事録", "# Q&A", "# 改訂", "# ログ", "# 評価")

        test_args = [
            "--input",
            str(input_file),
            "--output-dir",
            str(output_dir),
            "--context-turns",
            "3",
        ]

        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
                with patch("main.run_board_meeting", return_value=mock_return) as mock:
                    main()
                    # run_board_meetingが正しい引数で呼ばれたことを確認
                    mock.assert_called_once()
                    call_kwargs = mock.call_args[1]
                    assert call_kwargs["context_turns"] == 3


class TestMainIntegration:
    """main.py統合テスト."""

    def test_full_cli_flow(self, tmp_path):
        """CLIの全体フローのテスト（モック使用）."""
        # 入力ファイルの準備
        input_file = tmp_path / "proposal.md"
        input_content = """# 新規事業企画書

## 背景
市場拡大

## 目的
売上向上
"""
        input_file.write_text(input_content)
        output_dir = tmp_path / "outputs"

        # モックの戻り値
        mock_return = (
            "# 議事録\n\n会議を実施しました",
            "# Q&A\n\nQ: 質問\nA: 回答",
            "# 改訂企画書\n\n改訂版",
            "# 対話履歴\n\n発言記録",
            "# 評価\n\nスコア: 85点",
        )

        test_args = [
            "--input",
            str(input_file),
            "--output-dir",
            str(output_dir),
            "--rounds",
            "5",
            "--context-turns",
            "3",
        ]

        with patch.object(sys, "argv", ["main.py"] + test_args):
            with patch.dict("os.environ", {"OPENAI_API_KEY": "test-api-key"}):
                with patch("main.run_board_meeting", return_value=mock_return) as mock:
                    main()

                    # 関数が正しい引数で呼ばれたことを確認
                    mock.assert_called_once()
                    call_args = mock.call_args
                    assert call_args[1]["proposal_markdown"] == input_content
                    assert call_args[1]["rounds"] == 5
                    assert call_args[1]["context_turns"] == 3
                    assert call_args[1]["verbose"] is True

        # 出力ファイルの確認
        assert (output_dir / "minutes.md").exists()
        assert (output_dir / "qa.md").exists()
        assert (output_dir / "refined_proposal.md").exists()
        assert (output_dir / "discussion_log.md").exists()
        assert (output_dir / "evaluation.md").exists()

        # 内容の確認
        assert "会議を実施しました" in (output_dir / "minutes.md").read_text()
        assert "Q: 質問" in (output_dir / "qa.md").read_text()
        assert "改訂版" in (output_dir / "refined_proposal.md").read_text()
        assert "発言記録" in (output_dir / "discussion_log.md").read_text()
        assert "85点" in (output_dir / "evaluation.md").read_text()
