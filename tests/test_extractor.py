"""Unit tests for signal extraction."""

import pytest

from aistreet.extraction.rule_based import RuleBasedExtractor


class TestRuleBasedExtractor:
    """Tests for rule-based signal extractor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = RuleBasedExtractor()

    def test_multiple_signals_extracted(self):
        """Test that multiple signals can be extracted from one filing."""
        text = """
        Our AI infrastructure business experienced strong demand for GPUs during the quarter.
        We continue to see increased demand for training capacity across all regions.
        Strong demand for inference workloads, but power constraints limit expansion.
        We expect datacenter capacity to grow significantly in the next quarter.
        """

        signals = self.extractor.extract(text, source_id=1)

        # Should extract multiple signals
        assert len(signals) >= 2, "Should extract multiple signals"

        # Check that each signal has required fields
        for signal in signals:
            assert signal.source_id == 1
            assert signal.quote  # Non-empty quote
            assert signal.demand_direction in {"up", "down", "flat", "unclear"}
            assert signal.segment in {"training", "inference", "general"}
            assert signal.constraint_type in {
                "power",
                "chips",
                "networking",
                "capacity",
                "other",
                "none",
            }
            assert signal.pricing in {"up", "down", "stable", "unclear"}
            assert signal.time_horizon in {
                "now",
                "next_qtr",
                "6_12mo",
                "12mo_plus",
                "unclear",
            }
            assert 0.0 <= signal.confidence <= 1.0

        # Check specific signals
        demand_directions = [s.demand_direction for s in signals]
        assert "up" in demand_directions, "Should detect upward demand signals"

        segments = [s.segment for s in signals]
        assert "training" in segments or "inference" in segments, (
            "Should detect specific segments"
        )

        constraints = [s.constraint_type for s in signals]
        assert "power" in constraints, "Should detect power constraint"

    def test_zero_signals_extracted(self):
        """Test that no signals are extracted from irrelevant text."""
        text = """
        The company held its annual shareholder meeting last week.
        Board members discussed corporate governance and compensation.
        The fiscal year financial statements were approved by the board.
        Employee benefits programs were reviewed and updated.
        """

        signals = self.extractor.extract(text, source_id=2)

        # Should extract zero signals (no compute-related content)
        assert len(signals) == 0, "Should not extract signals from irrelevant text"

    def test_demand_direction_classification(self):
        """Test demand direction is correctly classified."""
        # Test upward demand
        text_up = "We are seeing strong demand for AI compute infrastructure and GPU capacity."
        signals_up = self.extractor.extract(text_up, source_id=3)
        assert len(signals_up) > 0
        assert signals_up[0].demand_direction == "up"

        # Test downward demand
        text_down = "We have experienced declining demand for data center capacity."
        signals_down = self.extractor.extract(text_down, source_id=4)
        assert len(signals_down) > 0
        assert signals_down[0].demand_direction == "down"

    def test_segment_classification(self):
        """Test segment classification."""
        # Test training segment
        text_training = "Increased demand for AI training infrastructure and model training workloads."
        signals_training = self.extractor.extract(text_training, source_id=5)
        assert len(signals_training) > 0
        assert signals_training[0].segment == "training"

        # Test inference segment
        text_inference = "Strong demand for AI inference capacity and inference workloads."
        signals_inference = self.extractor.extract(text_inference, source_id=6)
        assert len(signals_inference) > 0
        assert signals_inference[0].segment == "inference"

    def test_constraint_classification(self):
        """Test constraint classification."""
        # Test power constraint
        text_power = "Growing demand for AI compute, but power constraints limit our data center expansion."
        signals_power = self.extractor.extract(text_power, source_id=7)
        assert len(signals_power) > 0
        assert any(s.constraint_type == "power" for s in signals_power)

        # Test chip constraint
        text_chips = "Strong demand for GPUs continues, but chip supply constraints persist."
        signals_chips = self.extractor.extract(text_chips, source_id=8)
        assert len(signals_chips) > 0
        assert any(s.constraint_type == "chips" for s in signals_chips)

    def test_verbatim_quotes(self):
        """Test that quotes are verbatim sentences from source."""
        text = "Our AI infrastructure business saw increased demand for compute capacity this quarter."
        signals = self.extractor.extract(text, source_id=9)

        assert len(signals) > 0
        # Quote should be the full sentence
        assert "increased demand" in signals[0].quote
        assert "compute capacity" in signals[0].quote

    def test_confidence_scoring(self):
        """Test confidence scoring based on specificity."""
        # Specific signal (clear demand + segment + constraint) should have higher confidence
        text_specific = "Strong demand for AI training infrastructure, limited by power capacity."
        signals_specific = self.extractor.extract(text_specific, source_id=10)

        # Vague signal should have lower confidence
        text_vague = "We continue to see demand for data center services."
        signals_vague = self.extractor.extract(text_vague, source_id=11)

        if signals_specific and signals_vague:
            assert signals_specific[0].confidence >= signals_vague[0].confidence

    def test_sentence_notes_include_index(self):
        """Test that notes include sentence traceability."""
        text = "First sentence about AI. Second sentence shows increased demand for GPU compute."
        signals = self.extractor.extract(text, source_id=12)

        assert len(signals) > 0
        # Notes should contain sentence reference
        assert signals[0].notes is not None
        assert "Sentence" in signals[0].notes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
