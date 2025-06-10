import argparse
from sympy import sympify, simplify, expand
from sympy.core.sympify import SympifyError
import re
import random

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
        supported_functions = {'sin', 'cos', 'tan', 'cot', 'log'}

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
                    # Рекурсивно обробляємо аргумент функції
                    tokens.append(f"{identifier}({infix_to_prefix(arg)})")
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
            # Якщо токен є числом, змінною або функцією
            if (token.isalnum() or re.match(r'^(sin|cos|tan|cot|log)\(.+\)$', token) or 
                re.match(r'^-?\d*\.?\d*$', token)):
                vals.append(token)
            elif token == '(':
                ops.append(token)
            elif token == ')':
                while ops and ops[-1] != '(':
                    op = ops.pop()
                    b = vals.pop()
                    a = vals.pop()
                    vals.append(f"{op} {a} {b}")
                ops.pop()  # Видалити '('
                # Якщо перед '(' була функція, обробляємо її
                if ops and ops[-1] in {'sin', 'cos', 'tan', 'cot', 'log'}:
                    func = ops.pop()
                    arg = vals.pop()
                    vals.append(f"{func}({arg})")
            elif is_operator(token):
                while ops and ops[-1] != '(' and greater_precedence(ops[-1], token):
                    op = ops.pop()
                    b = vals.pop()
                    a = vals.pop()
                    vals.append(f"{op} {a} {b}")
                ops.append(token)
            # Обробка функцій як операторів
            elif token in {'sin', 'cos', 'tan', 'cot', 'log'}:
                ops.append(token)

        while ops:
            op = ops.pop()
            if op in {'sin', 'cos', 'tan', 'cot', 'log'}:
                arg = vals.pop()
                vals.append(f"{op}({arg})")
            else:
                b = vals.pop()
                a = vals.pop()
                vals.append(f"{op} {a} {b}")

        return vals[0]


    # Видаляємо зовнішні дужки, якщо вони є
    expr = expression.strip()
    if expr.startswith('(') and expr.endswith(')'):
        count = 0
        for i, char in enumerate(expr):
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
            if count == 0 and i < len(expr) - 1:
                break
        else:
            expr = expr[1:-1]

    tokens = tokenize(expr)
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

def process_with_sympy(expr_str):
    try:
        if re.search(r'[+\-*/]{2,}', expr_str):
            return "Помилка: два знаки оператора підряд."

        expr = sympify(expr_str)
        free_syms = expr.free_symbols

        if expr.has('Divide') and expr.is_zero:
            return "Помилка: ділення на нуль."

        if len(free_syms) == 0:
            return f"Результат: {expr.evalf()}"

        else:
            print("У виразі є змінні:", ', '.join(map(str, free_syms)))
            answer = input("Бажаєте ввести значення для змінних? (y/n): ").strip().lower()

            if answer in ['так', 'y', 'yes', 'т']:
                method = input("Ввести значення вручну чи згенерувати випадково? (y/n): ").strip().lower()
                values = {}

                if method in ['рандом', 'random', 'r', 'р', 'y', 'yes']:
                    for var in free_syms:
                        val = random.uniform(rnd_min, rnd_max)
                        print(f"{var} = {val:.2f} (згенеровано)")
                        values[var] = val
                else:
                    for var in free_syms:
                        val = input(f"Введіть значення для {var}: ").strip()
                        try:
                            values[var] = float(val)
                        except ValueError:
                            return f"Помилка: недійсне значення для {var}"

                evaluated = expr.evalf(subs=values)
                return f"Результат з підставленими значеннями: {evaluated}"

            else:
                if len(free_syms) == 1:
                    return f"Спростили: {expand(expr)}"
                else:
                    return f"Спростили: {simplify(expr)}"

    except SympifyError as e:
        return f"Помилка у виразі: {e}"

# Головна частина
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Двіжок для калькулятора')
    parser.add_argument("--value", "-v", dest="value", type=str, default="sin(sin((2+x)*x))")
    parser.add_argument("--rnd_min", "-min", dest="rnd_min", type=float, default=-10)
    parser.add_argument("--rnd_max", "-max", dest="rnd_max", type=float, default=10)
    args = parser.parse_args()
    rnd_min = args.rnd_min
    rnd_max = args.rnd_max
    input_expr = args.value

    validation_error = validate_expression(input_expr)
    if validation_error:
        print(validation_error)
        exit(1)

    print(f"Отримано вираз: {input_expr}")
    prefix_expr = infix_to_prefix(input_expr)
    print(f"Префіксна нотація: {prefix_expr}")
    result = process_with_sympy(input_expr)
    print(result)
