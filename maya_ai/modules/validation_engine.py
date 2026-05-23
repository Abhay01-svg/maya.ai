"""
Maya Validation Engine
Self-validation and quality assurance system
"""

import ast
import os
import re
import sys
import json
import logging
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class ValidationResult:
    """Individual validation result"""
    def __init__(self, level: ValidationLevel, message: str, 
                 file: str = None, line: int = None, suggestion: str = None):
        self.level = level
        self.message = message
        self.file = file
        self.line = line
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level.value,
            'message': self.message,
            'file': self.file,
            'line': self.line,
            'suggestion': self.suggestion
        }

class MayaValidationEngine:
    """
    Self-Validation Engine for Maya AI
    Validates: syntax, imports, execution feasibility, logical issues
    """
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.known_issues = set()
        logger.info("✅ Maya Validation Engine initialized")
    
    def _load_validation_rules(self) -> Dict:
        """Load validation rules"""
        return {
            'python': {
                'syntax_check': True,
                'import_check': True,
                'style_check': True,
                'security_check': True
            },
            'javascript': {
                'syntax_check': True,
                'import_check': True
            },
            'general': {
                'path_check': True,
                'permission_check': True
            }
        }
    
    def validate_code(self, code: str, language: str = 'python', 
                     filename: str = None) -> Dict[str, Any]:
        """
        Comprehensive code validation
        Returns validation results with errors, warnings, and suggestions
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'info': [],
            'metrics': {}
        }
        
        if language == 'python':
            # Syntax validation
            syntax_result = self._validate_python_syntax(code, filename)
            results['errors'].extend(syntax_result['errors'])
            results['warnings'].extend(syntax_result['warnings'])
            
            # Import validation
            import_result = self._validate_imports(code, filename)
            results['errors'].extend(import_result['errors'])
            results['warnings'].extend(import_result['warnings'])
            
            # Style validation
            style_result = self._validate_style(code, filename)
            results['warnings'].extend(style_result['warnings'])
            
            # Security validation
            security_result = self._validate_security(code, filename)
            results['warnings'].extend(security_result['warnings'])
            results['errors'].extend(security_result['errors'])
            
            # Calculate metrics
            results['metrics'] = self._calculate_code_metrics(code)
        
        elif language == 'javascript':
            # Basic JS validation
            js_result = self._validate_javascript(code, filename)
            results['errors'].extend(js_result['errors'])
            results['warnings'].extend(js_result['warnings'])
        
        # Determine overall validity
        results['valid'] = len(results['errors']) == 0
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        
        return results
    
    def _validate_python_syntax(self, code: str, filename: str = None) -> Dict:
        """Validate Python syntax using AST"""
        result = {'errors': [], 'warnings': []}
        
        try:
            ast.parse(code)
        except SyntaxError as e:
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Syntax error: {e.msg}",
                file=filename,
                line=e.lineno,
                suggestion="Check for missing colons, parentheses, or indentation"
            ))
        except IndentationError as e:
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Indentation error: {e.msg}",
                file=filename,
                line=e.lineno,
                suggestion="Fix indentation - Python requires consistent indentation"
            ))
        
        return result
    
    def _validate_imports(self, code: str, filename: str = None) -> Dict:
        """Validate imports and dependencies"""
        result = {'errors': [], 'warnings': []}
        
        try:
            tree = ast.parse(code)
            
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            # Check for unused imports
            defined_names = set()
            used_names = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        defined_names.add(node.id)
                    elif isinstance(node.ctx, ast.Load):
                        used_names.add(node.id)
            
            # Check each import
            for imp in imports:
                base_module = imp.split('.')[0]
                if base_module not in used_names and not imp.startswith('.'):
                    result['warnings'].append(ValidationResult(
                        level=ValidationLevel.WARNING,
                        message=f"Potentially unused import: {imp}",
                        file=filename,
                        suggestion=f"Remove if not used or use 'import {base_module}'"
                    ))
            
            # Check for circular imports (basic check)
            if filename:
                module_name = os.path.basename(filename).replace('.py', '')
                for imp in imports:
                    if module_name in imp:
                        result['warnings'].append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"Possible circular import detected: {imp}",
                            file=filename,
                            suggestion="Refactor to avoid circular dependencies"
                        ))
        
        except Exception as e:
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Import validation error: {e}",
                file=filename
            ))
        
        return result
    
    def _validate_style(self, code: str, filename: str = None) -> Dict:
        """Validate code style and best practices"""
        result = {'warnings': []}
        
        # Check for bare except
        if re.search(r'except\s*:', code):
            if 'except Exception' not in code:
                result['warnings'].append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message="Bare 'except:' clause found",
                    file=filename,
                    suggestion="Use 'except Exception:' or more specific exception types"
                ))
        
        # Check for print statements (should use logging)
        if re.search(r'\bprint\s*\(', code):
            result['warnings'].append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="Print statement found",
                file=filename,
                suggestion="Consider using logging instead of print for production code"
            ))
        
        # Check for TODO/FIXME
        todos = re.findall(r'#[\s]*(TODO|FIXME|XXX|HACK)[\s:]*(.*)', code, re.IGNORECASE)
        for todo_type, todo_text in todos:
            result['warnings'].append(ValidationResult(
                level=ValidationLevel.WARNING,
                message=f"{todo_type.upper()} found: {todo_text.strip()}",
                file=filename,
                suggestion="Address before finalizing"
            ))
        
        # Check function complexity
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Count statements in function
                    stmt_count = len([n for n in ast.walk(node) if isinstance(n, ast.stmt)])
                    if stmt_count > 50:
                        result['warnings'].append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            message=f"Function '{node.name}' is complex ({stmt_count} statements)",
                            file=filename,
                            line=node.lineno,
                            suggestion="Consider breaking into smaller functions"
                        ))
        except:
            pass
        
        return result
    
    def _validate_security(self, code: str, filename: str = None) -> Dict:
        """Validate security best practices"""
        result = {'errors': [], 'warnings': []}
        
        # Check for eval/exec usage
        if re.search(r'\beval\s*\(', code):
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="eval() usage detected - security risk",
                file=filename,
                suggestion="Use ast.literal_eval() or json.loads() instead"
            ))
        
        if re.search(r'\bexec\s*\(', code):
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message="exec() usage detected - security risk",
                file=filename,
                suggestion="Avoid exec() - use safer alternatives"
            ))
        
        # Check for hardcoded passwords/keys
        sensitive_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key detected"),
            (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret detected"),
            (r'token\s*=\s*["\'][^"\']+["\']', "Hardcoded token detected")
        ]
        
        for pattern, message in sensitive_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                result['warnings'].append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    message=message,
                    file=filename,
                    suggestion="Use environment variables or secure credential storage"
                ))
        
        # Check for SQL injection risks
        if re.search(r'(?:execute|query)\s*\(\s*["\'].*%s', code):
            result['warnings'].append(ValidationResult(
                level=ValidationLevel.WARNING,
                message="Potential SQL injection risk - string formatting in query",
                file=filename,
                suggestion="Use parameterized queries"
            ))
        
        return result
    
    def _validate_javascript(self, code: str, filename: str = None) -> Dict:
        """Basic JavaScript validation"""
        result = {'errors': [], 'warnings': []}
        
        # Check for basic syntax issues
        open_braces = code.count('{')
        close_braces = code.count('}')
        open_parens = code.count('(')
        close_parens = code.count(')')
        
        if open_braces != close_braces:
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Mismatched braces: {open_braces} open, {close_braces} close",
                file=filename
            ))
        
        if open_parens != close_parens:
            result['errors'].append(ValidationResult(
                level=ValidationLevel.ERROR,
                message=f"Mismatched parentheses: {open_parens} open, {close_parens} close",
                file=filename
            ))
        
        return result
    
    def _calculate_code_metrics(self, code: str) -> Dict:
        """Calculate code quality metrics"""
        try:
            tree = ast.parse(code)
            
            metrics = {
                'total_lines': len(code.split('\n')),
                'code_lines': len([l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]),
                'comment_lines': len([l for l in code.split('\n') if l.strip().startswith('#')]),
                'blank_lines': len([l for l in code.split('\n') if not l.strip()]),
                'functions': 0,
                'classes': 0,
                'imports': 0
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics['functions'] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics['classes'] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics['imports'] += 1
            
            return metrics
            
        except:
            return {'total_lines': len(code.split('\n'))}
    
    def _generate_summary(self, results: Dict) -> str:
        """Generate human-readable summary"""
        error_count = len(results['errors'])
        warning_count = len(results['warnings'])
        
        if error_count == 0 and warning_count == 0:
            return "✅ All validations passed"
        
        parts = []
        if error_count > 0:
            parts.append(f"❌ {error_count} error(s)")
        if warning_count > 0:
            parts.append(f"⚠️ {warning_count} warning(s)")
        
        return f"Validation: {', '.join(parts)}"
    
    def validate_execution_feasibility(self, code: str, language: str = 'python') -> Dict:
        """Check if code can be executed"""
        result = {
            'feasible': True,
            'issues': [],
            'dependencies': []
        }
        
        if language == 'python':
            # Check for required dependencies
            try:
                tree = ast.parse(code)
                imports = []
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module.split('.')[0])
                
                # Check if imports are available
                for imp in set(imports):
                    if imp in sys.stdlib_module_names:
                        continue
                    try:
                        __import__(imp)
                        result['dependencies'].append(f"{imp} (available)")
                    except ImportError:
                        result['issues'].append(f"Missing dependency: {imp}")
                        result['feasible'] = False
                        
            except Exception as e:
                result['issues'].append(f"Analysis error: {e}")
        
        return result
    
    def validate_file_path(self, filepath: str, check_exists: bool = False,
                          check_writable: bool = False) -> Dict:
        """Validate file path"""
        result = {
            'valid': True,
            'issues': []
        }
        
        # Check for invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            if char in filepath:
                result['issues'].append(f"Invalid character in path: {char}")
                result['valid'] = False
        
        # Check path length
        if len(filepath) > 260:
            result['issues'].append("Path too long (>260 characters)")
            result['valid'] = False
        
        if check_exists:
            if not os.path.exists(filepath):
                result['issues'].append("Path does not exist")
                result['valid'] = False
        
        if check_writable:
            dir_path = os.path.dirname(filepath) or '.'
            if not os.access(dir_path, os.W_OK):
                result['issues'].append("Directory not writable")
                result['valid'] = False
        
        return result
    
    def quick_validate(self, code: str, language: str = 'python') -> bool:
        """Quick validation - returns True/False"""
        try:
            if language == 'python':
                ast.parse(code)
                return True
            return True
        except:
            return False
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            'rules_loaded': len(self.validation_rules),
            'known_issues': len(self.known_issues)
        }

# Singleton instance
validation_engine = MayaValidationEngine()

if __name__ == "__main__":
    # Test
    test_code = """
def hello():
    print("Hello")
    x = 1 + 2
    return x
"""
    result = validation_engine.validate_code(test_code)
    print(result['summary'])
