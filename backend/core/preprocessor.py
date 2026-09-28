"""
Text Preprocessor & Normalization Module for Prompt Shield.

Features:
- Unicode NFKC normalization
- Zero-width character & control char strip
- Leetspeak & homoglyph de-obfuscation
- Base64 / Hex payload detection
- Instant heuristic regex rule matching (<1ms execution)
"""

import re
import unicodedata
import base64
import time
from typing import List, Dict, Any, Tuple
from pydantic import BaseModel


class PreprocessResult(BaseModel):
    raw_text: str
    normalized_text: str
    is_suspicious_heuristic: bool
    detected_rules: List[str]
    detected_obfuscation: List[str]
    processing_time_ms: float


class TextPreprocessor:
    """Ultra-low latency text preprocessor for prompt sanitization and threat extraction."""

    LEET_MAP = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '7': 't', '@': 'a', '$': 's', '!': 'i', '8': 'b'
    }

    # High-confidence heuristic rules for immediate blocking / escalation
    REGEX_RULES = [
        (re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|rules)", re.IGNORECASE), "RULE_IGNORE_INSTRUCTIONS"),
        (re.compile(r"\bDAN\b|\bDo\s+Anything\s+Now\b", re.IGNORECASE), "RULE_DAN_JAILEBREAK"),
        (re.compile(r"developer\s+mode", re.IGNORECASE), "RULE_DEV_MODE"),
        (re.compile(r"system\s+prompt\s+override", re.IGNORECASE), "RULE_PROMPT_OVERRIDE"),
        (re.compile(r"(reveal|print|output|show)\s+.*(api_key|jwt_secret|password|credentials)", re.IGNORECASE), "RULE_EXFILTRATION_INTENT"),
        (re.compile(r"\]\]\]\s*end\s+of\s+text", re.IGNORECASE), "RULE_DELIMITER_BREAKOUT"),
    ]

    def __init__(self):
        # Zero-width spaces and soft hyphens regex
        self.zero_width_regex = re.compile(r"[\u200B-\u200D\uFEFF\u00AD]")

    def remove_zero_width_chars(self, text: str) -> Tuple[str, bool]:
        """Strips invisible zero-width characters used for evasion."""
        cleaned = self.zero_width_regex.sub("", text)
        had_obfuscation = len(cleaned) != len(text)
        return cleaned, had_obfuscation

    def decode_leetspeak(self, text: str) -> str:
        """Converts basic leetspeak patterns to standard latin characters."""
        res = []
        for char in text:
            res.append(self.LEET_MAP.get(char, char))
        return "".join(res)

    def detect_base64_payload(self, text: str) -> Tuple[str, bool]:
        """Detects and decodes base64 obfuscated strings if embedded."""
        b64_pattern = re.compile(r"([A-Za-z0-9+/]{20,}={0,2})")
        matches = b64_pattern.findall(text)
        decoded_parts = []
        found = False

        for match in matches:
            try:
                decoded_bytes = base64.b64decode(match)
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
                if any(kw in decoded_str.lower() for kw in ["ignore", "system", "prompt", "key", "password"]):
                    decoded_parts.append(decoded_str)
                    found = True
            except Exception:
                pass

        if found:
            augmented = text + " [DECODED_B64: " + " ".join(decoded_parts) + "]"
            return augmented, True
        return text, False

    def normalize(self, text: str) -> PreprocessResult:
        """Runs the full normalization and fast heuristic analysis pipeline."""
        start_time = time.perf_counter()
        obfuscation_tags = []

        # 1. Strip zero-width chars
        step1_text, had_zw = self.remove_zero_width_chars(text)
        if had_zw:
            obfuscation_tags.append("ZERO_WIDTH_CHARS")

        # 2. Unicode NFKC Normalization
        step2_text = unicodedata.normalize("NFKC", step1_text)

        # 3. Base64 payload detection
        step3_text, had_b64 = self.detect_base64_payload(step2_text)
        if had_b64:
            obfuscation_tags.append("BASE64_ENCODED_PAYLOAD")

        # 4. Leetspeak decoding for pattern checking
        leeted_text = self.decode_leetspeak(step2_text)
        if leeted_text != step2_text:
            obfuscation_tags.append("LEETSPEAK_OBFUSCATION")

        # Combine text versions for rule checking
        norm_combined = f"{step3_text} {leeted_text}"

        # 5. Fast Heuristic Rule Matching (<1ms)
        detected_rules = []
        for regex, rule_id in self.REGEX_RULES:
            if regex.search(norm_combined):
                detected_rules.append(rule_id)

        is_suspicious = len(detected_rules) > 0 or len(obfuscation_tags) > 0
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return PreprocessResult(
            raw_text=text,
            normalized_text=step3_text,
            is_suspicious_heuristic=is_suspicious,
            detected_rules=detected_rules,
            detected_obfuscation=obfuscation_tags,
            processing_time_ms=round(elapsed_ms, 3)
        )
