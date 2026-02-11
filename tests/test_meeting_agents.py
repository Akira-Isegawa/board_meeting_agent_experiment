"""meeting_agents.pyのエージェント作成関数の単体テスト."""
import pytest
from agents import Agent
from meeting_agents import (
    ROLE_INSTRUCTIONS,
    create_facilitator,
    create_participant,
    create_minutes_writer,
    create_qa_writer,
    create_refiner,
    create_evaluator,
)
from models import (
    FacilitatorDecision,
    ParticipantResponse,
    MinutesOutput,
    QAOutput,
    RefinedProposalOutput,
    EvaluationOutput,
)


class TestRoleInstructions:
    """ROLE_INSTRUCTIONSの定数テスト."""

    def test_all_roles_defined(self, all_roles):
        """すべての役職が定義されているかテスト."""
        for role in all_roles:
            assert role in ROLE_INSTRUCTIONS, f"{role}の説明が定義されていません"

    def test_all_instructions_non_empty(self, all_roles):
        """各役職の説明が空でないことをテスト."""
        for role in all_roles:
            assert len(ROLE_INSTRUCTIONS[role]) > 0
            assert isinstance(ROLE_INSTRUCTIONS[role], str)

    def test_instructions_contain_role_context(self):
        """各役職の説明に役職名が含まれることをテスト."""
        assert "社長" in ROLE_INSTRUCTIONS["社長"]
        assert "営業" in ROLE_INSTRUCTIONS["営業担当役員"]
        assert "製造" in ROLE_INSTRUCTIONS["製造担当役員"]
        assert "知的財産" in ROLE_INSTRUCTIONS["知的財産権の専門家"]

    def test_role_count(self, all_roles):
        """定義されている役職数が正しいことをテスト."""
        assert len(ROLE_INSTRUCTIONS) == len(all_roles)


class TestCreateFacilitator:
    """create_facilitator関数のテスト."""

    def test_returns_agent_instance(self):
        """Agentインスタンスが返されることをテスト."""
        facilitator = create_facilitator()
        assert isinstance(facilitator, Agent)

    def test_agent_name(self):
        """エージェント名が正しいことをテスト."""
        facilitator = create_facilitator()
        assert facilitator.name == "Facilitator"

    def test_output_type(self):
        """出力型がFacilitatorDecisionであることをテスト."""
        facilitator = create_facilitator()
        assert facilitator.output_type == FacilitatorDecision

    def test_has_instructions(self):
        """インストラクションが設定されていることをテスト."""
        facilitator = create_facilitator()
        assert facilitator.instructions
        assert len(facilitator.instructions) > 0
        assert "ファシリテーター" in facilitator.instructions


class TestCreateParticipant:
    """create_participant関数のテスト."""

    def test_returns_agent_instance(self, all_roles):
        """すべての役職でAgentインスタンスが返されることをテスト."""
        for role in all_roles:
            agent = create_participant(role)
            assert isinstance(agent, Agent)

    def test_agent_name_matches_role(self, all_roles):
        """エージェント名が役職名と一致することをテスト."""
        for role in all_roles:
            agent = create_participant(role)
            assert agent.name == role

    def test_output_type(self):
        """出力型がParticipantResponseであることをテスト."""
        agent = create_participant("社長")
        assert agent.output_type == ParticipantResponse

    def test_instructions_contain_role_context(self):
        """インストラクションに役職に応じた内容が含まれることをテスト."""
        president = create_participant("社長")
        assert "社長" in president.instructions
        assert "全社視点" in president.instructions or "成長性" in president.instructions

        sales = create_participant("営業担当役員")
        assert "営業" in sales.instructions

    def test_instructions_contain_common_rules(self):
        """すべてのエージェントに共通ルールが含まれることをテスト."""
        agent = create_participant("社長")
        assert "日本語" in agent.instructions
        assert "懸念点" in agent.instructions or "改善" in agent.instructions

    def test_different_roles_have_different_instructions(self):
        """異なる役職は異なるインストラクションを持つことをテスト."""
        president = create_participant("社長")
        accountant = create_participant("会計の専門家")
        # インストラクションが異なることを確認
        assert president.instructions != accountant.instructions


class TestCreateMinutesWriter:
    """create_minutes_writer関数のテスト."""

    def test_returns_agent_instance(self):
        """Agentインスタンスが返されることをテスト."""
        writer = create_minutes_writer()
        assert isinstance(writer, Agent)

    def test_agent_name(self):
        """エージェント名が正しいことをテスト."""
        writer = create_minutes_writer()
        assert writer.name == "Minutes Writer"

    def test_output_type(self):
        """出力型がMinutesOutputであることをテスト."""
        writer = create_minutes_writer()
        assert writer.output_type == MinutesOutput

    def test_instructions_contain_required_sections(self):
        """インストラクションに必要なセクションが含まれることをテスト."""
        writer = create_minutes_writer()
        required_sections = [
            "会議概要",
            "参加者",
            "主な論点",
            "合意事項",
            "未決事項",
            "次のアクション",
        ]
        for section in required_sections:
            assert section in writer.instructions, f"{section}がインストラクションに含まれていません"


