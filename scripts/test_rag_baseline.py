"""
Test script for the RAG Baseline pipeline.
Tests: Chunking -> Retrieval (BM25 + Hybrid) -> Generation

Usage:
    python scripts/test_rag_baseline.py                 # Full test (needs API key)
    python scripts/test_rag_baseline.py --bm25-only     # BM25 only (no API needed)
"""

import os
import sys
import time
from dotenv import load_dotenv

# Fix Windows console encoding for Vietnamese + emoji
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from src.rag.chunker import MarkdownChunker
from src.rag.retriever import HybridRetriever
from src.rag.generator import RAGGenerator
from src.core.openai_provider import OpenAIProvider


def test_chunking():
    """Test 1: Document chunking."""
    print("=" * 70)
    print("[TEST 1] CHUNKING")
    print("=" * 70)

    chunker = MarkdownChunker(
        max_chunk_size=1500,
        chunk_overlap=200,
        min_chunk_size=100,
    )

    data_path = "data/data.md"
    chunks = chunker.chunk_file(data_path)

    print(f"\n[OK] Total chunks created: {len(chunks)}")
    print(f"   Average chunk size: {sum(c.char_count for c in chunks) // len(chunks)} chars")
    print(f"   Total words: {sum(c.word_count for c in chunks):,}")
    print(f"   Min chunk size: {min(c.char_count for c in chunks)} chars")
    print(f"   Max chunk size: {max(c.char_count for c in chunks)} chars")

    # Show a few sample chunks
    print("\n--- Sample Chunks ---")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n  Chunk {i+1} (ID: {chunk.chunk_id}):")
        ch = chunk.chapter[:60] + "..." if len(chunk.chapter) > 60 else chunk.chapter
        print(f"    Chapter: {ch}")
        sec = chunk.section[:60] + "..." if len(chunk.section) > 60 else chunk.section  
        print(f"    Section: {sec}")
        print(f"    Size: {chunk.char_count} chars, {chunk.word_count} words")
        print(f"    Preview: {chunk.content[:150]}...")

    # Save chunks for caching
    chunks_cache = "data/chunks.json"
    chunker.save_chunks(chunks, chunks_cache)
    print(f"\n[SAVED] Chunks saved to: {chunks_cache}")

    return chunks


def test_bm25_retrieval(chunks):
    """Test 2: BM25-only retrieval."""
    print("\n" + "=" * 70)
    print("[TEST 2] BM25 RETRIEVAL")
    print("=" * 70)

    retriever = HybridRetriever(
        chunks=chunks,
        use_semantic=False,
    )

    test_queries = [
        "Chien tranh pha hoai mien Bac",
        "Chu tich Ho Chi Minh tuyen bo",
        "Tong tien cong mua Xuan 1975",
    ]

    for query in test_queries:
        print(f"\n  Query: \"{query}\"")
        results = retriever.retrieve(query, top_k=3, mode="bm25")
        for i, r in enumerate(results, 1):
            sec = r.chunk.section[:50] if r.chunk.section else "N/A"
            print(f"    [{i}] Score: {r.score:.4f} | Section: {sec}")
            print(f"        Preview: {r.chunk.content[:100]}...")

    return retriever


def test_hybrid_retrieval(chunks):
    """Test 3: Hybrid retrieval (BM25 + Semantic)."""
    print("\n" + "=" * 70)
    print("[TEST 3] HYBRID RETRIEVAL (BM25 + Semantic)")
    print("=" * 70)

    retriever = HybridRetriever(
        chunks=chunks,
        use_semantic=True,
        embedding_cache_dir="data/embeddings",
    )

    query = "Vai tro cua hau phuong mien Bac trong khang chien chong My"
    print(f"\n  Query: \"{query}\"")

    results = retriever.retrieve(query, top_k=5, mode="hybrid")
    for i, r in enumerate(results, 1):
        ch = r.chunk.chapter[:60] if r.chunk.chapter else "N/A"
        sec = r.chunk.section[:60] if r.chunk.section else "N/A"
        print(f"\n    [{i}] Score: {r.score:.4f} | Source: {r.source}")
        print(f"        Chapter: {ch}")
        print(f"        Section: {sec}")
        print(f"        Preview: {r.chunk.content[:120]}...")

    return retriever


