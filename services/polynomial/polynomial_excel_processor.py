from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import os

from .polynomial_service import PolynomialService
from .polynomial_excel_config_loader import get_required_columns_for_degree
from .roots_formatting import simplify_roots_text

class PolynomialExcelProcessor:
    def __init__(self, degree: int, default_version: str = "fx799"):
        if degree not in [2,3,4]:
            raise ValueError("Degree must be 2, 3, or 4")
        self.degree = degree
        self.default_version = default_version
        self.service = PolynomialService()
        self.service.set_degree(degree)
        self.service.set_version(default_version)

    def _resolve_input_sheet(self, xl: pd.ExcelFile) -> str:
        candidates = ["Input", "input", "INPUT", "Sheet1", "Data", "Sheet"]
        sheets_lower = {s.lower(): s for s in xl.sheet_names}
        for name in candidates:
            if name.lower() in sheets_lower:
                return sheets_lower[name.lower()]
        return xl.sheet_names[0]

    def read_input(self, file_path: str) -> pd.DataFrame:
        xl = pd.ExcelFile(file_path)
        sheet_name = self._resolve_input_sheet(xl)
        df = xl.parse(sheet_name)
        df.columns = [str(c).strip().lower() for c in df.columns]
        required = get_required_columns_for_degree(self.degree)
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Input sheet missing required columns for degree {self.degree}: {missing}")
        return df

    def process_batch(self, file_path: str) -> pd.DataFrame:
        df = self.read_input(file_path).copy()
        required = get_required_columns_for_degree(self.degree)
        for col in ["keylog", "roots", "real_roots_count", "status", "message"]:
            if col not in df.columns:
                df[col] = ""
        for idx, row in df.iterrows():
            try:
                coeffs = [str(row[c]) if pd.notna(row[c]) else "" for c in required]
                is_valid, msg = self.service.validate_input(coeffs)
                if not is_valid:
                    df.at[idx, "status"] = "invalid"; df.at[idx, "message"] = msg
                    df.at[idx, "keylog"] = ""; df.at[idx, "roots"] = ""; df.at[idx, "real_roots_count"] = 0
                    continue
                success, status_msg, roots_display, final_keylog = self.service.process_complete_workflow(coeffs)
                if success:
                    df.at[idx, "keylog"] = final_keylog
                    df.at[idx, "roots"] = simplify_roots_text(roots_display)
                    df.at[idx, "real_roots_count"] = len(self.service.get_real_roots_only())
                    df.at[idx, "status"] = "ok"; df.at[idx, "message"] = status_msg or ""
                else:
                    df.at[idx, "status"] = "error"; df.at[idx, "message"] = status_msg
            except Exception as e:
                df.at[idx, "status"] = "error"; df.at[idx, "message"] = str(e)
        return df

    def export_results(self, updated_df: pd.DataFrame, output_path: str, meta: Dict[str, Any] | None = None) -> str:
        meta = meta or {}
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            updated_df.to_excel(writer, sheet_name='Input', index=False)
            md = {'degree':[self.degree], 'default_version':[self.default_version], 'timestamp':[datetime.now().strftime('%Y-%m-%d %H:%M:%S')]}
            for k,v in meta.items(): md[k] = [v]
            pd.DataFrame(md).to_excel(writer, sheet_name='Metadata', index=False)
        return output_path
