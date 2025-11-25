"""
Excel Processor - Xử lý file Excel
"""
import pandas as pd
import os


class ExcelProcessor:
    def __init__(self, service):
        self.service = service

    def process_file(self, input_path, output_path, operation, shape_a, shape_b,
                     dim_a, dim_b, version, progress_callback=None):
        """
        Xử lý file Excel batch

        Returns:
            Dict {'success': bool, 'output_file': path, 'processed': int, 'errors': int}
        """
        try:
            # Đọc Excel
            df = pd.read_excel(input_path)
            total_rows = len(df)
            processed = 0
            errors = 0
            results = []

            # Process từng row
            for idx, row in df.iterrows():
                try:
                    # Extract data from row
                    data_a = self._extract_data_from_row(row, 'A', shape_a)
                    data_b = self._extract_data_from_row(row, 'B', shape_b) if shape_b else None

                    # Process
                    result = self.service.process_manual_data(data_a, data_b)

                    if result['success']:
                        results.append(result['encoded'])
                        processed += 1
                    else:
                        results.append(f"ERROR: {result['error']}")
                        errors += 1

                    # Progress callback
                    if progress_callback:
                        progress = ((idx + 1) / total_rows) * 100
                        progress_callback(progress, idx + 1, total_rows, errors)

                except Exception as e:
                    results.append(f"ERROR: {str(e)}")
                    errors += 1

            # Ghi output
            output_df = df.copy()
            output_df['Encoded'] = results
            output_df.to_excel(output_path, index=False)

            return {
                'success': True,
                'output_file': output_path,
                'processed': processed,
                'errors': errors
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi xử lý Excel: {str(e)}'
            }

    def _extract_data_from_row(self, row, group, shape):
        """Extract data từ Excel row"""
        # TODO: Implement extraction logic theo format columns
        data = {}
        prefix = f"{group}_"

        # Example: extract coordinates
        if shape == "Điểm":
            data['point_input'] = f"{row.get(f'{prefix}x', 0)}, {row.get(f'{prefix}y', 0)}, {row.get(f'{prefix}z', 0)}"
        # ... other shapes

        return data

    def create_template(self, output_path, operation, shape_a, shape_b):
        """Tạo Excel template"""
        try:
            # TODO: Create template với columns phù hợp
            columns = self._get_template_columns(operation, shape_a, shape_b)

            df = pd.DataFrame(columns=columns)
            df.to_excel(output_path, index=False)

            return {
                'success': True,
                'file': output_path
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Lỗi tạo template: {str(e)}'
            }

    def _get_template_columns(self, operation, shape_a, shape_b):
        """Get columns cho template"""
        columns = []

        # Columns cho shape A
        columns.extend(self._get_shape_columns('A', shape_a))

        # Columns cho shape B (nếu có)
        if shape_b:
            columns.extend(self._get_shape_columns('B', shape_b))

        # Column kết quả
        columns.append('Encoded')

        return columns

    def _get_shape_columns(self, group, shape):
        """Get columns cho một shape"""
        prefix = f"{group}_"

        if shape == "Điểm":
            return [f"{prefix}x", f"{prefix}y", f"{prefix}z"]
        elif shape == "Vecto":
            return [f"{prefix}vx", f"{prefix}vy", f"{prefix}vz"]
        elif shape == "Đường thẳng":
            return [f"{prefix}px", f"{prefix}py", f"{prefix}pz",
                    f"{prefix}dx", f"{prefix}dy", f"{prefix}dz"]
        # ... other shapes

        return [f"{prefix}data"]
