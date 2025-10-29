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
    HIGH-SPEED processor for large Excel files - OPTIMIZED FOR 400+ ROWS/SEC LIKE TL!
    Features: Ultra-fast streaming, minimal overhead, TL-matching performance
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.processing_cancelled = False
        self.max_memory_mb = 1500  # Increased to 1.5GB for speed
        self.emergency_cleanup = False
        self.max_rows_allowed = 250_000
        self.fast_mode = True  # NEW: Enable high-speed mode
        
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
                f"File có {total_rows} dòng, vượt quá giới hạn tối đa {self.max_rows_allowed} dòng.\n"
                f"Vui lòng chia nhỏ file hoặc lọc bớt dữ liệu trước khi import."
            )
    
    def estimate_optimal_chunksize(self, file_path: str) -> int:
        """HIGH-SPEED chunk sizing - optimized for 400+ rows/sec like TL"""
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            
            # AGGRESSIVE chunking for maximum speed (matching TL performance)
            if file_size_mb > 100:  # Files > 100MB
                return 2000  # INCREASED from 200 to 2000 for speed
            elif file_size_mb > 50:   # 50-100MB  
                return 3000  # INCREASED from 500 to 3000
            elif file_size_mb > 20:   # 20-50MB
                return 5000  # INCREASED from 1000 to 5000
            else:
                return 10000  # INCREASED from 2000 to 10000
                
        except Exception:
            return 2000  # High-speed fallback
    
    def read_excel_streaming_fast(self, file_path: str, chunksize: int = None) -> Iterator[pd.DataFrame]:
        """
        ULTRA-HIGH-SPEED Excel streaming - targeting 400+ rows/sec like TL
        Uses optimized pandas read_excel with chunking instead of openpyxl row-by-row
        """
        if chunksize is None:
            chunksize = self.estimate_optimal_chunksize(file_path)
        
        try:
            print(f"🚀 HIGH-SPEED mode: {os.path.basename(file_path)}")
            
            # Use pandas read_excel with chunksize for maximum speed
            # This is MUCH faster than openpyxl row-by-row reading
            chunk_iter = pd.read_excel(
                file_path, 
                engine='openpyxl',  # Use openpyxl engine for .xlsx
                chunksize=chunksize,  # Read in large chunks for speed
                dtype=str,  # All columns as string to avoid parsing overhead
                na_values=[''],  # Minimal NA handling
                keep_default_na=False  # Don't convert to NaN, keep as strings
            )
            
            # Quick file info without full scan
            try:
                sample_chunk = next(chunk_iter)
                total_cols = len(sample_chunk.columns)
                print(f"📊 Using HIGH-SPEED chunked reading: {chunksize} rows/chunk")
                print(f"📈 Columns: {total_cols}")
                print(f"⚡ Target speed: 400+ rows/sec (TL-matching!)")
                
                # Yield the first chunk we already read
                yield sample_chunk.fillna('')  # Clean NaN quickly
                del sample_chunk
                
                # Continue with the rest
                chunk_count = 1
                for chunk_df in chunk_iter:
                    chunk_count += 1
                    
                    # Quick cleanup and yield
                    chunk_df = chunk_df.fillna('')  # Fast NaN cleanup
                    print(f"⚡ Chunk {chunk_count}: {len(chunk_df)} rows (HIGH-SPEED)")
                    yield chunk_df
                    
                    # Minimal cleanup - only every 10 chunks to maintain speed
                    if chunk_count % 10 == 0:
                        gc.collect()
                        print(f"🔥 Speed checkpoint {chunk_count}: Memory {self.get_memory_usage():.1f}MB")
                    
                    del chunk_df
                    
            except StopIteration:
                pass
            
            print(f"⚡ HIGH-SPEED streaming completed!")
            
        except Exception as e:
            # Fallback to safer mode if high-speed fails
            print(f"⚠️ High-speed mode failed: {e}")
            print("🔄 Falling back to safe mode...")
            yield from self.read_excel_streaming_safe(file_path, chunksize // 2)
    
    def read_excel_streaming_safe(self, file_path: str, chunksize: int) -> Iterator[pd.DataFrame]:
        """
        Safe fallback streaming when high-speed mode fails
        """
        try:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            max_row = ws.max_row
            
            header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
            columns = [str(cell) if cell is not None else f"Col_{i}" for i, cell in enumerate(header_row)]
            wb.close()
            
            current_row = 2
            chunk_count = 0
            
            while current_row <= max_row:
                try:
                    end_row = min(current_row + chunksize - 1, max_row)
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
                    
                    current_row = end_row + 1
                    chunk_count += 1
                except Exception as e:
                    print(f"⚠️ Safe mode chunk error: {e}")
                    current_row += chunksize
                    continue
                    
        except Exception as e:
            raise Exception(f"Lỗi đọc file (safe mode): {str(e)}")
    
    def process_large_excel_fast(self, file_path: str, shape_a: str, shape_b: str,
                                operation: str, dimension_a: str, dimension_b: str,
                                output_path: str, progress_callback: Callable = None) -> Tuple[int, int, str]:
        """
        HIGH-SPEED Excel processing - targeting 400+ rows/sec performance like TL
        Returns: (success_count, error_count, output_file_path)
        """
        
        self.processing_cancelled = False
        success_count = 0
        error_count = 0
        processed_count = 0
        start_time = time.time()
        
        from services.geometry.geometry_service import GeometryService
        
        try:
            print(f"🚀 HIGH-SPEED processing: {os.path.basename(file_path)}")
            
            # Quick row estimation and limit check
            total_rows = self._estimate_total_rows_fast(file_path)
            self._enforce_row_limit(total_rows)
            
            # Initialize service once (don't recreate frequently for speed)
            service = GeometryService(self.config)
            service.set_current_shapes(shape_a, shape_b)
            service.set_kich_thuoc(dimension_a, dimension_b)
            service.set_current_operation(operation)
            
            chunk_size = self.estimate_optimal_chunksize(file_path)
            print(f"⚡ HIGH-SPEED chunk size: {chunk_size} rows")
            print(f"🎯 Target: {total_rows} rows at 400+ rows/sec")
            
            # Use memory-mapped temp file for ultra-fast results buffering
            temp_results_file = f"{output_path}.temp_results"
            results_buffer = []
            buffer_size = 5000  # INCREASED buffer size for speed
            
            chunk_count = 0
            last_speed_check = time.time()
            
            # Use HIGH-SPEED streaming
            for chunk_df in self.read_excel_streaming_fast(file_path, chunk_size):
                if self.processing_cancelled:
                    break
                
                chunk_count += 1
                chunk_start = time.time()
                
                # Process entire chunk in vectorized operations when possible
                chunk_results = []
                for index, row in chunk_df.iterrows():
                    try:
                        if self.processing_cancelled:
                            break
                            
                        data_a = self._extract_shape_data_fast(row, shape_a, 'A')
                        data_b = self._extract_shape_data_fast(row, shape_b, 'B') if shape_b else {}
                        
                        # Skip service recreation for speed (only every 10k rows)
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
                
                # Batch add results to buffer
                results_buffer.extend(chunk_results)
                
                # Write buffer when full (less frequent for speed)
                if len(results_buffer) >= buffer_size:
                    self._write_results_buffer_fast(temp_results_file, results_buffer)
                    results_buffer = []
                
                # Speed calculation and progress update
                chunk_time = time.time() - chunk_start
                chunk_speed = len(chunk_df) / chunk_time if chunk_time > 0 else 0
                
                # Progress callback (less frequent for speed)
                if progress_callback and processed_count % 100 == 0:  # Every 100 rows instead of 50
                    progress = (processed_count / total_rows) * 100 if total_rows > 0 else 0
                    progress_callback(progress, processed_count, total_rows, error_count)
                
                # Speed reporting every 5 seconds
                current_time = time.time()
                if current_time - last_speed_check >= 5:
                    elapsed = current_time - start_time
                    overall_speed = processed_count / elapsed if elapsed > 0 else 0
                    print(f"🔥 Speed: {overall_speed:.0f} rows/sec | Chunk: {chunk_speed:.0f} rows/sec | Progress: {processed_count}/{total_rows}")
                    last_speed_check = current_time
                
                # Minimal memory check (every 5 chunks instead of every chunk)
                if chunk_count % 5 == 0 and self.check_memory_limit():
                    print(f"⚠️ Memory: {self.get_memory_usage():.1f}MB - Quick cleanup")
                    gc.collect()
                
                del chunk_df
            
            # Write remaining buffer
            if results_buffer:
                self._write_results_buffer_fast(temp_results_file, results_buffer)
            
            # Create final file with high-speed method
            print("🔧 HIGH-SPEED Excel assembly...")
            final_output = self._create_excel_direct_fast(file_path, temp_results_file, output_path)
            
            # Cleanup
            if os.path.exists(temp_results_file):
                os.remove(temp_results_file)
            
            # Final speed report
            total_time = time.time() - start_time
            final_speed = processed_count / total_time if total_time > 0 else 0
            print(f"🏁 COMPLETED! Final speed: {final_speed:.0f} rows/sec (Target: 400+ rows/sec)")
            print(f"📊 Total: {processed_count} rows in {total_time:.1f}s")
            print(f"✅ Success: {success_count} | ❌ Errors: {error_count}")
            
            return success_count, error_count, final_output
        
        except Exception as e:
            raise Exception(f"Lỗi xử lý HIGH-SPEED: {str(e)}")
    
    def _estimate_total_rows_fast(self, file_path: str) -> int:
        """Fast row estimation without full file scan"""
        try:
            # Quick estimation based on file size
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            estimated_rows = int(file_size_mb * 1000)  # Rough estimate: 1k rows per MB
            
            # Cap at max allowed for quick validation
            return min(estimated_rows, self.max_rows_allowed)
        except Exception:
            return 0
    
    def _extract_shape_data_fast(self, row: pd.Series, shape_type: str, group: str) -> Dict:
        """OPTIMIZED data extraction - minimal string operations"""
        data_dict = {}
        
        # Use direct access without try/except for speed
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
        """HIGH-SPEED buffer writing with minimal I/O overhead"""
        try:
            mode = 'a' if os.path.exists(temp_file) else 'w'
            with open(temp_file, mode, encoding='utf-8', buffering=8192) as f:  # Large buffer
                f.write('\n'.join(results) + '\n')  # Batch write instead of loop
        except Exception as e:
            print(f"⚠️ Warning: Fast buffer write failed: {e}")
    
    def _read_temp_results_fast(self, temp_file: str) -> List[str]:
        """HIGH-SPEED results reading"""
        try:
            with open(temp_file, 'r', encoding='utf-8', buffering=8192) as f:
                return f.read().strip().split('\n')  # Batch read and split
        except Exception:
            return []
    
    def _create_excel_direct_fast(self, original_file: str, temp_results_file: str, output_path: str) -> str:
        """HIGH-SPEED Excel creation with minimal formatting for speed"""
        try:
            import openpyxl
            
            print("⚡ HIGH-SPEED Excel creation...")
            all_results = self._read_temp_results_fast(temp_results_file)
            
            # Use pandas for faster Excel creation when possible
            try:
                # Read original file quickly
                original_df = pd.read_excel(original_file, dtype=str, keep_default_na=False)
                
                # Add results column
                original_df['Kết quả mã hóa'] = all_results[:len(original_df)]
                
                # Quick save without heavy formatting
                with pd.ExcelWriter(output_path, engine='openpyxl', options={'remove_timezone': True}) as writer:
                    original_df.to_excel(writer, sheet_name='Results', index=False)
                    
                    # Minimal formatting for speed
                    worksheet = writer.sheets['Results']
                    for col in worksheet.columns:
                        max_length = 0
                        for cell in col:
                            try:
                                if cell.value and len(str(cell.value)) > max_length:
                                    max_length = min(len(str(cell.value)), 30)  # Cap at 30 for speed
                            except:
                                pass
                        adjusted_width = max_length + 2
                        worksheet.column_dimensions[col[0].column_letter].width = adjusted_width
                
                print("⚡ HIGH-SPEED Excel creation completed!")
                return output_path
                
            except Exception as e:
                # Fallback to openpyxl method if pandas fails
                print(f"⚠️ Pandas method failed, using openpyxl: {e}")
                return self._create_excel_openpyxl_fast(original_file, all_results, output_path)
                
        except Exception as e:
            raise Exception(f"Lỗi tạo Excel HIGH-SPEED: {str(e)}")
    
    def _create_excel_openpyxl_fast(self, original_file: str, results: List[str], output_path: str) -> str:
        """Fast openpyxl fallback method"""
        try:
            import openpyxl
            
            source_wb = openpyxl.load_workbook(original_file, read_only=True, data_only=True)
            source_ws = source_wb.active
            output_wb = openpyxl.Workbook()
            output_ws = output_wb.active
            
            # Copy header quickly
            header_row = next(source_ws.iter_rows(min_row=1, max_row=1, values_only=True))
            header = list(header_row) + ['Kết quả mã hóa']
            for col_idx, header_cell in enumerate(header, 1):
                output_ws.cell(row=1, column=col_idx, value=str(header_cell))
            
            # Copy data quickly without heavy formatting
            row_count = 2
            result_idx = 0
            for data_row in source_ws.iter_rows(min_row=2, values_only=True):
                if result_idx >= len(results):
                    break
                for col_idx, cell_value in enumerate(data_row, 1):
                    output_ws.cell(row=row_count, column=col_idx, value=str(cell_value) if cell_value else "")
                output_ws.cell(row=row_count, column=len(header), value=results[result_idx])
                row_count += 1
                result_idx += 1
            
            source_wb.close()
            output_wb.save(output_path)
            output_wb.close()
            return output_path
            
        except Exception as e:
            raise Exception(f"Lỗi openpyxl fallback: {str(e)}")
    
    # Use the high-speed method as the main processing method
    def process_large_excel_safe(self, file_path: str, shape_a: str, shape_b: str,
                                operation: str, dimension_a: str, dimension_b: str,
                                output_path: str, progress_callback: Callable = None) -> Tuple[int, int, str]:
        """Main processing method - now uses HIGH-SPEED approach"""
        return self.process_large_excel_fast(file_path, shape_a, shape_b, operation, 
                                           dimension_a, dimension_b, output_path, progress_callback)
    
    def validate_large_file_structure(self, file_path: str, shape_a: str, shape_b: str = None) -> Dict[str, Any]:
        """Fast validation with minimal file reading"""
        try:
            # Quick validation using pandas header read
            header_df = pd.read_excel(file_path, nrows=0)  # Read only header
            columns = header_df.columns.tolist()
            
            # Quick file size check
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            estimated_rows = self._estimate_total_rows_fast(file_path)
            
            over_limit = estimated_rows > self.max_rows_allowed
            required_columns_A = self._get_required_columns(shape_a, 'A')
            required_columns_B = self._get_required_columns(shape_b, 'B') if shape_b else []
            missing_columns = [col for col in (required_columns_A + required_columns_B) if col not in columns]
            
            return {
                'valid': len(missing_columns) == 0 and not over_limit,
                'file_size_mb': file_size_mb,
                'estimated_rows': estimated_rows,
                'columns': columns,
                'missing_columns': missing_columns,
                'recommended_chunk_size': self.estimate_optimal_chunksize(file_path),
                'max_rows_allowed': self.max_rows_allowed,
                'over_row_limit': over_limit,
                'validation_method': 'high_speed_optimized',
                'warning': 'File vượt quá giới hạn 250,000 dòng' if over_limit else ''
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
        """Enhanced statistics with speed tracking"""
        return {
            'memory_usage_mb': self.get_memory_usage(),
            'memory_limit_mb': self.max_memory_mb,
            'memory_usage_percent': (self.get_memory_usage() / self.max_memory_mb) * 100,
            'emergency_cleanup_triggered': self.emergency_cleanup,
            'processing_cancelled': self.processing_cancelled,
            'recommended_max_chunksize': 3000 if self.get_memory_usage() > 800 else 5000,
            'max_rows_allowed': self.max_rows_allowed,
            'fast_mode_enabled': self.fast_mode,
            'target_speed_rows_per_sec': 400
        }
