"""board_meeting - 経営会議討論シミュレーションCLI."""
import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from workflow import run_board_meeting


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenAI Agents SDKで経営会議の討論をシミュレーションします。",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="企画書Markdownファイルのパス",
    )
    parser.add_argument(
        "--output-dir",
        default="./outputs",
        help="出力先ディレクトリ（デフォルト: ./outputs）",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=12,
        help="討論ラウンド数（デフォルト: 12）",
    )
    parser.add_argument(
        "--context-turns",
        type=int,
        default=6,
        help="各発言時に参照する直近の発言数（デフォルト: 6）",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ エラー: OPENAI_API_KEY が設定されていません。")
        print(".env に OPENAI_API_KEY を設定するか、環境変数に設定してください。")
        sys.exit(1)

    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()

    if not input_path.exists():
        print(f"❌ 入力ファイルが見つかりません: {input_path}")
        sys.exit(1)

    if args.rounds < 1:
        print("❌ rounds は1以上を指定してください。")
        sys.exit(1)

    proposal_text = input_path.read_text(encoding="utf-8")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        minutes_md, qa_md, refined_md, discussion_log_md, evaluation_md = run_board_meeting(
            proposal_markdown=proposal_text,
            rounds=args.rounds,
            context_turns=args.context_turns,
            verbose=True,
        )
    except KeyboardInterrupt:
        print("\n❌ ユーザーによって中断されました。")
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌ エラーが発生しました: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    minutes_path = output_dir / "minutes.md"
    qa_path = output_dir / "qa.md"
    refined_path = output_dir / "refined_proposal.md"
    discussion_log_path = output_dir / "discussion_log.md"
    evaluation_path = output_dir / "evaluation.md"

    minutes_path.write_text(minutes_md, encoding="utf-8")
    qa_path.write_text(qa_md, encoding="utf-8")
    refined_path.write_text(refined_md, encoding="utf-8")
    discussion_log_path.write_text(discussion_log_md, encoding="utf-8")
    evaluation_path.write_text(evaluation_md, encoding="utf-8")

    print("✅ 生成完了")
    print(f"- 議事録: {minutes_path}")
    print(f"- 想定問答: {qa_path}")
    print(f"- 改訂企画書: {refined_path}")
    print(f"- 対話履歴: {discussion_log_path}")
    print(f"- 評価レポート: {evaluation_path}")


if __name__ == "__main__":
    main()
