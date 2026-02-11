"""経営会議の討論ワークフロー."""
import asyncio
from typing import Dict, List, Tuple

from agents import Runner
from meeting_agents import (
    ROLE_INSTRUCTIONS,
    create_facilitator,
    create_minutes_writer,
    create_participant,
    create_qa_writer,
    create_refiner,
    create_evaluator,
)
from models import FacilitatorDecision, MinutesOutput, ParticipantResponse, QAOutput, RefinedProposalOutput, EvaluationOutput


def _format_turns(turns: List[Dict], include_details: bool = True) -> str:
    lines: List[str] = []
    for idx, turn in enumerate(turns, start=1):
        lines.append(f"{idx}. {turn['role']}（指名理由: {turn['decision'].rationale}）")
        lines.append(f"   - ファシリテーター指示: {turn['decision'].prompt}")
        lines.append(f"   - 発言要約: {turn['response'].summary}")
        if include_details:
            if turn['response'].concerns:
                lines.append("   - 懸念点:")
                lines.extend([f"     - {c}" for c in turn['response'].concerns])
            if turn['response'].proposals:
                lines.append("   - 提案:")
                lines.extend([f"     - {p}" for p in turn['response'].proposals])
            if turn['response'].questions:
                lines.append("   - 質問:")
                lines.extend([f"     - {q}" for q in turn['response'].questions])
    return "\n".join(lines)


