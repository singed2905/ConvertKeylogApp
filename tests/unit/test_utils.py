"""Unit tests for utility functions."""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from utils.file_utils import get_file_extension, is_valid_file_type, sanitize_filename
from utils.string_utils import clean_string, is_valid_email, truncate_string, extract_numbers
from utils.math_utils import safe_divide, round_to_precision, clamp, is_valid_number


class TestFileUtils(unittest.TestCase):
    """Test cases for file utility functions."""
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        self.assertEqual(get_file_extension(Path("test.xlsx")), ".xlsx")
        self.assertEqual(get_file_extension(Path("test.CSV")), ".csv")
        self.assertEqual(get_file_extension(Path("test")), "")
    
    def test_is_valid_file_type(self):
        """Test file type validation."""
        allowed = [".xlsx", ".csv", ".json"]
        self.assertTrue(is_valid_file_type(Path("test.xlsx"), allowed))
        self.assertTrue(is_valid_file_type(Path("test.CSV"), allowed))
        self.assertFalse(is_valid_file_type(Path("test.txt"), allowed))


class TestStringUtils(unittest.TestCase):
    """Test cases for string utility functions."""
    
    def test_clean_string(self):
        """Test string cleaning."""
        self.assertEqual(clean_string("  test  "), "test")
        self.assertEqual(clean_string("\n\ttest\n\t"), "test")
    
    def test_is_valid_email(self):
        """Test email validation."""
        self.assertTrue(is_valid_email("test@example.com"))
        self.assertTrue(is_valid_email("user.name+tag@domain.co.uk"))
        self.assertFalse(is_valid_email("invalid-email"))
        self.assertFalse(is_valid_email("@domain.com"))
    
    def test_truncate_string(self):
        """Test string truncation."""
        text = "This is a long text"
        self.assertEqual(truncate_string(text, 10), "This is...")
        self.assertEqual(truncate_string(text, 50), text)
        self.assertEqual(truncate_string(text, 10, "!!!"), "This is!!!")
    
    def test_extract_numbers(self):
        """Test number extraction from text."""
        text = "Price: $12.99, Quantity: 5, Discount: -2.5%"
        numbers = extract_numbers(text)
        self.assertIn(12.99, numbers)
        self.assertIn(5.0, numbers)
        self.assertIn(-2.5, numbers)


class TestMathUtils(unittest.TestCase):
    """Test cases for math utility functions."""
    
    def test_safe_divide(self):
        """Test safe division function."""
        self.assertEqual(safe_divide(10, 2), 5.0)
        self.assertEqual(safe_divide(10, 0), 0.0)
        self.assertEqual(safe_divide(10, 0, -1), -1.0)
    
    def test_round_to_precision(self):
        """Test precision rounding."""
        self.assertEqual(round_to_precision(3.14159, 2), 3.14)
        self.assertEqual(round_to_precision(3.14159, 4), 3.1416)
        self.assertEqual(round_to_precision(3.0, 2), 3.0)
    
    def test_clamp(self):
        """Test value clamping."""
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)
    
    def test_is_valid_number(self):
        """Test number validation."""
        self.assertTrue(is_valid_number("123"))
        self.assertTrue(is_valid_number("12.34"))
        self.assertTrue(is_valid_number("-56.78"))
        self.assertFalse(is_valid_number("abc"))
        self.assertFalse(is_valid_number(""))


if __name__ == '__main__':
    unittest.main()
