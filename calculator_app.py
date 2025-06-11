import tkinter as tk
from tkinter import messagebox
from sympy import sympify, SympifyError
import math
import re

# --- backend логіка ---

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
        expr_str = expr_str.replace('arcsin', 'asin').replace('arccos', 'acos') \
            .replace('arctan', 'atan').replace('arccot', 'acot')

        expr = sympify(expr_str)
        free_syms = expr.free_symbols

        if len(free_syms) == 0:
            return f"Результат: {expr.evalf()}"

        elif len(free_syms) == 1:
            var = list(free_syms)[0]
            start, end = rng
            results = []
            x = start
            while x <= end:
                val = round(x, 4)
                y = expr.evalf(subs={var: val})
                results.append((val, y))
                x += 0.01
            return results

        else:
            return f"Помилка: очікується лише одна змінна, знайдено: {', '.join(map(str, free_syms))}"

    except SympifyError as e:
        return f"Помилка у виразі: {e}"

# --- графічний інтерфейс ---

class Plotter:
    def __init__(self, root):
        self.root = root
        self.root.title("Графічний калькулятор")
        self.root.geometry("850x600")
        self.root.configure(bg="#f0f0f0")

        tk.Label(root, text="Введіть функцію f(x):", font=("Segoe UI", 12)).pack(pady=(10, 0))

        self.e_func = tk.Entry(root, font=("Segoe UI", 14), width=40)
        self.e_func.pack(pady=5)

        frame = tk.Frame(root, bg="#f0f0f0")
        frame.pack(pady=5)

        tk.Label(frame, text="Від X =", font=("Segoe UI", 12)).pack(side="left", padx=(0, 5))
        self.e_min = tk.Entry(frame, width=6)
        self.e_min.insert(0, "-10")
        self.e_min.pack(side="left", padx=(0, 10))

        tk.Label(frame, text="До X =", font=("Segoe UI", 12)).pack(side="left", padx=(0, 5))
        self.e_max = tk.Entry(frame, width=6)
        self.e_max.insert(0, "10")
        self.e_max.pack(side="left")

        tk.Button(root, text="Побудувати графік", font=("Segoe UI", 12, "bold"),
                  command=self.plot).pack(pady=10)

        self.canvas = tk.Canvas(root, bg="white", height=450, width=800)
        self.canvas.pack(pady=10)

    def plot(self):
        func = self.e_func.get().strip()

        try:
            xmin = float(self.e_min.get())
            xmax = float(self.e_max.get())
            if xmin >= xmax:
                raise ValueError("xmin має бути менше xmax")
        except ValueError:
            messagebox.showerror("Помилка", "Некоректні межі X.")
            return

        error = validate_expression(func)
        if error:
            messagebox.showerror("Помилка", error)
            return

        result = process_with_sympy(func, (xmin, xmax))
        if isinstance(result, str):
            messagebox.showinfo("Результат", result)
            return

        self.canvas.delete("all")

        w, h = int(self.canvas["width"]), int(self.canvas["height"])
        margin = 50
        pw, ph = w - 2 * margin, h - 2 * margin

        raw_points = []
        for x, y in result:
            try:
                fy = float(y)
                if not math.isnan(fy) and not math.isinf(fy):
                    raw_points.append((x, fy))
            except:
                continue

        if not raw_points:
            messagebox.showerror("Помилка", "Неможливо побудувати графік.")
            return

        # 🔧 Масштабуємо за адекватними y (відфільтрованими)
        visible_points = [y for x, y in raw_points if abs(y) < 20]
        if not visible_points:
            messagebox.showerror("Помилка", "Значення функції виходять за межі графіку.")
            return

        ymin = min(visible_points)
        ymax = max(visible_points)
        if ymin == ymax:
            ymin -= 1
            ymax += 1

        def to_canvas(x, y):
            cx = margin + (x - xmin) / (xmax - xmin) * pw
            cy = margin + (ymax - y) / (ymax - ymin) * ph
            return (cx, cy)

        # 📏 Сегментування — щоб уникнути стрибків
        segments = []
        segment = []

        for i in range(len(raw_points)):
            x, y = raw_points[i]
            if segment:
                y_prev = segment[-1][1]
                if abs(y - y_prev) > 10:
                    if len(segment) >= 2:
                        segments.append(segment)
                    segment = []
            segment.append((x, y))

        if len(segment) >= 2:
            segments.append(segment)

        self.draw_grid(w, h, margin, xmin, xmax, ymin, ymax)

        for seg in segments:
            coords = []
            for x, y in seg:
                coords.extend(to_canvas(x, y))
            if len(coords) >= 4:
                self.canvas.create_line(coords, fill="blue", width=2, smooth=True)

        self.canvas.create_text(w//2, 20, text=f"f(x) = {func}", font=("Segoe UI", 14, "bold"), fill="black")

    def draw_grid(self, w, h, margin, xmin, xmax, ymin, ymax):
        pw, ph = w - 2 * margin, h - 2 * margin
        step_x = pw / 10
        step_y = ph / 10

        for i in range(11):
            x = margin + i * step_x
            val = xmin + i * (xmax - xmin) / 10
            self.canvas.create_line(x, margin, x, margin + ph, fill="#ddd")
            self.canvas.create_text(x, margin + ph + 15, text=f"{val:.1f}", font=("Segoe UI", 8))

        for i in range(11):
            y = margin + i * step_y
            val = ymax - i * (ymax - ymin) / 10
            self.canvas.create_line(margin, y, margin + pw, y, fill="#ddd")
            self.canvas.create_text(margin - 25, y, text=f"{val:.1f}", font=("Segoe UI", 8))

        if ymin < 0 < ymax:
            y0 = margin + (ymax - 0) / (ymax - ymin) * ph
            self.canvas.create_line(margin, y0, margin + pw, y0, fill="black", width=2)

        if xmin < 0 < xmax:
            x0 = margin + (-xmin) / (xmax - xmin) * pw
            self.canvas.create_line(x0, margin, x0, margin + ph, fill="black", width=2)

def main():
    root = tk.Tk()
    app = Plotter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
