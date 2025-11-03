from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import os

from .polynomial_service import PolynomialService
from .polynomial_excel_config_loader import get_required_columns_for_degree

class PolynomialExcelProcessor:
    """Process imported Excel and write results back into original file (append columns)."""
    def __init__(self, degree: int, default_version: str = "fx799"):
        if degree not in [2,3,4]:
            raise ValueError("Degree must be 2, 3, or 4")
        self.degree = degree
        self.default_version = default_version
        self.service = PolynomialService()
        self.service.set_degree(degree)
        self.service.set_version(default_version)

    def read_input(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path, sheet_name="Input")
        df.columns = [str(c).strip().lower() for c in df.columns]
        required = get_required_columns_for_degree(self.degree)
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Input sheet missing required columns for degree {self.degree}: {missing}")
        return df

    def process_batch(self, file_path: str) -> pd.DataFrame:
        df = self.read_input(file_path).copy()
        required = get_required_columns_for_degree(self.degree)
        # Ensure output columns exist (will fill later)
        out_cols = ["keylog", "roots", "real_roots_count", "status", "message"]
        for col in out_cols:
            if col not in df.columns:
                df[col] = ""
        # Process each row
        results = []
        for idx, row in df.iterrows():
            try:
                coeffs = [str(row[c]) if pd.notna(row[c]) else "" for c in required]
                is_valid, msg = self.service.validate_input(coeffs)
                if not is_valid:
                    df.at[idx, "status"] = "invalid"
                    df.at[idx, "message"] = msg
                    df.at[idx, "keylog"] = ""
                    df.at[idx, "roots"] = ""
                    df.at[idx, "real_roots_count"] = 0
                    continue
                success, status_msg, roots_display, final_keylog = self.service.process_complete_workflow(coeffs)
                if success:
                    df.at[idx, "keylog"] = final_keylog
                    df.at[idx, "roots"] = roots_display.replace("\n", " | ")
                    df.at[idx, "real_roots_count"] = len(self.service.get_real_roots_only())
                    df.at[idx, "status"] = "ok"
                    df.at[idx, "message"] = status_msg or ""
                else:
                    df.at[idx, "status"] = "error"
                    df.at[idx, "message"] = status_msg
            except Exception as e:
                df.at[idx, "status"] = "error"
                df.at[idx, "message"] = str(e)
        return df

    def export_results(self, updated_df: pd.DataFrame, output_path: str, meta: Dict[str, Any] | None = None) -> str:
        """Write the updated Input sheet (with appended columns) back to Excel.
        - Reuse the same Input sheet with extra columns
        - Add a Metadata sheet for audit
        """
        meta = meta or {}
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            updated_df.to_excel(writer, sheet_name='Input', index=False)
            # Metadata
            md = {
                'degree': [self.degree],
                'default_version': [self.default_version],
                'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            }
            for k,v in meta.items():
                md[k] = [v]
            pd.DataFrame(md).to_excel(writer, sheet_name='Metadata', index=False)
        return output_path
