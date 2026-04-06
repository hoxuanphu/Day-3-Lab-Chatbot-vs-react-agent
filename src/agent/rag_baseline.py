"""
RAG Baseline Agent.
This is the simple chatbot that directly uses RAG to answer questions
without any reasoning or tool-use capabilities.
"""

from typing import Optional
from src.core.openai_provider import OpenAIProvider
from src.rag.chunker import MarkdownChunker
from src.rag.retriever import HybridRetriever
from src.rag.generator import RAGGenerator
from src.telemetry.logger import logger


class RAGBaselineAgent:
    """
    RAG Baseline Chatbot Agent.
    
    This agent retrieves relevant context from the history knowledge base
    and generates a grounded answer. No reasoning loop, no tool use.
    
    Usage:
        llm = OpenAIProvider(model_name="gpt-4o-mini")
        agent = RAGBaselineAgent(llm)
        answer = agent.run("Ai là lãnh đạo của Trận Bạch Đằng năm 1288?")
    """

    def __init__(
        self,
        llm: OpenAIProvider,
        data_path: str = "data/data.md",
        chunks_cache_path: str = "data/chunks.json",
        use_semantic: bool = True,
        top_k: int = 5,
        retrieval_mode: str = "hybrid",
    ):
        self.llm = llm
        self.data_path = data_path
        self.top_k = top_k
        self.retrieval_mode = retrieval_mode

        logger.log_event("RAG_BASELINE_INIT", {
            "data_path": data_path,
            "use_semantic": use_semantic,
            "top_k": top_k,
            "retrieval_mode": retrieval_mode,
        })

        # Step 1: Chunk the document
        chunker = MarkdownChunker(
            max_chunk_size=1500,
            chunk_overlap=200,
            min_chunk_size=100,
        )

        # Try to load cached chunks first
        import os
        if os.path.exists(chunks_cache_path):
            logger.info("[RAGBaselineAgent] Loading cached chunks...")
            chunks = chunker.load_chunks(chunks_cache_path)
        else:
            logger.info("[RAGBaselineAgent] Chunking document...")
            chunks = chunker.chunk_file(data_path)
            chunker.save_chunks(chunks, chunks_cache_path)

        logger.info(f"[RAGBaselineAgent] Total chunks: {len(chunks)}")

        # Step 2: Build retriever
        self.retriever = HybridRetriever(
            chunks=chunks,
            use_semantic=use_semantic,
            embedding_cache_dir="data/embeddings",
        )

        # Step 3: Build generator
        self.generator = RAGGenerator(
            retriever=self.retriever,
            llm=self.llm,
            top_k=self.top_k,
            retrieval_mode=self.retrieval_mode,
        )

        logger.info("[RAGBaselineAgent] Initialization complete!")

    def run(self, question: str) -> str:
        """
        Answer a question using the RAG pipeline.
        
        Args:
            question: User's question about Vietnamese history.
            
        Returns:
            Generated answer grounded in the knowledge base.
        """
        logger.log_event("RAG_BASELINE_RUN", {"question": question[:100]})
        
        result = self.generator.generate(question)
        
        # Format output
        answer = result["answer"]

        logger.log_event("RAG_BASELINE_COMPLETE", {
            "answer_length": len(answer),
            "sources": len(result["sources"]),
            "latency_ms": result["metadata"].get("llm_latency_ms", 0),
        })

        return answer

