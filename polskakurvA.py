import argparse
from sympy import sympify, simplify, expand
from sympy.core.sympify import SympifyError
import re

# Пріоритети операторів
precedence = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
    '%': 3,
}

# Перетворення інфіксного виразу в префіксний
def infix_to_prefix(expression):
    def is_operator(token):
        return token in precedence

    def greater_precedence(op1, op2):
        return precedence[op1] >= precedence[op2]

    def tokenize(expr):
        tokens = []
        i = 0
        supported_functions = {'sin', 'cos','tan','cot','log','asin','acot','acos','atan'}

        while i < len(expr):
            if expr[i].isspace():
                i += 1
                continue

            if expr[i].isalpha():
                identifier = ''
                while i < len(expr) and expr[i].isalpha():
                    identifier += expr[i]
                    i += 1

                if identifier in supported_functions and i < len(expr) and expr[i] == '(':
                    i += 1
                    count = 1
                    arg = ''
                    while i < len(expr) and count > 0:
                        if expr[i] == '(':
                            count += 1
                        elif expr[i] == ')':
                            count -= 1
                        arg += expr[i] if count > 0 else ''
                        i += 1
                    tokens.append(f"{identifier}({arg})")
                else:
                    tokens.append(identifier)
                continue

            if expr[i].isdigit() or expr[i] == '.':
                num = ''
                has_dot = False
                while i < len(expr) and (expr[i].isdigit() or (expr[i] == '.' and not has_dot)):
                    if expr[i] == '.':
                        has_dot = True
                    num += expr[i]
                    i += 1
                tokens.append(num)
                continue

            if expr[i] in "+-*/%^()":
                tokens.append(expr[i])
                i += 1
                continue

            raise ValueError(f"Невідомий символ: {expr[i]}")

        return tokens

    def to_prefix(tokens):
        ops = []
        vals = []

        for token in tokens:
            if token.isalnum() or re.match(r'^(sin|cos|tan|cot|log|asin|acos|atan|acot)\(.+\)$', token) or re.match(r'^-?\d*\.?\d*$', token):
                vals.append(token)
            elif token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    op = ops.pop()
                    b = vals.pop()
                    a = vals.pop()
                    vals.append(f"{op} {a} {b}")
                ops.pop()
            elif is_operator(token):
                while ops and ops[-1] != '(' and greater_precedence(ops[-1], token):
                    op = ops.pop()
                    b = vals.pop()
                    a = vals.pop()
                    vals.append(f"{op} {a} {b}")
                ops.append(token)

        while ops:
            op = ops.pop()
            b = vals.pop()
            a = vals.pop()
            vals.append(f"{op} {a} {b}")

        return vals[0]

    tokens = tokenize(expression)
    return to_prefix(tokens)

def validate_expression(expr):
    stack = []
    for char in expr:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                return "Помилка: зайва закриваюча дужка."
            stack.pop()
    if stack:
        return "Помилка: незакрита дужка."

    if re.search(r'\(\s*\)', expr):
        return "Помилка: порожні дужки."

    if re.search(r'[+\-*/%^]{2,}', expr):
        return "Помилка: два або більше операторів підряд."

    if re.match(r'^[+\-*/%^]', expr.strip()) or re.search(r'[+\-*/%^]$', expr.strip()):
        return "Помилка: вираз починається або закінчується оператором."

    try:
        sympify(expr)
    except (SympifyError, SyntaxError):
        return "Помилка: синтаксична помилка у виразі."

    return None

def process_with_sympy(expr_str, rng):
    try:
        if re.search(r'[+\-*/]{2,}', expr_str):
            return "Помилка: два знаки оператора підряд."
        expr_str = expr_str.replace('arcsin', 'asin')
        expr_str = expr_str.replace('arccos', 'acos')
        expr_str = expr_str.replace('arctan', 'atan')
        expr_str = expr_str.replace('arccot', 'acot')
        expr = sympify(expr_str)
        free_syms = expr.free_symbols

        if expr.has('Divide') and expr.is_zero:
            return "Помилка: ділення на нуль."

        if len(free_syms) == 0:
            return f"Результат: {expr.evalf()}"

        elif len(free_syms) == 1:
            var = list(free_syms)[0]
            start, end = rng
            results = []
            x = start
            while x <= end:
                val = round(x, 2)
                y = expr.evalf(subs={var: val})
                results.append((val, y))
                x += 0.01
            return results

        else:
            return f"Помилка: очікується лише одна змінна, знайдено: {', '.join(map(str, free_syms))}"

    except SympifyError as e:
        return f"Помилка у виразі: {e}"

# Головна частина
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Калькулятор для обчислення виразів та координат')
    parser.add_argument("--value", "-v", dest="value", type=str, default="sin(x)")
    parser.add_argument("--rng", nargs=2, type=float, metavar=('START', 'END'), default=[0.0, 1.0])
    args = parser.parse_args()
    input_expr = args.value
    rng = args.rng

    validation_error = validate_expression(input_expr)
    if validation_error:
        print(validation_error)
        exit(1)

    print(f"Отримано вираз: {input_expr}")
    prefix_expr = infix_to_prefix(input_expr)
    print(f"Префіксна нотація: {prefix_expr}")
    result = process_with_sympy(input_expr, rng)

    if isinstance(result, list):
        print("Координати (x -> y):")
        for x, y in result:
            print(f"{x:.2f} -> {y}")
    else:
        print(result)