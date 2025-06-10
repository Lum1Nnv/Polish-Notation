#!/usr/bin/env python3
"""
Convert infix notation to Reverse Polish Notation (RPN)
with improved validation and extended operators
Supports complex numbers for all operations
"""

import re
import math
import cmath
import argparse
import random
from typing import List, Tuple, Optional, Dict, Union

# Operator priorities and associativity
# Format: (priority, associativity) where 'L' = left, 'R' = right
OPERATORS = {
    '+': (1, 'L'),      # Addition
    '-': (1, 'L'),      # Subtraction
    '*': (2, 'L'),      # Multiplication
    '/': (2, 'L'),      # Division
    '%': (2, 'L'),      # Modulo
    '//': (2, 'L'),     # Integer division
    '^': (3, 'R'),      # Power (right associative)
    '**': (3, 'R'),     # Alternative power notation
}

# Unary operators (prefix)
UNARY_OPERATORS = {
    '-': 4,  # Unary minus
    '+': 4,  # Unary plus
}

# Functions (treated as operators with highest priority)
FUNCTIONS = {
    'sqrt': 1,      # Square root
    'abs': 1,       # Absolute value
    'ln': 1,        # Natural logarithm
    'log': 1,       # Base 10 logarithm
    'log2': 1,      # Base 2 logarithm
    'exp': 1,       # Exponential (e^x)
    'floor': 1,     # Floor
    'ceil': 1,      # Ceiling
    'round': 1,     # Round
    'fact': 1,      # Factorial
    # Trigonometric functions (work with radians)
    'sin': 1,       # Sine
    'cos': 1,       # Cosine
    'tan': 1,       # Tangent
    'cot': 1,       # Cotangent
    'sec': 1,       # Secant
    'csc': 1,       # Cosecant
    'asin': 1,      # Arcsine
    'acos': 1,      # Arccosine
    'atan': 1,      # Arctangent
    'acot': 1,      # Arccotangent
    'asec': 1,      # Arcsecant
    'acsc': 1,      # Arccosecant
    # Hyperbolic functions
    'sinh': 1,      # Hyperbolic sine
    'cosh': 1,      # Hyperbolic cosine
    'tanh': 1,      # Hyperbolic tangent
    'coth': 1,      # Hyperbolic cotangent
    'sech': 1,      # Hyperbolic secant
    'csch': 1,      # Hyperbolic cosecant
    'asinh': 1,     # Inverse hyperbolic sine
    'acosh': 1,     # Inverse hyperbolic cosine
    'atanh': 1,     # Inverse hyperbolic tangent
    'acoth': 1,     # Inverse hyperbolic cotangent
    'asech': 1,     # Inverse hyperbolic secant
    'acsch': 1,     # Inverse hyperbolic cosecant
    # Angle conversion
    'rad': 1,       # Degrees to radians
    'deg': 1,       # Radians to degrees
}

# Error messages in plain language
ERROR_MESSAGES = {
    'empty': 'Expression is empty',
    'invalid_char': 'Invalid character: {}',
    'unmatched_close': 'Extra closing parenthesis )',
    'unmatched_open': 'Unclosed parenthesis (',
    'empty_brackets': 'Empty parentheses ()',
    'two_operands': 'Two numbers/variables in a row',
    'two_operators': 'Two operators in a row',
    'starts_with_op': 'Expression starts with a binary operator',
    'ends_with_op': 'Expression ends with an operator',
    'op_after_open': 'Binary operator immediately after (',
    'close_after_op': 'Closing parenthesis ) after operator',
    'no_tokens': 'No data to process',
    'operand_after_close': 'Number/variable immediately after )',
    'open_after_operand': 'Opening parenthesis ( after number/variable without operator',
    'starts_with_close': 'Expression starts with )',
    'close_after_open': 'Closing parenthesis ) immediately after (',
    'invalid_function': 'Unknown function: {}',
    'function_without_paren': 'Function {} must be followed by (',
}

