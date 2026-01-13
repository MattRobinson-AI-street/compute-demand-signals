"""Base interface for signal extractors."""

from abc import ABC, abstractmethod
from typing import Protocol

from aistreet.db.repository import Signal


class Extractor(ABC):
    """Abstract base class for signal extraction."""

    @abstractmethod
    def extract(self, text: str, source_id: int) -> list[Signal]:
        """
        Extract signals from text.

        Args:
            text: The filing text to analyze
            source_id: Database ID of the source

        Returns:
            List of Signal objects (may be empty)
        """
        pass
