"""Equation Batch Processor - Import/Process/Export for Equation Mode
Format: Columns 'Phương trình 1'..'Phương trình n' where each cell is comma-separated coefficients.
Auto-fills missing coefficients with 0 to length n+1 per row.
"""
from typing import List, Dict
import pandas as pd
import os

from services.equation.equation_service import EquationService

PH_COL_BASE = "Phương trình "

class EquationBatchProcessor:
    def __init__(self):
        self.service = EquationService()

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
