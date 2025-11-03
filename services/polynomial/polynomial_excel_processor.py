"""Polynomial Excel Processor - Batch import, process and export results
Reads Input sheet with required columns by degree (a..c|d|e), uses PolynomialService to solve,
then exports a Results sheet with full information.
"""
from typing import List, Dict, Any, Tuple
import pandas as pd
from datetime import datetime

from .polynomial_service import PolynomialService

REQUIRED_COLS = {
    2: ["a", "b", "c"],
    3: ["a", "b", "c", "d"],
    4: ["a", "b", "c", "d", "e"],
}

OPTIONAL_COLS = ["version", "method", "precision"]

class PolynomialExcelProcessor:
    def __init__(self, degree: int, default_version: str = "fx799"):
        if degree not in [2,3,4]:
            raise ValueError("Degree must be 2, 3, or 4")
        self.degree = degree
        self.default_version = default_version
        self.service = PolynomialService()
        self.service.set_degree(degree)

    def read_input(self, file_path: str) -> pd.DataFrame:
        df = pd.read_excel(file_path, sheet_name="Input")
        # Normalize columns to lower
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Validate required columns
        missing = [c for c in REQUIRED_COLS[self.degree] if c not in df.columns]
        if missing:
            raise ValueError(f"Input sheet missing required columns for degree {self.degree}: {missing}")
        return df

    def _row_to_coeffs(self, row: pd.Series) -> List[str]:
        cols = REQUIRED_COLS[self.degree]
        return [str(row.get(c, "")).strip() for c in cols]

    def _apply_row_options(self, row: pd.Series):
        # Version
        version = str(row.get("version", self.default_version)).strip() or self.default_version
        self.service.set_version(version)
        # Method
        method = str(row.get("method", self.service.solver.method)).strip()
        if method in ["numpy", "analytical"]:
            self.service.set_solver_method(method)
        # Precision
        try:
            precision_val = row.get("precision", self.service.solver.precision)
            if pd.notna(precision_val):
                self.service.set_precision(int(precision_val))
        except Exception:
            pass

    def process_batch(self, file_path: str) -> pd.DataFrame:
        df = self.read_input(file_path)
        results: List[Dict[str, Any]] = []

        for idx, row in df.iterrows():
            try:
                self._apply_row_options(row)
                coeffs = self._row_to_coeffs(row)
                success, msg, roots_display, final_keylog = self.service.process_complete_workflow(coeffs)

                result_item = {
                    "Row_Index": idx + 1,
                    "Degree": self.degree,
                    "Version": self.service.version,
                    "Method": self.service.solver.method,
                    "Precision": self.service.solver.precision,
                    # coefficients
                    "a": row.get("a", ""),
                    "b": row.get("b", ""),
                    "c": row.get("c", ""),
                    "d": row.get("d", "") if self.degree >= 3 else "",
                    "e": row.get("e", "") if self.degree >= 4 else "",
                    # encoded + outputs
                    "Encoded_Coefficients": " | ".join(self.service.get_last_encoded_coefficients()) if success else "",
                    "Roots_Solution": roots_display.replace("\n", " | ") if success else "",
                    "Compact_Display": self.service.get_last_compact_display() if success else "",
                    "Final_Keylog": final_keylog if success else "",
                    "Real_Roots_Count": len(self.service.get_real_roots_only()) if success else 0,
                    "Status": "Success" if success else "Failed",
                    "Message": msg if not success else "",
                }
                results.append(result_item)
            except Exception as e:
                results.append({
                    "Row_Index": idx + 1,
                    "Degree": self.degree,
                    "Status": "Failed",
                    "Message": str(e)
                })
        return pd.DataFrame(results)

    def export_results(self, results_df: pd.DataFrame, output_path: str, meta: Dict[str, Any] = None):
        meta = meta or {}
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            results_df.to_excel(writer, index=False, sheet_name="Results")
            # Metadata sheet
            meta_df = pd.DataFrame([{
                "Degree": self.degree,
                "Default_Version": self.default_version,
                "Processed_At": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                **meta
            }])
            meta_df.to_excel(writer, index=False, sheet_name="Metadata")
