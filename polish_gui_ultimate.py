import tkinter as tk
from tkinter import ttk, messagebox
import math
import re
from sympy import sympify, Symbol, sin, cos, tan, log, sqrt, asin, acos, atan
from sympy.core.sympify import SympifyError
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

# Пріоритети операторів
precedence = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
    '%': 3,
}

class FunctionSelector:
    """Селектор функцій"""
    
    FUNCTIONS = {
        'Базові': {
            'x^2': 'x^2',
            'x^3': 'x^3', 
            'x^2+2*x+1': 'x^2+2*x+1',
            '√x': 'sqrt(x)',
            '1/x': '1/x',
            'x': 'x'
        },
        'Тригонометричні': {
            'sin(x)': 'sin(x)',
            'cos(x)': 'cos(x)',
            'tan(x)': 'tan(x)',
            'cot(x)': 'cot(x)',
            'sin(2x)': 'sin(2*x)',
            'cos(x/2)': 'cos(x/2)'
        },
        'Обернені тригонометричні': {
            'arcsin(x)': 'asin(x)',
            'arccos(x)': 'acos(x)',
            'arctan(x)': 'atan(x)',
            'arccot(x)': 'acot(x)'
        },
        'Логарифмічні': {
            'ln(x)': 'log(x)',
            'log₁₀(x)': 'log(x)/log(10)',
            'log₂(x)': 'log(x)/log(2)'
        }
    }
    
    def __init__(self, parent, callback):
        self.callback = callback
        self.create_selector(parent)
    
    def create_selector(self, parent):
        selector_frame = tk.Frame(parent, bg="#1E1E1E")
        selector_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(selector_frame, text="Швидкий вибір функції:", 
                 foreground="white", background="#1E1E1E").pack(anchor="w", pady=(0, 5))
        
        for category, functions in self.FUNCTIONS.items():
            cat_frame = tk.Frame(selector_frame, bg="#1E1E1E")
            cat_frame.pack(fill="x", pady=2)
            
            ttk.Label(cat_frame, text=f"{category}:", 
                     foreground="lightgray", background="#1E1E1E").pack(side="left", padx=(0, 10))
            
            for display_name, func_code in functions.items():
                btn = tk.Button(cat_frame, text=display_name, 
                              command=lambda f=func_code: self.callback(f),
                              bg="#404040", fg="white", font=("Segoe UI", 9),
                              relief="flat", padx=8, pady=2)
                btn.pack(side="left", padx=2)
                btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#505050"))
                btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#404040"))

