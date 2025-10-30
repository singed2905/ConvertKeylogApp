"""Equation Batch Processor - Import/Process/Export for Equation Mode
Enhanced with large file handling: size check, chunked processing, and memory-safe writing.
"""
from typing import List, Dict
import pandas as pd
import os
import gc
import warnings

from services.equation.equation_service import EquationService

PH_COL_BASE = "Phương trình "

class EquationBatchProcessor:
    def __init__(self):
        self.service = EquationService()
        # Tuning params
        self.chunk_size = 1000  # rows per chunk when large file
        self.large_file_mb = 100  # threshold to switch to chunked mode
        self.memory_warn_mb = 1000  # show warning if memory exceeds (MB)

    # ================== Helpers ==================
    def _normalize_equation_cell(self, cell: str, needed_len: int) -> str:
        """Ensure a cell string has at least needed_len comma-separated parts, pad with 0."""
        if cell is None:
            parts = []
        else:
            text = str(cell).strip()
            parts = [p.strip() for p in text.split(',')] if text else []
        if len(parts) < needed_len:
            parts.extend(["0"] * (needed_len - len(parts)))
        # Join exactly needed_len
        return ",".join(parts[:needed_len])

    def _build_inputs_from_row(self, row: pd.Series, n_vars: int) -> List[str]:
        needed_len = n_vars + 1
        inputs: List[str] = []
        for i in range(1, n_vars + 1):
            col = f"{PH_COL_BASE}{i}"
            inputs.append(self._normalize_equation_cell(row.get(col, ""), needed_len))
        return inputs

    def _get_current_memory_mb(self) -> float:
        try:
            import psutil
            p = psutil.Process()
            return p.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

    # ================== Core small/medium file ==================
    def process_dataframe(self, df: pd.DataFrame, variables: int, version: str) -> pd.DataFrame:
        out_rows: List[Dict] = []
        self.service.set_variables_count(variables)
        self.service.set_version(version)

        for _, row in df.iterrows():
            try:
                equation_inputs = self._build_inputs_from_row(row, variables)
                ok, status, solutions, keylog = self.service.process_complete_workflow(equation_inputs)
                out_rows.append({
                    **row.to_dict(),
                    "solutions": solutions,
                    "keylog": keylog if ok else "",
                    "status": "Thành công" if ok else "Lỗi",
                    "error_message": "" if ok else status
                })
            except Exception as e:
                out_rows.append({
                    **row.to_dict(),
                    "solutions": "",
                    "keylog": "",
                    "status": "Lỗi",
                    "error_message": str(e)
                })
        return pd.DataFrame(out_rows)

    def process_file(self, input_path: str, variables: int, version: str, output_path: str = "") -> str:
        df = pd.read_excel(input_path)
        result_df = self.process_dataframe(df, variables, version)
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = base + "_output.xlsx"
        result_df.to_excel(output_path, index=False)
        return output_path

    # ================== Large file path ==================
    def process_file_smart(self, input_path: str, variables: int, version: str, output_path: str = "") -> str:
        """Smart processing: choose standard or chunked based on file size."""
        try:
            size_mb = os.path.getsize(input_path) / (1024 * 1024)
        except Exception:
            size_mb = 0
        if size_mb < self.large_file_mb:
            return self.process_file(input_path, variables, version, output_path)
        return self.process_file_chunked(input_path, variables, version, output_path)

    def process_file_chunked(self, input_path: str, variables: int, version: str, output_path: str = "") -> str:
        """Process large Excel by chunks to reduce memory footprint."""
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = base + "_large_output.xlsx"

        # Setup service
        self.service.set_variables_count(variables)
        self.service.set_version(version)

        # Prepare writer (xlsxwriter is generally memory-efficient for writes)
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter', options={'strings_to_numbers': True})
        processed = 0
        first_chunk = True

        try:
            # Use dtype=str to avoid heavy type inference, engine explicit
            chunk_iter = pd.read_excel(input_path, chunksize=self.chunk_size, engine='openpyxl', dtype=str)
            for chunk in chunk_iter:
                out_rows: List[Dict] = []
                for _, row in chunk.iterrows():
                    try:
                        eq_inputs = self._build_inputs_from_row(row, variables)
                        ok, status, solutions, keylog = self.service.process_complete_workflow(eq_inputs)
                        out_rows.append({
                            **row.to_dict(),
                            "solutions": solutions,
                            "keylog": keylog if ok else "",
                            "status": "Thành công" if ok else "Lỗi",
                            "error_message": "" if ok else status
                        })
                    except Exception as e:
                        out_rows.append({
                            **row.to_dict(),
                            "solutions": "",
                            "keylog": "",
                            "status": "Lỗi",
                            "error_message": str(e)
                        })

                result_chunk = pd.DataFrame(out_rows)
                # Write out incrementally
                result_chunk.to_excel(writer, sheet_name='Results', startrow=processed if not first_chunk else 0, header=first_chunk, index=False)
                processed += len(result_chunk)
                first_chunk = False

                # Cleanup memory between chunks
                del chunk, out_rows, result_chunk
                gc.collect()

                # Soft memory warning
                mem_mb = self._get_current_memory_mb()
                if mem_mb > self.memory_warn_mb:
                    warnings.warn(f"High memory usage: {mem_mb:.0f}MB while processing chunks")
        finally:
            writer.close()

        return output_path
