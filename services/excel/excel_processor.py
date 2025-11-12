import pandas as pd
import json
import os
import openpyxl
from typing import Dict, List, Tuple, Any, Optional
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill
import re
from datetime import datetime
from .large_file_processor import LargeFileProcessor

class ExcelProcessor:
    """Excel Processor for ConvertKeylogApp - Enhanced with large file support"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.mapping = self._load_mapping()
        self.large_file_processor = LargeFileProcessor(config)  # NEW: Large file handler
        self.large_file_threshold_mb = 20  # Files > 20MB use large file processor
        self.large_file_threshold_rows = 50000  # Files > 50k rows use large file processor

    def _clean_cell_value(self, value: str) -> str:
        """
        Clean cell value by removing brackets and quotes
        Example: ["35.196152423", "0", "0"] -> 35.196152423,0,0
        """
        if pd.isna(value) or not value:
            return ""
        value_str = str(value).strip()
        if value_str.startswith('[') and value_str.endswith(']'):
            value_str = value_str[1:-1]
            elements = value_str.split(',')
            cleaned_elements = []
            for elem in elements:
                elem = elem.strip().strip('"').strip("'").strip()
                if elem:
                    cleaned_elements.append(elem)
            return ','.join(cleaned_elements)
        return value_str

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_cleaned = df.copy()
        for col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].apply(self._clean_cell_value)
        return df_cleaned

    def validate_excel_headers(self, file_path: str, shape_a: str, shape_b: str = None) -> Dict[str, Any]:
        try:
            df_headers = pd.read_excel(file_path, nrows=0)
            df_headers.columns = df_headers.columns.str.strip()
            available_columns = list(df_headers.columns)
            required_columns_a = []
            required_columns_b = []
            missing_columns = []
            if shape_a in self.mapping['group_a_mapping']:
                required_columns_a = self.mapping['group_a_mapping'][shape_a]['required_columns']
            if shape_b and shape_b in self.mapping['group_b_mapping']:
                required_columns_b = self.mapping['group_b_mapping'][shape_b]['required_columns']
            all_required = required_columns_a + required_columns_b
            for col in all_required:
                if col not in available_columns:
                    group = "Nhóm A" if col in required_columns_a else "Nhóm B"
                    missing_columns.append(f"{group} - {col}")
            is_valid = len(missing_columns) == 0
            return {
                'valid': is_valid,
                'available_columns': available_columns,
                'required_columns_a': required_columns_a,
                'required_columns_b': required_columns_b,
                'missing_columns': missing_columns,
                'total_available': len(available_columns),
                'total_required': len(all_required),
                'message': self._generate_validation_message(is_valid, missing_columns, available_columns)
            }
        except Exception as e:
            return {
                'valid': False,
                'error': f"Không thể đọc header Excel: {str(e)}",
                'available_columns': [],
                'required_columns_a': [],
                'required_columns_b': [],
                'missing_columns': [],
                'message': f"Lỗi: {str(e)}"
            }

    def _generate_validation_message(self, is_valid: bool, missing_columns: List[str], available_columns: List[str]) -> str:
        if is_valid:
            return "✅ Header hợp lệ! Tất cả cột yêu cầu đều có."
        else:
            msg = "❌ Header không hợp lệ!\n\n"
            msg += f"Thiếu {len(missing_columns)} cột:\n"
            for col in missing_columns:
                msg += f"  - {col}\n"
            msg += f"\nCác cột hiện có ({len(available_columns)}):\n"
            msg += f"  {', '.join(available_columns[:10])}"
            if len(available_columns) > 10:
                msg += f"... và {len(available_columns) - 10} cột khác"
            return msg

    # ... các hàm cũ giữ nguyên ...
