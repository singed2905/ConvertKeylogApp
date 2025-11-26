"""
Excel Processor for Geometry V2 Mode
- Validates Excel columns based on UI dropdown selections
- Processes batch encoding with shape-specific data extraction
- Supports chunked processing for large files
"""

import pandas as pd
import os
import json
import gc
import warnings
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable

# Suppress pandas warnings
warnings.filterwarnings('ignore', category=FutureWarning)


class ExcelProcessor:
    def __init__(self, service):
        """
        Initialize Excel Processor

        Args:
            service: GeometryV2Service instance
        """
        self.service = service
        self.column_mapping = self._load_column_mapping()

        # Large file thresholds
        self.LARGE_FILE_SIZE_MB = 10
        self.LARGE_FILE_ROWS = 50000
        self.DEFAULT_CHUNK_SIZE = 1000

    def _load_column_mapping(self) -> Dict:
        """Load Excel column mapping config"""
        try:
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            parent_dir = os.path.dirname(current_dir)
            root_dir = os.path.dirname(parent_dir)

            config_path = os.path.join(
                root_dir, 'config', 'geometry_v2_mode', 'excel_column_mapping.json'
            )

            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"⚠️ Warning: Column mapping file not found: {config_path}")
                return {}
        except Exception as e:
            print(f"⚠️ Warning: Could not load column mapping: {e}")
            return {}

    # ========== FILE VALIDATION ==========

    def is_large_file(self, file_path: str) -> Tuple[bool, Dict]:
        """
        Kiểm tra file có phải large file không

        Args:
            file_path: Đường dẫn file Excel

        Returns:
            Tuple[bool, Dict]: (is_large, file_info)
        """
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            is_large = file_size_mb > self.LARGE_FILE_SIZE_MB

            file_info = {
                'size_mb': round(file_size_mb, 2),
                'is_large': is_large,
                'recommended_chunk_size': self.DEFAULT_CHUNK_SIZE if is_large else None
            }

            return is_large, file_info

        except Exception as e:
            return False, {'error': str(e)}

    def _get_shape_required_columns(self, shape: str, group: str) -> List[str]:
        """
        Lấy danh sách columns cần thiết cho 1 shape

        Args:
            shape: Tên shape (Điểm, Vecto, Đường thẳng, ...)
            group: 'a' hoặc 'b'

        Returns:
            List các column names cần có trong Excel
        """
        if not shape:
            return []

        mapping_key = f"group_{group}_mapping"
        shape_mapping = self.column_mapping.get(mapping_key, {}).get(shape, {})

        if not shape_mapping:
            print(f"⚠️ Warning: No mapping found for {group.upper()} - {shape}")
            return []

        return shape_mapping.get('required_columns', [])

    def _extract_shape_data_from_row(self, row: pd.Series, shape: str, group: str) -> Dict:
        """
        Extract data từ Excel row cho một shape cụ thể

        Args:
            row: Pandas Series (1 row)
            shape: Shape name (Điểm, Vecto, ...)
            group: 'a' hoặc 'b'

        Returns:
            Dict data cho encoder
        """
        mapping_key = f"group_{group}_mapping"
        shape_mapping = self.column_mapping.get(mapping_key, {}).get(shape, {})

        if not shape_mapping:
            raise ValueError(f"No mapping found for {group.upper()} - {shape}")

        data = {}
        columns_config = shape_mapping.get('columns', {})

        for data_key, col_config in columns_config.items():
            excel_col = col_config['excel_column']

            if excel_col in row.index:
                value = row[excel_col]

                # Convert NaN to empty string
                if pd.isna(value):
                    value = ""
                else:
                    value = str(value).strip()

                # Check required
                if col_config.get('required', False) and not value:
                    raise ValueError(
                        f"Missing required value in '{excel_col}' for {shape}"
                    )

                data[data_key] = value
            elif col_config.get('required', False):
                raise ValueError(
                    f"Column '{excel_col}' not found (required for {shape})"
                )

        return data

    # ========== NORMAL FILE PROCESSING ==========

    def process_file(self, input_path: str, output_path: str,
                     progress_callback: Optional[Callable] = None,
                     operation: str = None,
                     shape_a: str = None,
                     shape_b: str = None,
                     dimension_a: str = "3",
                     dimension_b: str = "3",
                     version: str = "fx799") -> Dict:
        """
        Xử lý Excel theo workflow:
        1. Validate columns dựa trên Shape A & B từ UI
        2. Đọc Operation từ UI
        3. Xử lý hàng loạt

        Args:
            input_path: File Excel input
            output_path: File Excel output
            progress_callback: Progress callback function
            operation: Phép toán từ UI dropdown
            shape_a: Shape nhóm A từ UI dropdown
            shape_b: Shape nhóm B từ UI dropdown (None nếu single-object)
            dimension_a: Dimension A (2D/3D)
            dimension_b: Dimension B (2D/3D)
            version: Casio version
        """
        try:
            # ========== 1. READ EXCEL ==========
            df = pd.read_excel(input_path)
            total_rows = len(df)

            print(f"\n📊 Processing {total_rows} rows...")
            print(f"📋 Excel columns: {list(df.columns)}")

            # ========== 2. VALIDATE REQUIRED PARAMS ==========
            if not operation or not shape_a:
                return {
                    'success': False,
                    'error': 'Vui lòng chọn Phép toán và Shape A từ UI dropdown!'
                }

            print(f"\n📌 Config từ UI:")
            print(f"   Operation: {operation}")
            print(f"   Shape A: {shape_a} ({dimension_a}D)")
            if shape_b:
                print(f"   Shape B: {shape_b} ({dimension_b}D)")

            # ========== 3. GET REQUIRED COLUMNS cho Shape A & B ==========
            required_columns_a = self._get_shape_required_columns(shape_a, 'a')
            required_columns_b = self._get_shape_required_columns(shape_b, 'b') if shape_b else []

            all_required_columns = required_columns_a + required_columns_b

            print(f"\n🔍 Checking Excel columns...")
            print(f"   Shape A ({shape_a}) cần: {required_columns_a}")
            if shape_b:
                print(f"   Shape B ({shape_b}) cần: {required_columns_b}")

            # ========== 4. VALIDATE EXCEL HAS REQUIRED COLUMNS ==========
            excel_columns = set(df.columns)
            missing_columns = [col for col in all_required_columns if col not in excel_columns]

            if missing_columns:
                error_msg = (
                    f"❌ File Excel thiếu các cột cần thiết!\n\n"
                    f"Dropdown hiện tại:\n"
                    f"  • Shape A: {shape_a}\n"
                )
                if shape_b:
                    error_msg += f"  • Shape B: {shape_b}\n"

                error_msg += f"\nCác cột bị thiếu:\n"
                for col in missing_columns:
                    error_msg += f"  ❌ {col}\n"

                error_msg += f"\nCác cột có trong Excel:\n"
                for col in sorted(excel_columns):
                    error_msg += f"  ✓ {col}\n"

                print(error_msg)
                return {'success': False, 'error': error_msg}

            print(f"   ✅ Tất cả columns cần thiết đều có!")

            # ========== 5. ENSURE KEYLOG COLUMN ==========
            if 'keylog' not in df.columns:
                df['keylog'] = pd.Series('', dtype='str', index=df.index)
                print("   → Added 'keylog' column")
            else:
                df['keylog'] = df['keylog'].astype('str')
                print("   → 'keylog' column exists, will overwrite")

            # ========== 6. CONFIGURE SERVICE ==========
            self.service.set_operation(operation)
            self.service.set_shapes(shape_a, shape_b)
            self.service.set_dimension(dimension_a, dimension_b)
            self.service.set_version(version)

            # ========== 7. PROCESS ROWS ==========
            processed = 0
            errors = 0

            print(f"\n⚙️ Processing rows...\n")

            for idx, row in df.iterrows():
                try:
                    # Extract data cho Shape A
                    data_a = self._extract_shape_data_from_row(row, shape_a, 'a')

                    # Extract data cho Shape B (nếu có)
                    data_b = None
                    if shape_b:
                        data_b = self._extract_shape_data_from_row(row, shape_b, 'b')

                    # Encode
                    result = self.service.process_manual_data(data_a, data_b)

                    if result['success']:
                        df.loc[idx, 'keylog'] = str(result['encoded'])
                        processed += 1
                    else:
                        df.loc[idx, 'keylog'] = f"ERROR: {result.get('error', 'Unknown')}"
                        errors += 1

                    # Progress callback
                    if progress_callback and (idx + 1) % 100 == 0:
                        progress_callback(idx + 1, total_rows, errors)

                except Exception as e:
                    df.loc[idx, 'keylog'] = f"ERROR: {str(e)}"
                    errors += 1
                    if errors <= 5:
                        print(f"⚠️ Row {idx + 1}: {str(e)}")

            # ========== 8. SAVE OUTPUT ==========
            # Move keylog to end
            if 'keylog' in df.columns:
                cols = [c for c in df.columns if c != 'keylog'] + ['keylog']
                df = df[cols]

            df.to_excel(output_path, index=False)

            print(f"\n✅ Processing complete!")
            print(f"   Success: {processed}/{total_rows}")
            print(f"   Errors: {errors}/{total_rows}")
            print(f"📁 Output: {output_path}")

            return {
                'success': True,
                'processed': processed,
                'errors': errors,
                'total': total_rows,
                'output_file': output_path
            }

        except Exception as e:
            return {'success': False, 'error': f'Lỗi xử lý file: {str(e)}'}

    # ========== LARGE FILE PROCESSING (CHUNKED) ==========

    def process_large_file(self, input_path: str, output_path: str,
                           chunk_size: int = 1000,
                           progress_callback: Optional[Callable] = None,
                           operation: str = None,
                           shape_a: str = None,
                           shape_b: str = None,
                           dimension_a: str = "3",
                           dimension_b: str = "3",
                           version: str = "fx799") -> Dict:
        """
        Xử lý large file với manual chunking (pandas read_excel không support chunksize)
        """
        try:
            print(f"🔄 Large file processing: chunk_size={chunk_size}")

            # Validate params
            if not operation or not shape_a:
                return {
                    'success': False,
                    'error': 'Vui lòng chọn Phép toán và Shape A từ UI dropdown!'
                }

            # ✅ READ ENTIRE FILE FIRST (có thể tốn memory nhưng cần thiết)
            print(f"📖 Reading Excel file...")
            df = pd.read_excel(input_path)
            total_rows = len(df)

            print(f"📊 Total rows: {total_rows}")

            # Get required columns
            required_columns_a = self._get_shape_required_columns(shape_a, 'a')
            required_columns_b = self._get_shape_required_columns(shape_b, 'b') if shape_b else []
            all_required_columns = required_columns_a + required_columns_b

            # Validate columns
            excel_columns = set(df.columns)
            missing_columns = [col for col in all_required_columns if col not in excel_columns]

            if missing_columns:
                error_msg = (
                    f"❌ File Excel thiếu các cột:\n"
                    f"{', '.join(missing_columns)}\n\n"
                    f"Cần có: {', '.join(all_required_columns)}"
                )
                return {'success': False, 'error': error_msg}

            print(f"\n📌 Config từ UI:")
            print(f"   Operation: {operation}")
            print(f"   Shape A: {shape_a} ({dimension_a}D)")
            if shape_b:
                print(f"   Shape B: {shape_b} ({dimension_b}D)")

            # Configure service once
            self.service.set_operation(operation)
            self.service.set_shapes(shape_a, shape_b)
            self.service.set_dimension(dimension_a, dimension_b)
            self.service.set_version(version)

            # Ensure keylog column
            if 'keylog' not in df.columns:
                df['keylog'] = pd.Series('', dtype='str', index=df.index)
            else:
                df['keylog'] = df['keylog'].astype('str')

            # ✅ PROCESS IN CHUNKS MANUALLY
            processed = 0
            errors = 0
            num_chunks = (total_rows + chunk_size - 1) // chunk_size

            print(f"\n⚙️ Processing {num_chunks} chunks...")

            for chunk_idx in range(num_chunks):
                start_idx = chunk_idx * chunk_size
                end_idx = min(start_idx + chunk_size, total_rows)

                print(f"📦 Chunk {chunk_idx + 1}/{num_chunks} (rows {start_idx}-{end_idx})")

                # Process rows in this chunk
                for idx in range(start_idx, end_idx):
                    try:
                        row = df.iloc[idx]

                        data_a = self._extract_shape_data_from_row(row, shape_a, 'a')
                        data_b = None
                        if shape_b:
                            data_b = self._extract_shape_data_from_row(row, shape_b, 'b')

                        result = self.service.process_manual_data(data_a, data_b)

                        if result['success']:
                            df.at[idx, 'keylog'] = str(result['encoded'])
                            processed += 1
                        else:
                            df.at[idx, 'keylog'] = f"ERROR: {result.get('error', 'Unknown')}"
                            errors += 1

                        if progress_callback and (idx + 1) % 100 == 0:
                            progress_callback(idx + 1, total_rows, errors)

                    except Exception as e:
                        df.at[idx, 'keylog'] = f"ERROR: {str(e)}"
                        errors += 1

                # Memory cleanup after each chunk
                gc.collect()

            # Move keylog to end
            if 'keylog' in df.columns:
                cols = [c for c in df.columns if c != 'keylog'] + ['keylog']
                df = df[cols]

            # ✅ WRITE OUTPUT
            print(f"\n💾 Writing output file...")
            df.to_excel(output_path, index=False)

            print(f"\n✅ Large file processing complete!")
            print(f"   Total: {total_rows} | Success: {processed} | Errors: {errors}")

            return {
                'success': True,
                'processed': processed,
                'errors': errors,
                'total': total_rows,
                'output_file': output_path,
                'chunks_processed': num_chunks
            }

        except Exception as e:
            return {'success': False, 'error': f'Lỗi xử lý large file: {str(e)}'}

    def _get_total_rows(self, file_path: str) -> int:
        """Get total rows trong Excel file"""
        try:
            with pd.ExcelFile(file_path) as xls:
                sheet = xls.parse(xls.sheet_names[0])
                return len(sheet)
        except:
            return 0

    # ========== AUTO PROCESSOR (SMART SELECTION) ==========

    def process_file_auto(self, input_path: str, output_path: str,
                          progress_callback: Optional[Callable] = None,
                          operation: str = None,
                          shape_a: str = None,
                          shape_b: str = None,
                          dimension_a: str = "3",
                          dimension_b: str = "3",
                          version: str = "fx799") -> Dict:
        """
        Tự động chọn processor phù hợp (normal vs chunked)
        """
        is_large, file_info = self.is_large_file(input_path)

        if is_large:
            print(f"📊 Large file detected ({file_info['size_mb']} MB)")
            print(f"   Using chunked processing...")
            return self.process_large_file(
                input_path,
                output_path,
                chunk_size=file_info['recommended_chunk_size'],
                progress_callback=progress_callback,
                operation=operation,
                shape_a=shape_a,
                shape_b=shape_b,
                dimension_a=dimension_a,
                dimension_b=dimension_b,
                version=version
            )
        else:
            print(f"📄 Normal file ({file_info['size_mb']} MB)")
            print(f"   Using standard processing...")
            return self.process_file(
                input_path,
                output_path,
                progress_callback=progress_callback,
                operation=operation,
                shape_a=shape_a,
                shape_b=shape_b,
                dimension_a=dimension_a,
                dimension_b=dimension_b,
                version=version
            )