class ExpressionValidator:
    """Class for validating mathematical expressions"""
    
    @staticmethod
    def clean_expression(expression: str) -> str:
        """Cleans expression from extra spaces and comments"""
        # Remove comments (everything after #)
        if '#' in expression:
            expression = expression[:expression.index('#')]
        
        # Replace multiple spaces with one
        expression = ' '.join(expression.split())
        
        return expression.strip()
    
    @staticmethod
    def validate_expression(expression: str) -> Tuple[bool, Optional[str]]:
        """Checks expression correctness"""
        # Clean expression
        expression = ExpressionValidator.clean_expression(expression)
        
        if not expression:
            return False, ERROR_MESSAGES['empty']
        
        # Check allowed characters (updated to include new operators)
        allowed_pattern = r'^[0-9a-zA-Z\+\-\*/\^\%\(\)\.\s]+$'
        if not re.match(allowed_pattern, expression):
            # Find first invalid character
            for char in expression:
                if not re.match(r'[0-9a-zA-Z\+\-\*/\^\%\(\)\.\s]', char):
                    return False, ERROR_MESSAGES['invalid_char'].format(char)
        
        # Check parentheses
        bracket_count = 0
        for i, char in enumerate(expression):
            if char == '(':
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
                if bracket_count < 0:
                    return False, ERROR_MESSAGES['unmatched_close']
        
        if bracket_count > 0:
            return False, ERROR_MESSAGES['unmatched_open']
        
        return True, None
    
    @staticmethod
    def validate_tokens(tokens: List[str]) -> Tuple[bool, Optional[str]]:
        """Checks token sequence correctness"""
        if not tokens:
            return False, ERROR_MESSAGES['no_tokens']
        
        # Check for empty parentheses
        for i in range(len(tokens) - 1):
            if tokens[i] == '(' and tokens[i + 1] == ')':
                return False, ERROR_MESSAGES['empty_brackets']
        
        # Check sequence
        prev_token = None
        prev_type = None
        
        for i, token in enumerate(tokens):
            curr_type = get_token_type(token)
            
            # Check for unknown functions
            if curr_type == 'function' and token not in FUNCTIONS:
                return False, ERROR_MESSAGES['invalid_function'].format(token)
            
            # Function must be followed by (
            if curr_type == 'function':
                if i + 1 >= len(tokens) or tokens[i + 1] != '(':
                    return False, ERROR_MESSAGES['function_without_paren'].format(token)
            
            # Checks for operands (numbers and variables)
            if curr_type == 'operand':
                if prev_type == 'operand':
                    return False, ERROR_MESSAGES['two_operands']
                if prev_type == 'close':
                    return False, ERROR_MESSAGES['operand_after_close']
                    
            # Checks for binary operators
            elif curr_type == 'operator':
                # Allow unary minus/plus at start or after (, or operator
                if token in ['-', '+'] and (i == 0 or prev_type in ['open', 'operator']):
                    # This is a unary operator, it's OK
                    pass
                else:
                    if i == 0:
                        return False, ERROR_MESSAGES['starts_with_op']
                    if prev_type == 'operator':
                        # Allow unary after binary operator
                        if not (token in ['-', '+'] and prev_token not in ['-', '+']):
                            return False, ERROR_MESSAGES['two_operators']
                    if prev_type == 'open' and token not in ['-', '+']:
                        return False, ERROR_MESSAGES['op_after_open']
                    if i == len(tokens) - 1:
                        return False, ERROR_MESSAGES['ends_with_op']
                    
            # Checks for opening parenthesis
            elif token == '(':
                if prev_type == 'operand':
                    return False, ERROR_MESSAGES['open_after_operand']
                if prev_type == 'close':
                    return False, ERROR_MESSAGES['open_after_operand']
                    
            # Checks for closing parenthesis
            elif token == ')':
                if i == 0:
                    return False, ERROR_MESSAGES['starts_with_close']
                if prev_type == 'operator':
                    return False, ERROR_MESSAGES['close_after_op']
                if prev_type == 'open':
                    return False, ERROR_MESSAGES['close_after_open']
            
            prev_token = token
            prev_type = curr_type
        
        return True, None

def get_token_type(token: str) -> str:
    """Determines token type"""
    if token.replace('.', '').isdigit():
        return 'operand'
    elif token in FUNCTIONS:
        return 'function'
    elif token.isalpha():
        return 'operand'  # variable
    elif token in OPERATORS:
        return 'operator'
    elif token == '(':
        return 'open'
    elif token == ')':
        return 'close'
    return 'unknown'

