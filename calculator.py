"""Maya Calculator Module
Advanced calculator with error handling
"""

import math
from typing import Union

class Calculator:
    """Advanced calculator with multiple operations"""
    
    def __init__(self):
        self.history = []
        
    def add(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Add two numbers"""
        self._validate_input(a, b)
        result = a + b
        self._log_operation(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Subtract b from a"""
        self._validate_input(a, b)
        result = a - b
        self._log_operation(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Multiply two numbers"""
        self._validate_input(a, b)
        result = a * b
        self._log_operation(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """Divide a by b with zero check"""
        self._validate_input(a, b)
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._log_operation(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> float:
        """Calculate base raised to power"""
        self._validate_input(base, exponent)
        result = base ** exponent
        self._log_operation(f"{base} ^ {exponent} = {result}")
        return result
    
    def sqrt(self, x: Union[int, float]) -> float:
        """Calculate square root"""
        if not isinstance(x, (int, float)):
            raise TypeError("Input must be a number")
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(x)
        self._log_operation(f"sqrt({x}) = {result}")
        return result
    
    def _validate_input(self, *args):
        """Validate all inputs are numbers"""
        for arg in args:
            if not isinstance(arg, (int, float)):
                raise TypeError(f"Input must be a number, got {type(arg).__name__}")
    
    def _log_operation(self, operation: str):
        """Log operation to history"""
        self.history.append(operation)
    
    def get_history(self) -> list:
        """Get operation history"""
        return self.history.copy()
    
    def clear_history(self):
        """Clear operation history"""
        self.history.clear()


if __name__ == "__main__":
    calc = Calculator()
    
    print("Maya Calculator Demo")
    print("=" * 30)
    
    print(f"10 + 5 = {calc.add(10, 5)}")
    print(f"10 - 5 = {calc.subtract(10, 5)}")
    print(f"10 * 5 = {calc.multiply(10, 5)}")
    print(f"10 / 5 = {calc.divide(10, 5)}")
    print(f"2 ^ 8 = {calc.power(2, 8)}")
    print(f"sqrt(16) = {calc.sqrt(16)}")
    
    print("\nOperation History:")
    for op in calc.get_history():
        print(f"  {op}")
