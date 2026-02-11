"""pytest共通フィクスチャとテストデータ."""
import pytest
from typing import Dict, List


@pytest.fixture
def sample_proposal_text() -> str:
    """テスト用のサンプル企画書."""
    return """# 新規事業企画書

## 背景と目的
市場拡大を目指し、新製品を開発します。

## 事業概要
- 製品名: テスト製品
- ターゲット: 法人向け
- 予算: 5000万円

## 実行計画
2026年Q2から開始予定。

## リスクと対策
競合対策が必要。
"""


@pytest.fixture
def sample_turns_data() -> List[Dict]:
    """テスト用のターンデータ."""
    from models import FacilitatorDecision, ParticipantResponse
    
    return [
        {
            "role": "社長",
            "decision": FacilitatorDecision(
                next_speaker="社長",
                prompt="全社視点での見解をお聞かせください",
                rationale="最初の発言として",
            ),
            "response": ParticipantResponse(
                summary="売上拡大に期待します。投資対効果を重視します。",
                concerns=["市場リスクの詳細が不明"],
                proposals=["段階的投資を提案"],
                questions=["営業担当の見解は?"],
            ),
        },
        {
            "role": "営業担当役員",
            "decision": FacilitatorDecision(
                next_speaker="営業担当役員",
                prompt="市場ニーズはどうですか",
                rationale="営業視点が必要",
            ),
            "response": ParticipantResponse(
                summary="顧客からの問い合わせが増えています。",
                concerns=["価格設定が課題"],
                proposals=["市場調査を実施"],
                questions=[],
            ),
        },
    ]


@pytest.fixture
def all_roles() -> List[str]:
    """全役職のリスト."""
    return [
        "社長",
        "営業担当役員",
        "企画・設計担当役員",
        "製造担当役員",
        "バックオフィス担当役員",
        "製造業のコンサルタント",
        "知的財産権の専門家",
        "法務の専門家",
        "会計の専門家",
    ]