def tokenize(expression: str) -> List[str]:
    """Splits expression into tokens"""
    # Clean expression
    expression = ExpressionValidator.clean_expression(expression)
    
    # Replace commas with dots for decimal numbers
    expression = expression.replace(',', '.')
    
    # First check for consecutive numbers separated by spaces
    # This is done before removing spaces to catch errors like "3 3"
    temp_tokens = []
    i = 0
    while i < len(expression):
        # Skip spaces
        if expression[i].isspace():
            i += 1
            continue
            
        # Match numbers
        if expression[i].isdigit() or (expression[i] == '.' and i + 1 < len(expression) and expression[i + 1].isdigit()):
            j = i
            while j < len(expression) and (expression[j].isdigit() or expression[j] == '.'):
                j += 1
            temp_tokens.append(('number', expression[i:j]))
            i = j
            
        # Match functions and variables
        elif expression[i].isalpha():
            j = i
            while j < len(expression) and expression[j].isalpha():
                j += 1
            temp_tokens.append(('alpha', expression[i:j]))
            i = j
            
        # Match operators
        elif i + 1 < len(expression) and expression[i:i+2] in ['**', '//']:
            temp_tokens.append(('operator', expression[i:i+2]))
            i += 2
        elif expression[i] in '+-*/^%()':
            temp_tokens.append(('operator', expression[i]))
            i += 1
        else:
            # Invalid character
            raise ValueError(ERROR_MESSAGES['invalid_char'].format(expression[i]))
    
    # Check for consecutive numbers
    for i in range(len(temp_tokens) - 1):
        if temp_tokens[i][0] == 'number' and temp_tokens[i+1][0] == 'number':
            # Two numbers in a row without operator
            # Create a more specific error message
            return None  # This will trigger an error in convert_to_rpn
    
    # Extract just the token values
    tokens = [token[1] for token in temp_tokens]
    
    return tokens

def infix_to_rpn(tokens: List[str]) -> List[str]:
    """
    Converts infix notation to Reverse Polish Notation (RPN)
    Uses Shunting Yard algorithm with support for unary operators and functions
    """
    output = []
    stack = []
    
    # Track if we expect unary operator
    expect_unary = True
    
    for i, token in enumerate(tokens):
        token_type = get_token_type(token)
        
        if token_type == 'operand':
            output.append(token)
            expect_unary = False
            
        elif token_type == 'function':
            stack.append(token)
            expect_unary = True
            
        elif token == '(':
            stack.append(token)
            expect_unary = True
            
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()  # Remove '('
                # If there's a function before (, pop it too
                if stack and stack[-1] in FUNCTIONS:
                    output.append(stack.pop())
            expect_unary = False
                
        elif token_type == 'operator':
            # Check if this is a unary operator
            if expect_unary and token in ['-', '+']:
                # Treat as unary operator
                stack.append('u' + token)  # u- for unary minus, u+ for unary plus
            else:
                # Binary operator
                priority, assoc = OPERATORS[token]
                
                while stack:
                    if stack[-1] in ['(', 'u-', 'u+']:
                        break
                    if stack[-1] in FUNCTIONS:
                        # Functions have highest priority
                        output.append(stack.pop())
                    elif stack[-1] in OPERATORS:
                        top_priority, top_assoc = OPERATORS[stack[-1]]
                        if (assoc == 'L' and top_priority >= priority) or \
                           (assoc == 'R' and top_priority > priority):
                            output.append(stack.pop())
                        else:
                            break
                    else:
                        break
                
                stack.append(token)
                expect_unary = True
    
    # Pop remaining operators
    while stack:
        output.append(stack.pop())
    
    return output

