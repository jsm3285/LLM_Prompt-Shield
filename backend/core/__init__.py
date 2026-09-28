"""
Core module for Prompt Shield.
Contains text preprocessor, obfuscation normalization, and dataset loaders.
"""

from core.preprocessor import TextPreprocessor, PreprocessResult
from core.dataset import AttackVectorDataset, AttackVector

__all__ = ["TextPreprocessor", "PreprocessResult", "AttackVectorDataset", "AttackVector"]
