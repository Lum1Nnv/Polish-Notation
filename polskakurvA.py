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
        current = ''
        for char in expr:
            if char.isalnum():  # буква або цифра
                current += char
            else:
                if current:
                    tokens.append(current)
                    current = ''
                if char in "+-*/%^()":
                    tokens.append(char)
        if current:
            tokens.append(current)
        return tokens

    def to_prefix(tokens):
        ops = []
        vals = []

        for token in tokens:
            if token.isalnum():
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

<<<<<<< HEAD

def validate_expression(expr):
    # 1. Перевірка балансу дужок
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

    # 2. Порожні дужки
    if re.search(r'\(\s*\)', expr):
        return "Помилка: порожні дужки."

    # 3. Подвійні оператори
    if re.search(r'[+\-*/%^]{2,}', expr):
        return "Помилка: два або більше операторів підряд."

    # 4. Початок або кінець виразу — оператор
    if re.match(r'^[+\-*/%^]', expr.strip()) or re.search(r'[+\-*/%^]$', expr.strip()):
        return "Помилка: вираз починається або закінчується оператором."

    # 5. Спроба символьного парсингу
    try:
        sympify(expr)
    except (SympifyError, SyntaxError):
        return "Помилка: синтаксична помилка у виразі."

    return None  # якщо все ок

=======
# Обчислення алгебраїчного виразу з sympy
import random
from sympy import sympify, simplify, expand
from sympy.core.sympify import SympifyError
import re
>>>>>>> 77227cc861e0a608fe51d0bc60d61dd215b2d6ca

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
            answer = input("Бажаєте ввести значення для змінних? (так/ні): ").strip().lower()

            if answer in ['так', 'y', 'yes', 'т']:
                method = input("Ввести значення вручну чи згенерувати випадково? (вручну/рандом): ").strip().lower()
                values = {}

                if method in ['рандом', 'random','r','р']:
                    for var in free_syms:
                        val = random.uniform(rnd_min, rnd_max)  # змінити діапазон за бажанням
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
<<<<<<< HEAD
    parser.add_argument("--value", "-v", dest="value", type=str, default="x+2")
=======
    parser.add_argument("--value", "-v", dest="value", type=str, default="x^(1/2)")
>>>>>>> 77227cc861e0a608fe51d0bc60d61dd215b2d6ca
    parser.add_argument("--rnd_min", "-min", dest="rnd_min", type=float, default= -10)
    parser.add_argument("--rnd_max", "-max", dest="rnd_max", type=float, default= 10)
    args = parser.parse_args()
    rnd_min = (args.rnd_min)
    rnd_max = (args.rnd_max)
<<<<<<< HEAD
    input_expr = args.value

    validation_error = validate_expression(input_expr)
    if validation_error:
        print(validation_error)
        exit(1)
=======
>>>>>>> 77227cc861e0a608fe51d0bc60d61dd215b2d6ca

    input_expr = args.value
    print(f"Отримано вираз: {input_expr}")

    prefix_expr = infix_to_prefix(input_expr)
    print(f"Префіксна нотація: {prefix_expr}")

    result = process_with_sympy(input_expr)
    print(result)