def evaluate_rpn(rpn_tokens: List[str], variables: Dict[str, Union[float, complex]] = None) -> Union[float, complex]:
    """Evaluates RPN expression value (supports complex numbers)"""
    if variables is None:
        variables = {}
    
    stack = []
    
    for token in rpn_tokens:
        if token.replace('.', '').isdigit():
            stack.append(float(token))
        elif token.isalpha() and token not in FUNCTIONS:
            if token in variables:
                stack.append(variables[token])
            else:
                raise ValueError(f"Variable {token} is not defined")
        elif token in OPERATORS:
            if len(stack) < 2:
                raise ValueError("Not enough values for operation")
            
            b = stack.pop()
            a = stack.pop()
            
            if token == '+':
                result = a + b
            elif token == '-':
                result = a - b
            elif token == '*':
                result = a * b
            elif token == '/':
                if b == 0:
                    raise ValueError("Division by zero")
                result = a / b
            elif token == '%':
                if b == 0:
                    raise ValueError("Division by zero")
                # For complex numbers, use fmod for real and imaginary parts
                if isinstance(a, complex) or isinstance(b, complex):
                    raise ValueError("Modulo operation not defined for complex numbers")
                result = a % b
            elif token == '//':
                if b == 0:
                    raise ValueError("Division by zero")
                # Floor division for complex numbers is not well-defined
                if isinstance(a, complex) or isinstance(b, complex):
                    raise ValueError("Floor division not defined for complex numbers")
                result = a // b
            elif token in ['^', '**']:
                result = a ** b
            
            stack.append(result)
            
        elif token in ['u-', 'u+']:
            # Unary operators
            if len(stack) < 1:
                raise ValueError("Not enough values for unary operation")
            
            a = stack.pop()
            if token == 'u-':
                result = -a
            else:  # u+
                result = +a
            
            stack.append(result)
            
        elif token in FUNCTIONS:
            if len(stack) < 1:
                raise ValueError(f"Not enough values for function {token}")
            
            a = stack.pop()
            
            # Math functions that work with complex numbers
            if token == 'sqrt':
                result = cmath.sqrt(a)
            elif token == 'abs':
                result = abs(a)
            elif token == 'ln':
                if a == 0:
                    raise ValueError("Logarithm of zero")
                result = cmath.log(a)
            elif token == 'log':
                if a == 0:
                    raise ValueError("Logarithm of zero")
                result = cmath.log10(a)
            elif token == 'log2':
                if a == 0:
                    raise ValueError("Logarithm of zero")
                result = cmath.log(a) / cmath.log(2)
            elif token == 'exp':
                result = cmath.exp(a)
            elif token == 'floor':
                if isinstance(a, complex):
                    raise ValueError("Floor not defined for complex numbers")
                result = math.floor(a)
            elif token == 'ceil':
                if isinstance(a, complex):
                    raise ValueError("Ceiling not defined for complex numbers")
                result = math.ceil(a)
            elif token == 'round':
                if isinstance(a, complex):
                    raise ValueError("Round not defined for complex numbers")
                result = round(a)
            elif token == 'fact':
                if isinstance(a, complex) or a < 0 or a != int(a):
                    raise ValueError("Factorial requires non-negative integer")
                result = math.factorial(int(a))
            # Trigonometric functions (work with complex)
            elif token == 'sin':
                result = cmath.sin(a)
            elif token == 'cos':
                result = cmath.cos(a)
            elif token == 'tan':
                result = cmath.tan(a)
            elif token == 'cot':
                tan_val = cmath.tan(a)
                if tan_val == 0:
                    raise ValueError("Cotangent undefined (tan = 0)")
                result = 1 / tan_val
            elif token == 'sec':
                cos_val = cmath.cos(a)
                if cos_val == 0:
                    raise ValueError("Secant undefined (cos = 0)")
                result = 1 / cos_val
            elif token == 'csc':
                sin_val = cmath.sin(a)
                if sin_val == 0:
                    raise ValueError("Cosecant undefined (sin = 0)")
                result = 1 / sin_val
            elif token == 'asin':
                result = cmath.asin(a)
            elif token == 'acos':
                result = cmath.acos(a)
            elif token == 'atan':
                result = cmath.atan(a)
            elif token == 'acot':
                if a == 0:
                    result = math.pi / 2
                else:
                    result = cmath.atan(1 / a)
            elif token == 'asec':
                if a == 0:
                    raise ValueError("Arcsecant undefined at 0")
                result = cmath.acos(1 / a)
            elif token == 'acsc':
                if a == 0:
                    raise ValueError("Arccosecant undefined at 0")
                result = cmath.asin(1 / a)
            # Hyperbolic functions
            elif token == 'sinh':
                result = cmath.sinh(a)
            elif token == 'cosh':
                result = cmath.cosh(a)
            elif token == 'tanh':
                result = cmath.tanh(a)
            elif token == 'coth':
                if a == 0:
                    raise ValueError("Hyperbolic cotangent undefined at 0")
                result = 1 / cmath.tanh(a)
            elif token == 'sech':
                result = 1 / cmath.cosh(a)
            elif token == 'csch':
                if a == 0:
                    raise ValueError("Hyperbolic cosecant undefined at 0")
                result = 1 / cmath.sinh(a)
            elif token == 'asinh':
                result = cmath.asinh(a)
            elif token == 'acosh':
                result = cmath.acosh(a)
            elif token == 'atanh':
                result = cmath.atanh(a)
            elif token == 'acoth':
                if a == 0:
                    raise ValueError("Inverse hyperbolic cotangent undefined at 0")
                result = cmath.atanh(1 / a)
            elif token == 'asech':
                if a == 0:
                    raise ValueError("Inverse hyperbolic secant undefined at 0")
                result = cmath.acosh(1 / a)
            elif token == 'acsch':
                if a == 0:
                    raise ValueError("Inverse hyperbolic cosecant undefined at 0")
                result = cmath.asinh(1 / a)
            # Angle conversion
            elif token == 'rad':
                if isinstance(a, complex):
                    raise ValueError("Angle conversion not defined for complex numbers")
                result = math.radians(a)
            elif token == 'deg':
                if isinstance(a, complex):
                    raise ValueError("Angle conversion not defined for complex numbers")
                result = math.degrees(a)
            
            stack.append(result)
    
    if len(stack) != 1:
        raise ValueError("Invalid expression")
    
    return stack[0]

