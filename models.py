"""board_meeting 用の出力スキーマ."""
from typing import List
from pydantic import BaseModel, Field


class FacilitatorDecision(BaseModel):
    next_speaker: str = Field(..., description="次に発言する役職")
    prompt: str = Field(..., description="次の発言者への質問/指示")
    rationale: str = Field(..., description="指名理由の簡潔な説明")


class ParticipantResponse(BaseModel):
    summary: str = Field(..., description="発言の要約（2-4文）")
    concerns: List[str] = Field(default_factory=list, description="懸念点")
    proposals: List[str] = Field(default_factory=list, description="提案・改善案")
    questions: List[str] = Field(default_factory=list, description="他メンバーへの質問")


class MinutesOutput(BaseModel):
    markdown: str = Field(..., description="議事録Markdown")


class QAOutput(BaseModel):
    markdown: str = Field(..., description="想定問答集Markdown")


class RefinedProposalOutput(BaseModel):
    markdown: str = Field(..., description="改訂企画書Markdown")


class EvaluationOutput(BaseModel):
    markdown: str = Field(..., description="企画書評価レポートMarkdown")
