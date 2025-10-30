"""Equation Template Generator - create Excel templates with 'Phương trình i' columns.
Generates sample rows including expressions like sqrt(4), sin(pi/2), etc.
"""
import pandas as pd
from typing import List

PH_COL_BASE = "Phương trình "

class EquationTemplateGenerator:
    @staticmethod
    def _columns(n_vars: int) -> List[str]:
        cols = [f"{PH_COL_BASE}{i}" for i in range(1, n_vars + 1)]
        cols += ["keylog", "solutions", "status"]
        return cols

    @staticmethod
    def _samples_2() -> List[List[str]]:
        return [
            ["2,3,7", "1,-1,1", "", "", ""],
            ["sqrt(4),pi,10", "sin(pi/2),cos(0),3", "", "", ""],
            ["1,2,5", "3,1,7", "", "", ""],
        ]

    @staticmethod
    def _samples_3() -> List[List[str]]:
        return [
            ["1,1,1,6", "2,-1,1,1", "1,2,-1,2", "", "", ""],
            ["sqrt(4),1,0,5", "0,pi,1,4", "2,2,1,3", "", "", ""],
            ["3,2,1,9", "1,3,1,7", "2,1,2,8", "", "", ""],
        ]

    @staticmethod
    def _samples_4() -> List[List[str]]:
        return [
            ["1,2,3,4,10", "2,1,0,1,5", "0,3,1,2,8", "1,1,1,1,6", "", "", ""],
            ["sqrt(4),1,0,0,5", "0,pi,1,0,4", "2,2,1,1,3", "1,0,1,0,2", "", "", ""],
            ["3,2,1,0,9", "1,3,1,0,7", "2,1,2,1,8", "0,0,1,1,3", "", "", ""],
        ]

    @classmethod
    def create_template(cls, n_vars: int, output_path: str) -> str:
        if n_vars not in (2,3,4):
            raise ValueError("Only 2,3,4 variables supported")
        cols = cls._columns(n_vars)
        if n_vars == 2:
            data = cls._samples_2()
        elif n_vars == 3:
            data = cls._samples_3()
        else:
            data = cls._samples_4()
        df = pd.DataFrame(data, columns=cols)
        df.to_excel(output_path, index=False)
        return output_path
