"""Equation Excel actions wiring for quick manual run (CLI).
This is a helper script to quickly generate templates and process files without UI.
"""
import sys
import os

# Allow local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.equation.equation_template_generator import EquationTemplateGenerator
from services.equation.equation_batch_processor import EquationBatchProcessor


def create_template(n_vars: int, output_path: str):
    path = EquationTemplateGenerator.create_template(n_vars, output_path)
    print(f"Template created: {path}")


def process_file(input_path: str, n_vars: int, version: str = "fx799", output_path: str = ""):
    processor = EquationBatchProcessor()
    out = processor.process_file(input_path, n_vars, version, output_path)
    print(f"Processed -> {out}")


if __name__ == "__main__":
    # Usage examples:
    # python equation_excel_cli.py template 2 equation_template_2x2.xlsx
    # python equation_excel_cli.py run input.xlsx 3 fx799 output.xlsx
    if len(sys.argv) < 2:
        print("Usage:\n  template <n_vars> <output.xlsx>\n  run <input.xlsx> <n_vars> [version] [output.xlsx]")
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "template":
        if len(sys.argv) < 4:
            print("template <n_vars> <output.xlsx>")
            sys.exit(1)
        n_vars = int(sys.argv[2])
        output = sys.argv[3]
        create_template(n_vars, output)
    elif cmd == "run":
        if len(sys.argv) < 4:
            print("run <input.xlsx> <n_vars> [version] [output.xlsx]")
            sys.exit(1)
        input_path = sys.argv[2]
        n_vars = int(sys.argv[3])
        version = sys.argv[4] if len(sys.argv) >= 5 else "fx799"
        output = sys.argv[5] if len(sys.argv) >= 6 else ""
        process_file(input_path, n_vars, version, output)
    else:
        print("Unknown command")
