"""Maya Calculator Module
Advanced calculator with error handling
"""

import math
from typing import Union
import numbers
import math as _math
import os
from pathlib import Path
from typing import Callable
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except Exception:
    HAS_MATPLOTLIB = False
try:
    import tkinter as tk
    from tkinter import Toplevel
    TK_AVAILABLE = True
except Exception:
    TK_AVAILABLE = False
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

    # ------------------ Advanced Numeric & Scientific ------------------
    def log(self, x: Union[int, float], base: Union[int, float] = _math.e) -> float:
        """Logarithm with optional base (natural log by default)"""
        self._validate_input(x)
        self._validate_input(base)
        if x <= 0 or base <= 0:
            raise ValueError("Logarithm domain error: x and base must be positive")
        if base == _math.e:
            return _math.log(x)
        return _math.log(x, base)

    def ln(self, x: Union[int, float]) -> float:
        """Natural logarithm"""
        return self.log(x, _math.e)

    def log10(self, x: Union[int, float]) -> float:
        """Base-10 logarithm"""
        return self.log(x, 10)

    def sin(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.sin(x)

    def cos(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.cos(x)

    def tan(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.tan(x)

    def asin(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.asin(x)

    def acos(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.acos(x)

    def atan(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.atan(x)

    def deg2rad(self, deg: Union[int, float]) -> float:
        self._validate_input(deg)
        return _math.radians(deg)

    def rad2deg(self, rad: Union[int, float]) -> float:
        self._validate_input(rad)
        return _math.degrees(rad)

    def factorial(self, n: int) -> int:
        if not isinstance(n, int) or n < 0:
            raise ValueError('factorial requires a non-negative integer')
        return _math.factorial(n)

    def comb(self, n: int, k: int) -> int:
        return _math.comb(n, k)

    def exp(self, x: Union[int, float]) -> float:
        self._validate_input(x)
        return _math.exp(x)

    # ------------------ Expression evaluation ------------------
    def evaluate_expression(self, expr: str, variables: dict = None) -> float:
        """Safely evaluate a numeric algebraic expression using AST.

        Supports math functions from the math module and numeric operations.
        """
        import ast

        allowed_names = {k: getattr(_math, k) for k in dir(_math) if not k.startswith('_')}
        allowed_names.update({'pi': _math.pi, 'e': _math.e})
        if variables:
            for k, v in variables.items():
                if not isinstance(k, str):
                    continue
                if not isinstance(v, numbers.Number):
                    raise ValueError('Variable values must be numeric')
                allowed_names[k] = v

        node = ast.parse(expr, mode='eval')

        class SafeEval(ast.NodeVisitor):
            ALLOWED_NODES = (ast.Expression, ast.BinOp, ast.UnaryOp,
                             ast.Num, ast.Load, ast.Call, ast.Name,
                             ast.Pow, ast.Add, ast.Sub, ast.Mult, ast.Div,
                             ast.Mod, ast.USub, ast.UAdd, ast.FloorDiv)

            def visit(self, node):
                if not isinstance(node, self.ALLOWED_NODES):
                    raise ValueError(f'Unsupported expression element: {type(node).__name__}')
                return super().visit(node)

            def visit_Call(self, node):
                if not isinstance(node.func, ast.Name):
                    raise ValueError('Only direct function calls allowed')
                if node.func.id not in allowed_names:
                    raise ValueError(f'Function {node.func.id} is not allowed')
                for arg in node.args:
                    self.visit(arg)

            def visit_Name(self, node):
                if node.id not in allowed_names:
                    raise ValueError(f'Name {node.id} is not allowed')

        SafeEval().visit(node)

        compiled = compile(node, '<string>', 'eval')
        return eval(compiled, {'__builtins__': {}}, allowed_names)

    # ------------------ Plotting ------------------
    def plot_function(self, expr: str, x_min: float = -10, x_max: float = 10,
                      points: int = 400, filename: str = None) -> str:
        """Plot a function expression over a range and save an image file.

        Returns path to saved image. Requires matplotlib and numpy.
        Expression should be a function of `x`, e.g. 'sin(x) + x**2'.
        """
        if not HAS_MATPLOTLIB:
            raise RuntimeError('Matplotlib or numpy not available')

        xs = np.linspace(x_min, x_max, points)
        vals = []
        for x in xs:
            try:
                v = self.evaluate_expression(expr, {'x': float(x)})
            except Exception:
                v = float('nan')
            vals.append(v)

        out_dir = Path('outputs') / 'plots'
        out_dir.mkdir(parents=True, exist_ok=True)
        if not filename:
            filename = f'plot_{abs(hash(expr)) % 10_000}_{int(x_min)}_{int(x_max)}.png'
        out_path = out_dir / filename

        plt.figure()
        plt.plot(xs, vals)
        plt.title(expr)
        plt.xlabel('x')
        plt.ylabel('f(x)')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(out_path)
        plt.close()
        return str(out_path)

    def show_plot_gui(self, expr: str, x_min: float = -10, x_max: float = 10,
                      points: int = 400, filename: str = None, title: str = None,
                      blocking: bool = False) -> str:
        """Generate the plot and display it in a simple Tkinter GUI window.

        Returns the path to the generated image. If `blocking` is True the
        function will start the Tk mainloop and block; otherwise it will open
        the window in a background thread.
        """
        if not HAS_MATPLOTLIB:
            raise RuntimeError('Matplotlib or numpy not available')

        img_path = Path(self.plot_function(expr, x_min, x_max, points, filename))

        if not TK_AVAILABLE:
            raise RuntimeError('Tkinter not available for GUI display')

        def _open_window():
            root = tk.Tk()
            root.title(title or f'Plot: {expr}')
            # Load image via PhotoImage (PNG supported)
            try:
                img = tk.PhotoImage(file=str(img_path))
            except Exception:
                # Fallback: try to use PIL if available
                try:
                    from PIL import Image, ImageTk
                    pil_img = Image.open(str(img_path))
                    img = ImageTk.PhotoImage(pil_img)
                except Exception as e:
                    root.destroy()
                    raise RuntimeError(f'Failed to load plot image: {e}')

            lbl = tk.Label(root, image=img)
            lbl.image = img
            lbl.pack(fill='both', expand=True)

            # Add a close button
            btn = tk.Button(root, text='Close', command=root.destroy)
            btn.pack(side='bottom', pady=6)

            root.mainloop()

        if blocking:
            _open_window()
        else:
            import threading
            t = threading.Thread(target=_open_window, daemon=True)
            t.start()

        return str(img_path)

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
