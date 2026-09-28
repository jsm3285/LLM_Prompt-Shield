"""
Configuration manager for Prompt Shield Gateway.
"""

import os
import secrets
import logging


class Settings:
    def __init__(self):
        self.PORT: int = int(os.getenv("PORT", "8000"))
        self.HOST: str = os.getenv("HOST", "127.0.0.1")
        self.DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
        
        # Upstream OpenAI Configuration
        self.OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-demo-mock-key")
        self.OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
        
        # Guard Engine Parameters
        self.SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.72"))
        self.MAX_LATENCY_BUDGET_MS: float = float(os.getenv("MAX_LATENCY_BUDGET_MS", "25.0"))
        
        # Resolve dataset path dynamically
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        default_data_path = os.path.join(base_dir, "data", "attack_vectors.json")
        self.ATTACK_DATASET_PATH: str = os.getenv("ATTACK_DATASET_PATH", default_data_path)
        
        # Security Parameters
        raw_jwt = os.getenv("JWT_SECRET_KEY", "")
        if not raw_jwt:
            self.JWT_SECRET_KEY = secrets.token_hex(32)
            logging.warning("JWT_SECRET_KEY environment variable missing. Generated ephemeral random secret token.")
        else:
            self.JWT_SECRET_KEY = raw_jwt


settings = Settings()
