from typing import Dict, Any, List, Optional
import pandas as pd
from .mapping_adapter import GeometryMappingAdapter

class GeometryExcelLoader:
    """Excel loader for geometry data - simplified version of TL ExcelProcessor"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.mapping_adapter = GeometryMappingAdapter(config)
    
    def read_excel_file(self, file_path: str) -> pd.DataFrame:
        """Read Excel file and return DataFrame"""
        try:
            df = pd.read_excel(file_path)
            return df
        except Exception as e:
            raise Exception(f"Lỗi đọc file Excel: {str(e)}")
    
    def validate_excel_structure(self, df: pd.DataFrame, shape_a: str, shape_b: str = None) -> tuple[bool, List[str]]:
        """Validate Excel structure has required columns"""
        required_columns = self._get_required_columns(shape_a, shape_b)
        missing_columns = [col for col in required_columns if col not in df.columns]
        return len(missing_columns) == 0, missing_columns
    
    def _get_required_columns(self, shape_a: str, shape_b: str = None) -> List[str]:
        """Get required columns for given shapes"""
        columns = []
        
        # Get columns for shape A
        mapping_a = self.mapping_adapter.get_excel_column_mapping(shape_a, 'A')
        columns.extend(mapping_a.values())
        
        # Get columns for shape B if provided
        if shape_b:
            mapping_b = self.mapping_adapter.get_excel_column_mapping(shape_b, 'B')
            columns.extend(mapping_b.values())
        
        return columns
    
    def extract_shape_data(self, row: pd.Series, shape: str, group: str) -> Dict[str, str]:
        """Extract shape data from Excel row"""
        mapping = self.mapping_adapter.get_excel_column_mapping(shape, group)
        data = {}
        
        for field_name, column_name in mapping.items():
            try:
                if column_name in row.index:
                    value = row[column_name]
                    # Convert to string, handle NaN values
                    if pd.isna(value):
                        data[field_name] = ""
                    else:
                        data[field_name] = str(value)
                else:
                    data[field_name] = ""
            except Exception as e:
                print(f"Warning: Could not extract {field_name} from column {column_name}: {e}")
                data[field_name] = ""
        
        return data
    
    def export_results(self, original_df: pd.DataFrame, results: List[str], output_path: str) -> str:
        """Export results to Excel file"""
        try:
            # Create new DataFrame with original data + results
            export_df = original_df.copy()
            export_df['Kết quả mã hóa'] = results
            
            # Export to Excel
            export_df.to_excel(output_path, index=False)
            return output_path
        except Exception as e:
            raise Exception(f"Lỗi xuất file Excel: {str(e)}")
    
    def get_total_rows(self, file_path: str) -> int:
        """Get total number of rows in Excel file"""
        try:
            df = pd.read_excel(file_path)
            return len(df)
        except Exception:
            return 0
    
    def read_excel_data_chunked(self, file_path: str, chunksize: int = 1000):
        """Read Excel data in chunks for large files"""
        try:
            # For Excel files, we need to read the entire file first
            # then yield chunks - pandas doesn't support chunked Excel reading
            df = pd.read_excel(file_path)
            
            # Yield chunks
            for i in range(0, len(df), chunksize):
                yield df.iloc[i:i + chunksize]
        except Exception as e:
            raise Exception(f"Lỗi đọc file Excel theo chunk: {str(e)}")