class TestCreateQAWriter:
    """create_qa_writer関数のテスト."""

    def test_returns_agent_instance(self):
        """Agentインスタンスが返されることをテスト."""
        writer = create_qa_writer()
        assert isinstance(writer, Agent)

    def test_agent_name(self):
        """エージェント名が正しいことをテスト."""
        writer = create_qa_writer()
        assert writer.name == "Q&A Writer"

    def test_output_type(self):
        """出力型がQAOutputであることをテスト."""
        writer = create_qa_writer()
        assert writer.output_type == QAOutput

    def test_instructions_contain_qa_format(self):
        """インストラクションにQ&Aフォーマットが含まれることをテスト."""
        writer = create_qa_writer()
        assert "Q:" in writer.instructions or "質問" in writer.instructions
        assert "A:" in writer.instructions or "回答" in writer.instructions

    def test_instructions_specify_minimum_questions(self):
        """インストラクションに最低質問数が指定されていることをテスト."""
        writer = create_qa_writer()
        assert "12" in writer.instructions


class TestCreateRefiner:
    """create_refiner関数のテスト."""

    def test_returns_agent_instance(self):
        """Agentインスタンスが返されることをテスト."""
        refiner = create_refiner()
        assert isinstance(refiner, Agent)

    def test_agent_name(self):
        """エージェント名が正しいことをテスト."""
        refiner = create_refiner()
        assert refiner.name == "Proposal Refiner"

    def test_output_type(self):
        """出力型がRefinedProposalOutputであることをテスト."""
        refiner = create_refiner()
        assert refiner.output_type == RefinedProposalOutput

    def test_instructions_contain_required_sections(self):
        """インストラクションに必要なセクションが含まれることをテスト."""
        refiner = create_refiner()
        required_sections = [
            "背景と目的",
            "事業概要",
            "実行計画",
            "予算",
            "リスクと対策",
        ]
        for section in required_sections:
            assert section in refiner.instructions, f"{section}がインストラクションに含まれていません"


class TestCreateEvaluator:
    """create_evaluator関数のテスト."""

    def test_returns_agent_instance(self):
        """Agentインスタンスが返されることをテスト."""
        evaluator = create_evaluator()
        assert isinstance(evaluator, Agent)

    def test_agent_name(self):
        """エージェント名が正しいことをテスト."""
        evaluator = create_evaluator()
        assert evaluator.name == "Proposal Evaluator"

    def test_output_type(self):
        """出力型がEvaluationOutputであることをテスト."""
        evaluator = create_evaluator()
        assert evaluator.output_type == EvaluationOutput

    def test_instructions_contain_evaluation_criteria(self):
        """インストラクションに評価観点が含まれることをテスト."""
        evaluator = create_evaluator()
        criteria = [
            "売上",
            "成長性",
            "リスク",
            "実現可能性",
            "シナジー",
        ]
        for criterion in criteria:
            assert criterion in evaluator.instructions, f"{criterion}が評価観点に含まれていません"

    def test_instructions_contain_output_format(self):
        """インストラクションに出力形式が含まれることをテスト."""
        evaluator = create_evaluator()
        output_elements = [
            "総合評価",
            "スコアカード",
            "推奨事項",
            "Go/No-Go",
        ]
        for element in output_elements:
            assert element in evaluator.instructions, f"{element}が出力形式に含まれていません"


class TestAgentsIntegration:
    """エージェント統合テスト."""

    def test_all_agents_can_be_created(self, all_roles):
        """すべてのエージェントが正常に作成できることをテスト."""
        # ファシリテーター
        facilitator = create_facilitator()
        assert facilitator is not None

        # 参加者
        for role in all_roles:
            participant = create_participant(role)
            assert participant is not None

        # 出力生成エージェント
        assert create_minutes_writer() is not None
        assert create_qa_writer() is not None
        assert create_refiner() is not None
        assert create_evaluator() is not None

    def test_agents_have_unique_output_types(self):
        """各エージェントが適切な出力型を持つことをテスト."""
        # Agentオブジェクトはハッシュ可能でないため、リストで管理
        agent_output_pairs = [
            (create_facilitator(), FacilitatorDecision),
            (create_participant("社長"), ParticipantResponse),
            (create_minutes_writer(), MinutesOutput),
            (create_qa_writer(), QAOutput),
            (create_refiner(), RefinedProposalOutput),
            (create_evaluator(), EvaluationOutput),
        ]

        for agent, expected_type in agent_output_pairs:
            assert agent.output_type == expected_type
