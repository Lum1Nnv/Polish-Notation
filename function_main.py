#!/usr/bin/env python3
"""
Преобразование инфиксной нотации в обратную польскую (RPN)
с улучшенной валидацией и понятными сообщениями об ошибках
"""

import re
from typing import List, Tuple, Optional, Dict

# Приоритеты операторов
OPERATORS = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
}

# Сообщения об ошибках на простом языке
ERROR_MESSAGES = {
    'empty': 'Выражение пустое',
    'invalid_char': 'Недопустимый символ: {}',
    'unmatched_close': 'Лишняя закрывающая скобка )',
    'unmatched_open': 'Не закрыта скобка (',
    'empty_brackets': 'Пустые скобки ()',
    'two_operands': 'Два числа/переменные подряд',
    'two_operators': 'Два оператора подряд',
    'starts_with_op': 'Выражение начинается с оператора',
    'ends_with_op': 'Выражение заканчивается оператором',
    'op_after_open': 'Оператор сразу после (',
    'close_after_op': 'Закрывающая скобка ) после оператора',
    'no_tokens': 'Нет данных для обработки',
    'operand_after_close': 'Число/переменная сразу после )',
    'open_after_operand': 'Открывающая скобка ( после числа/переменной',
    'starts_with_close': 'Выражение начинается с )',
    'close_after_open': 'Закрывающая скобка ) сразу после (',
}

class ExpressionValidator:
    """Класс для валидации математических выражений"""
    
    @staticmethod
    def clean_expression(expression: str) -> str:
        """Очищает выражение от лишних пробелов и комментариев"""
        # Удаляем комментарии (всё после #)
        if '#' in expression:
            expression = expression[:expression.index('#')]
        
        # Заменяем множественные пробелы на один
        expression = ' '.join(expression.split())
        
        # Удаляем пробелы вокруг операторов и скобок
        for char in '+-*/()':
            expression = expression.replace(f' {char} ', char)
            expression = expression.replace(f' {char}', char)
            expression = expression.replace(f'{char} ', char)
        
        return expression.strip()
    
    @staticmethod
    def validate_expression(expression: str) -> Tuple[bool, Optional[str]]:
        """Проверяет корректность выражения"""
        # Очищаем выражение
        expression = ExpressionValidator.clean_expression(expression)
        
        if not expression:
            return False, ERROR_MESSAGES['empty']
        
        # Проверка допустимых символов
        allowed_pattern = r'^[0-9a-zA-Z\+\-\*/\(\)\.\s]+$'
        if not re.match(allowed_pattern, expression):
            # Находим первый недопустимый символ
            for char in expression:
                if not re.match(r'[0-9a-zA-Z\+\-\*/\(\)\.\s]', char):
                    return False, ERROR_MESSAGES['invalid_char'].format(char)
        
        # Проверка скобок
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
        """Проверяет корректность последовательности токенов"""
        if not tokens:
            return False, ERROR_MESSAGES['no_tokens']
        
        # Проверка на пустые скобки
        for i in range(len(tokens) - 1):
            if tokens[i] == '(' and tokens[i + 1] == ')':
                return False, ERROR_MESSAGES['empty_brackets']
        
        # Проверка последовательности
        prev_token = None
        prev_type = None
        
        for i, token in enumerate(tokens):
            curr_type = get_token_type(token)
            
            # Проверки для операндов (числа и переменные)
            if curr_type == 'operand':
                if prev_type == 'operand':
                    return False, ERROR_MESSAGES['two_operands']
                if prev_type == 'close':
                    return False, ERROR_MESSAGES['operand_after_close']
                    
            # Проверки для операторов
            elif curr_type == 'operator':
                if i == 0:
                    return False, ERROR_MESSAGES['starts_with_op']
                if prev_type == 'operator':
                    return False, ERROR_MESSAGES['two_operators']
                if prev_type == 'open':
                    return False, ERROR_MESSAGES['op_after_open']
                if i == len(tokens) - 1:
                    return False, ERROR_MESSAGES['ends_with_op']
                    
            # Проверки для открывающей скобки
            elif token == '(':
                if prev_type == 'operand':
                    return False, ERROR_MESSAGES['open_after_operand']
                if prev_type == 'close':
                    return False, ERROR_MESSAGES['open_after_operand']
                    
            # Проверки для закрывающей скобки
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
    """Определяет тип токена"""
    if token.replace('.', '').isdigit() or token.isalpha():
        return 'operand'
    elif token in OPERATORS:
        return 'operator'
    elif token == '(':
        return 'open'
    elif token == ')':
        return 'close'
    return 'unknown'

