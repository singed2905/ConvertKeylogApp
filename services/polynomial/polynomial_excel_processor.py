"""Update PolynomialExcelProcessor to read required columns from JSON config"""
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime

from .polynomial_service import PolynomialService
from .polynomial_excel_config_loader import get_required_columns_for_degree

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
        df.columns = [str(c).strip().lower() for c in df.columns]
        required = get_required_columns_for_degree(self.degree)
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Input sheet missing required columns for degree {self.degree}: {missing}")
        return df

    # ... rest of the original implementation remains unchanged ...
