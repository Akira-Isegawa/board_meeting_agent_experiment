"""models.pyのPydanticモデルの単体テスト."""
import pytest
from pydantic import ValidationError
from models import (
    FacilitatorDecision,
    ParticipantResponse,
    MinutesOutput,
    QAOutput,
    RefinedProposalOutput,
    EvaluationOutput,
)


class TestFacilitatorDecision:
    """FacilitatorDecisionモデルのテスト."""

    def test_valid_creation(self):
        """正常なインスタンス作成のテスト."""
        decision = FacilitatorDecision(
            next_speaker="社長",
            prompt="全社視点での見解をお聞かせください",
            rationale="最初の発言として",
        )
        assert decision.next_speaker == "社長"
        assert decision.prompt == "全社視点での見解をお聞かせください"
        assert decision.rationale == "最初の発言として"

    def test_missing_required_field(self):
        """必須フィールドが欠けている場合のテスト."""
        with pytest.raises(ValidationError) as exc_info:
            FacilitatorDecision(
                next_speaker="社長",
                prompt="質問内容",
                # rationale が欠けている
            )
        assert "rationale" in str(exc_info.value)

    def test_empty_strings(self):
        """空文字列での作成テスト（許容される）."""
        decision = FacilitatorDecision(
            next_speaker="",
            prompt="",
            rationale="",
        )
        assert decision.next_speaker == ""
        assert decision.prompt == ""
        assert decision.rationale == ""


class TestParticipantResponse:
    """ParticipantResponseモデルのテスト."""

    def test_valid_creation_with_all_fields(self):
        """全フィールド指定での正常作成テスト."""
        response = ParticipantResponse(
            summary="テスト要約",
            concerns=["懸念1", "懸念2"],
            proposals=["提案1"],
            questions=["質問1", "質問2", "質問3"],
        )
        assert response.summary == "テスト要約"
        assert len(response.concerns) == 2
        assert len(response.proposals) == 1
        assert len(response.questions) == 3

    def test_valid_creation_with_summary_only(self):
        """summaryのみ指定した場合のテスト."""
        response = ParticipantResponse(summary="要約のみ")
        assert response.summary == "要約のみ"
        assert response.concerns == []
        assert response.proposals == []
        assert response.questions == []

    def test_missing_summary(self):
        """summaryが欠けている場合のエラーテスト."""
        with pytest.raises(ValidationError) as exc_info:
            ParticipantResponse(
                concerns=["懸念"],
                proposals=["提案"],
            )
        assert "summary" in str(exc_info.value)

    def test_empty_lists(self):
        """空リストでの作成テスト."""
        response = ParticipantResponse(
            summary="テスト",
            concerns=[],
            proposals=[],
            questions=[],
        )
        assert response.concerns == []
        assert response.proposals == []
        assert response.questions == []


class TestMinutesOutput:
    """MinutesOutputモデルのテスト."""

    def test_valid_creation(self):
        """正常なMarkdown出力のテスト."""
        minutes = MinutesOutput(markdown="# 議事録\n\n内容...")
        assert minutes.markdown == "# 議事録\n\n内容..."

    def test_empty_markdown(self):
        """空のMarkdownでのテスト."""
        minutes = MinutesOutput(markdown="")
        assert minutes.markdown == ""

    def test_missing_markdown(self):
        """markdownフィールド欠損のエラーテスト."""
        with pytest.raises(ValidationError) as exc_info:
            MinutesOutput()
        assert "markdown" in str(exc_info.value)


class TestQAOutput:
    """QAOutputモデルのテスト."""

    def test_valid_creation(self):
        """正常なQA出力のテスト."""
        qa = QAOutput(markdown="# Q&A\n\nQ: 質問\nA: 回答")
        assert "Q: 質問" in qa.markdown

    def test_multiline_markdown(self):
        """複数行Markdownのテスト."""
        content = """# 想定問答
        
## Q1: 質問1
A: 回答1

## Q2: 質問2
A: 回答2
"""
        qa = QAOutput(markdown=content)
        assert "Q1" in qa.markdown
        assert "Q2" in qa.markdown


class TestRefinedProposalOutput:
    """RefinedProposalOutputモデルのテスト."""

    def test_valid_creation(self):
        """正常な改訂企画書出力のテスト."""
        refined = RefinedProposalOutput(markdown="# 改訂企画書\n\n内容...")
        assert refined.markdown.startswith("# 改訂企画書")

    def test_large_markdown(self):
        """大きなMarkdownコンテンツのテスト."""
        large_content = "# 企画書\n\n" + ("内容 " * 10000)
        refined = RefinedProposalOutput(markdown=large_content)
        assert len(refined.markdown) > 10000


class TestEvaluationOutput:
    """EvaluationOutputモデルのテスト."""

    def test_valid_creation(self):
        """正常な評価レポート出力のテスト."""
        evaluation = EvaluationOutput(markdown="# 評価レポート\n\n## 総合評価\n...")
        assert "評価レポート" in evaluation.markdown

    def test_with_special_characters(self):
        """特殊文字を含むMarkdownのテスト."""
        content = "# 評価\n\n- スコア: 85/100 ⭐\n- 判定: Go ✅"
        evaluation = EvaluationOutput(markdown=content)
        assert "85/100" in evaluation.markdown
        assert "Go" in evaluation.markdown


class TestModelsIntegration:
    """複数のモデルを組み合わせた統合テスト."""

    def test_full_workflow_data_structure(self):
        """ワークフロー全体で使用されるデータ構造のテスト."""
        # ファシリテーターの決定
        decision = FacilitatorDecision(
            next_speaker="社長",
            prompt="ご意見をお聞かせください",
            rationale="最初の発言",
        )

        # 参加者の応答
        response = ParticipantResponse(
            summary="全社視点で重要な企画です",
            concerns=["予算オーバーのリスク"],
            proposals=["段階的投資"],
            questions=["営業担当の見解は?"],
        )

        # 出力物
        minutes = MinutesOutput(markdown="# 議事録")
        qa = QAOutput(markdown="# Q&A")
        refined = RefinedProposalOutput(markdown="# 改訂版")
        evaluation = EvaluationOutput(markdown="# 評価")

        # すべてが正常に作成されることを確認
        assert decision.next_speaker == "社長"
        assert len(response.concerns) == 1
        assert minutes.markdown == "# 議事録"
        assert qa.markdown == "# Q&A"
        assert refined.markdown == "# 改訂版"
        assert evaluation.markdown == "# 評価"

    def test_turn_data_structure(self, sample_turns_data):
        """ターンデータ構造の妥当性テスト."""
        for turn in sample_turns_data:
            assert "role" in turn
            assert "decision" in turn
            assert "response" in turn
            assert isinstance(turn["decision"], FacilitatorDecision)
            assert isinstance(turn["response"], ParticipantResponse)
            assert turn["decision"].next_speaker == turn["role"]
