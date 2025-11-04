import pytest
from area_code_locator import AreaCodeLocator, __version__


class TestAreaCodeLocator:
    def test_import(self):
        """Test that the module can be imported."""
        assert AreaCodeLocator is not None
        assert __version__ == "0.2.0"

    def test_locator_initialization_missing_file(self):
        """Test that initialization fails gracefully with missing file."""
        with pytest.raises(FileNotFoundError):
            AreaCodeLocator("nonexistent.parquet")

    # Note: Additional tests would require actual area code data files
    # def test_lookup(self):
    #     locator = AreaCodeLocator("test_data.parquet")
    #     result = locator.lookup(40.7128, -74.0060)
    #     assert isinstance(result, list)
    #     assert len(result) > 0