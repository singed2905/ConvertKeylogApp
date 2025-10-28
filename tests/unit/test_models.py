"""Unit tests for model classes."""

import unittest
from datetime import datetime
from core.models.keylog_model import KeylogEntry, KeylogData
from core.models.conversion_result import ConversionResult, ConversionStatus
from core.models.file_metadata import FileMetadata
from pathlib import Path


class TestKeylogModels(unittest.TestCase):
    """Test cases for keylog model classes."""
    
    def test_keylog_entry_creation(self):
        """Test KeylogEntry creation."""
        entry = KeylogEntry(
            timestamp=datetime.now(),
            key_data="test_key",
            metadata={"session": "test"}
        )
        self.assertIsInstance(entry, KeylogEntry)
        self.assertIsInstance(entry.timestamp, datetime)
        self.assertEqual(entry.key_data, "test_key")
    
    def test_keylog_data_creation(self):
        """Test KeylogData creation."""
        data = KeylogData(
            entries=[],
            file_info={"name": "test.xlsx"},
            created_at=datetime.now()
        )
        self.assertIsInstance(data, KeylogData)
        self.assertIsInstance(data.entries, list)
        self.assertEqual(data.version, "1.0")


class TestConversionResult(unittest.TestCase):
    """Test cases for ConversionResult class."""
    
    def test_conversion_result_creation(self):
        """Test ConversionResult creation."""
        result = ConversionResult(
            status=ConversionStatus.SUCCESS,
            input_data="test_input",
            output_data="test_output",
            errors=[],
            warnings=[],
            metadata={},
            processing_time=1.5,
            created_at=datetime.now()
        )
        self.assertIsInstance(result, ConversionResult)
        self.assertEqual(result.status, ConversionStatus.SUCCESS)
    
    def test_is_successful_method(self):
        """Test is_successful method."""
        success_result = ConversionResult(
            status=ConversionStatus.SUCCESS,
            input_data=None, output_data=None, errors=[], warnings=[],
            metadata={}, processing_time=0, created_at=datetime.now()
        )
        failed_result = ConversionResult(
            status=ConversionStatus.FAILED,
            input_data=None, output_data=None, errors=[], warnings=[],
            metadata={}, processing_time=0, created_at=datetime.now()
        )
        
        self.assertTrue(success_result.is_successful())
        self.assertFalse(failed_result.is_successful())


class TestFileMetadata(unittest.TestCase):
    """Test cases for FileMetadata class."""
    
    def test_file_metadata_creation(self):
        """Test FileMetadata creation."""
        metadata = FileMetadata(
            file_path=Path("test.xlsx"),
            file_name="test.xlsx",
            file_size=1024,
            file_type="xlsx",
            created_at=datetime.now(),
            modified_at=datetime.now()
        )
        self.assertIsInstance(metadata, FileMetadata)
        self.assertEqual(metadata.file_name, "test.xlsx")
        self.assertIsInstance(metadata.additional_info, dict)


if __name__ == '__main__':
    unittest.main()
