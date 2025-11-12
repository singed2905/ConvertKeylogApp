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
        self.large_file_processor = LargeFileProcessor(config)
        self.large_file_threshold_mb = 20
        self.large_file_threshold_rows = 50000

    def _clean_cell_value(self, value: str) -> str:
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

    def _load_mapping(self) -> Dict:
        try:
            if self.config and 'geometry' in self.config:
                geometry_config = self.config['geometry']
                if 'excel_mapping' in geometry_config:
                    return geometry_config['excel_mapping']
            mapping_file = "config/geometry_mode/geometry_excel_mapping.json"
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load Excel mapping: {e}")
        return self._get_default_mapping()

    def _get_default_mapping(self) -> Dict:
        return {
            "group_a_mapping": {
                "Điểm": {
                    "required_columns": ["data_A"],
                    "columns": {
                        "point_input": {"excel_column": "data_A"}
                    }
                },
                "Đường thẳng": {
                    "required_columns": ["d_P_data_A", "d_V_data_A"],
                    "columns": {
                        "line_A1": {"excel_column": "d_P_data_A"},
                        "line_X1": {"excel_column": "d_V_data_A"}
                    }
                },
                "Mặt phẳng": {
                    "required_columns": ["P1_a", "P1_b", "P1_c", "P1_d"],
                    "columns": {
                        "plane_a": {"excel_column": "P1_a"},
                        "plane_b": {"excel_column": "P1_b"},
                        "plane_c": {"excel_column": "P1_c"},
                        "plane_d": {"excel_column": "P1_d"}
                    }
                },
                "Đường tròn": {
                    "required_columns": ["C_data_I1", "C_data_R1"],
                    "columns": {
                        "circle_center": {"excel_column": "C_data_I1"},
                        "circle_radius": {"excel_column": "C_data_R1"}
                    }
                },
                "Mặt cầu": {
                    "required_columns": ["S_data_I1", "S_data_R1"],
                    "columns": {
                        "sphere_center": {"excel_column": "S_data_I1"},
                        "sphere_radius": {"excel_column": "S_data_R1"}
                    }
                }
            },
            "group_b_mapping": {
                "Điểm": {
                    "required_columns": ["data_B"],
                    "columns": {
                        "point_input": {"excel_column": "data_B"}
                    }
                },
                "Đường thẳng": {
                    "required_columns": ["d_P_data_B", "d_V_data_B"],
                    "columns": {
                        "line_A2": {"excel_column": "d_P_data_B"},
                        "line_X2": {"excel_column": "d_V_data_B"}
                    }
                },
                "Mặt phẳng": {
                    "required_columns": ["P2_a", "P2_b", "P2_c", "P2_d"],
                    "columns": {
                        "plane_a": {"excel_column": "P2_a"},
                        "plane_b": {"excel_column": "P2_b"},
                        "plane_c": {"excel_column": "P2_c"},
                        "plane_d": {"excel_column": "P2_d"}
                    }
                },
                "Đường tròn": {
                    "required_columns": ["C_data_I2", "C_data_R2"],
                    "columns": {
                        "circle_center": {"excel_column": "C_data_I2"},
                        "circle_radius": {"excel_column": "C_data_R2"}
                    }
                },
                "Mặt cầu": {
                    "required_columns": ["S_data_I2", "S_data_R2"],
                    "columns": {
                        "sphere_center": {"excel_column": "S_data_I2"},
                        "sphere_radius": {"excel_column": "S_data_R2"}
                    }
                }
            }
        }

    def is_large_file(self, file_path: str) -> Tuple[bool, Dict[str, Any]]:
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            estimated_rows = ws.max_row - 1 if hasattr(ws, 'max_row') else 0
            wb.close()
            is_large = (file_size_mb > self.large_file_threshold_mb or 
                       estimated_rows > self.large_file_threshold_rows)
            return is_large, {
                'file_size_mb': file_size_mb,
                'estimated_rows': estimated_rows,
                'recommended_processor': 'large_file' if is_large else 'normal',
                'recommended_chunk_size': self.large_file_processor.estimate_optimal_chunksize(file_path)
            }
        except Exception as e:
            return False, {'error': f'Không thể phân tích file: {str(e)}'}

    def read_excel_data(self, file_path: str) -> pd.DataFrame:
        try:
            is_large, file_info = self.is_large_file(file_path)
            if is_large:
                raise Exception(
                    f"File quá lớn cho phương thức thông thường!\n"
                    f"Kích thước: {file_info.get('file_size_mb', 0):.1f}MB\n"
                    f"Dòng ước tính: {file_info.get('estimated_rows', 0):,}\n\n"
                    f"Vui lòng sử dụng chế độ xử lý file lớn."
                )
            df = pd.read_excel(file_path)
            df.columns = df.columns.str.strip()
            df = self._clean_dataframe(df)
            return df
        except Exception as e:
            raise Exception(f"Không thể đọc file Excel: {str(e)}")

    def validate_excel_structure(self, df: pd.DataFrame, shape_a: str, shape_b: str = None) -> Tuple[bool, List[str]]:
        missing_columns = []
        if shape_a in self.mapping['group_a_mapping']:
            required_cols = self.mapping['group_a_mapping'][shape_a]['required_columns']
            for col in required_cols:
                if col not in df.columns:
                    missing_columns.append(f"Nhóm A - {col}")
        if shape_b and shape_b in self.mapping['group_b_mapping']:
            required_cols = self.mapping['group_b_mapping'][shape_b]['required_columns']
            for col in required_cols:
                if col not in df.columns:
                    missing_columns.append(f"Nhóm B - {col}")
        return len(missing_columns) == 0, missing_columns

    def validate_large_file_structure(self, file_path: str, shape_a: str, shape_b: str = None) -> Dict[str, Any]:
        return self.large_file_processor.validate_large_file_structure(file_path, shape_a, shape_b)

    def extract_shape_data(self, row: pd.Series, shape_type: str, group: str) -> Dict:
        if group == 'A':
            shape_mapping = self.mapping['group_a_mapping'].get(shape_type, {})
        else:
            shape_mapping = self.mapping['group_b_mapping'].get(shape_type, {})
        data_dict = {}
        for field, config in shape_mapping.get('columns', {}).items():
            excel_column = config.get('excel_column')
            if excel_column and excel_column in row.index:
                value = row[excel_column]
                if pd.isna(value):
                    data_dict[field] = ""
                else:
                    cleaned_value = self._clean_cell_value(value)
                    data_dict[field] = cleaned_value
            else:
                data_dict[field] = ""
        return data_dict

    # Giữ nguyên các hàm xuất, tạo template, kiểm tra chất lượng, format worksheet, các phân tích large file ...