async def _run_board_meeting(
    proposal_markdown: str,
    rounds: int = 12,
    context_turns: int = 6,
    verbose: bool = True,
) -> Tuple[str, str, str, str, str]:
    roles = list(ROLE_INSTRUCTIONS.keys())
    effective_rounds = max(rounds, len(roles))

    facilitator = create_facilitator()
    participants = {role: create_participant(role) for role in roles}
    minutes_writer = create_minutes_writer()
    qa_writer = create_qa_writer()
    refiner = create_refiner()
    evaluator = create_evaluator()

    counts: Dict[str, int] = {role: 0 for role in roles}
    turns: List[Dict] = []

    if verbose:
        print("=" * 80)
        print("🏢 経営会議討論を開始します")
        print("=" * 80)
        print(f"\n📋 参加者: {', '.join(roles)}")
        print(f"🔄 討論ラウンド数: {effective_rounds}\n")

    for round_idx in range(effective_rounds):
        missing_roles = [role for role, count in counts.items() if count == 0]
        allowed_roles = missing_roles if missing_roles else roles

        recent_turns = turns[-context_turns:] if context_turns > 0 else []
        discussion_context = _format_turns(recent_turns, include_details=True) or "(まだ発言はありません)"

        facilitator_prompt = f"""あなたは経営会議のファシリテーターです。
次の発言者を選んでください。

## 企画書（抜粋）
{proposal_markdown}

## これまでの議論（直近）
{discussion_context}

## 参加状況
""" + "\n".join([f"- {role}: {counts[role]}回" for role in roles]) + f"""

## 次に指名できる役割
{', '.join(allowed_roles)}

指名理由は簡潔にし、重要論点が未整理なら質問で掘り下げてください。
"""

        if verbose:
            print(f"\n{'─' * 80}")
            print(f"🔄 ラウンド {round_idx + 1}/{effective_rounds}")
            print(f"{'─' * 80}")

        decision_result = await Runner.run(facilitator, facilitator_prompt)
        decision = decision_result.final_output_as(FacilitatorDecision)
        speaker = decision.next_speaker.strip()

        if verbose:
            print(f"\n👤 ファシリテーター → {speaker} を指名")
            print(f"   理由: {decision.rationale}")
            print(f"   指示: {decision.prompt}")

        if speaker not in allowed_roles:
            speaker = allowed_roles[0]

        participant_prompt = f"""あなたは「{speaker}」として発言してください。

## 企画書
{proposal_markdown}

## ファシリテーターからの指示
{decision.prompt}

## これまでの議論（直近）
{discussion_context}

上記を踏まえ、役割の観点から意見・懸念・改善提案・質問を出してください。
"""

        response_result = await Runner.run(participants[speaker], participant_prompt)
        response = response_result.final_output_as(ParticipantResponse)

        if verbose:
            print(f"\n💬 {speaker} の発言:")
            print(f"   {response.summary}")
            if response.concerns:
                print(f"   ⚠️  懸念点: {len(response.concerns)}件")
            if response.proposals:
                print(f"   💡 提案: {len(response.proposals)}件")
            if response.questions:
                print(f"   ❓ 質問: {len(response.questions)}件")

        counts[speaker] += 1
        turns.append(
            {
                "role": speaker,
                "decision": decision,
                "response": response,
            }
        )

        if all(counts[role] > 0 for role in roles) and len(turns) >= effective_rounds:
            break

    if verbose:
        print("\n" + "=" * 80)
        print("✅ 討論完了")
        print("=" * 80)
        print("\n📊 発言回数:")
        for role in roles:
            print(f"   - {role}: {counts[role]}回")
        print(f"\n📝 議事録・想定問答・改訂企画書を生成中...\n")

    full_discussion = _format_turns(turns, include_details=True)
    
    # 対話履歴をMarkdown形式で整形
    discussion_log_md = f"""# 経営会議 対話履歴

## 会議情報
- 討論ラウンド数: {len(turns)}
- 参加者: {', '.join(roles)}

## 発言回数
"""
    for role in roles:
        discussion_log_md += f"- {role}: {counts[role]}回\n"
    
    discussion_log_md += "\n## 討論詳細\n\n"
    
    for idx, turn in enumerate(turns, start=1):
        discussion_log_md += f"### ラウンド {idx}: {turn['role']}\n\n"
        discussion_log_md += f"**ファシリテーターの指名理由:** {turn['decision'].rationale}\n\n"
        discussion_log_md += f"**ファシリテーターからの指示:**\n{turn['decision'].prompt}\n\n"
        discussion_log_md += f"**発言要約:**\n{turn['response'].summary}\n\n"
        
        if turn['response'].concerns:
            discussion_log_md += "**懸念点:**\n"
            for concern in turn['response'].concerns:
                discussion_log_md += f"- {concern}\n"
            discussion_log_md += "\n"
        
        if turn['response'].proposals:
            discussion_log_md += "**提案:**\n"
            for proposal in turn['response'].proposals:
                discussion_log_md += f"- {proposal}\n"
            discussion_log_md += "\n"
        
        if turn['response'].questions:
            discussion_log_md += "**質問:**\n"
            for question in turn['response'].questions:
                discussion_log_md += f"- {question}\n"
            discussion_log_md += "\n"
        
        discussion_log_md += "---\n\n"

    minutes_prompt = f"""以下の経営会議の討論ログを議事録にまとめてください。

## 企画書
{proposal_markdown}

## 参加者
""" + "\n".join([f"- {role}" for role in roles]) + f"""

## 討論ログ
{full_discussion}
"""

    minutes_result = await Runner.run(minutes_writer, minutes_prompt)
    minutes = minutes_result.final_output_as(MinutesOutput)

    qa_prompt = f"""以下の経営会議内容をもとに想定問答集を作成してください。

## 企画書
{proposal_markdown}

## 討論ログ
{full_discussion}
"""

    qa_result = await Runner.run(qa_writer, qa_prompt)
    qa_output = qa_result.final_output_as(QAOutput)

    refined_prompt = f"""以下の企画書を経営会議の議論を踏まえてブラッシュアップしてください。

## 元の企画書
{proposal_markdown}

## 討論ログ
{full_discussion}
"""

    refined_result = await Runner.run(refiner, refined_prompt)
    refined_output = refined_result.final_output_as(RefinedProposalOutput)

    if verbose:
        print("📊 提案書の評価レポートを生成中...\n")

    evaluation_prompt = f"""以下の原版と改訂版の企画書を比較評価してください。

## 原版企画書
{proposal_markdown}

## 改訂版企画書（経営会議の議論を踏まえた改訂）
{refined_output.markdown}

## 討論ログ, str
{full_discussion}

上記を踏まえ、提案の質を詳細に評価し、経営判断のための推奨事項をまとめてください。
"""

    evaluation_result = await Runner.run(evaluator, evaluation_prompt)
    evaluation_output = evaluation_result.final_output_as(EvaluationOutput)

    if verbose:
        print("✅ すべての成果物の生成が完了しました\n")

    return minutes.markdown, qa_output.markdown, refined_output.markdown, discussion_log_md, evaluation_output.markdown


def run_board_meeting(
    proposal_markdown: str,
    rounds: int = 12,
    context_turns: int = 6,
    verbose: bool = True,
) -> Tuple[str, str, str, str, str]:
    return asyncio.run(
        _run_board_meeting(
            proposal_markdown=proposal_markdown,
            rounds=rounds,
            context_turns=context_turns,
            verbose=verbose,
        )
    )
