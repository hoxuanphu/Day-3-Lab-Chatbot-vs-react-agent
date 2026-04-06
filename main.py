"""
History Chatbot - Main Entry Point

Usage:
    python main.py --mode baseline   # RAG Chatbot (no reasoning)
    python main.py --mode agent      # Planner Agent (reasoning + tools)
    python main.py --mode baseline --query "câu hỏi"
    python main.py --mode agent --query "câu hỏi"
"""

import sys
import os
import argparse
import time

# Fix Windows console encoding for Vietnamese
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure the root directory is in the PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()


def run_baseline(question: str):
    """Run the Baseline RAG Chatbot (no reasoning, just retrieve + generate)."""
    from src.agent.rag_baseline import RAGBaselineAgent
    from src.core.gemini_provider import GeminiProvider

    llm = GeminiProvider(model_name="gemini-2.5-flash")

    print("[*] Initializing Baseline Chatbot (RAG)...")
    agent = RAGBaselineAgent(
        llm=llm,
        data_path="data/data.md",
        use_semantic=False,
        top_k=5,
        retrieval_mode="hybrid",
    )
    print("[*] Ready!\n")

    start = time.time()
    answer = agent.run(question)
    elapsed = time.time() - start

    print(answer)
    print(f"\n[Time: {elapsed:.2f}s]")


def run_agent(question: str):
    """Run the Planner Agent (reasoning + tool selection + synthesis)."""
    from src.agent.agent import HistoryAgent
    from src.tools.tool_registry import ToolRegistry
    from src.core.gemini_provider import GeminiProvider

    llm = GeminiProvider(model_name="gemini-2.5-flash")

    print("[*] Initializing Planner Agent...")
    tool_registry = ToolRegistry(data_path="data/data.md")
    agent = HistoryAgent(llm=llm, tool_registry=tool_registry)
    print("[*] Ready!\n")

    start = time.time()
    answer = agent.run(question)
    elapsed = time.time() - start

    print(answer)
    print(f"\n[Time: {elapsed:.2f}s]")


def main():
    parser = argparse.ArgumentParser(
        description="History Chatbot - Baseline vs Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --mode baseline
  python main.py --mode agent
  python main.py --mode agent --query "Duong Truong Son phat trien nhu the nao?"
        """
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "agent"],
        default="baseline",
        help="baseline = RAG Chatbot | agent = Planner Agent with tools"
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Custom question (default: uses built-in test question)"
    )
    args = parser.parse_args()

    # Default test question
    default_question = (
        "hãy theo dõi sự phát triển về quy mô (chiều dài, năng lực vận tải) "
        "của tuyến đường chiến lược Trường Sơn (Đoàn 559) từ những năm 1965 "
        "đến đầu năm 1975. Sự lớn mạnh của tuyến đường này đã đóng vai trò "
        "quyết định như thế nào trong khâu hậu cần cho cuộc Tổng tiến công "
        "và nổi dậy mùa Xuân 1975?"
    )
    question = args.query if args.query else default_question

    print("=" * 60)
    print(f"  Mode: {args.mode.upper()}")
    print(f"  Question: {question[:80]}...")
    print("=" * 60)

    if args.mode == "baseline":
        run_baseline(question)
    else:
        run_agent(question)


if __name__ == "__main__":
    main()
