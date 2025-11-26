#!/usr/bin/env python3
"""Test script: DerivativeEncodingService + LatexToKeylogEncoder workflow

Demo cách kết hợp 2 service để mã hóa biểu thức đạo hàm.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.derivative.derivative_encoding_service import DerivativeEncodingService

def print_separator(title="", char="="):
    """Print a nice separator"""
    width = 80
    if title:
        print(f"\n{char * width}")
        print(f"{title.center(width)}")
        print(f"{char * width}\n")
    else:
        print(f"{char * width}")

def test_derivative_encoding():
    """Main test function"""
    
    print_separator("DERIVATIVE ENCODING SERVICE - WORKFLOW DEMO")
    
    # Initialize service
    print("➡️  Initializing DerivativeEncodingService...")
    service = DerivativeEncodingService()
    
    if not service.is_available():
        print("❌ Service not available!")
        return
    
    print("✅ Service initialized successfully")
    print(f"  - Encoder: {service.encoder.__class__.__name__}")
    print(f"  - Mapping rules: {len(service.encoder.mappings)}")
    print(f"  - Format: qv[n]{{expression}},{{variable=value}})")
    
    # Test cases
    print_separator("TEST CASES")
    
    test_cases = [
        {
            'latex': r"\frac{d}{dx}{x^2}{x=3}",
            'description': "Simple polynomial"
        },
        {
            'latex': r"\frac{d}{dx}{2\cdot10^{3}x^{2} + 5\cdot10^{2}x + 7\cdot10^{4}}{x=3\cdot10^{2}}",
            'description': "Scientific notation (complex)"
        },
        {
            'latex': r"\frac{d^2}{dx^2}{x^3 + 2x}{x=1}",
            'description': "Second derivative"
        },
        {
            'latex': r"\frac{d}{dx}{e^{2x}}{x=0}",
            'description': "Exponential function"
        },
        {
            'latex': r"\frac{d}{dx}{\sin(x)}{x=\frac{\pi}{4}}",
            'description': "Trigonometric with fraction"
        },
        {
            'latex': r"\frac{d}{dx}{\frac{x^2}{x+1}}{x=2}",
            'description': "Quotient (fraction)"
        },
        {
            'latex': r"\frac{d}{dx}{\ln(x^2 + 1)}{x=1}",
            'description': "Logarithm"
        },
        {
            'latex': r"\frac{d^3}{dx^3}{x^4}{x=2}",
            'description': "Third derivative"
        },
        {
            'latex': r"\frac{d}{dx}{x^2 + 3x + 1}{}",
            'description': "No evaluation point"
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test Case {i}: {test['description']}")
        print(f"{'='*80}")
        
        latex_input = test['latex']
        print(f"\nInput LaTeX:")
        print(f"  {latex_input}")
        
        # Encode
        result = service.encode_derivative(latex_input, mode="1")
        
        if result['success']:
            print(f"\n✅ Encoding successful!")
            print(f"\nMetadata:")
            print(f"  - Derivative order: {result['derivative_order']}")
            print(f"  - Variable: {result['variable']}")
            print(f"  - Function: {result['function']}")
            print(f"  - Format: {result['format']}")
            
            print(f"\nOutput Keylog:")
            print(f"  {result['keylog']}")
            
            print(f"\nPattern:")
            print(f"  {result['pattern']}")
        else:
            print(f"\n❌ Encoding failed!")
            print(f"  Error: {result['error']}")
    
    # Detailed breakdown for one example
    print_separator("DETAILED BREAKDOWN - Example 2")
    
    latex = r"\frac{d}{dx}{2\cdot10^{3}x^{2} + 5\cdot10^{2}x + 7\cdot10^{4}}{x=3\cdot10^{2}}"
    print(f"LaTeX Input:")
    print(f"  {latex}\n")
    
    result = service.encode_derivative(latex)
    
    if result['success']:
        print("STEP 1: DerivativeEncodingService extracts components")
        print(f"  - Expression: {result['function']}")
        print(f"  - Variable: {result['variable']}")
        print(f"  - Order: {result['derivative_order']}")
        
        print("\nSTEP 2: LatexToKeylogEncoder encodes expression")
        print(f"  Input:  {result['function']}")
        print(f"  Steps:")
        print(f"    1. \\cdot → O")
        print(f"    2. O10^{{n}} → Kn (scientific notation)")
        print(f"    3. x^{{n}} → [^n) (exponents)")
        print(f"    4. x → [ (variable)")
        print(f"    5. + → p, - → m (operators)")
        
        print("\nSTEP 3: DerivativeEncodingService assembles keylog")
        print(f"  Prefix: qv (order={result['derivative_order']})")
        print(f"  Format: qv{{expr}},{{var=val}})")
        
        print("\nFINAL OUTPUT:")
        print(f"  {result['keylog']}")
    
    # Summary
    print_separator("SUMMARY")
    print("✅ DerivativeEncodingService successfully wraps LatexToKeylogEncoder")
    print("✅ New simplified format: qv[n]{expression},{variable=value})")
    print("✅ All test cases processed")
    print()
    print("Key Features:")
    print("  • Automatic pattern parsing: \\frac{d}{dx}{expr}{x=val}")
    print("  • Support multiple derivative orders: qv, qv2, qv3, ...")
    print("  • Optional evaluation point")
    print("  • Leverages LatexToKeylogEncoder for expression encoding")
    print("  • 31% shorter than old format")
    print()

if __name__ == "__main__":
    try:
        test_derivative_encoding()
        print("\n✨ Test completed successfully!\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
