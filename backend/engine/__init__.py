"""
AI Embedding & Threat Classification Engine module for Prompt Shield.
"""

from engine.guard_engine import GuardEngine, ThreatDecision
from engine.vector_store import VectorStore

__all__ = ["GuardEngine", "ThreatDecision", "VectorStore"]
