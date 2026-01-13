"""Rule-based signal extractor."""

import re
from typing import Optional

from aistreet.db.repository import Signal
from aistreet.extraction.base import Extractor
from aistreet.extraction.keywords import (
    CAPACITY_KEYWORDS,
    CHIP_KEYWORDS,
    COMPUTE_KEYWORDS,
    DEMAND_DOWN_KEYWORDS,
    DEMAND_FLAT_KEYWORDS,
    DEMAND_UP_KEYWORDS,
    INFERENCE_KEYWORDS,
    NETWORKING_KEYWORDS,
    NOW_KEYWORDS,
    NEXT_QTR_KEYWORDS,
    POWER_KEYWORDS,
    PRICING_DOWN_KEYWORDS,
    PRICING_STABLE_KEYWORDS,
    PRICING_UP_KEYWORDS,
    SIX_TO_TWELVE_KEYWORDS,
    TRAINING_KEYWORDS,
    TWELVE_PLUS_KEYWORDS,
    contains_any,
)


class RuleBasedExtractor(Extractor):
    """Deterministic rule-based signal extraction."""

    def extract(self, text: str, source_id: int) -> list[Signal]:
        """
        Extract signals from text using keyword matching and proximity rules.

        Args:
            text: The filing text to analyze
            source_id: Database ID of the source

        Returns:
            List of Signal objects
        """
        signals = []

        # Split text into sentences
        sentences = self._split_into_sentences(text)

        for i, sentence in enumerate(sentences):
            sentence_lower = sentence.lower()

            # Must contain compute-related terms to be relevant
            if not contains_any(sentence_lower, COMPUTE_KEYWORDS):
                continue

            # Must contain some demand signal
            demand_direction = self._classify_demand(sentence_lower)
            if demand_direction == "unclear":
                continue

            # Extract other attributes
            segment = self._classify_segment(sentence_lower)
            constraint = self._classify_constraint(sentence_lower)
            pricing = self._classify_pricing(sentence_lower)
            time_horizon = self._classify_time_horizon(sentence_lower)

            # Confidence based on specificity
            confidence = self._calculate_confidence(
                sentence_lower, demand_direction, segment, constraint
            )

            # Create signal
            signal = Signal(
                source_id=source_id,
                quote=sentence.strip(),
                demand_direction=demand_direction,
                segment=segment,
                constraint_type=constraint,
                pricing=pricing,
                time_horizon=time_horizon,
                confidence=confidence,
                notes=f"Sentence {i+1}",
            )

            signals.append(signal)

        return signals

    def _split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences using simple heuristics."""
        # Basic sentence splitting on period, exclamation, question mark
        # followed by space and capital letter
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def _classify_demand(self, text_lower: str) -> str:
        """Classify demand direction."""
        if contains_any(text_lower, DEMAND_UP_KEYWORDS):
            return "up"
        elif contains_any(text_lower, DEMAND_DOWN_KEYWORDS):
            return "down"
        elif contains_any(text_lower, DEMAND_FLAT_KEYWORDS):
            return "flat"
        else:
            return "unclear"

    def _classify_segment(self, text_lower: str) -> str:
        """Classify compute segment."""
        has_training = contains_any(text_lower, TRAINING_KEYWORDS)
        has_inference = contains_any(text_lower, INFERENCE_KEYWORDS)

        if has_training and not has_inference:
            return "training"
        elif has_inference and not has_training:
            return "inference"
        else:
            return "general"

    def _classify_constraint(self, text_lower: str) -> str:
        """Classify constraint type."""
        if contains_any(text_lower, POWER_KEYWORDS):
            return "power"
        elif contains_any(text_lower, CHIP_KEYWORDS):
            return "chips"
        elif contains_any(text_lower, NETWORKING_KEYWORDS):
            return "networking"
        elif contains_any(text_lower, CAPACITY_KEYWORDS):
            return "capacity"
        else:
            return "none"

    def _classify_pricing(self, text_lower: str) -> str:
        """Classify pricing trend."""
        if contains_any(text_lower, PRICING_UP_KEYWORDS):
            return "up"
        elif contains_any(text_lower, PRICING_DOWN_KEYWORDS):
            return "down"
        elif contains_any(text_lower, PRICING_STABLE_KEYWORDS):
            return "stable"
        else:
            return "unclear"

    def _classify_time_horizon(self, text_lower: str) -> str:
        """Classify time horizon."""
        if contains_any(text_lower, NOW_KEYWORDS):
            return "now"
        elif contains_any(text_lower, NEXT_QTR_KEYWORDS):
            return "next_qtr"
        elif contains_any(text_lower, SIX_TO_TWELVE_KEYWORDS):
            return "6_12mo"
        elif contains_any(text_lower, TWELVE_PLUS_KEYWORDS):
            return "12mo_plus"
        else:
            return "unclear"

    def _calculate_confidence(
        self, text_lower: str, demand: str, segment: str, constraint: str
    ) -> float:
        """Calculate confidence score based on signal specificity."""
        confidence = 0.5  # Base confidence

        # Higher confidence for specific demand direction
        if demand in {"up", "down"}:
            confidence += 0.2

        # Higher confidence for specific segment
        if segment in {"training", "inference"}:
            confidence += 0.15

        # Higher confidence for identified constraint
        if constraint != "none":
            confidence += 0.15

        return min(confidence, 1.0)