def convert_to_rpn(expression: str) -> Tuple[bool, Optional[List[str]], Optional[str]]:
    """
    Main conversion function with validation
    
    Returns:
        (success, result_in_rpn, error_message)
    """
    try:
        # Validate expression
        valid, error = ExpressionValidator.validate_expression(expression)
        if not valid:
            return False, None, error
        
        # Tokenization
        tokens = tokenize(expression)
        
        # Check if tokenization failed (consecutive numbers detected)
        if tokens is None:
            return False, None, ERROR_MESSAGES['two_operands']
        
        # Validate tokens
        valid, error = ExpressionValidator.validate_tokens(tokens)
        if not valid:
            return False, None, error
        
        # Convert to RPN
        rpn = infix_to_rpn(tokens)
        
        return True, rpn, None
        
    except Exception as e:
        # Handle unexpected errors
        error_msg = str(e)
        if len(error_msg) > 50:
            error_msg = "Error processing expression"
        return False, None, error_msg

def interactive_mode():
    """Interactive mode"""
    print("=== Extended Polish Notation (RPN) Converter ===")
    print("Supported:")
    print("  - Numbers: 123, 3.14, 2j, 3+4j (complex)")
    print("  - Variables: a, x, price")
    print("  - Binary operators: + - * / % // ^ **")
    print("  - Unary operators: - + (unary minus/plus)")
    print("  - Math functions: sqrt, abs, ln, log, log2, exp")
    print("                   floor, ceil, round, fact")
    print("  - Trig functions: sin, cos, tan, cot, sec, csc")
    print("                   asin, acos, atan, acot, asec, acsc")
    print("  - Hyperbolic:    sinh, cosh, tanh, coth, sech, csch")
    print("                   asinh, acosh, atanh, acoth, asech, acsch")
    print("  - Angle convert: rad (deg→rad), deg (rad→deg)")
    print("  - Constants:     pi, e, j (imaginary unit)")
    print("  - Parentheses: ( )")
    print("  - Comments: # text")
    print("\nExamples:")
    print("  sin(pi/2)     # = 1")
    print("  cot(pi/4)     # = 1")
    print("  sqrt(-1)      # = 1j (imaginary)")
    print("  (3+4j)^2      # complex power")
    print("\nCommands:")
    print("  set variable value - set value")
    print("  vars - show variables")
    print("  clear - clear variables")
    print("  quit - exit")
    print("-" * 50)
    
    # Initialize with mathematical constants
    variables = {
        'pi': math.pi,
        'e': math.e,
        'PI': math.pi,  # Alternative notation
        'E': math.e,    # Alternative notation
    }
    print("\nPredefined constants: pi (π ≈ 3.14159), e (≈ 2.71828)")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            # Commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Exit")
                break
            
            if user_input.lower() == 'vars':
                if variables:
                    print("Variables:")
                    for var, val in sorted(variables.items()):
                        print(f"  {var} = {val}")
                else:
                    print("No variables")
                continue
            
            if user_input.lower() == 'clear':
                # Keep mathematical constants
                variables = {
                    'pi': math.pi,
                    'e': math.e,
                    'PI': math.pi,
                    'E': math.e,
                }
                print("Variables cleared (constants pi, e kept)")
                continue
            
            if user_input.lower().startswith('set '):
                parts = user_input.split()
                if len(parts) >= 3:
                    var_name = parts[1]
                    try:
                        var_value = float(parts[2])
                        variables[var_name] = var_value
                        print(f"OK: {var_name} = {var_value}")
                    except ValueError:
                        print("Error: value must be a number")
                else:
                    print("Format: set variable value")
                continue
            
            if not user_input:
                continue
            
            # Conversion
            success, rpn, error = convert_to_rpn(user_input)
            
            if success:
                print(f"Infix:  {user_input}")
                print(f"RPN:    {' '.join(rpn)}")
                
                # Try to evaluate
                try:
                    result = evaluate_rpn(rpn, variables)
                    print(f"Result: {result}")
                except ValueError as e:
                    if "is not defined" in str(e):
                        undefined_vars = [t for t in rpn if t.isalpha() and t not in FUNCTIONS and t not in variables]
                        if undefined_vars:
                            print(f"Need values: {', '.join(undefined_vars)}")
                            print("Use: set variable value")
                    else:
                        print(f"Error: {e}")
            else:
                print(f"Error: {error}")
                
        except KeyboardInterrupt:
            print("\nInterrupted")
            break
        except Exception as e:
            print(f"Error: {e}")

