import pandas as pd
import os
import gc
import psutil
from typing import Dict, List, Tuple, Any, Optional, Iterator, Callable
from datetime import datetime
import threading
import time

class LargeFileProcessor:
    """
    Specialized processor for very large Excel files (200k+ rows, 50MB+)
    Features: Memory-optimized streaming, crash protection, emergency cleanup
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.processing_cancelled = False
        self.max_memory_mb = 1000  # Limit memory usage to 1GB
        self.emergency_cleanup = False
        self.max_rows_allowed = 250_000  # NEW: hard limit of 250,000 rows
        
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
        """Emergency memory cleanup when limit is reached"""
        self.emergency_cleanup = True
        gc.collect()
        time.sleep(0.1)  # Allow GC to complete
        
    def _enforce_row_limit(self, total_rows: int):
        """Raise if total rows exceed the allowed hard limit"""
        if total_rows > self.max_rows_allowed:
            raise Exception(
                f"File có {total_rows} dòng, vượt quá giới hạn tối đa {self.max_rows_allowed} dòng.\n"
                f"Vui lòng chia nhỏ file hoặc lọc bớt dữ liệu trước khi import."
            )
    
    def estimate_optimal_chunksize(self, file_path: str) -> int:
        """Estimate optimal chunk size based on file size and available memory"""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Conservative chunking strategy for very large files
            if file_size_mb > 100:  # Files > 100MB
                return 200
            elif file_size_mb > 50:   # 50-100MB  
                return 500
            elif file_size_mb > 20:   # 20-50MB
                return 1000
            else:
                return 2000
                
        except Exception:
            return 200
    
    def read_excel_streaming(self, file_path: str, chunksize: int = None) -> Iterator[pd.DataFrame]:
        """
        Stream Excel file in very small chunks with aggressive memory management
        Designed specifically to handle up to 250k rows without crashing
        """
        if chunksize is None:
            chunksize = self.estimate_optimal_chunksize(file_path)
        
        try:
            import openpyxl
            print(f"🔍 Analyzing large file: {os.path.basename(file_path)}")
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            
            max_row = ws.max_row  # includes header
            max_col = ws.max_column
            total_rows = max(0, (max_row - 1))  # exclude header
            
            # NEW: enforce hard limit
            self._enforce_row_limit(total_rows)
            
            print(f"📊 File dimensions: {total_rows} data rows × {max_col} columns")
            print(f"📦 Using chunk size: {chunksize} rows")
            print(f"💾 Estimated chunks: {(total_rows + chunksize - 1)//chunksize}")
            
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            columns = [str(cell) if cell is not None else f"Col_{i}" for i, cell in enumerate(header_row)]
            wb.close()
            
            current_row = 2
            chunk_count = 0
            
            while current_row <= max_row:
                try:
                    if self.check_memory_limit():
                        print(f"⚠️ Memory limit reached: {self.get_memory_usage():.1f}MB")
                        self.emergency_memory_cleanup()
                        if self.check_memory_limit():
                            raise MemoryError(f"Memory usage too high: {self.get_memory_usage():.1f}MB > {self.max_memory_mb}MB")
                    
                    if self.processing_cancelled:
                        print("🛑 Processing cancelled by user")
                        break
                    
                    end_row = min(current_row + chunksize - 1, max_row)
                    
                    print(f"📖 Reading chunk {chunk_count + 1}: rows {current_row}-{end_row}")
                    wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
                    ws = wb.active
                    chunk_data = []
                    for row in ws.iter_rows(min_row=current_row, max_row=end_row, values_only=True):
                        row_data = [str(cell) if cell is not None else "" for cell in row]
                        chunk_data.append(row_data)
                    wb.close()
                    
                    if chunk_data:
                        chunk_df = pd.DataFrame(chunk_data, columns=columns)
                        chunk_df = chunk_df.replace('nan', '').fillna('')
                        yield chunk_df
                        del chunk_df, chunk_data
                        gc.collect()
                    
                    current_row = end_row + 1
                    chunk_count += 1
                    if chunk_count % 5 == 0:
                        print(f"💾 Memory after chunk {chunk_count}: {self.get_memory_usage():.1f}MB")
                except Exception as e:
                    print(f"❌ Error reading chunk starting at row {current_row}: {e}")
                    current_row += chunksize
                    continue
            
            print(f"✅ Streaming completed: {chunk_count} chunks processed")
        except Exception as e:
            raise Exception(f"Lỗi đọc file lớn: {str(e)}")
    
    def process_large_excel_safe(self, file_path: str, shape_a: str, shape_b: str,
                                operation: str, dimension_a: str, dimension_b: str,
                                output_path: str, progress_callback: Callable = None) -> Tuple[int, int, str]:
        """
        Safely process very large Excel files with comprehensive memory management
        Enforces a hard row limit of 250,000 rows
        Returns: (success_count, error_count, output_file_path)
        """
        
        self.processing_cancelled = False
        success_count = 0
        error_count = 0
        processed_count = 0
        
        from services.geometry.geometry_service import GeometryService
        
        try:
            print(f"🚀 Starting large file processing: {os.path.basename(file_path)}")
            
            # Estimate and enforce row limit before processing
            total_rows = self._estimate_total_rows(file_path)
            self._enforce_row_limit(total_rows)
            
            service = GeometryService(self.config)
            service.set_current_shapes(shape_a, shape_b)
            service.set_kich_thuoc(dimension_a, dimension_b)
            service.set_current_operation(operation)
            
            chunk_size = self.estimate_optimal_chunksize(file_path)
            print(f"🎯 Using chunk size: {chunk_size} rows")
            print(f"📊 Estimated total rows: {total_rows}")
            
            temp_results_file = f"{output_path}.temp_results"
            results_buffer = []
            buffer_size = 1000
            
            chunk_count = 0
            for chunk_df in self.read_excel_streaming(file_path, chunk_size):
                if self.processing_cancelled:
                    print("🛑 Processing cancelled by user")
                    break
                
                chunk_count += 1
                print(f"⚙️ Processing chunk {chunk_count} ({len(chunk_df)} rows)")
                
                for index, row in chunk_df.iterrows():
                    try:
                        if self.processing_cancelled:
                            break
                        data_a = self._extract_shape_data_safe(row, shape_a, 'A')
                        data_b = self._extract_shape_data_safe(row, shape_b, 'B') if shape_b else {}
                        
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
                    
                    if len(results_buffer) >= buffer_size:
                        self._write_results_buffer(temp_results_file, results_buffer)
                        results_buffer = []
                        gc.collect()
                    
                    if progress_callback and processed_count % 50 == 0:
                        progress = (processed_count / total_rows) * 100 if total_rows > 0 else 0
                        progress_callback(progress, processed_count, total_rows, error_count)
                    
                    if processed_count % 500 == 0 and self.check_memory_limit():
                        print(f"⚠️ Memory high: {self.get_memory_usage():.1f}MB - Emergency cleanup")
                        self.emergency_memory_cleanup()
                
                del chunk_df
                gc.collect()
                print(f"✅ Chunk {chunk_count} completed. Memory: {self.get_memory_usage():.1f}MB")
            
            if results_buffer:
                self._write_results_buffer(temp_results_file, results_buffer)
            
            print("🔧 Assembling final Excel file...")
            final_output = self._create_final_excel_from_temp(file_path, temp_results_file, output_path)
            if os.path.exists(temp_results_file):
                os.remove(temp_results_file)
            
            print(f"🎉 Complete! Success: {success_count}, Errors: {error_count}")
            return success_count, error_count, final_output
        
        except Exception as e:
            raise Exception(f"Lỗi xử lý file lớn: {str(e)}")
    
    def _estimate_total_rows(self, file_path: str) -> int:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            max_row = ws.max_row if hasattr(ws, 'max_row') else 0
            wb.close()
            return max(0, max_row - 1)
        except Exception:
            return 0
    
    def _extract_shape_data_safe(self, row: pd.Series, shape_type: str, group: str) -> Dict:
        data_dict = {}
        try:
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
            else:
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
        except Exception as e:
            print(f"⚠️ Warning: Data extraction error for {shape_type} {group}: {e}")
        return data_dict
    
    def _write_results_buffer(self, temp_file: str, results: List[str]):
        try:
            mode = 'a' if os.path.exists(temp_file) else 'w'
            with open(temp_file, mode, encoding='utf-8') as f:
                for result in results:
                    f.write(result + '\n')
        except Exception as e:
            print(f"⚠️ Warning: Could not write buffer to temp file: {e}")
    
    def _read_temp_results(self, temp_file: str) -> List[str]:
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f.readlines()]
        except Exception:
            return []
    
    def _create_final_excel_from_temp(self, original_file: str, temp_results_file: str, output_path: str) -> str:
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
            
            print("📝 Creating final Excel file...")
            all_results = self._read_temp_results(temp_results_file)
            
            source_wb = openpyxl.load_workbook(original_file, read_only=True, data_only=True)
            source_ws = source_wb.active
            
            output_wb = openpyxl.Workbook()
            output_ws = output_wb.active
            output_ws.title = "Processed_Results"
            
            header_row = next(source_ws.iter_rows(min_row=1, max_row=1, values_only=True))
            header = list(header_row) + ['Kết quả mã hóa']
            for col_idx, header_cell in enumerate(header, 1):
                cell = output_ws.cell(row=1, column=col_idx, value=str(header_cell))
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="2E86AB", end_color="2E86AB", fill_type="solid")
            
            row_count = 2
            result_idx = 0
            print(f"📝 Writing {len(all_results)} results to Excel...")
            for data_row in source_ws.iter_rows(min_row=2, values_only=True):
                if result_idx >= len(all_results):
                    break
                for col_idx, cell_value in enumerate(data_row, 1):
                    value = str(cell_value) if cell_value is not None else ""
                    output_ws.cell(row=row_count, column=col_idx, value=value)
                keylog_col = len(header)
                output_ws.cell(row=row_count, column=keylog_col, value=all_results[result_idx])
                row_count += 1
                result_idx += 1
                if row_count % 1000 == 0 and self.check_memory_limit():
                    gc.collect()
            
            source_wb.close()
            output_wb.save(output_path)
            output_wb.close()
            return output_path
        except Exception as e:
            raise Exception(f"Lỗi tạo Excel trực tiếp: {str(e)}")
    
    def validate_large_file_structure(self, file_path: str, shape_a: str, shape_b: str = None) -> Dict[str, Any]:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            columns = [str(cell) for cell in header_row if cell is not None]
            estimated_rows = max(0, (ws.max_row if hasattr(ws, 'max_row') else 0) - 1)
            wb.close()
            
            # NEW: enforce limit at validation stage
            over_limit = estimated_rows > self.max_rows_allowed
            
            required_columns_A = self._get_required_columns(shape_a, 'A')
            required_columns_B = self._get_required_columns(shape_b, 'B') if shape_b else []
            missing_columns = [col for col in (required_columns_A + required_columns_B) if col not in columns]
            
            return {
                'valid': len(missing_columns) == 0 and not over_limit,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'estimated_rows': estimated_rows,
                'columns': columns,
                'missing_columns': missing_columns,
                'recommended_chunk_size': self.estimate_optimal_chunksize(file_path),
                'max_rows_allowed': self.max_rows_allowed,
                'over_row_limit': over_limit,
                'warning': 'File vượt quá giới hạn 250,000 dòng' if over_limit else ''
            }
        except Exception as e:
            return {'valid': False, 'error': f'Lỗi kiểm tra file: {str(e)}'}
    
    def _get_required_columns(self, shape: str, group: str) -> List[str]:
        if group == 'A':
            mapping = {
                "Điểm": ["data_A"],
                "Đường thẳng": ["d_P_data_A", "d_V_data_A"],
                "Mặt phẳng": ["P1_a", "P1_b", "P1_c", "P1_d"],
                "Đường tròn": ["C_data_I1", "C_data_R1"],
                "Mặt cầu": ["S_data_I1", "S_data_R1"]
            }
        else:
            mapping = {
                "Điểm": ["data_B"],
                "Đường thẳng": ["d_P_data_B", "d_V_data_B"],
                "Mặt phẳng": ["P2_a", "P2_b", "P2_c", "P2_d"],
                "Đường tròn": ["C_data_I2", "C_data_R2"],
                "Mặt cầu": ["S_data_I2", "S_data_R2"]
            }
        return mapping.get(shape, [])
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        return {
            'memory_usage_mb': self.get_memory_usage(),
            'memory_limit_mb': self.max_memory_mb,
            'memory_usage_percent': (self.get_memory_usage() / self.max_memory_mb) * 100,
            'emergency_cleanup_triggered': self.emergency_cleanup,
            'processing_cancelled': self.processing_cancelled,
            'recommended_max_chunksize': 500 if self.get_memory_usage() > 500 else 1000,
            'max_rows_allowed': self.max_rows_allowed
        }