class Plotter:
    def __init__(self, root, width=900, height=700):
        self.root = root
        self.root.title("Графіки функцій")
        self.root.geometry(f"{width}x{height}")
        self.root.configure(bg="#1E1E1E")
        self.xmin, self.xmax, self.tab = -10, 10, 0
        self.root.state('zoomed')

        self.create_menu()
        self.setup_styles()
        self.create_interface()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=5, 
                       background="#2E2E2E", foreground="white")
        style.configure("Accent.TButton", background="#28a745", foreground="white")
        style.configure("TLabel", background="#1E1E1E", foreground="white")
        style.configure("TEntry", fieldbackground="#2E2E2E", foreground="white")
        style.configure("TNotebook", background="#1E1E1E", borderwidth=0)
        style.configure("TNotebook.Tab", background="#404040", foreground="white", padding=[12, 8])
        style.map("TNotebook.Tab", background=[("selected", "#28a745")])

    def create_interface(self):
        main_frame = tk.Frame(self.root, bg="#1E1E1E")
        main_frame.pack(fill="both", expand=1, padx=15, pady=15)

        FunctionSelector(main_frame, self.select_function)
        self.create_control_panel(main_frame)
        
        # Create notebook for tabs
        self.nb = ttk.Notebook(main_frame)
        self.nb.pack(fill="both", expand=1)

    def create_control_panel(self, parent):
        control_frame = tk.Frame(parent, bg="#1E1E1E")
        control_frame.pack(fill="x", pady=(0, 10))

        top_row = tk.Frame(control_frame, bg="#1E1E1E")
        top_row.pack(fill="x", pady=(0, 5))

        ttk.Label(top_row, text="f(x):").pack(side="left", padx=(0, 5))
        self.e_func = ttk.Entry(top_row, width=30, font=("Segoe UI", 11))
        self.e_func.pack(side="left", padx=5)

        bottom_row = tk.Frame(control_frame, bg="#1E1E1E")
        bottom_row.pack(fill="x")

        range_frame = tk.Frame(bottom_row, bg="#1E1E1E")
        range_frame.pack(side="left")

        ttk.Label(range_frame, text="Від:").pack(side="left", padx=(0, 5))
        self.e_min = ttk.Entry(range_frame, width=8)
        self.e_min.pack(side="left", padx=(0, 10))
        self.e_min.insert(0, str(self.xmin))

        ttk.Label(range_frame, text="До:").pack(side="left", padx=(0, 5))
        self.e_max = ttk.Entry(range_frame, width=8)
        self.e_max.pack(side="left", padx=(0, 15))
        self.e_max.insert(0, str(self.xmax))

        button_frame = tk.Frame(bottom_row, bg="#1E1E1E")
        button_frame.pack(side="left")

        ttk.Button(button_frame, text="✓ Валідація", 
                  command=self.validate_input, style="Accent.TButton").pack(side="left", padx=2)
        ttk.Button(button_frame, text="⇨ Префікс", 
                  command=self.show_prefix, style="Accent.TButton").pack(side="left", padx=2)
        ttk.Button(button_frame, text="∑ Обчислити", 
                  command=self.show_result, style="Accent.TButton").pack(side="left", padx=2)
        ttk.Button(button_frame, text="📈 Побудувати", 
                  command=self.plot_expression, style="Accent.TButton").pack(side="left", padx=2)
        ttk.Button(button_frame, text="🗑 Очистити", 
                  command=self.clear_function).pack(side="left", padx=2)
        ttk.Button(button_frame, text="❌ Закрити вкладку", 
                  command=self.close_current_tab).pack(side="left", padx=2)

    def select_function(self, func_code):
        self.e_func.delete(0, tk.END)
        self.e_func.insert(0, func_code)

    def clear_function(self):
        self.e_func.delete(0, tk.END)

    def close_current_tab(self):
        """Закрити поточну активну вкладку"""
        try:
            current_tab = self.nb.select()
            if current_tab:
                self.nb.forget(current_tab)
        except tk.TclError:
            pass  # Немає вкладок для закриття

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Закрити всі вкладки", command=self.close_all_tabs)
        file_menu.add_separator()
        file_menu.add_command(label="Вихід", command=self.root.quit)
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Довідка", menu=help_menu)
        help_menu.add_command(label="Про програму", command=self.show_about)

    def close_all_tabs(self):
        for tab_id in self.nb.tabs()[:]:
            self.nb.forget(tab_id)

    def show_about(self):
        messagebox.showinfo("Про програму", 
                           "Калькулятор функцій v2.0\n\n"
                           "Можливості:\n"
                           "• Побудова графіків функцій\n"
                           "• Валідація виразів\n"
                           "• Конвертація в префіксну форму\n"
                           "• Обчислення значень\n"
                           "• Швидкий вибір функцій\n"
                           "• Керування вкладками\n"
                           "118", 
                           parent=self.root)

    def make_tab(self, func=""):
        tab = tk.Frame(self.nb, bg="#2E2E2E")
        canvas = tk.Frame(tab, bg="#2E2E2E")
        canvas.pack(fill="both", expand=1)
        
        # Add tab with cleaner name
        tab_name = func[:15] + "..." if len(func) > 15 else func
        self.nb.add(tab, text=tab_name)
        self.nb.select(tab)
        
        tab.canvas, tab.function = canvas, func
        self.tab += 1
        self.plot(canvas, func)

    def plot_expression(self):
        func = self.e_func.get().strip()
        if not func:
            messagebox.showwarning("Попередження", "Введіть функцію!", parent=self.root)
            return
        error = self.validate_expression(func)
        if error:
            messagebox.showerror("Помилка", error, icon="error", parent=self.root)
            return
        self.make_tab(func)

    def get_asymptotes(self, func):
        """Знайти асимптоти та точки розриву для тригонометричних функцій"""
        asymptotes = []
        
        if 'tan(' in func:
            n_start = math.ceil((self.xmin - math.pi/2) / math.pi)
            n_end = math.floor((self.xmax - math.pi/2) / math.pi)
            for n in range(n_start, n_end + 1):
                asymptote = math.pi/2 + n * math.pi
                if self.xmin <= asymptote <= self.xmax:
                    asymptotes.append(asymptote)
        
        if 'cot(' in func:
            n_start = math.ceil(self.xmin / math.pi)
            n_end = math.floor(self.xmax / math.pi)
            for n in range(n_start, n_end + 1):
                asymptote = n * math.pi
                if self.xmin <= asymptote <= self.xmax:
                    asymptotes.append(asymptote)
        
        # arccot has no vertical asymptotes
        return asymptotes

    def plot(self, canvas, func):
        try:
            xmin, xmax = float(self.e_min.get()), float(self.e_max.get())
            if xmin >= xmax:
                messagebox.showerror("Помилка", "x_min має бути менше x_max!", parent=self.root)
                return

            # Встановлення стилю seaborn
            sns.set_style("darkgrid", {"axes.facecolor": "#2E2E2E", "figure.facecolor": "#2E2E2E"})
            
            # Створення фігури
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            
            # Отримати асимптоти
            asymptotes = self.get_asymptotes(func)
            
            # Побудова графіка
            x_vals = np.linspace(xmin, xmax, 10000)
            self.plot_with_asymptotes(ax, x_vals, func, asymptotes)
            
            # Налаштування стилів
            ax.set_title(f"f(x) = {func}", color='white', fontsize=14, pad=10)
            ax.set_xlabel("x", color='white', fontsize=12)
            ax.set_ylabel("f(x)", color='white', fontsize=12)
            ax.tick_params(colors='white', labelsize=10)
            ax.grid(True, which="both", linestyle='--', linewidth=0.7, alpha=0.7, color='gray')
            ax.axhline(y=0, color='white', linewidth=2.5, zorder=0)
            ax.axvline(x=0, color='white', linewidth=2.5, zorder=0)
            
            # Встановлення меж
            ax.set_xlim(xmin, xmax)
            if 'tan(' in func or 'cot(' in func:
                ax.set_ylim(-10, 10)
            else:
                # Динамічне масштабування по осі Y
                y_vals = np.array([self.safe_eval(func, x) for x in x_vals])
                valid_y = y_vals[np.isfinite(y_vals)]
                if valid_y.size > 0:
                    y_range = np.ptp(valid_y) if np.ptp(valid_y) > 0 else 1
                    y_center = np.mean(valid_y)
                    margin = y_range * 0.1 or 1
                    ax.set_ylim(y_center - y_range/2 - margin, y_center + y_range/2 + margin)
            
            # Додавання асимптот
            for asymptote in asymptotes:
                ax.axvline(x=asymptote, color='red', linestyle='--', alpha=0.7, linewidth=1)
            
            plt.tight_layout()

            # Очищення попереднього вмісту канви
            for child in canvas.winfo_children():
                child.destroy()

            # Інтеграція з Tkinter
            graph = FigureCanvasTkAgg(fig, master=canvas)
            graph.get_tk_widget().pack(fill="both", expand=True)
            
            # Додавання панелі навігації
            toolbar = NavigationToolbar2Tk(graph, canvas)
            toolbar.update()
            toolbar.pack(side=tk.TOP, fill=tk.X)

            # Прив'язка подій прокрутки миші
            graph.get_tk_widget().bind("<MouseWheel>", lambda event: self.zoom(event, ax, graph))
            graph.get_tk_widget().bind("<Button-4>", lambda event: self.zoom(event, ax, graph))  # Для Linux
            graph.get_tk_widget().bind("<Button-5>", lambda event: self.zoom(event, ax, graph))  # Для Linux

            graph.draw()

        except ValueError as e:
            messagebox.showerror("Помилка", f"Невалідне значення меж: {str(e)}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося виглядати графіку: {str(e)}", parent=self.root)

    def zoom(self, event, ax, canvas):
        # Фактор масштабування
        zoom_factor = 1.1 if event.delta > 0 or event.num == 4 else 0.9 if event.delta < 0 or event.num == 5 else 1.0
        
        # Поточні межі осей
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        # Центр графіку
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        # Нові межі після масштабування
        x_range = (x_max - x_min) * zoom_factor
        y_range = (y_max - y_min) * zoom_factor
        
        # Оновлення меж графіка
        new_x_min = x_center - x_range / 2
        new_x_max = x_center + x_range / 2
        ax.set_xlim(new_x_min, new_x_max)
        ax.set_ylim(y_center - y_range / 2, y_center + y_range / 2)
        
        # Оновлення полів "Від" і "До"
        self.e_min.delete(0, tk.END)
        self.e_min.insert(0, f"{new_x_min:.2f}")
        self.e_max.delete(0, tk.END)
        self.e_max.insert(0, f"{new_x_max:.2f}")
        
        canvas.draw()

    def plot_with_asymptotes(self, ax, x_vals, func, asymptotes):
        """Малювання функції з урахуванням асимптот та точок розриву"""
        split_points = sorted(asymptotes + [x_vals[0] - 1, x_vals[-1] + 1]) if asymptotes else [x_vals[0] - 1, x_vals[-1] + 1]
        segments = []
        tolerance = (x_vals[-1] - x_vals[0]) / 10000
        
        # Створення сегментів між асимптотами
        for i in range(len(split_points) - 1):
            start, end = split_points[i], split_points[i + 1]
            start_idx = np.searchsorted(x_vals, start, side='right')
            end_idx = np.searchsorted(x_vals, end, side='left')
            
            if start_idx < end_idx and start_idx < len(x_vals) and end_idx > 0:
                if i > 0:
                    start_val = split_points[i] + tolerance
                    start_idx = np.searchsorted(x_vals, start_val, side='right')
                if i < len(split_points) - 2:
                    end_val = split_points[i + 1] - tolerance
                    end_idx = np.searchsorted(x_vals, end_val, side='left')
                
                if start_idx < end_idx:
                    segments.append((start_idx, end_idx))
        
        # Побудова сегментів
        for start_idx, end_idx in segments:
            x_segment = x_vals[start_idx:end_idx]
            if len(x_segment) == 0:
                continue
            
            y_segment = np.array([self.safe_eval(func, x) for x in x_segment])
            valid_mask = np.logical_not(np.isnan(y_segment)) & (np.abs(y_segment) < 10000)
            
            if np.any(valid_mask):
                x_valid = x_segment[valid_mask]
                y_valid = y_segment[valid_mask]
                if len(x_valid) > 1:
                    ax.plot(x_valid, y_valid, color='cyan', linewidth=2, label=f"f(x) = {func}" if start_idx == segments[0][0] else "")
        
        if segments:
            ax.legend(loc='best', fontsize=10, facecolor='#2E2E2E', edgecolor='white', labelcolor='white')

    def safe_eval(self, expr, x):
        try:
            # Preprocessing: replace function names and operators
            expr = expr.replace('^', '**')
        
            # Handle logarithmic functions first (before arcsin/arccos replacements)
            expr = expr.replace('ln(', 'log(')  # ln -> log (natural log)
            expr = expr.replace('log₁₀(', 'log10(')  # log base 10
            expr = expr.replace('log₂(', 'log2(')   # log base 2
        
            # Handle inverse trig functions
            expr = expr.replace('arcsin(', 'asin(')
            expr = expr.replace('arccos(', 'acos(')
            expr = expr.replace('arctan(', 'atan(')
            expr = expr.replace('arccot(', 'acot(')

            # Safe function dictionary
            safe_locals = {
                "x": x,
                "abs": abs,
                "pow": pow,
                "pi": math.pi,  
                "e": math.e,
                "sin": math.sin,
                "cos": math.cos,
                "tan": lambda val: math.tan(val) if abs(math.cos(val)) > 1e-10 else float('nan'),
                "cot": lambda val: 1/math.tan(val) if abs(math.sin(val)) > 1e-10 else float('nan'),
                "asin": lambda val: math.asin(val) if -1 <= val <= 1 else float('nan'),
                "acos": lambda val: math.acos(val) if -1 <= val <= 1 else float('nan'),
                "atan": math.atan,
                "acot": lambda val: math.pi/2 - math.atan(val),
                "log": lambda val: math.log(val) if val > 0 else float('nan'),  # Natural log
                "log10": lambda val: math.log10(val) if val > 0 else float('nan'),  # Log base 10
                "log2": lambda val: math.log2(val) if val > 0 else float('nan'),   # Log base 2
                "sqrt": lambda val: math.sqrt(val) if val >= 0 else float('nan'),
                "exp": lambda val: math.exp(val) if abs(val) < 700 else (float('inf') if val > 0 else 0)
            }

            # Evaluate expression
            result = eval(expr, {"__builtins__": {}}, safe_locals)
        
            # Check and return result
            if isinstance(result, (int, float)):
                if math.isnan(result) or math.isinf(result):
                    return float('nan')  # Return NaN for undefined or infinite results
                elif abs(result) > 1e6:  # Limit very large values
                    return float('nan')
                else:
                    return round(result, 6)
            else:
                return float('nan')
            
        except (ZeroDivisionError, ValueError, OverflowError, TypeError, SyntaxError):
            return float('nan')
        except Exception:
            return float('nan')

    def validate_input(self):
        expr = self.e_func.get().strip()
        if not expr:
            messagebox.showwarning("Попередження", "Введіть функцію!", parent=self.root)
            return
        error = self.validate_expression(expr)
        if error:
            messagebox.showerror("Помилка", error, icon="error", parent=self.root)
        else:
            messagebox.showinfo("Успіх", "Вираз валідний!", parent=self.root)

    def validate_expression(self, expr):
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
            expr = (expr.replace('^', '**')
                       .replace('arcsin', 'asin')
                       .replace('arccos', 'acos')
                       .replace('arctan', 'atan')
                       .replace('arccot', 'acot')
                       .replace('cot', '1/tan'))
            sympify(expr, locals={'x': Symbol('x'), 'cot': 1/Symbol('tan')})
        except (SympifyError, SyntaxError):
            return "Помилка: синтаксична помилка у виразі."
        return None

    def infix_to_prefix(self, expression):
        def is_operator(token):
            return token in precedence

        def greater_precedence(op1, op2):
            return precedence[op1] >= precedence[op2]

        def tokenize(expr):
            tokens = []
            i = 0
            funcs = {'sin', 'cos', 'tan', 'cot', 'log', 'asin', 'acos', 'atan', 'acot', 'sqrt', 'exp'}
            while i < len(expr):
                if expr[i].isspace():
                    i += 1
                    continue
                if expr[i].isalpha():
                    ident = ''
                    while i < len(expr) and expr[i].isalpha():
                        ident += expr[i]
                        i += 1
                    if ident in funcs:
                        if i < len(expr) and expr[i] == '(':
                            tokens.append(ident)
                        else:
                            tokens.append(ident)
                    else:
                        tokens.append(ident)
                    continue
                if expr[i].isdigit() or expr[i] == '.':
                    num = ''
                    while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                        num += expr[i]
                        i += 1
                    tokens.append(num)
                    continue
                if expr[i] in '+-*/%^()':
                    tokens.append(expr[i])
                    i += 1
                    continue
                raise ValueError(f"Невідомий символ: {expr[i]}")
            return tokens

        def to_prefix(tokens):
            stack = []
            output = []
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token.isalnum() or re.match(r'^\d+\.?\d*$', token) or token == 'x':
                    output.append(token)
                elif token in {'sin', 'cos', 'tan', 'cot', 'log', 'asin', 'acos', 'atan', 'acot', 'sqrt', 'exp'}:
                    stack.append(token)
                elif token == '(':
                    stack.append(token)
                elif token == ')':
                    while stack and stack[-1] != '(':
                        output.append(stack.pop())
                    if stack and stack[-1] == '(':
                        stack.pop()
                        if stack and stack[-1] in {'sin', 'cos', 'tan', 'cot', 'log', 'asin', 'acos', 'atan', 'acot', 'sqrt', 'exp'}:
                            output.append(stack.pop())
                elif is_operator(token):
                    while (stack and stack[-1] != '(' and 
                           greater_precedence(stack[-1], token)):
                        output.append(stack.pop())
                    stack.append(token)
                i += 1
            while stack:
                output.append(stack.pop())
            # Reverse to get prefix notation
            return ' '.join(reversed(output))

        try:
            tokens = tokenize(expression)
            return to_prefix(tokens)
        except Exception as e:
            raise ValueError(f"Помилка при конвертації: {e}")

    def process_with_sympy(self, expr_str, rng):
        try:
            start, end = rng
            results = []
        
            # Обчислюємо рівно 100 значень
            num_points = 100
            step = (end - start) / (num_points - 1) if num_points > 1 else 0
        
            # Перевіряємо, чи є в виразі змінна x
            if 'x' not in expr_str:
                try:
                    result_value = self.safe_eval(expr_str, 0)
                    if result_value is not None and not math.isnan(result_value):
                        return f"Результат: {result_value}"
                    else:
                        return "Помилка: не вдалося обчислити константу"
                except Exception as e:
                    return f"Помилка при обчисленні константи: {str(e)}"
        
            # Обчислення для функції з змінною x
            for i in range(num_points):
                x_val = start + i * step
                val = round(x_val, 2)
            
                try:
                    y = self.safe_eval(expr_str, x_val)
                    if y is not None and not math.isnan(y):
                        results.append((val, y))
                except Exception:
                    continue
        
            return results if results else "Помилка: функція не визначена в заданому діапазоні"
        
        except Exception as e:
            return f"Помилка при обчисленні: {str(e)}"

    def show_prefix(self):
        expr = self.e_func.get().strip()
        if not expr:
            messagebox.showwarning("Попередження", "Введіть функцію!", parent=self.root)
            return
        error = self.validate_expression(expr)
        if error:
            messagebox.showerror("Помилка", error, icon="error", parent=self.root)
            return
        try:
            prefix_expr = self.infix_to_prefix(expr)
            messagebox.showinfo("Префіксна форма", f"Префіксна форма: {prefix_expr}", parent=self.root)
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при конвертації: {str(e)}", icon="error", parent=self.root)

    def show_result(self):
        expr = self.e_func.get().strip()
        if not expr:
            messagebox.showwarning("Попередження", "Введіть функцію!", parent=self.root)
            return
        error = self.validate_expression(expr)
        if error:
            messagebox.showerror("Помилка", error, icon="error", parent=self.root)
            return
        try:
            rng = (float(self.e_min.get()), float(self.e_max.get()))
            result = self.process_with_sympy(expr, rng)
            if isinstance(result, str):
                messagebox.showinfo("Результат", result, parent=self.root)
            else:
                formatted_results = []
                for x, y in result[:10]:
                    if y is None or math.isnan(y):
                        y_str = "не визначено"
                    elif math.isinf(y):
                        y_str = "∞" if y > 0 else "-∞"
                    elif isinstance(y, complex):
                        if abs(y.imag) < 1e-10:
                            y_str = f"{y.real:.4f}"
                        else:
                            y_str = f"{y.real:.4f} + {y.imag:.4f}i"
                    elif isinstance(y, (int, float)):
                        y_str = f"{y:.4f}"
                    else:
                        y_str = str(y)
                    formatted_results.append(f"x={x:.2f}, y={y_str}")
            
                result_text = "\n".join(formatted_results)
                if len(result) > 10:
                    result_text += f"\n... та ще {len(result)-10} значень"
            
                messagebox.showinfo("Результати обчислень", result_text, parent=self.root)
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка при обчисленні: {str(e)}", icon="error", parent=self.root)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Калькулятор для обчислення виразів та координат')
    parser.add_argument("--value", "-v", dest="value", type=str, default="sin(x)")
    parser.add_argument("--rng", nargs=2, type=float, metavar=('START', 'END'), default=[-10.0, 10.0])
    args = parser.parse_args()
    input_expr = args.value
    rng = args.rng

    root = tk.Tk()
    app = Plotter(root)
    app.e_func.insert(0, input_expr)
    app.e_min.delete(0, tk.END)
    app.e_max.delete(0, tk.END)
    app.e_min.insert(0, str(rng[0]))
    app.e_max.insert(0, str(rng[1]))
    app.plot_expression()
    root.mainloop()