def format_result(value: Union[float, complex]) -> str:
    """Formats the result for display, handling complex numbers nicely"""
    if isinstance(value, complex):
        if value.imag == 0:
            # Pure real number
            return str(value.real)
        elif value.real == 0:
            # Pure imaginary number
            return f"{value.imag}j"
        else:
            # Full complex number
            if value.imag >= 0:
                return f"{value.real} + {value.imag}j"
            else:
                return f"{value.real} - {abs(value.imag)}j"
    else:
        return str(value)

def evaluate_with_random_variables(expression: str, variables: Dict[str, Union[float, complex]], 
                                 rnd_min: float = -10, rnd_max: float = 10) -> Optional[Union[float, complex]]:
    """
    Evaluates expression with random values for undefined variables
    """
    success, rpn, error = convert_to_rpn(expression)
    if not success:
        print(f"Conversion error: {error}")
        return None
    
    # Find undefined variables
    undefined_vars = set()
    for token in rpn:
        if token.isalpha() and token not in FUNCTIONS and token not in variables:
            undefined_vars.add(token)
    
    # Generate random values for undefined variables
    for var in undefined_vars:
        value = random.uniform(rnd_min, rnd_max)
        variables[var] = value
        print(f"Random value: {var} = {value:.6f}")
    
    try:
        result = evaluate_rpn(rpn, variables)
        return result
    except ValueError as e:
        print(f"Evaluation error: {e}")
        return None

def main():
    """Main function with command line support"""
    parser = argparse.ArgumentParser(
        description='RPN Calculator Engine - converts infix to RPN and evaluates expressions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  python %(prog)s                           # Interactive mode
  python %(prog)s -v "2+3*4"               # Evaluate expression
  python %(prog)s -v "x^2+y" -min 0 -max 5 # With random variables
  python %(prog)s -v "sin(pi/2)"           # Trigonometric functions
        '''
    )
    
    parser.add_argument("--value", "-v", dest="value", type=str, default=None,
                        help="Expression to evaluate (if not provided, starts interactive mode)")
    parser.add_argument("--rnd_min", "-min", dest="rnd_min", type=float, default=-10,
                        help="Minimum value for random variables (default: -10)")
    parser.add_argument("--rnd_max", "-max", dest="rnd_max", type=float, default=10,
                        help="Maximum value for random variables (default: 10)")
    parser.add_argument("--no-eval", "-n", dest="no_eval", action="store_true",
                        help="Only convert to RPN without evaluation")
    
    args = parser.parse_args()
    
    # If no expression provided, start interactive mode
    if args.value is None:
        interactive_mode()
        return
    
    # Command line mode
    input_expr = args.value
    print(f"Input expression: {input_expr}")
    
    # Convert to RPN
    success, rpn, error = convert_to_rpn(input_expr)
    
    if not success:
        print(f"Error: {error}")
        return
    
    print(f"RPN notation: {' '.join(rpn)}")
    
    # If no evaluation requested, stop here
    if args.no_eval:
        return
    
    # Initialize variables with constants
    variables = {
        'pi': math.pi,
        'e': math.e,
        'PI': math.pi,
        'E': math.e,
    }
    
    # Evaluate with random variables if needed
    result = evaluate_with_random_variables(input_expr, variables, args.rnd_min, args.rnd_max)
    
    if result is not None:
        print(f"Result: {result}")

if __name__ == "__main__":
    main()