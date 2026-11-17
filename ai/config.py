"""Central configuration for the SPECTRE AI engine.

Every tunable lives here so the rest of the code never hard-codes paths,
thresholds or model names. Override any of the commonly changed values with
environment variables (see ``Settings.from_env``).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

AI_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = AI_DIR.parent


@dataclass(frozen=True)
class Settings:
    # --- Paths -----------------------------------------------------------
    data_dir: Path = AI_DIR / "data" / "legal documents"
    manifest_path: Path = AI_DIR / "data" / "manifest.json"
    chroma_dir: Path = AI_DIR / "data" / "chroma_db"
    collection_name: str = "spectre_legal"

    # --- Ingestion -------------------------------------------------------
    supported_extensions: tuple[str, ...] = (".pdf", ".docx", ".txt")
    chunk_size: int = 1200  # characters
    chunk_overlap: int = 150  # characters (only used when a section is split)
    min_chunk_chars: int = 40

    # --- Embeddings ------------------------------------------------------
    # Use "hashing" for offline development/tests only (not semantic).
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    query_prefix: str = "Represent this sentence for searching relevant passages: "

    # --- Retrieval -------------------------------------------------------
    top_k: int = 4  # small models answer better from fewer, more relevant sources
    min_similarity: float = 0.35  # drop chunks below this cosine similarity
    min_top_score: float = 0.45  # best chunk must reach this to attempt an answer
    exact_ref_bonus: float = 0.15  # boost when the query names "Section 66C" etc.

    # --- Generation ------------------------------------------------------
    llm_provider: str = "ollama"  # "ollama" (local, open source) or "anthropic"
    llm_model: str = "qwen3:4b"  # Ollama model tag, or an Anthropic model id
    ollama_think: bool = False  # Qwen3 "thinking" mode off: faster, and keeps output pure JSON
    ollama_base_url: str = "http://localhost:11434"
    ollama_num_ctx: int = 8192  # Ollama's default window is small; our prompts need more
    llm_timeout_s: float = 180.0
    llm_max_tokens: int = 1500
    max_context_chars: int = 8000  # keeps prompt + answer well inside ollama_num_ctx on 8 GB RAM

    # --- Safety / validation --------------------------------------------
    max_question_chars: int = 2000

    @classmethod
    def from_env(cls) -> "Settings":
        """Build settings, letting ``SPECTRE_*`` environment variables override defaults."""
        s = cls()
        updates: dict = {}
        if v := os.environ.get("SPECTRE_DATA_DIR"):
            updates["data_dir"] = Path(v)
        if v := os.environ.get("SPECTRE_CHROMA_DIR"):
            updates["chroma_dir"] = Path(v)
        if v := os.environ.get("SPECTRE_EMBEDDING_MODEL"):
            updates["embedding_model"] = v
        if v := os.environ.get("SPECTRE_LLM_PROVIDER"):
            updates["llm_provider"] = v.lower()
        if v := os.environ.get("SPECTRE_LLM_MODEL"):
            updates["llm_model"] = v
        if v := os.environ.get("SPECTRE_OLLAMA_URL"):
            updates["ollama_base_url"] = v
        if v := os.environ.get("SPECTRE_TOP_K"):
            updates["top_k"] = int(v)
        if v := os.environ.get("SPECTRE_MIN_TOP_SCORE"):
            updates["min_top_score"] = float(v)
        return replace(s, **updates) if updates else s


DEFAULT_SETTINGS = Settings()