def tokenize(expression: str) -> List[str]:
    """Разбивает выражение на токены"""
    # Очищаем выражение
    expression = ExpressionValidator.clean_expression(expression)
    
    # Заменяем запятые на точки для десятичных чисел
    expression = expression.replace(',', '.')
    
    # Удаляем все пробелы для упрощения токенизации
    expression = expression.replace(' ', '')
    
    # Регулярное выражение для поиска токенов
    # Поддерживаем: числа (целые и дробные), переменные (последовательности букв), операторы
    pattern = r'(\d+\.?\d*|[a-zA-Z]+|[+\-*/()])'
    tokens = re.findall(pattern, expression)
    
    # Проверка, что всё выражение было разобрано
    reconstructed = ''.join(tokens)
    if reconstructed != expression:
        # Находим, что не удалось разобрать
        for i, char in enumerate(expression):
            if i >= len(reconstructed) or char != reconstructed[i]:
                raise ValueError(ERROR_MESSAGES['invalid_char'].format(char))
    
    return tokens

def infix_to_rpn(tokens: List[str]) -> List[str]:
    """
    Преобразует инфиксную нотацию в обратную польскую (RPN)
    Использует алгоритм Shunting Yard
    """
    output = []
    stack = []
    
    for token in tokens:
        token_type = get_token_type(token)
        
        if token_type == 'operand':
            output.append(token)
            
        elif token == '(':
            stack.append(token)
            
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            if stack:
                stack.pop()  # Удаляем '('
                
        elif token_type == 'operator':
            while (stack and 
                   stack[-1] != '(' and 
                   stack[-1] in OPERATORS and
                   OPERATORS[stack[-1]] >= OPERATORS[token]):
                output.append(stack.pop())
            stack.append(token)
    
    # Выталкиваем оставшиеся операторы
    while stack:
        output.append(stack.pop())
    
    return output

def convert_to_rpn(expression: str) -> Tuple[bool, Optional[List[str]], Optional[str]]:
    """
    Главная функция преобразования с валидацией
    
    Returns:
        (успех, результат_в_rpn, сообщение_об_ошибке)
    """
    try:
        # Валидация выражения
        valid, error = ExpressionValidator.validate_expression(expression)
        if not valid:
            return False, None, error
        
        # Токенизация
        tokens = tokenize(expression)
        
        # Валидация токенов
        valid, error = ExpressionValidator.validate_tokens(tokens)
        if not valid:
            return False, None, error
        
        # Преобразование в RPN
        rpn = infix_to_rpn(tokens)
        
        return True, rpn, None
        
    except Exception as e:
        # Обработка непредвиденных ошибок
        error_msg = str(e)
        if len(error_msg) > 50:
            error_msg = "Ошибка обработки выражения"
        return False, None, error_msg

def evaluate_rpn(rpn_tokens: List[str], variables: Dict[str, float] = None) -> float:
    """Вычисляет значение выражения в RPN"""
    if variables is None:
        variables = {}
    
    stack = []
    
    for token in rpn_tokens:
        if token.replace('.', '').isdigit():
            stack.append(float(token))
        elif token.isalpha():
            if token in variables:
                stack.append(variables[token])
            else:
                raise ValueError(f"Переменная {token} не определена")
        elif token in OPERATORS:
            if len(stack) < 2:
                raise ValueError("Недостаточно значений для операции")
            
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
                    raise ValueError("Деление на ноль")
                result = a / b
            
            stack.append(result)
    
    if len(stack) != 1:
        raise ValueError("Некорректное выражение")
    
    return stack[0]

def main():
    """Интерактивный режим работы"""
    print("=== Конвертер в польскую нотацию (RPN) ===")
    print("Поддерживается:")
    print("  - Числа: 123, 3.14")
    print("  - Переменные: a, x, price")
    print("  - Операторы: + - * /")
    print("  - Скобки: ( )")
    print("  - Комментарии: # текст")
    print("\nКоманды:")
    print("  set переменная значение - задать значение")
    print("  vars - показать переменные")
    print("  clear - очистить переменные")
    print("  quit - выход")
    print("-" * 45)
    
    variables = {}
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            # Команды
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Выход")
                break
            
            if user_input.lower() == 'vars':
                if variables:
                    print("Переменные:")
                    for var, val in sorted(variables.items()):
                        print(f"  {var} = {val}")
                else:
                    print("Нет переменных")
                continue
            
            if user_input.lower() == 'clear':
                variables.clear()
                print("Переменные очищены")
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
                        print("Ошибка: значение должно быть числом")
                else:
                    print("Формат: set переменная значение")
                continue
            
            if not user_input:
                continue
            
            # Преобразование
            success, rpn, error = convert_to_rpn(user_input)
            
            if success:
                print(f"Инфикс: {user_input}")
                print(f"RPN:    {' '.join(rpn)}")
                
                # Попытка вычислить
                try:
                    result = evaluate_rpn(rpn, variables)
                    print(f"Результат: {result}")
                except ValueError as e:
                    if "не определена" in str(e):
                        undefined_vars = [t for t in rpn if t.isalpha() and t not in variables]
                        if undefined_vars:
                            print(f"Нужны значения: {', '.join(undefined_vars)}")
                            print("Используйте: set переменная значение")
                    else:
                        print(f"Ошибка: {e}")
            else:
                print(f"Ошибка: {error}")
                
        except KeyboardInterrupt:
            print("\nПрервано")
            break
        except Exception as e:
            print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()