

import pandas as pd
import os
import json
import gc
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable


class ExcelProcessor:
    def __init__(self, service):

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

        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)

            # Quick row count check (read only first sheet metadata)
            try:
                with pd.ExcelFile(file_path) as xls:
                    # Get first sheet
                    sheet_name = xls.sheet_names[0]
                    df_sample = pd.read_excel(xls, sheet_name=sheet_name, nrows=0)

                    # Estimate total rows (might not be exact)
                    # For accurate count, need to read entire file
                    row_count = None  # Unknown for now
            except:
                row_count = None

            is_large = file_size_mb > self.LARGE_FILE_SIZE_MB

            file_info = {
                'size_mb': round(file_size_mb, 2),
                'row_count': row_count,
                'is_large': is_large,
                'recommended_chunk_size': self.DEFAULT_CHUNK_SIZE if is_large else None
            }

            return is_large, file_info

        except Exception as e:
            return False, {'error': str(e)}

    def validate_columns(self, df: pd.DataFrame, operation: str,
                        shape_a: str, shape_b: Optional[str] = None) -> Dict:

        try:
            required_columns = self._get_required_columns(operation, shape_a, shape_b)
            existing_columns = set(df.columns)
            missing_columns = [col for col in required_columns if col not in existing_columns]

            if missing_columns:
                return {
                    'valid': False,
                    'missing_columns': missing_columns,
                    'message': f"Thiếu {len(missing_columns)} cột: {', '.join(missing_columns)}"
                }

            return {
                'valid': True,
                'missing_columns': [],
                'message': 'Tất cả columns cần thiết đều có sẵn'
            }

        except Exception as e:
            return {
                'valid': False,
                'missing_columns': [],
                'message': f'Lỗi validation: {str(e)}'
            }

    def _get_required_columns(self, operation: str, shape_a: str,
                             shape_b: Optional[str] = None) -> List[str]:
        """Get danh sách columns cần thiết"""
        columns = []

        # Common columns
        common = self.column_mapping.get('common_columns', {})
        if common:
            columns.append(common.get('operation', {}).get('excel_column', 'operation'))
            columns.append(common.get('shape_a', {}).get('excel_column', 'shape_A'))

            if shape_b:
                columns.append(common.get('shape_b', {}).get('excel_column', 'shape_B'))

            columns.append(common.get('dimension_a', {}).get('excel_column', 'dim_A'))
            if shape_b:
                columns.append(common.get('dimension_b', {}).get('excel_column', 'dim_B'))

        # Shape A columns
        shape_a_mapping = self.column_mapping.get('group_a_mapping', {}).get(shape_a, {})
        if shape_a_mapping:
            columns.extend(shape_a_mapping.get('required_columns', []))

        # Shape B columns
        if shape_b:
            shape_b_mapping = self.column_mapping.get('group_b_mapping', {}).get(shape_b, {})
            if shape_b_mapping:
                columns.extend(shape_b_mapping.get('required_columns', []))

        return columns

    # ========== DATA EXTRACTION ==========

    def _extract_data_from_row(self, row: pd.Series, group: str, shape: str) -> Dict:

        data = {}

        mapping_key = f"group_{group}_mapping"
        shape_mapping = self.column_mapping.get(mapping_key, {}).get(shape, {})

        if not shape_mapping:
            raise ValueError(f"No mapping found for {group.upper()} - {shape}")

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
                        f"Missing required value in column '{excel_col}' for {shape}"
                    )

                data[data_key] = value
            elif col_config.get('required', False):
                raise ValueError(
                    f"Required column '{excel_col}' not found"
                )

        return data

    # ========== NORMAL FILE PROCESSING ==========

    def process_file(self, input_path: str, output_path: str,
                     progress_callback: Optional[Callable] = None) -> Dict:

        try:
            # Read Excel
            df = pd.read_excel(input_path)
            total_rows = len(df)

            print(f"📊 Processing {total_rows} rows...")
            print(f"📋 Original columns: {list(df.columns)}")

            # ✅ Check nếu đã có column keylog
            if 'keylog' not in df.columns:
                df['keylog'] = ''  # Thêm mới
                print("   → Added 'keylog' column")
            else:
                print("   → 'keylog' column exists, will overwrite")

            processed = 0
            errors = 0

            # Process từng row
            for idx, row in df.iterrows():
                try:
                    # Extract metadata
                    operation = str(row.get('operation', '')).strip()
                    shape_a = str(row.get('shape_A', '')).strip()
                    shape_b = str(row.get('shape_B', '')).strip() if pd.notna(row.get('shape_B')) else None
                    dimension_a = str(row.get('dim_A', '3')).strip()
                    dimension_b = str(row.get('dim_B', '3')).strip()
                    version = str(row.get('version', 'fx799')).strip()

                    # Extract data
                    data_a = self._extract_data_from_row(row, 'a', shape_a)
                    data_b = self._extract_data_from_row(row, 'b', shape_b) if shape_b else None

                    # Configure service
                    self.service.set_operation(operation)
                    self.service.set_shapes(shape_a, shape_b)
                    self.service.set_dimension(dimension_a, dimension_b)
                    self.service.set_version(version)

                    # Encode
                    result = self.service.process_manual_data(data_a, data_b)

                    if result['success']:
                        # ✅ CHỈ GHI VÀO COLUMN KEYLOG
                        df.at[idx, 'keylog'] = result['encoded']
                        processed += 1
                    else:
                        # Ghi error vào keylog (hoặc để trống)
                        df.at[idx, 'keylog'] = f"ERROR: {result.get('error', 'Unknown error')}"
                        errors += 1

                    # Progress callback
                    if progress_callback:
                        progress_callback(idx + 1, total_rows, errors)

                except Exception as e:
                    # Ghi error message vào keylog
                    df.at[idx, 'keylog'] = f"ERROR: {str(e)}"
                    errors += 1


            if 'keylog' in df.columns:
                cols = [c for c in df.columns if c != 'keylog'] + ['keylog']
                df = df[cols]

            df.to_excel(output_path, index=False)

            print(f"✅ Processing complete: {processed} success, {errors} errors")
            print(f"📁 Output: {output_path}")

            return {
                'success': True,
                'processed': processed,
                'errors': errors,
                'total': total_rows,
                'output_file': output_path
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi xử lý file: {str(e)}'
            }

    # ========== LARGE FILE PROCESSING (CHUNKED) ==========

    def process_large_file(self, input_path: str, output_path: str,
                           chunk_size: int = 1000,
                           progress_callback: Optional[Callable] = None) -> Dict:

        try:
            print(f"🔄 Large file processing: chunk_size={chunk_size}")

            # Get total rows
            total_rows = self._get_total_rows(input_path)

            processed = 0
            errors = 0
            current_row = 0

            # Create Excel writer
            writer = pd.ExcelWriter(output_path, engine='openpyxl')

            # Process chunks
            chunk_iterator = pd.read_excel(input_path, chunksize=chunk_size)

            first_chunk = True

            for chunk_idx, chunk_df in enumerate(chunk_iterator):
                print(f"📦 Processing chunk {chunk_idx + 1} ({len(chunk_df)} rows)...")

                # ✅ Check và thêm column keylog nếu cần
                if 'keylog' not in chunk_df.columns:
                    chunk_df['keylog'] = ''

                # Process rows in chunk
                for idx, row in chunk_df.iterrows():
                    try:
                        # Extract & process (same as normal processing)
                        operation = str(row.get('operation', '')).strip()
                        shape_a = str(row.get('shape_A', '')).strip()
                        shape_b = str(row.get('shape_B', '')).strip() if pd.notna(row.get('shape_B')) else None
                        dimension_a = str(row.get('dim_A', '3')).strip()
                        dimension_b = str(row.get('dim_B', '3')).strip()
                        version = str(row.get('version', 'fx799')).strip()

                        data_a = self._extract_data_from_row(row, 'a', shape_a)
                        data_b = self._extract_data_from_row(row, 'b', shape_b) if shape_b else None

                        self.service.set_operation(operation)
                        self.service.set_shapes(shape_a, shape_b)
                        self.service.set_dimension(dimension_a, dimension_b)
                        self.service.set_version(version)

                        result = self.service.process_manual_data(data_a, data_b)

                        if result['success']:
                            # ✅ CHỈ GHI VÀO KEYLOG
                            chunk_df.at[idx, 'keylog'] = result['encoded']
                            processed += 1
                        else:
                            chunk_df.at[idx, 'keylog'] = f"ERROR: {result.get('error', 'Unknown')}"
                            errors += 1

                        current_row += 1

                        if progress_callback and current_row % 100 == 0:
                            progress_callback(current_row, total_rows, errors)

                    except Exception as e:
                        chunk_df.at[idx, 'keylog'] = f"ERROR: {str(e)}"
                        errors += 1
                        current_row += 1

                # ✅ Move keylog column to end (if newly added)
                if 'keylog' in chunk_df.columns:
                    cols = [c for c in chunk_df.columns if c != 'keylog'] + ['keylog']
                    chunk_df = chunk_df[cols]

                # Write chunk
                if first_chunk:
                    chunk_df.to_excel(writer, sheet_name='Data', index=False, startrow=0)
                    first_chunk = False
                else:
                    startrow = writer.sheets['Data'].max_row
                    chunk_df.to_excel(writer, sheet_name='Data', index=False,
                                      startrow=startrow, header=False)

                # Clean memory
                del chunk_df
                gc.collect()

                print(f"✓ Chunk {chunk_idx + 1} complete")

            # Add summary sheet
            summary_df = pd.DataFrame({
                'Metric': ['Total Rows', 'Processed', 'Errors', 'Success Rate'],
                'Value': [
                    total_rows,
                    processed,
                    errors,
                    f"{(processed / total_rows * 100):.2f}%" if total_rows > 0 else "0%"
                ]
            })
            summary_df.to_excel(writer, sheet_name='Summary', index=False)

            writer.close()

            print(f"✅ Large file processing complete!")
            print(f"   Total: {total_rows} | Success: {processed} | Errors: {errors}")

            return {
                'success': True,
                'processed': processed,
                'errors': errors,
                'total': total_rows,
                'output_file': output_path,
                'chunks_processed': chunk_idx + 1
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi xử lý large file: {str(e)}'
            }

    def _get_total_rows(self, file_path: str) -> int:
        """Get total rows trong Excel file"""
        try:
            df = pd.read_excel(file_path, nrows=0)
            # Count rows (excluding header)
            with pd.ExcelFile(file_path) as xls:
                sheet = xls.parse(xls.sheet_names[0])
                return len(sheet)
        except:
            return 0

    # ========== AUTO PROCESSOR (SMART SELECTION) ==========

    def process_file_auto(self, input_path: str, output_path: str,
                         progress_callback: Optional[Callable] = None) -> Dict:

        is_large, file_info = self.is_large_file(input_path)

        if is_large:
            print(f"📊 Large file detected ({file_info['size_mb']} MB)")
            print(f"   Using chunked processing...")
            return self.process_large_file(
                input_path,
                output_path,
                chunk_size=file_info['recommended_chunk_size'],
                progress_callback=progress_callback
            )
        else:
            print(f"📄 Normal file ({file_info['size_mb']} MB)")
            print(f"   Using standard processing...")
            return self.process_file(
                input_path,
                output_path,
                progress_callback=progress_callback
            )

    # ========== TEMPLATE GENERATION ==========

    def create_template(self, output_path: str, operation: str,
                       shape_a: str, shape_b: Optional[str] = None) -> Dict:

        try:
            columns = self._get_required_columns(operation, shape_a, shape_b)

            # Add output columns
            output_cols = self.column_mapping.get('output_columns', {})
            columns.append(output_cols.get('encoded', {}).get('excel_column', 'keylog'))
            columns.append(output_cols.get('status', {}).get('excel_column', 'status'))
            columns.append(output_cols.get('error_message', {}).get('excel_column', 'error'))

            # Create DataFrame with sample data
            sample_data = self._generate_sample_data(operation, shape_a, shape_b)
            df = pd.DataFrame(sample_data)

            # Ensure all columns exist
            for col in columns:
                if col not in df.columns:
                    df[col] = ''

            # Reorder columns
            df = df[columns]

            # Write to Excel
            df.to_excel(output_path, index=False)

            print(f"✅ Template created: {output_path}")
            print(f"   Columns: {len(columns)}")

            return {
                'success': True,
                'file': output_path,
                'columns': columns,
                'sample_rows': len(sample_data)
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi tạo template: {str(e)}'
            }

    def _generate_sample_data(self, operation: str, shape_a: str,
                             shape_b: Optional[str] = None) -> List[Dict]:
        """Generate sample data cho template"""
        samples = []

        # Sample 1: Basic example
        sample1 = {
            'operation': operation,
            'shape_A': shape_a,
            'shape_B': shape_b if shape_b else '',
            'dim_A': '3',
            'dim_B': '3' if shape_b else '',
            'version': 'fx799'
        }

        # Add shape-specific data
        if shape_a == 'Điểm':
            sample1['data_A'] = '1,2,3'
        elif shape_a == 'Vecto':
            sample1['data_v1'] = '4,5,6'
        elif shape_a == 'Đường thẳng':
            sample1['d_P_data_A'] = '1,2,3'
            sample1['d_V_data_A'] = '1,1,1'
        elif shape_a == 'Mặt phẳng':
            sample1['P1_a'] = '1'
            sample1['P1_b'] = '1'
            sample1['P1_c'] = '1'
            sample1['P1_d'] = '-6'
        elif shape_a == 'Đường tròn':
            sample1['C_data_I1'] = '0,0'
            sample1['C_data_R1'] = '5'
        elif shape_a == 'Mặt cầu':
            sample1['S_data_I1'] = '0,0,0'
            sample1['S_data_R1'] = '5'
        elif shape_a == 'Tam giác':
            sample1['T_data_a'] = '3'
            sample1['T_data_b'] = '4'
            sample1['T_data_c'] = '90'

        # Add shape B data if needed
        if shape_b:
            if shape_b == 'Điểm':
                sample1['data_B'] = '4,5,6'
            elif shape_b == 'Vecto':
                sample1['data_v2'] = '1,0,0'
            elif shape_b == 'Đường thẳng':
                sample1['d_P_data_B'] = '0,0,0'
                sample1['d_V_data_B'] = '1,1,1'
            elif shape_b == 'Mặt phẳng':
                sample1['P2_a'] = '1'
                sample1['P2_b'] = '0'
                sample1['P2_c'] = '0'
                sample1['P2_d'] = '0'
            elif shape_b == 'Đường tròn':
                sample1['C_data_I2'] = '3,4'
                sample1['C_data_R2'] = '10'
            elif shape_b == 'Mặt cầu':
                sample1['S_data_I2'] = '1,2,3'
                sample1['S_data_R2'] = '7'

        samples.append(sample1)

        # Sample 2: With expressions
        sample2 = sample1.copy()
        if shape_a == 'Điểm':
            sample2['data_A'] = 'sqrt(2),-3,0'
        samples.append(sample2)

        return samples
