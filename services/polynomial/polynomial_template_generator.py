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
                
                # Format the workbook
                workbook = writer.book
                PolynomialTemplateGenerator._format_workbook(workbook, writer, degree)
            
            return True
            
        except Exception as e:
            print(f"Error creating polynomial template: {e}")
            return False
    
    @staticmethod
    def _generate_template_data(degree: int) -> Dict[str, Any]:
        """Generate template data for specified degree"""
        
        # Column headers based on degree
        headers = PolynomialTemplateGenerator._get_headers(degree)
        
        # Input data template
        input_data = {header: [""] * 10 for header in headers}  # 10 empty rows
        input_data['Row'] = list(range(1, 11))
        
        # Move Row to first column
        input_data = {'Row': input_data['Row'], **{k: v for k, v in input_data.items() if k != 'Row'}}
        
        # Examples data
        examples = PolynomialTemplateGenerator._get_examples(degree)
        examples_data = {'Example': [], 'Description': []}
        for desc, coeffs in examples.items():
            examples_data['Example'].append(' | '.join(map(str, coeffs)))
            examples_data['Description'].append(desc)
        
        # Add headers to examples
        for i, header in enumerate(headers):
            examples_data[header] = [example.split(' | ')[i] if i < len(example.split(' | ')) else '0' 
                                   for example in examples_data['Example']]
        
        # Instructions
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
        """Get column headers for polynomial degree"""
        headers_map = {
            2: ['a_coeff', 'b_coeff', 'c_coeff'],
            3: ['a_coeff', 'b_coeff', 'c_coeff', 'd_coeff'],
            4: ['a_coeff', 'b_coeff', 'c_coeff', 'd_coeff', 'e_coeff']
        }
        return headers_map[degree]
    
    @staticmethod
    def _get_examples(degree: int) -> Dict[str, list]:
        """Get example polynomials for each degree"""
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
        """Get instructions for template usage"""
        base_instructions = [
            f"This template is for polynomial equations of degree {degree}",
            f"Each row represents one polynomial equation of the form: {PolynomialTemplateGenerator._get_polynomial_form(degree)}",
            "Enter coefficients in the corresponding columns",
            "Supported expressions: sqrt(5), sin(pi/2), cos(0), tan(pi/4), log(10), ln(2), pi, e, 2^3",
            "Empty cells will be treated as 0",
            "Leading coefficient 'a' cannot be zero",
            "Save this file and import into Polynomial Mode for processing",
            "Results will include all roots (real and complex) plus encoded keylog",
            "Check the Examples sheet for sample polynomials"
        ]
        
        # Add degree-specific notes
        if degree == 2:
            base_instructions.append("Quadratic equations always have exactly 2 roots (may be complex)")
        elif degree == 3:
            base_instructions.append("Cubic equations have 1-3 real roots depending on discriminant")
        elif degree == 4:
            base_instructions.append("Quartic equations can have 0-4 real roots")
        
        return base_instructions
    
    @staticmethod
    def _get_polynomial_form(degree: int) -> str:
        """Get polynomial form string"""
        forms = {
            2: "ax² + bx + c = 0",
            3: "ax³ + bx² + cx + d = 0",
            4: "ax⁴ + bx³ + cx² + dx + e = 0"
        }
        return forms[degree]
    
    @staticmethod
    def _format_workbook(workbook, writer, degree: int):
        """Format the Excel workbook with colors and styling"""
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#1E3A8A',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        example_format = workbook.add_format({
            'bg_color': '#E8F4FD',
            'border': 1,
            'align': 'center'
        })
        
        instruction_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # Format Input sheet
        input_sheet = writer.sheets['Input']
        input_sheet.set_row(0, 25, header_format)  # Header row
        
        # Set column widths
        col_widths = [8] + [15] * (degree + 1)  # Row column + coefficient columns
        for i, width in enumerate(col_widths):
            input_sheet.set_column(i, i, width)
        
        # Format Examples sheet
        examples_sheet = writer.sheets['Examples']
        examples_sheet.set_row(0, 25, header_format)
        
        # Set column widths for examples
        examples_sheet.set_column(0, 0, 20)  # Example column
        examples_sheet.set_column(1, 1, 30)  # Description column
        for i in range(2, degree + 3):
            examples_sheet.set_column(i, i, 12)  # Coefficient columns
        
        # Format Instructions sheet
        instructions_sheet = writer.sheets['Instructions']
        instructions_sheet.set_row(0, 25, header_format)
        instructions_sheet.set_column(0, 0, 8)   # Step column
        instructions_sheet.set_column(1, 1, 80)  # Instruction column
        
        # Apply instruction format to content rows
        for row in range(1, len(PolynomialTemplateGenerator._get_instructions(degree)) + 1):
            instructions_sheet.set_row(row, 25, instruction_format)
    
    @staticmethod
    def get_template_info(degree: int) -> Dict[str, Any]:
        """Get information about template structure"""
        return {
            'degree': degree,
            'coefficient_count': degree + 1,
            'polynomial_form': PolynomialTemplateGenerator._get_polynomial_form(degree),
            'headers': PolynomialTemplateGenerator._get_headers(degree),
            'example_count': len(PolynomialTemplateGenerator._get_examples(degree)),
            'supports_expressions': True,
            'sheets': ['Input', 'Examples', 'Instructions']
        }


# ========== TESTING ==========
if __name__ == "__main__":
    # Test template generation
    print("=== TESTING POLYNOMIAL TEMPLATE GENERATOR ===")
    
    for degree in [2, 3, 4]:
        print(f"\n--- Degree {degree} Template ---")
        
        # Get template info
        info = PolynomialTemplateGenerator.get_template_info(degree)
        print(f"Polynomial form: {info['polynomial_form']}")
        print(f"Coefficient count: {info['coefficient_count']}")
        print(f"Headers: {info['headers']}")
        print(f"Example count: {info['example_count']}")
        
        # Create template
        output_path = f"test_polynomial_template_degree_{degree}.xlsx"
        success = PolynomialTemplateGenerator.create_template(degree, output_path)
        
        if success:
            print(f"✅ Template created: {output_path}")
            # Clean up test file
            try:
                os.remove(output_path)
                print(f"🧹 Cleaned up test file")
            except:
                pass
        else:
            print(f"❌ Failed to create template for degree {degree}")
    
    print("\n=== TEMPLATE GENERATOR TEST COMPLETED ===")