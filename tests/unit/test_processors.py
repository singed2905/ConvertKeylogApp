"""Unit tests for processor classes."""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import pandas as pd
from core.processors.excel_processor import ExcelProcessor
from core.processors.csv_processor import CSVProcessor
from core.processors.json_processor import JSONProcessor
from core.processors.validator import DataValidator


class TestExcelProcessor(unittest.TestCase):
    """Test cases for ExcelProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = ExcelProcessor()
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor.config)
        self.assertIsInstance(self.processor.config, dict)
    
    def test_read_excel_method_exists(self):
        """Test that read_excel method exists."""
        self.assertTrue(hasattr(self.processor, 'read_excel'))
        self.assertTrue(callable(self.processor.read_excel))
    
    def test_write_excel_method_exists(self):
        """Test that write_excel method exists."""
        self.assertTrue(hasattr(self.processor, 'write_excel'))
        self.assertTrue(callable(self.processor.write_excel))
    
    def test_validate_structure_method_exists(self):
        """Test that validate_structure method exists."""
        self.assertTrue(hasattr(self.processor, 'validate_structure'))
        self.assertTrue(callable(self.processor.validate_structure))


class TestCSVProcessor(unittest.TestCase):
    """Test cases for CSVProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = CSVProcessor()
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor.config)
        self.assertIsInstance(self.processor.config, dict)


class TestJSONProcessor(unittest.TestCase):
    """Test cases for JSONProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = JSONProcessor()
    
    def test_initialization(self):
        """Test processor initialization."""
        self.assertIsNotNone(self.processor.config)
        self.assertIsInstance(self.processor.config, dict)


class TestDataValidator(unittest.TestCase):
    """Test cases for DataValidator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = DataValidator()
    
    def test_initialization(self):
        """Test validator initialization."""
        self.assertIsNotNone(self.validator.rules)
        self.assertIsInstance(self.validator.rules, dict)
    
    def test_validate_method_returns_boolean(self):
        """Test that validate method returns boolean."""
        result = self.validator.validate("test_data", "test_rule")
        self.assertIsInstance(result, bool)
    
    def test_get_validation_errors_returns_list(self):
        """Test that get_validation_errors returns list."""
        result = self.validator.get_validation_errors("test_data", "test_rule")
        self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()
