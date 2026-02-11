"""workflow.pyの単体テスト."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from workflow import _format_turns, run_board_meeting
from models import FacilitatorDecision, ParticipantResponse


class TestFormatTurns:
    """_format_turns関数のテスト."""

    def test_format_empty_turns(self):
        """空のターンリストのフォーマットテスト."""
        result = _format_turns([])
        assert result == ""

    def test_format_single_turn(self, sample_turns_data):
        """単一ターンのフォーマットテスト."""
        result = _format_turns([sample_turns_data[0]])
        assert "1. 社長" in result
        assert "指名理由: 最初の発言として" in result
        assert "売上拡大に期待します" in result

    def test_format_multiple_turns(self, sample_turns_data):
        """複数ターンのフォーマットテスト."""
        result = _format_turns(sample_turns_data)
        assert "1. 社長" in result
        assert "2. 営業担当役員" in result

    def test_format_with_details(self, sample_turns_data):
        """詳細情報を含むフォーマットテスト."""
        result = _format_turns(sample_turns_data, include_details=True)
        assert "懸念点:" in result
        assert "提案:" in result
        assert "市場リスクの詳細が不明" in result
        assert "段階的投資を提案" in result

    def test_format_without_details(self, sample_turns_data):
        """詳細情報を含まないフォーマットテスト."""
        result = _format_turns(sample_turns_data, include_details=False)
        assert "社長" in result
        assert "営業担当役員" in result
        # 詳細情報は含まれない
        assert "懸念点:" not in result
        assert "提案:" not in result

    def test_format_turn_with_no_concerns_proposals_questions(self):
        """懸念点・提案・質問がない場合のテスト."""
        turn = {
            "role": "社長",
            "decision": FacilitatorDecision(
                next_speaker="社長",
                prompt="ご意見を",
                rationale="最初",
            ),
            "response": ParticipantResponse(
                summary="特に問題ありません",
                concerns=[],
                proposals=[],
                questions=[],
            ),
        }
        result = _format_turns([turn], include_details=True)
        assert "1. 社長" in result
        assert "特に問題ありません" in result
        # 空のリストは表示されない
        lines = result.split("\n")
        concern_lines = [line for line in lines if "懸念点:" in line]
        assert len(concern_lines) == 0

    def test_format_indexing_starts_at_one(self, sample_turns_data):
        """インデックスが1から始まることをテスト."""
        result = _format_turns(sample_turns_data)
        assert result.startswith("1.")
        assert "0." not in result

    def test_format_preserves_order(self):
        """ターンの順序が保持されることをテスト."""
        turns = [
            {
                "role": "役職A",
                "decision": FacilitatorDecision(
                    next_speaker="役職A", prompt="", rationale=""
                ),
                "response": ParticipantResponse(summary="発言A"),
            },
            {
                "role": "役職B",
                "decision": FacilitatorDecision(
                    next_speaker="役職B", prompt="", rationale=""
                ),
                "response": ParticipantResponse(summary="発言B"),
            },
            {
                "role": "役職C",
                "decision": FacilitatorDecision(
                    next_speaker="役職C", prompt="", rationale=""
                ),
                "response": ParticipantResponse(summary="発言C"),
            },
        ]
        result = _format_turns(turns)
        # 順序を確認
        idx_a = result.find("役職A")
        idx_b = result.find("役職B")
        idx_c = result.find("役職C")
        assert idx_a < idx_b < idx_c


class TestRunBoardMeeting:
    """run_board_meeting関数のテスト（モック使用）."""

    @pytest.mark.asyncio
    async def test_run_board_meeting_basic_structure(
        self, sample_proposal_text, monkeypatch
    ):
        """run_board_meetingの基本構造テスト（モックを使用）."""
        # Runnerをモック化
        mock_result = MagicMock()
        mock_result.final_output_as.side_effect = [
            # ファシリテーターの決定
            FacilitatorDecision(
                next_speaker="社長",
                prompt="ご意見を",
                rationale="最初",
            ),
            # 参加者の応答
            ParticipantResponse(summary="テスト発言"),
            # 議事録
            MagicMock(markdown="# 議事録"),
            # Q&A
            MagicMock(markdown="# Q&A"),
            # 改訂企画書
            MagicMock(markdown="# 改訂企画書"),
            # 評価レポート
            MagicMock(markdown="# 評価レポート"),
        ]

        async def mock_run(*args, **kwargs):
            return mock_result

        # 最小ラウンドでテスト
        with patch("workflow.Runner.run", new=mock_run):
            from workflow import _run_board_meeting

            result = await _run_board_meeting(
                proposal_markdown=sample_proposal_text,
                rounds=1,
                context_turns=0,
                verbose=False,
            )

        # 5つの出力が返されることを確認
        assert len(result) == 5
        minutes, qa, refined, discussion_log, evaluation = result
        assert isinstance(minutes, str)
        assert isinstance(qa, str)
        assert isinstance(refined, str)
        assert isinstance(discussion_log, str)
        assert isinstance(evaluation, str)

    def test_run_board_meeting_sync_wrapper(self, sample_proposal_text):
        """run_board_meetingの同期ラッパーテスト."""
        # 非同期関数をモック化
        mock_result = (
            "# 議事録",
            "# Q&A",
            "# 改訂企画書",
            "# 対話履歴",
            "# 評価",
        )

        async def mock_run_async(*args, **kwargs):
            return mock_result

        with patch("workflow._run_board_meeting", new=mock_run_async):
            result = run_board_meeting(
                proposal_markdown=sample_proposal_text,
                rounds=1,
                context_turns=0,
                verbose=False,
            )

        assert len(result) == 5
        assert result[0] == "# 議事録"


class TestWorkflowIntegration:
    """ワークフロー統合テスト."""

    def test_format_turns_integration_with_real_data(self, sample_turns_data):
        """実際のデータ構造との統合テスト."""
        # sample_turns_dataは正しい構造を持っている
        result = _format_turns(sample_turns_data, include_details=True)

        # 基本情報の確認
        assert "社長" in result
        assert "営業担当役員" in result

        # 詳細情報の確認
        assert "市場リスクの詳細が不明" in result
        assert "段階的投資を提案" in result
        assert "営業担当の見解は?" in result
        assert "価格設定が課題" in result

    def test_discussion_log_markdown_format(self, sample_turns_data):
        """対話履歴のMarkdown形式テスト."""
        # _format_turnsで生成されたテキストがMarkdownとして有効か確認
        result = _format_turns(sample_turns_data, include_details=True)

        # 箇条書きフォーマットの確認
        lines = result.split("\n")
        numbered_lines = [line for line in lines if line.strip().startswith("1.") or line.strip().startswith("2.")]
        assert len(numbered_lines) >= 2

        # インデント付き項目の確認
        indented_lines = [line for line in lines if line.startswith("   -")]
        assert len(indented_lines) > 0


class TestWorkflowEdgeCases:
    """ワークフローのエッジケーステスト."""

    def test_format_turns_with_long_summary(self):
        """長い要約のフォーマットテスト."""
        long_summary = "これは非常に長い要約です。" * 100
        turn = {
            "role": "テスト役職",
            "decision": FacilitatorDecision(
                next_speaker="テスト役職",
                prompt="質問",
                rationale="理由",
            ),
            "response": ParticipantResponse(summary=long_summary),
        }
        result = _format_turns([turn])
        assert long_summary in result

    def test_format_turns_with_multiple_concerns(self):
        """多数の懸念点を持つターンのテスト."""
        concerns = [f"懸念点{i}" for i in range(20)]
        turn = {
            "role": "テスト役職",
            "decision": FacilitatorDecision(
                next_speaker="テスト役職",
                prompt="質問",
                rationale="理由",
            ),
            "response": ParticipantResponse(
                summary="要約",
                concerns=concerns,
            ),
        }
        result = _format_turns([turn], include_details=True)
        assert "懸念点0" in result
        assert "懸念点19" in result

    def test_format_turns_with_special_characters(self):
        """特殊文字を含むターンのテスト."""
        turn = {
            "role": "社長 & CEO",
            "decision": FacilitatorDecision(
                next_speaker="社長 & CEO",
                prompt="投資対効果（ROI）は？",
                rationale="重要な論点",
            ),
            "response": ParticipantResponse(
                summary="売上: 5,000万円 / 利益率: 20%",
                concerns=["コスト > 予算"],
            ),
        }
        result = _format_turns([turn], include_details=True)
        assert "社長 & CEO" in result
        assert "ROI" in result
        assert "5,000万円" in result

    def test_format_turns_with_multiline_summary(self):
        """複数行の要約のテスト."""
        multiline_summary = """第一段落です。
第二段落です。
第三段落です。"""
        turn = {
            "role": "テスト役職",
            "decision": FacilitatorDecision(
                next_speaker="テスト役職",
                prompt="質問",
                rationale="理由",
            ),
            "response": ParticipantResponse(summary=multiline_summary),
        }
        result = _format_turns([turn])
        assert "第一段落" in result
        assert "第二段落" in result
        assert "第三段落" in result
