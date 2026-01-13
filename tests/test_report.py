"""Unit tests for report generation."""

import tempfile
from pathlib import Path

import pytest

from aistreet.db.models import get_connection, init_db
from aistreet.db.repository import Signal, Source, insert_signal, insert_source
from aistreet.reporting.generator import generate_report, save_report


class TestReportGeneration:
    """Tests for report generation."""

    def setup_method(self):
        """Set up test database."""
        # Use temp file database for testing
        import aistreet.config as config
        import aistreet.db.models as models

        # Save original DB_PATH
        self.original_db_path = config.DB_PATH

        # Create temp database
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")

        # Update DB_PATH in both config and models modules
        config.DB_PATH = Path(self.temp_db.name)
        models.DB_PATH = Path(self.temp_db.name)

        # Initialize test database
        init_db()

    def teardown_method(self):
        """Clean up test database."""
        import aistreet.config as config

        # Restore original DB_PATH
        config.DB_PATH = self.original_db_path

        # Clean up temp file
        Path(self.temp_db.name).unlink(missing_ok=True)

    def test_report_with_no_signals(self):
        """Test report generation with no signals."""
        report = generate_report()

        assert "AI Street Compute Demand Report" in report
        assert "Total Signals:** 0" in report
        assert "Summary Statistics" in report

    def test_report_with_signals(self):
        """Test report generation with signals."""
        # Insert test source
        source = Source(
            company="Test Corp",
            cik="0000012345",
            form_type="10-Q",
            filing_date="2025-01-15",
            title="10-Q - 0001234567890",
            url="https://www.sec.gov/Archives/test",
            text_path="data/raw/sec/test.txt",
        )
        source_id = insert_source(source)

        # Insert test signals
        signal1 = Signal(
            source_id=source_id,
            quote="We are seeing strong demand for AI compute infrastructure.",
            demand_direction="up",
            segment="general",
            constraint_type="none",
            pricing="unclear",
            time_horizon="now",
            confidence=0.8,
            notes="Test signal 1",
        )
        insert_signal(signal1)

        signal2 = Signal(
            source_id=source_id,
            quote="Power constraints are limiting our data center expansion.",
            demand_direction="up",
            segment="general",
            constraint_type="power",
            pricing="unclear",
            time_horizon="unclear",
            confidence=0.75,
            notes="Test signal 2",
        )
        insert_signal(signal2)

        # Generate report
        report = generate_report()

        # Verify report content
        assert "AI Street Compute Demand Report" in report
        assert "Total Signals:** 2" in report
        assert "Test Corp" in report
        assert "strong demand" in report
        assert "Power constraints" in report
        assert "| up |" in report
        assert "| power |" in report

    def test_report_filtering_by_date(self):
        """Test report filters signals by filing date."""
        # Insert old source
        old_source = Source(
            company="Old Corp",
            cik="0000011111",
            form_type="10-K",
            filing_date="2024-01-01",
            title="10-K - Old",
            url="https://www.sec.gov/Archives/old",
            text_path="data/raw/sec/old.txt",
        )
        old_source_id = insert_source(old_source)

        old_signal = Signal(
            source_id=old_source_id,
            quote="Old signal about declining demand.",
            demand_direction="down",
            segment="general",
            constraint_type="none",
            pricing="unclear",
            time_horizon="unclear",
            confidence=0.7,
        )
        insert_signal(old_signal)

        # Insert new source
        new_source = Source(
            company="New Corp",
            cik="0000022222",
            form_type="10-Q",
            filing_date="2025-01-15",
            title="10-Q - New",
            url="https://www.sec.gov/Archives/new",
            text_path="data/raw/sec/new.txt",
        )
        new_source_id = insert_source(new_source)

        new_signal = Signal(
            source_id=new_source_id,
            quote="New signal about growing demand.",
            demand_direction="up",
            segment="general",
            constraint_type="none",
            pricing="unclear",
            time_horizon="unclear",
            confidence=0.8,
        )
        insert_signal(new_signal)

        # Generate report with date filter
        report = generate_report(since_date="2025-01-01")

        # Should only include new signal
        assert "New Corp" in report
        assert "growing demand" in report
        assert "Old Corp" not in report
        assert "declining demand" not in report

    def test_report_groups_by_company(self):
        """Test report groups signals by company."""
        # Insert sources for two companies
        for i, company in enumerate(["Company A", "Company B"]):
            source = Source(
                company=company,
                cik=f"000000{i:04d}",
                form_type="10-Q",
                filing_date="2025-01-15",
                title=f"10-Q - {company}",
                url=f"https://www.sec.gov/Archives/{company}",
                text_path=f"data/raw/sec/{company}.txt",
            )
            source_id = insert_source(source)

            signal = Signal(
                source_id=source_id,
                quote=f"Signal from {company}.",
                demand_direction="up",
                segment="general",
                constraint_type="none",
                pricing="unclear",
                time_horizon="unclear",
                confidence=0.7,
            )
            insert_signal(signal)

        # Generate report
        report = generate_report()

        # Should have company sections
        assert "## Signals by Company" in report
        assert "### Company A" in report
        assert "### Company B" in report

    def test_save_report(self):
        """Test saving report to file."""
        content = "# Test Report\n\nThis is a test."

        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as f:
            temp_path = f.name

        try:
            save_report(content, temp_path)

            # Verify file was created
            assert Path(temp_path).exists()

            # Verify content
            saved_content = Path(temp_path).read_text()
            assert saved_content == content

        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