def test_generation(retriever):
    """Test 4: Full RAG generation."""
    print("\n" + "=" * 70)
    print("[TEST 4] RAG GENERATION")
    print("=" * 70)

    llm = OpenAIProvider(model_name="gpt-4o-mini")
    generator = RAGGenerator(
        retriever=retriever,
        llm=llm,
        top_k=5,
        retrieval_mode="hybrid",
    )

    test_questions = [
        "Chien luoc 'chien tranh cuc bo' cua My la gi va duoc trien khai nhu the nao?",
        "Mien Bac da chuyen huong kinh te sang thoi chien nhu the nao trong giai doan 1965-1968?",
        "Vai tro cua giao thong van tai trong khang chien chong My ra sao?",
    ]

    for question in test_questions:
        print(f"\n{'~' * 60}")
        print(f"[Q] Cau hoi: {question}")
        print(f"{'~' * 60}")

        start_time = time.time()
        result = generator.generate(question)
        elapsed = time.time() - start_time

        print(f"\n[A] Tra loi:\n{result['answer']}")
        print(f"\n[TIME] {elapsed:.2f}s")
        print(f"[SOURCES] {len(result['sources'])} sources used")
        usage = result['metadata'].get('llm_usage', {})
        if usage:
            print(f"[TOKENS] {usage}")


def test_rag_baseline():
    """Test 5: Full Baseline Agent end-to-end."""
    print("\n" + "=" * 70)
    print("[TEST 5] BASELINE AGENT (End-to-End)")
    print("=" * 70)

    from src.agent.rag_baseline import RAGBaselineAgent
    
    llm = OpenAIProvider(model_name="gpt-4o-mini")
    
    print("\n[INIT] Initializing Baseline Agent...")
    agent = RAGBaselineAgent(
        llm=llm,
        data_path="data/data.md",
        use_semantic=True,
        top_k=5,
    )

    question = "Chien luoc 'chien tranh cuc bo' cua My la gi va duoc trien khai nhu the nao?"
    
    print(f"\n[Q] Cau hoi: {question}")
    print(f"{'~' * 60}")
    
    start_time = time.time()
    answer = agent.run(question)
    elapsed = time.time() - start_time

    print(f"\n[A] Tra loi:\n{answer}")
    print(f"\n[TIME] Tong thoi gian: {elapsed:.2f}s")


if __name__ == "__main__":
    bm25_only = "--bm25-only" in sys.argv

    print("=" * 70)
    print("RAG Baseline Pipeline Test")
    if bm25_only:
        print("  Mode: BM25 only (no API key needed)")
    else:
        print("  Mode: Full (requires OpenAI API key)")
    print("=" * 70)

    # Test 1: Chunking (no API needed)
    chunks = test_chunking()

    # Test 2: BM25 retrieval (no API needed)
    test_bm25_retrieval(chunks)

    if bm25_only:
        print("\n" + "=" * 70)
        print("[DONE] BM25-only tests completed!")
        print("  Run without --bm25-only for full hybrid + generation tests.")
        print("=" * 70)
        sys.exit(0)

    # Test 3: Hybrid retrieval (needs OpenAI API for embeddings)
    try:
        retriever = test_hybrid_retrieval(chunks)
    except Exception as e:
        print(f"\n[WARN] Hybrid retrieval skipped (API error): {e}")
        print("    Falling back to BM25-only retriever for generation test...")
        retriever = HybridRetriever(chunks=chunks, use_semantic=False)

    # Test 4: RAG generation (needs OpenAI API)
    try:
        test_generation(retriever)
    except Exception as e:
        print(f"\n[WARN] Generation test failed: {e}")

    # Test 5: Full Baseline Agent
    try:
        test_rag_baseline()
    except Exception as e:
        print(f"\n[WARN] Baseline Agent test failed: {e}")

    print("\n" + "=" * 70)
    print("[DONE] All tests completed!")
    print("=" * 70)
