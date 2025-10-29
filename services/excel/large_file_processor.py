import pandas as pd
import os
import gc
import psutil
from typing import Dict, List, Tuple, Any, Optional, Iterator, Callable
from datetime import datetime
import threading
import time

class LargeFileProcessor:
    """Specialized processor for very large Excel files (200k+ rows, 50MB+)"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.processing_cancelled = False
        self.max_memory_mb = 1000  # Limit memory usage to 1GB
        self.emergency_cleanup = False
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except:
            return 0.0
    
    def check_memory_limit(self) -> bool:
        """Check if memory usage exceeds limit"""
        current_memory = self.get_memory_usage()
        return current_memory > self.max_memory_mb
    
    def emergency_memory_cleanup(self):
        """Emergency memory cleanup"""
        self.emergency_cleanup = True
        gc.collect()
        time.sleep(0.1)  # Allow GC to complete
        
    def estimate_optimal_chunksize(self, file_path: str) -> int:
        """Estimate optimal chunk size based on file size and available memory"""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Conservative chunking for very large files
            if file_size_mb > 100:  # > 100MB
                return 500
            elif file_size_mb > 50:   # 50-100MB  
                return 1000
            elif file_size_mb > 20:   # 20-50MB
                return 2000
            else:
                return 5000
                
        except Exception:
            return 500  # Safe fallback
    
    def read_excel_streaming(self, file_path: str, chunksize: int = None) -> Iterator[pd.DataFrame]:
        """
        Stream Excel file in very small chunks with memory management
        Fixed for 200k+ rows crash issue
        """
        if chunksize is None:
            chunksize = self.estimate_optimal_chunksize(file_path)
        
        try:
            # First, try to get basic file info without loading entire file
            print(f"🔍 Analyzing large file: {os.path.basename(file_path)}")
            
            # Use openpyxl for better memory management with large files
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            
            # Get dimensions without loading all data
            max_row = ws.max_row
            max_col = ws.max_column
            
            print(f"📊 File dimensions: {max_row} rows × {max_col} columns")
            print(f"📦 Using chunk size: {chunksize}")
            
            # Read header first
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            columns = [str(cell) if cell is not None else f"Col_{i}" for i, cell in enumerate(header_row)]
            
            wb.close()  # Close workbook immediately
            
            # Now read in chunks using openpyxl
            current_row = 2  # Start after header
            chunk_count = 0
            
            while current_row <= max_row:
                try:
                    # Memory check before each chunk
                    if self.check_memory_limit():
                        print(f"⚠️ Memory limit reached: {self.get_memory_usage():.1f}MB")
                        self.emergency_memory_cleanup()
                        
                        if self.check_memory_limit():  # Still high after cleanup
                            raise MemoryError(f"Memory usage too high: {self.get_memory_usage():.1f}MB > {self.max_memory_mb}MB")
                    
                    if self.processing_cancelled:
                        break
                    
                    # Calculate chunk range
                    end_row = min(current_row + chunksize - 1, max_row)
                    
                    print(f"📖 Reading chunk {chunk_count + 1}: rows {current_row}-{end_row}")
                    
                    # Read specific range using openpyxl for memory efficiency  
                    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                    ws = wb.active
                    
                    chunk_data = []
                    for row in ws.iter_rows(min_row=current_row, max_row=end_row, values_only=True):
                        # Convert None values to empty strings
                        row_data = [str(cell) if cell is not None else "" for cell in row]
                        chunk_data.append(row_data)
                    
                    wb.close()  # Close immediately
                    
                    # Create DataFrame from chunk data
                    if chunk_data:
                        chunk_df = pd.DataFrame(chunk_data, columns=columns)
                        # Clean up data
                        chunk_df = chunk_df.replace('nan', '')
                        chunk_df = chunk_df.fillna('')
                        
                        yield chunk_df
                        
                        # Force cleanup after yield
                        del chunk_df
                        del chunk_data
                        gc.collect()
                    
                    current_row = end_row + 1
                    chunk_count += 1
                    
                    # Memory usage logging
                    memory_usage = self.get_memory_usage()
                    if chunk_count % 10 == 0:  # Log every 10 chunks
                        print(f"💾 Memory usage after chunk {chunk_count}: {memory_usage:.1f}MB")
                    
                except Exception as e:
                    print(f"❌ Error reading chunk starting at row {current_row}: {e}")
                    # Try to continue with next chunk
                    current_row += chunksize
                    continue
            
            print(f"✅ Completed streaming {chunk_count} chunks")
            
        except Exception as e:
            raise Exception(f"Lỗi đọc file lớn: {str(e)}")
    
    def process_large_excel_safe(self, file_path: str, shape_a: str, shape_b: str,
                                operation: str, dimension_a: str, dimension_b: str,
                                output_path: str, progress_callback: Callable = None) -> Tuple[int, int, str]:
        """
        Safely process very large Excel files with memory management
        Returns: (success_count, error_count, output_file)
        """
        
        self.processing_cancelled = False
        success_count = 0
        error_count = 0
        processed_count = 0
        
        # Import geometry service here to avoid circular imports
        from services.geometry.geometry_service import GeometryService
        
        try:
            # Initialize fresh service for large file processing
            service = GeometryService(self.config)
            service.set_current_shapes(shape_a, shape_b)
            service.set_kich_thuoc(dimension_a, dimension_b)
            service.set_current_operation(operation)
            
            # Get optimal chunk size
            chunk_size = self.estimate_optimal_chunksize(file_path)
            print(f"🎯 Processing large file with chunk size: {chunk_size}")
            
            # Estimate total rows for progress
            total_rows = self._estimate_total_rows(file_path)
            print(f"📊 Estimated total rows: {total_rows}")
            
            # Initialize results storage - write directly to file to save memory
            temp_results_file = f"{output_path}.temp_results"
            results_buffer = []
            buffer_size = 1000  # Write every 1000 results
            
            # Process in streaming chunks
            chunk_count = 0
            for chunk_df in self.read_excel_streaming(file_path, chunk_size):
                if self.processing_cancelled:
                    break
                
                chunk_count += 1
                print(f"🔄 Processing chunk {chunk_count} ({len(chunk_df)} rows)")
                
                # Process each row in chunk
                for index, row in chunk_df.iterrows():
                    try:
                        if self.processing_cancelled:
                            break
                        
                        # Extract data
                        data_a = self._extract_shape_data_safe(row, shape_a, 'A')
                        data_b = self._extract_shape_data_safe(row, shape_b, 'B') if shape_b else {}
                        
                        # Process - create fresh service instance periodically to prevent memory buildup
                        if processed_count % 1000 == 0 and processed_count > 0:
                            del service
                            gc.collect()
                            service = GeometryService(self.config)
                            service.set_current_shapes(shape_a, shape_b)
                            service.set_kich_thuoc(dimension_a, dimension_b)
                            service.set_current_operation(operation)
                        
                        service.thuc_thi_tat_ca(data_a, data_b)
                        result = service.generate_final_result()
                        
                        results_buffer.append(result)
                        success_count += 1
                        
                    except Exception as e:
                        results_buffer.append(f"LỖI: {str(e)}")
                        error_count += 1
                    
                    processed_count += 1
                    
                    # Write buffer to temp file when full
                    if len(results_buffer) >= buffer_size:
                        self._write_results_buffer(temp_results_file, results_buffer)
                        results_buffer = []
                        gc.collect()
                    
                    # Update progress
                    if progress_callback and processed_count % 100 == 0:
                        progress = (processed_count / total_rows) * 100 if total_rows > 0 else 0
                        progress_callback(progress, processed_count, total_rows, error_count)
                    
                    # Emergency memory check
                    if processed_count % 500 == 0:
                        if self.check_memory_limit():
                            self.emergency_memory_cleanup()
                            
                            if self.check_memory_limit():
                                # Still too high - reduce chunk size
                                chunk_size = max(chunk_size // 2, 100)
                                print(f"⚠️ Reducing chunk size to: {chunk_size}")
                
                # Cleanup after each chunk
                del chunk_df
                gc.collect()
            
            # Write remaining buffer
            if results_buffer:
                self._write_results_buffer(temp_results_file, results_buffer)
            
            # Combine results and create final Excel file
            print("📝 Creating final Excel file...")
            final_output = self._create_final_excel_from_temp(file_path, temp_results_file, output_path)
            
            # Cleanup temp file
            if os.path.exists(temp_results_file):
                os.remove(temp_results_file)
            
            return success_count, error_count, final_output
            
        except MemoryError as e:
            raise Exception(f"Hết bộ nhớ khi xử lý file lớn: {str(e)}\n\nHướng dẫn:\n1. Đóng các ứng dụng khác\n2. Giảm chunk size xuống 200-500\n3. Chia nhỏ file Excel thành nhiều file nhỏ hơn")
        except Exception as e:
            raise Exception(f"Lỗi xử lý file lớn: {str(e)}")
    
    def _estimate_total_rows(self, file_path: str) -> int:
        """Estimate total rows without loading entire file"""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            max_row = ws.max_row
            wb.close()
            return max_row - 1  # Exclude header
        except:
            return 0
    
    def _extract_shape_data_safe(self, row: pd.Series, shape_type: str, group: str) -> Dict:
        """Safe data extraction with memory optimization"""
        # Simplified extraction to reduce memory usage
        data_dict = {}
        
        if group == 'A':
            if shape_type == "Điểm":
                data_dict['point_input'] = str(row.get('data_A', '')).strip()
            elif shape_type == "Đường thẳng":
                data_dict['line_A1'] = str(row.get('d_P_data_A', '')).strip()
                data_dict['line_X1'] = str(row.get('d_V_data_A', '')).strip()
            elif shape_type == "Mặt phẳng":
                data_dict['plane_a'] = str(row.get('P1_a', '')).strip()
                data_dict['plane_b'] = str(row.get('P1_b', '')).strip()
                data_dict['plane_c'] = str(row.get('P1_c', '')).strip()
                data_dict['plane_d'] = str(row.get('P1_d', '')).strip()
            elif shape_type == "Đường tròn":
                data_dict['circle_center'] = str(row.get('C_data_I1', '')).strip()
                data_dict['circle_radius'] = str(row.get('C_data_R1', '')).strip()
            elif shape_type == "Mặt cầu":
                data_dict['sphere_center'] = str(row.get('S_data_I1', '')).strip()
                data_dict['sphere_radius'] = str(row.get('S_data_R1', '')).strip()
        else:  # Group B
            if shape_type == "Điểm":
                data_dict['point_input'] = str(row.get('data_B', '')).strip()
            elif shape_type == "Đường thẳng":
                data_dict['line_A2'] = str(row.get('d_P_data_B', '')).strip()
                data_dict['line_X2'] = str(row.get('d_V_data_B', '')).strip()
            elif shape_type == "Mặt phẳng":
                data_dict['plane_a'] = str(row.get('P2_a', '')).strip()
                data_dict['plane_b'] = str(row.get('P2_b', '')).strip()
                data_dict['plane_c'] = str(row.get('P2_c', '')).strip()
                data_dict['plane_d'] = str(row.get('P2_d', '')).strip()
            elif shape_type == "Đường tròn":
                data_dict['circle_center'] = str(row.get('C_data_I2', '')).strip()
                data_dict['circle_radius'] = str(row.get('C_data_R2', '')).strip()
            elif shape_type == "Mặt cầu":
                data_dict['sphere_center'] = str(row.get('S_data_I2', '')).strip()
                data_dict['sphere_radius'] = str(row.get('S_data_R2', '')).strip()
        
        return data_dict
    
    def _write_results_buffer(self, temp_file: str, results: List[str]):
        """Write results buffer to temporary file"""
        try:
            mode = 'a' if os.path.exists(temp_file) else 'w'
            with open(temp_file, mode, encoding='utf-8') as f:
                for result in results:
                    f.write(result + '\n')
        except Exception as e:
            print(f"⚠️ Warning: Could not write buffer to temp file: {e}")
    
    def _read_temp_results(self, temp_file: str) -> List[str]:
        """Read all results from temporary file"""
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines()]
        except Exception:
            return []
    
    def _create_final_excel_from_temp(self, original_file: str, temp_results_file: str, output_path: str) -> str:
        """Create final Excel file by combining original data with temp results"""
        try:
            print("📝 Creating final Excel file...")
            
            # Read results from temp file
            all_results = self._read_temp_results(temp_results_file)
            
            # For very large files, we'll create output using openpyxl directly
            # to avoid loading the entire original file into memory
            return self._create_excel_direct(original_file, all_results, output_path)
            
        except Exception as e:
            raise Exception(f"Lỗi tạo file Excel cuối: {str(e)}")
    
    def _create_excel_direct(self, original_file: str, results: List[str], output_path: str) -> str:
        """Create Excel output directly using openpyxl for memory efficiency"""
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
            
            # Open original file read-only
            source_wb = openpyxl.load_workbook(original_file, read_only=True, data_only=True)
            source_ws = source_wb.active
            
            # Create new workbook
            output_wb = openpyxl.Workbook()
            output_ws = output_wb.active
            output_ws.title = "Results"
            
            # Copy header and add keylog column
            header_row = next(source_ws.iter_rows(min_row=1, max_row=1, values_only=True))
            header = list(header_row) + ['Kết quả mã hóa']
            
            # Write header with formatting
            for col_idx, header_cell in enumerate(header, 1):
                cell = output_ws.cell(row=1, column=col_idx, value=str(header_cell))
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="2E86AB", end_color="2E86AB", fill_type="solid")
            
            # Process data row by row to avoid memory issues
            row_count = 2  # Start after header
            result_idx = 0
            
            print(f"📊 Writing {len(results)} results to Excel...")
            
            for data_row in source_ws.iter_rows(min_row=2, values_only=True):
                if result_idx >= len(results):
                    break
                
                # Write original data
                for col_idx, cell_value in enumerate(data_row, 1):
                    output_ws.cell(row=row_count, column=col_idx, value=str(cell_value) if cell_value is not None else "")
                
                # Write result in keylog column
                keylog_col = len(header)
                result_cell = output_ws.cell(row=row_count, column=keylog_col, value=results[result_idx])
                result_cell.font = Font(bold=True, color="2E7D32")
                
                row_count += 1
                result_idx += 1
                
                # Memory management
                if row_count % 1000 == 0:
                    print(f"📝 Written {row_count-1} rows... ({self.get_memory_usage():.1f}MB)")
                    if self.check_memory_limit():
                        gc.collect()
            
            # Close source workbook
            source_wb.close()
            
            # Auto-adjust column widths (only for first 1000 rows to save time)
            print("🎨 Auto-adjusting column widths...")
            for column in output_ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                # Check only first 1000 rows for performance
                for i, cell in enumerate(column):
                    if i > 1000:  # Limit to first 1000 rows
                        break
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)  # Max width 50
                output_ws.column_dimensions[column_letter].width = adjusted_width
            
            # Save final file
            print(f"💾 Saving final file: {output_path}")
            output_wb.save(output_path)
            output_wb.close()
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Lỗi tạo Excel trực tiếp: {str(e)}")
    
    def validate_large_file_structure(self, file_path: str, shape_a: str, shape_b: str = None) -> Dict[str, Any]:
        """Validate large file structure without loading entire file"""
        try:
            import openpyxl
            
            # Open read-only
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            
            # Get header row
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            columns = [str(cell) for cell in header_row if cell is not None]
            
            wb.close()
            
            # Check required columns based on shape selection
            required_columns_A = self._get_required_columns(shape_a, 'A')
            required_columns_B = self._get_required_columns(shape_b, 'B') if shape_b else []
            
            missing_columns = []
            for col in required_columns_A + required_columns_B:
                if col not in columns:
                    missing_columns.append(col)
            
            file_info = {
                'valid': len(missing_columns) == 0,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'estimated_rows': ws.max_row - 1 if hasattr(ws, 'max_row') else 0,
                'columns': columns,
                'missing_columns': missing_columns,
                'recommended_chunk_size': self.estimate_optimal_chunksize(file_path)
            }
            
            return file_info
            
        except Exception as e:
            return {'valid': False, 'error': f'Lỗi kiểm tra file: {str(e)}'}
    
    def _get_required_columns(self, shape: str, group: str) -> List[str]:
        """Get required columns for shape and group"""
        if group == 'A':
            mapping = {
                "Điểm": ["data_A"],
                "Đường thẳng": ["d_P_data_A", "d_V_data_A"],
                "Mặt phẳng": ["P1_a", "P1_b", "P1_c", "P1_d"],
                "Đường tròn": ["C_data_I1", "C_data_R1"],
                "Mặt cầu": ["S_data_I1", "S_data_R1"]
            }
        else:  # Group B
            mapping = {
                "Điểm": ["data_B"],
                "Đường thẳng": ["d_P_data_B", "d_V_data_B"],
                "Mặt phẳng": ["P2_a", "P2_b", "P2_c", "P2_d"],
                "Đường tròn": ["C_data_I2", "C_data_R2"],
                "Mặt cầu": ["S_data_I2", "S_data_R2"]
            }
        
        return mapping.get(shape, [])
