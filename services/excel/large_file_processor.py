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
    OPTIMIZED HIGH-SPEED processor for large Excel files - Phương án A
    Features: Single-workbook streaming, 400+ rows/sec, TL-matching performance
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.processing_cancelled = False
        self.max_memory_mb = 1500  # 1.5GB for speed
        self.emergency_cleanup = False
        self.max_rows_allowed = 250_000
        self.fast_mode = True
        
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
        
    def _enforce_row_limit(self, total_rows: int):
        """Raise if total rows exceed the allowed hard limit"""
        if total_rows > self.max_rows_allowed:
            raise Exception(
                f"File có {total_rows:,} dòng, vượt quá giới hạn tối đa {self.max_rows_allowed:,} dòng.\n"
                f"Vui lòng chia nhỏ file hoặc lọc bớt dữ liệu trước khi import."
            )
    
    def estimate_optimal_chunksize(self, file_path: str) -> int:
        """HIGH-SPEED chunk sizing for Phương án A - optimized for single-workbook streaming"""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # OPTIMIZED chunk sizes for single-workbook streaming
            if file_size_mb > 100:    # Files > 100MB
                return 3000  # Large but manageable for memory
            elif file_size_mb > 50:   # 50-100MB (like user's 45.9MB file)  
                return 5000  # Optimal for 45MB+ files
            elif file_size_mb > 20:   # 20-50MB
                return 7000  # Aggressive for medium files
            else:
                return 10000  # Maximum speed for small files
                
        except Exception:
            return 5000  # Optimized fallback
    
    def _get_actual_total_rows(self, file_path: str) -> int:
        """Get ACTUAL total rows by reading file header info"""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            actual_total = max(0, (ws.max_row - 1)) if hasattr(ws, 'max_row') and ws.max_row else 0
            wb.close()
            print(f"📊 Actual file dimensions: {actual_total:,} data rows")
            return actual_total
        except Exception as e:
            print(f"⚠️ Could not get actual rows: {e}")
            return 0
    
    def read_excel_streaming_single_workbook(self, file_path: str, chunksize: int = None) -> Iterator[pd.DataFrame]:
        """
        PHƯƠNG ÁN A: Single-workbook streaming for maximum I/O efficiency
        Mở workbook 1 lần duy nhất, stream theo chunk, đóng 1 lần cuối
        """
        if chunksize is None:
            chunksize = self.estimate_optimal_chunksize(file_path)
        
        try:
            import openpyxl
            print(f"🚀 PHƯƠNG ÁN A: Single-workbook streaming")
            print(f"📁 File: {os.path.basename(file_path)}")
            
            # MỞ WORKBOOK 1 LẦN DUY NHẤT
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            
            # Lấy thông tin file
            max_row = ws.max_row if hasattr(ws, 'max_row') and ws.max_row else 0
            max_col = ws.max_column if hasattr(ws, 'max_column') else 0
            total_rows = max(0, max_row - 1)  # Exclude header
            
            # Enforce row limit
            self._enforce_row_limit(total_rows)
            
            print(f"📊 Dimensions: {total_rows:,} rows × {max_col} columns")
            print(f"⚡ Chunk size: {chunksize:,} rows")
            print(f"📦 Estimated chunks: {(total_rows + chunksize - 1) // chunksize}")
            
            # Đọc header 1 lần
            try:
                header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
                columns = [str(cell) if cell is not None else f"Col_{i}" 
                          for i, cell in enumerate(header_row)]
            except Exception:
                # Fallback if no header
                columns = [f"Col_{i}" for i in range(max_col)]
            
            # STREAM THEO CHUNK - KHÔNG ĐÓNG WORKBOOK
            current_row = 2  # Start from row 2 (after header)
            chunk_count = 0
            
            while current_row <= max_row and not self.processing_cancelled:
                try:
                    end_row = min(current_row + chunksize - 1, max_row)
                    
                    print(f"⚡ Reading chunk {chunk_count + 1}: rows {current_row:,}-{end_row:,}")
                    
                    # ĐỌC VÙNG KHÔNG ĐÓNG WORKBOOK
                    chunk_data = []
                    for row in ws.iter_rows(min_row=current_row, max_row=end_row, values_only=True):
                        row_data = [str(cell) if cell is not None else "" for cell in row]
                        chunk_data.append(row_data)
                    
                    if chunk_data:
                        chunk_df = pd.DataFrame(chunk_data, columns=columns)
                        chunk_df = chunk_df.fillna('')  # Clean and fast
                        yield chunk_df
                        del chunk_df, chunk_data
                        
                        # Minimal cleanup (every 10 chunks for speed)
                        if chunk_count % 10 == 0 and chunk_count > 0:
                            gc.collect()
                            print(f"🧹 Cleanup checkpoint: Memory {self.get_memory_usage():.1f}MB")
                    
                    current_row = end_row + 1
                    chunk_count += 1
                    
                except Exception as e:
                    print(f"❌ Error reading chunk {chunk_count + 1}: {e}")
                    current_row += chunksize  # Skip problematic chunk
                    continue
            
            # ĐÓNG WORKBOOK 1 LẦN CUỐI
            wb.close()
            print(f"✅ Single-workbook streaming completed: {chunk_count} chunks")
            
        except Exception as e:
            raise Exception(f"Lỗi streaming single-workbook: {str(e)}")
    
    def process_large_excel_fast(self, file_path: str, shape_a: str, shape_b: str,
                                operation: str, dimension_a: str, dimension_b: str,
                                output_path: str, progress_callback: Callable = None) -> Tuple[int, int, str]:
        """
        PHƯƠNG ÁN A: High-speed processing với single-workbook streaming
        Target: 400+ rows/sec matching TL performance
        """
        
        self.processing_cancelled = False
        success_count = 0
        error_count = 0
        processed_count = 0
        start_time = time.time()
        
        from services.geometry.geometry_service import GeometryService
        
        try:
            print(f"🚀 PHƯƠNG ÁN A - HIGH-SPEED processing: {os.path.basename(file_path)}")
            
            # Get ACTUAL total rows (not estimation)
            total_rows = self._get_actual_total_rows(file_path)
            self._enforce_row_limit(total_rows)
            
            # Initialize service once
            service = GeometryService(self.config)
            service.set_current_shapes(shape_a, shape_b)
            service.set_kich_thuoc(dimension_a, dimension_b)
            service.set_current_operation(operation)
            
            chunk_size = self.estimate_optimal_chunksize(file_path)
            print(f"⚡ Optimized chunk size: {chunk_size:,} rows")
            print(f"🎯 Target: {total_rows:,} rows at 400+ rows/sec")
            
            # Results buffering
            temp_results_file = f"{output_path}.temp_results"
            results_buffer = []
            buffer_size = 5000  # Large buffer for speed
            
            chunk_count = 0
            last_speed_check = time.time()
            last_eta_update = time.time()
            
            # Use SINGLE-WORKBOOK streaming
            for chunk_df in self.read_excel_streaming_single_workbook(file_path, chunk_size):
                if self.processing_cancelled:
                    break
                
                chunk_count += 1
                chunk_start = time.time()
                
                # Process chunk
                chunk_results = []
                for index, row in chunk_df.iterrows():
                    try:
                        if self.processing_cancelled:
                            break
                            
                        data_a = self._extract_shape_data_fast(row, shape_a, 'A')
                        data_b = self._extract_shape_data_fast(row, shape_b, 'B') if shape_b else {}
                        
                        # Service recreation only every 10k rows for speed
                        if processed_count % 10000 == 0 and processed_count > 0:
                            service = GeometryService(self.config)
                            service.set_current_shapes(shape_a, shape_b)
                            service.set_kich_thuoc(dimension_a, dimension_b)
                            service.set_current_operation(operation)
                        
                        service.thuc_thi_tat_ca(data_a, data_b)
                        result = service.generate_final_result()
                        chunk_results.append(result)
                        success_count += 1
                        
                    except Exception as e:
                        chunk_results.append(f"LỖI: {str(e)}")
                        error_count += 1
                    
                    processed_count += 1
                
                # Add results to buffer
                results_buffer.extend(chunk_results)
                
                # Write buffer when full (less frequent for speed)
                if len(results_buffer) >= buffer_size:
                    self._write_results_buffer_fast(temp_results_file, results_buffer)
                    results_buffer = []
                
                # Calculate speeds
                chunk_time = time.time() - chunk_start
                chunk_speed = len(chunk_df) / chunk_time if chunk_time >= 0.5 else None  # Only if meaningful
                
                current_time = time.time()
                elapsed = current_time - start_time
                avg_speed = processed_count / elapsed if elapsed > 0 else 0
                
                # Progress callback (every 100 rows for balance of accuracy vs speed)
                if progress_callback and processed_count % 100 == 0:
                    processed_display = min(processed_count, total_rows)  # Clamp progress
                    progress_percent = (processed_display / total_rows) * 100 if total_rows > 0 else 0
                    progress_callback(progress_percent, processed_display, total_rows, error_count)
                
                # Speed reporting every 5 seconds with ETA
                if current_time - last_speed_check >= 5:
                    processed_display = min(processed_count, total_rows)
                    progress_percent = (processed_display / total_rows) * 100 if total_rows > 0 else 0
                    
                    # Calculate ETA
                    remaining_rows = total_rows - processed_display
                    eta_seconds = remaining_rows / max(avg_speed, 1e-6) if remaining_rows > 0 else 0
                    eta_minutes = int(eta_seconds // 60)
                    eta_secs = int(eta_seconds % 60)
                    eta_str = f"{eta_minutes:02d}:{eta_secs:02d}"
                    
                    # Format speed display
                    if chunk_speed is not None:
                        speed_display = f"🔥 Speed: {avg_speed:.0f} rows/sec (avg) | {chunk_speed:.0f} rows/sec (current)"
                    else:
                        speed_display = f"🔥 Speed: {avg_speed:.0f} rows/sec (avg)"
                    
                    print(f"{speed_display} | Progress: {processed_display:,}/{total_rows:,} ({progress_percent:.1f}%) | ETA: {eta_str}")
                    last_speed_check = current_time
                
                # Memory check every 5 chunks for speed
                if chunk_count % 5 == 0 and self.check_memory_limit():
                    print(f"⚠️ Memory: {self.get_memory_usage():.1f}MB - Quick cleanup")
                    gc.collect()
                
                del chunk_df
            
            # Write remaining buffer
            if results_buffer:
                self._write_results_buffer_fast(temp_results_file, results_buffer)
            
            # Create final Excel file
            print("🔧 Creating final Excel file with high-speed method...")
            final_output = self._create_excel_direct_fast(file_path, temp_results_file, output_path)
            
            # Cleanup temp file
            if os.path.exists(temp_results_file):
                os.remove(temp_results_file)
            
            # Final speed report
            total_time = time.time() - start_time
            final_speed = processed_count / total_time if total_time > 0 else 0
            
            print(f"🏁 PHƯƠNG ÁN A COMPLETED!")
            print(f"⚡ Final speed: {final_speed:.0f} rows/sec (Target: 400+ rows/sec)")
            print(f"📊 Total: {processed_count:,} rows in {total_time:.1f}s")
            print(f"✅ Success: {success_count:,} | ❌ Errors: {error_count:,}")
            
            # Performance assessment
            if final_speed >= 400:
                print(f"🎉 PERFORMANCE TARGET ACHIEVED! ({final_speed:.0f} ≥ 400 rows/sec)")
            elif final_speed >= 300:
                print(f"✅ GOOD PERFORMANCE! ({final_speed:.0f} rows/sec, close to target)")
            else:
                print(f"⚠️ Below target speed. Consider SSD, more RAM, or smaller chunks.")
            
            return success_count, error_count, final_output
        
        except Exception as e:
            raise Exception(f"Lỗi xử lý PHƯƠNG ÁN A: {str(e)}")
    
    def _extract_shape_data_fast(self, row: pd.Series, shape_type: str, group: str) -> Dict:
        """OPTIMIZED data extraction - minimal string operations"""
        data_dict = {}
        
        if not shape_type:
            return data_dict
        
        # Direct access for speed (no try/except overhead)
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
    
    def _write_results_buffer_fast(self, temp_file: str, results: List[str]):
        """HIGH-SPEED buffer writing with large I/O buffer"""
        try:
            mode = 'a' if os.path.exists(temp_file) else 'w'
            with open(temp_file, mode, encoding='utf-8', buffering=16384) as f:  # 16KB buffer
                f.write('\n'.join(results) + '\n')  # Batch write
        except Exception as e:
            print(f"⚠️ Warning: Fast buffer write failed: {e}")
    
    def _read_temp_results_fast(self, temp_file: str) -> List[str]:
        """HIGH-SPEED results reading"""
        try:
            with open(temp_file, 'r', encoding='utf-8', buffering=16384) as f:
                return f.read().strip().split('\n')  # Batch read and split
        except Exception:
            return []
    
    def _create_excel_direct_fast(self, original_file: str, temp_results_file: str, output_path: str) -> str:
        """HIGH-SPEED Excel creation - optimized for large files"""
        try:
            print("⚡ HIGH-SPEED Excel assembly...")
            all_results = self._read_temp_results_fast(temp_results_file)
            
            # Try pandas approach first (fastest for large files)
            try:
                original_df = pd.read_excel(original_file, dtype=str, keep_default_na=False, engine='openpyxl')
                
                # Ensure results match data rows
                results_to_add = all_results[:len(original_df)]
                if len(results_to_add) < len(original_df):
                    results_to_add.extend([''] * (len(original_df) - len(results_to_add)))
                
                original_df['Kết quả mã hóa'] = results_to_add
                
                # High-speed save
                with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                    original_df.to_excel(writer, sheet_name='Results', index=False)
                    
                    # Minimal auto-width for readability
                    worksheet = writer.sheets['Results']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if cell.value and len(str(cell.value)) > max_length:
                                    max_length = min(len(str(cell.value)), 40)  # Cap for speed
                            except:
                                pass
                        worksheet.column_dimensions[column_letter].width = max(max_length + 2, 10)
                
                print("✅ HIGH-SPEED Excel creation completed!")
                return output_path
                
            except Exception as pandas_error:
                print(f"⚠️ Pandas method failed: {pandas_error}")
                return self._create_excel_openpyxl_fast(original_file, all_results, output_path)
                
        except Exception as e:
            raise Exception(f"Lỗi tạo Excel HIGH-SPEED: {str(e)}")
    
    def _create_excel_openpyxl_fast(self, original_file: str, results: List[str], output_path: str) -> str:
        """Fast openpyxl fallback method"""
        try:
            import openpyxl
            
            print("🔄 Using openpyxl fast method...")
            source_wb = openpyxl.load_workbook(original_file, read_only=True, data_only=True)
            source_ws = source_wb.active
            output_wb = openpyxl.Workbook()
            output_ws = output_wb.active
            output_ws.title = "Results"
            
            # Copy header
            header_row = next(source_ws.iter_rows(min_row=1, max_row=1, values_only=True))
            header = list(header_row) + ['Kết quả mã hóa']
            for col_idx, header_cell in enumerate(header, 1):
                output_ws.cell(row=1, column=col_idx, value=str(header_cell) if header_cell else "")
            
            # Copy data with results (fast, minimal formatting)
            row_count = 2
            result_idx = 0
            for data_row in source_ws.iter_rows(min_row=2, values_only=True):
                if result_idx >= len(results):
                    break
                    
                # Copy original data
                for col_idx, cell_value in enumerate(data_row, 1):
                    value = str(cell_value) if cell_value is not None else ""
                    output_ws.cell(row=row_count, column=col_idx, value=value)
                
                # Add result
                output_ws.cell(row=row_count, column=len(header), value=results[result_idx])
                
                row_count += 1
                result_idx += 1
                
                # Periodic memory cleanup
                if row_count % 5000 == 0:
                    gc.collect()
            
            source_wb.close()
            output_wb.save(output_path)
            output_wb.close()
            
            print("✅ Openpyxl fast method completed!")
            return output_path
            
        except Exception as e:
            raise Exception(f"Lỗi openpyxl fast fallback: {str(e)}")
    
    # Use high-speed method as main method
    def process_large_excel_safe(self, file_path: str, shape_a: str, shape_b: str,
                                operation: str, dimension_a: str, dimension_b: str,
                                output_path: str, progress_callback: Callable = None) -> Tuple[int, int, str]:
        """Main processing method - now uses PHƯƠNG ÁN A approach"""
        return self.process_large_excel_fast(file_path, shape_a, shape_b, operation, 
                                           dimension_a, dimension_b, output_path, progress_callback)
    
    def validate_large_file_structure(self, file_path: str, shape_a: str, shape_b: str = None) -> Dict[str, Any]:
        """Fast validation with actual row counting"""
        try:
            # Get actual file info
            actual_rows = self._get_actual_total_rows(file_path)
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # Quick header check
            header_df = pd.read_excel(file_path, nrows=0, engine='openpyxl')
            columns = header_df.columns.tolist()
            
            over_limit = actual_rows > self.max_rows_allowed
            required_columns_A = self._get_required_columns(shape_a, 'A')
            required_columns_B = self._get_required_columns(shape_b, 'B') if shape_b else []
            missing_columns = [col for col in (required_columns_A + required_columns_B) if col not in columns]
            
            return {
                'valid': len(missing_columns) == 0 and not over_limit,
                'file_size_mb': file_size_mb,
                'actual_rows': actual_rows,  # Use actual instead of estimated
                'columns': columns,
                'missing_columns': missing_columns,
                'recommended_chunk_size': self.estimate_optimal_chunksize(file_path),
                'max_rows_allowed': self.max_rows_allowed,
                'over_row_limit': over_limit,
                'validation_method': 'phương_án_A_optimized',
                'warning': f'File vượt quá giới hạn {self.max_rows_allowed:,} dòng' if over_limit else ''
            }
        except Exception as e:
            return {'valid': False, 'error': f'Lỗi kiểm tra file: {str(e)}'}
    
    def _get_required_columns(self, shape: str, group: str) -> List[str]:
        """Get required columns mapping"""
        if not shape:
            return []
            
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
        """Enhanced statistics for PHƯƠNG ÁN A"""
        return {
            'memory_usage_mb': self.get_memory_usage(),
            'memory_limit_mb': self.max_memory_mb,
            'memory_usage_percent': (self.get_memory_usage() / self.max_memory_mb) * 100,
            'emergency_cleanup_triggered': self.emergency_cleanup,
            'processing_cancelled': self.processing_cancelled,
            'recommended_max_chunksize': 5000 if self.get_memory_usage() > 800 else 7000,
            'max_rows_allowed': self.max_rows_allowed,
            'processing_method': 'phương_án_A_single_workbook_streaming',
            'target_speed_rows_per_sec': 400,
            'optimizations': ['single_workbook_open', 'large_chunks', 'minimal_gc', 'batch_io']
        }