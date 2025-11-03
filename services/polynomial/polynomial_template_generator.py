"""Polynomial Template Generator - Creates Excel templates for polynomial equation input
Generates structured templates for degrees 2, 3, and 4 with proper headers and examples
"""
import pandas as pd
from typing import Dict, Any
import os


class PolynomialTemplateGenerator:
    """Generator for polynomial Excel templates"""
    
    @staticmethod
    def create_template(degree: int, output_path: str) -> bool:
        """
        Create Excel template for polynomial equations of specified degree
        Args:
            degree: Polynomial degree (2, 3, or 4)
            output_path: Path to save the template
        Returns:
            bool: Success status
        """
        try:
            if degree not in [2, 3, 4]:
                raise ValueError("Degree must be 2, 3, or 4")
            # Ensure output directory exists
            out_dir = os.path.dirname(output_path) or "."
            os.makedirs(out_dir, exist_ok=True)
            
            # Generate template data
            template_data = PolynomialTemplateGenerator._generate_template_data(degree)
            
            # Create Excel file with multiple sheets
            with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
                # Main input sheet
                input_df = pd.DataFrame(template_data['input_data'])
                input_df.to_excel(writer, sheet_name='Input', index=False)
                
                # Examples sheet
                examples_df = pd.DataFrame(template_data['examples'])
                examples_df.to_excel(writer, sheet_name='Examples', index=False)
                
                # Instructions sheet
                instructions_df = pd.DataFrame(template_data['instructions'])
                instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
                
                # Format workbook
                try:
                    workbook = writer.book
                    PolynomialTemplateGenerator._format_workbook(workbook, writer, degree)
                except Exception:
                    # Don't fail template creation on formatting issues
                    pass
            
            return True
            
        except Exception as e:
            print(f"Error creating polynomial template: {e}")
            return False
    
    @staticmethod
    def _generate_template_data(degree: int) -> Dict[str, Any]:
        """Generate template data for specified degree"""
        headers = PolynomialTemplateGenerator._get_headers(degree)
        input_data = {header: [""] * 10 for header in headers}
        input_data['Row'] = list(range(1, 11))
        input_data = {'Row': input_data['Row'], **{k: v for k, v in input_data.items() if k != 'Row'}}
        examples = PolynomialTemplateGenerator._get_examples(degree)
        examples_data = {'Example': [], 'Description': []}
        for desc, coeffs in examples.items():
            examples_data['Example'].append(' | '.join(map(str, coeffs)))
            examples_data['Description'].append(desc)
        for i, header in enumerate(headers):
            examples_data[header] = [example.split(' | ')[i] if i < len(example.split(' | ')) else '0' 
                                   for example in examples_data['Example']]
        instructions = PolynomialTemplateGenerator._get_instructions(degree)
        instructions_data = {
            'Step': list(range(1, len(instructions) + 1)),
            'Instruction': instructions
        }
        return {
            'input_data': input_data,
            'examples': examples_data, 
            'instructions': instructions_data
        }
    
    @staticmethod
    def _get_headers(degree: int) -> list:
        headers_map = {
            2: ['a','b','c'],
            3: ['a','b','c','d'],
            4: ['a','b','c','d','e']
        }
        return headers_map[degree]
    
    @staticmethod
    def _get_examples(degree: int) -> Dict[str, list]:
        examples_map = {
            2: {
                'Simple quadratic (x² - 5x + 6)': [1, -5, 6],
                'No real roots (x² + 1)': [1, 0, 1], 
                'Perfect square (x² - 4x + 4)': [1, -4, 4],
                'With expressions (x² - sqrt(4)x + pi)': [1, '-sqrt(4)', 'pi']
            },
            3: {
                'Simple cubic (x³ - 6x² + 11x - 6)': [1, -6, 11, -6],
                'Depressed cubic (x³ - 2x + 1)': [1, 0, -2, 1],
                'With expressions (x³ + sin(pi/2)x² - cos(0))': [1, 'sin(pi/2)', 0, '-cos(0)']
            },
            4: {
                'Simple quartic (x⁴ - 5x² + 4)': [1, 0, -5, 0, 4],
                'General quartic': [1, -10, 35, -50, 24],
                'With expressions': [1, '-sqrt(9)', 'pi^2', 'log(10)', 'sin(pi/2)']
            }
        }
        return examples_map[degree]
    
    @staticmethod
    def _get_instructions(degree: int) -> list:
        base_instructions = [
            f"Template cho phương trình bậc {degree}",
            f"Mỗi hàng là một phương trình dạng: {PolynomialTemplateGenerator._get_polynomial_form(degree)}",
            "Nhập hệ số theo cột a..e (tùy bậc)",
            "Hỗ trợ: sqrt(5), sin(pi/2), cos(0), tan(pi/4), log(10), ln(2), pi, e, 2^3",
            "Ô trống sẽ được coi là 0",
            "Hệ số a ≠ 0",
            "Lưu file và xử lý bằng Polynomial Mode",
            "Kết quả gồm nghiệm và chuỗi keylog",
            "Xem sheet Examples để tham khảo"
        ]
        if degree == 2:
            base_instructions.append("Bậc 2 luôn có 2 nghiệm (có thể phức)")
        elif degree == 3:
            base_instructions.append("Bậc 3 có 1-3 nghiệm thực tùy delta")
        elif degree == 4:
            base_instructions.append("Bậc 4 có 0-4 nghiệm thực")
        return base_instructions
    
    @staticmethod
    def _get_polynomial_form(degree: int) -> str:
        forms = {2: "ax² + bx + c = 0", 3: "ax³ + bx² + cx + d = 0", 4: "ax⁴ + bx³ + cx² + dx + e = 0"}
        return forms[degree]
    
    @staticmethod
    def _format_workbook(workbook, writer, degree: int):
        header_format = workbook.add_format({'bold': True,'bg_color': '#1E3A8A','font_color': 'white','align': 'center','valign': 'vcenter','border': 1})
        instruction_format = workbook.add_format({'text_wrap': True,'valign': 'top','border': 1})
        input_sheet = writer.sheets['Input']; input_sheet.set_row(0, 25, header_format)
        col_widths = [8] + [15] * (degree + 1)
        for i, w in enumerate(col_widths): input_sheet.set_column(i, i, w)
        examples_sheet = writer.sheets['Examples']; examples_sheet.set_row(0, 25, header_format)
        examples_sheet.set_column(0, 0, 20); examples_sheet.set_column(1, 1, 30)
        for i in range(2, degree + 3): examples_sheet.set_column(i, i, 12)
        instructions_sheet = writer.sheets['Instructions']; instructions_sheet.set_row(0, 25, header_format)
        instructions_sheet.set_column(0, 0, 8); instructions_sheet.set_column(1, 1, 80)
        for row in range(1, len(PolynomialTemplateGenerator._get_instructions(degree)) + 1): instructions_sheet.set_row(row, 25, instruction_format)
