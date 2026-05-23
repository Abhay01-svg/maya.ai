"""
Maya AI Calculator Module
Fast engineering mathematics without AI models
Uses sympy, numpy, scipy for instant calculations
"""

import re
import logging
from sympy import *
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application
import numpy as np
from scipy import integrate, special
from config import DEBUG_MODE

logger = logging.getLogger(__name__)

class MayaCalculator:
    """Engineering mathematics calculator"""
    
    def __init__(self):
        self.transformations = standard_transformations + (implicit_multiplication_application,)
    
    def evaluate_expression(self, expr_str: str) -> str:
        """Evaluate mathematical expression"""
        try:
            # Preprocess expression to handle common patterns
            processed_expr = self._preprocess_expression(expr_str)
            
            # Parse and evaluate
            expr = parse_expr(processed_expr, transformations=self.transformations)
            result = expr.evalf()
            return str(result)
        except Exception as e:
            return f"❌ Expression error: {str(e)}"
    
    def _preprocess_expression(self, expr_str: str) -> str:
        """Preprocess expression to handle common mathematical patterns"""
        import re

        # Convert trigonometric functions without parentheses or with spaces to standard form
        # sin 90 -> sin(90), sin90 -> sin(90)
        processed = expr_str.lower().strip()
        
        # Add parentheses to trig functions if missing
        processed = re.sub(r'(sin|cos|tan|log|ln|sqrt)\s*(\d+\.?\d*)', r'\1(\2)', processed)
        
        # Convert degrees to radians for trigonometric functions
        # This handles sin(30), cos(45), etc.
        def convert_to_radians(match):
            func_name = match.group(1)
            angle = match.group(2)
            # Only convert if it's a number (avoid variables like x)
            try:
                float(angle)
                return f"{func_name}(({angle})*pi/180)"
            except ValueError:
                return f"{func_name}({angle})"

        processed = re.sub(r'(sin|cos|tan)\(([\d\.]+)\)', convert_to_radians, processed)

        return processed
    
    # ==================== ALGEBRA ====================
    
    def solve_equation(self, equation: str, variable: str = 'x') -> str:
        """Solve algebraic equation
        Example: "x**2 - 5*x + 6 = 0"
        """
        try:
            x = symbols(variable)
            # Parse equation
            eq_str = equation.replace('=', ' - ')
            expr = parse_expr(eq_str, transformations=self.transformations)
            
            solutions = solve(expr, x)
            if solutions:
                result = f"Solutions: {solutions}"
            else:
                result = "No solutions found"
            return result
        except Exception as e:
            return f"❌ Error solving equation: {str(e)}"
    
    # ==================== MATRIX OPERATIONS ====================
    
    def matrix_determinant(self, matrix_list: list) -> str:
        """Calculate determinant of matrix"""
        try:
            M = Matrix(matrix_list)
            det = M.det()
            return f"Determinant: {det}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def matrix_inverse(self, matrix_list: list) -> str:
        """Calculate inverse of matrix"""
        try:
            M = Matrix(matrix_list)
            inv = M.inv()
            return f"Inverse:\n{inv}"
        except Exception as e:
            return f"❌ Cannot invert (singular): {str(e)}"
    
    def matrix_eigenvalues(self, matrix_list: list) -> str:
        """Calculate eigenvalues and eigenvectors"""
        try:
            M = Matrix(matrix_list)
            eigenvals = M.eigenvals()
            eigenvects = M.eigenvects()
            
            result = "Eigenvalues:\n"
            for val, mult in eigenvals.items():
                result += f"  {val} (multiplicity: {mult})\n"
            
            return result
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== CALCULUS ====================
    
    def derivative(self, func_str: str, variable: str = 'x', order: int = 1) -> str:
        """Calculate derivative
        Example: "sin(x)*x**2"
        """
        try:
            var = symbols(variable)
            func = parse_expr(func_str, transformations=self.transformations)
            
            deriv = diff(func, var, order)
            return f"d^{order}f/d{variable}^{order} = {deriv}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def integral(self, func_str: str, variable: str = 'x') -> str:
        """Calculate indefinite integral"""
        try:
            var = symbols(variable)
            func = parse_expr(func_str, transformations=self.transformations)
            
            integral_result = integrate(func, var)
            return f"∫{func}d{variable} = {integral_result} + C"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def definite_integral(self, func_str: str, variable: str = 'x', a: float = 0, b: float = 1) -> str:
        """Calculate definite integral"""
        try:
            var = symbols(variable)
            func = parse_expr(func_str, transformations=self.transformations)
            
            integral_result = integrate(func, (var, a, b))
            return f"∫[{a},{b}] {func}d{variable} = {integral_result}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== COMPLEX NUMBERS ====================
    
    def complex_operations(self, operation: str, a: complex, b: complex = None) -> str:
        """Complex number operations"""
        try:
            if operation == "magnitude":
                result = abs(a)
                return f"|{a}| = {result}"
            elif operation == "conjugate":
                result = a.conjugate()
                return f"Conjugate of {a} = {result}"
            elif operation == "phase":
                result = np.angle(a)
                return f"Phase of {a} = {result} radians"
            elif operation == "add":
                result = a + b
                return f"{a} + {b} = {result}"
            elif operation == "multiply":
                result = a * b
                return f"{a} * {b} = {result}"
            else:
                return "❌ Unknown operation"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== LINEAR ALGEBRA ====================
    
    def solve_linear_system(self, A: list, b: list) -> str:
        """Solve Ax = b"""
        try:
            A_matrix = Matrix(A)
            b_vector = Matrix(b)
            
            solution = A_matrix.solve(b_vector)
            return f"Solution: {solution.T}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== TRANSFORMS ====================
    
    def laplace_transform(self, func_str: str, variable: str = 't', s_var: str = 's') -> str:
        """Calculate Laplace transform"""
        try:
            t, s = symbols(variable), symbols(s_var)
            func = parse_expr(func_str, transformations=self.transformations)
            
            # Manual Laplace for common functions
            if 't' in str(func):
                result = laplace_transform(func, t, s)
                return f"L{{{func}}} = {result[0]}"
            else:
                return "⚠️  Limited Laplace support for constants"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def fourier_series(self, func_str: str, variable: str = 'x', n_terms: int = 5) -> str:
        """Calculate Fourier series (simple)"""
        try:
            x = symbols(variable)
            func = parse_expr(func_str, transformations=self.transformations)
            
            # For now, return formula
            return f"⚠️  Fourier series calculation limited. Formula: f(x) = a0 + Σ(an*cos(nx) + bn*sin(nx))"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== STATISTICS ====================
    
    def statistics(self, data: list) -> str:
        """Calculate statistics"""
        try:
            arr = np.array(data)
            
            result = f"""
📊 Statistics:
  Mean: {np.mean(arr):.4f}
  Median: {np.median(arr):.4f}
  Std Dev: {np.std(arr):.4f}
  Variance: {np.var(arr):.4f}
  Min: {np.min(arr):.4f}
  Max: {np.max(arr):.4f}
            """
            return result
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==================== QUICK MATH ====================
    
    def parse_and_calculate(self, query: str) -> dict:
        """Smart math detection and calculation"""
        result = {
            "type": "math",
            "result": None,
            "hinglish": None
        }
        
        try:
            # Clean query
            query_clean = query.lower().strip()
            
            # Replace words with operators
            query_clean = query_clean.replace('plus', '+').replace('add', '+')
            query_clean = query_clean.replace('minus', '-').replace('subtract', '-')
            query_clean = query_clean.replace('multiply', '*').replace('times', '*').replace(' x ', '*')
            query_clean = query_clean.replace('divide', '/').replace('divided by', '/')
            query_clean = query_clean.replace('square', '**2').replace('cube', '**3').replace('^', '**')
            query_clean = query_clean.replace('square root', 'sqrt')

            # Evaluate
            calc_result = self.evaluate_expression(query_clean)
            
            if "❌" in calc_result:
                result["result"] = calc_result
                result["hinglish"] = f"Maaf kijiye, calculation mein error hai: {calc_result}"
            else:
                result["result"] = calc_result
                result["hinglish"] = f"✅ Answer hai: {calc_result}."
            
            return result
        except Exception as e:
            return {
                "type": "error",
                "result": str(e),
                "hinglish": f"❌ Calculation error: {str(e)}"
            }

    # Backwards-compatible alias used by unified decision maker
    def calculate(self, query: str) -> dict:
        """Legacy entrypoint: calculate(query) -> dict

        Returns the same structure as `parse_and_calculate`.
        """
        return self.parse_and_calculate(query)

# Singleton
calculator = MayaCalculator()

if DEBUG_MODE:
    print("🧮 Maya Calculator initialized")
