import customtkinter as ctk
from tkinter import messagebox
from sympy import sympify, SympifyError
import math
import re

# Налаштування теми додатку
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Сучасна колірна палітра 2025
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#4CAF50',
    'warning': '#FF7043',
    'error': '#E53935',
    'background': '#1A1A1A',
    'surface': '#2D2D2D',
    'text_primary': '#FFFFFF',
    'text_secondary': '#B0B0B0',
    'accent': '#7EBC59'
}

# --- backend логіка (оригінальна) ---

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

# --- сучасний графічний інтерфейс ---

class Plotter:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Графічний калькулятор 2025")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Центрування вікна
        self.center_window()
        
        # Створення інтерфейсу
        self.create_modern_ui()

    def center_window(self):
        """Центрування вікна на екрані"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")

    def create_modern_ui(self):
        """Створення сучасного інтерфейсу"""
        # Головний контейнер
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            main_frame,
            text="📊 Графічний Калькулятор",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Картка вводу
        input_card = ctk.CTkFrame(
            main_frame,
            fg_color=COLORS['surface'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['primary']
        )
        input_card.pack(fill="x", pady=(0, 20))
        
        # Підзаголовок
        ctk.CTkLabel(
            input_card,
            text="Введіть функцію f(x):",
            font=ctk.CTkFont(size=16),
            text_color=COLORS['text_secondary']
        ).pack(pady=(20, 5))

        # Поле вводу функції
        self.e_func = ctk.CTkEntry(
            input_card,
            placeholder_text="Наприклад: x**2 + 2*x - 1",
            font=ctk.CTkFont(size=14),
            height=40,
            corner_radius=8
        )
        self.e_func.pack(fill="x", padx=20, pady=(0, 15))

        # Фрейм для діапазону
        range_frame = ctk.CTkFrame(input_card, fg_color="transparent")
        range_frame.pack(pady=(0, 15))

        ctk.CTkLabel(
            range_frame,
            text="Діапазон:",
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        ).pack(pady=(0, 8))

        # Контейнер для полів діапазону
        range_container = ctk.CTkFrame(range_frame, fg_color="transparent")
        range_container.pack()

        ctk.CTkLabel(range_container, text="Від X =", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        self.e_min = ctk.CTkEntry(range_container, width=80, height=32)
        self.e_min.insert(0, "-10")
        self.e_min.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(range_container, text="До X =", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 5))
        self.e_max = ctk.CTkEntry(range_container, width=80, height=32)
        self.e_max.insert(0, "10")
        self.e_max.pack(side="left")

        # Кнопка побудови
        plot_btn = ctk.CTkButton(
            input_card,
            text="🚀 Побудувати графік",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            corner_radius=12,
            fg_color=COLORS['primary'],
            hover_color=COLORS['secondary'],
            command=self.plot
        )
        plot_btn.pack(pady=(0, 20))

        # Картка для графіка
        graph_card = ctk.CTkFrame(
            main_frame,
            fg_color=COLORS['surface'],
            corner_radius=16,
            border_width=1,
            border_color=COLORS['accent']
        )
        graph_card.pack(fill="both", expand=True)

        # Заголовок графіка
        ctk.CTkLabel(
            graph_card,
            text="📈 Графік функції",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS['accent']
        ).pack(pady=(15, 5))

        # Канвас для графіка
        self.canvas = ctk.CTkCanvas(
            graph_card,
            bg=COLORS['background'],
            highlightthickness=0,
            height=400
        )
        self.canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def plot(self):
        """Побудова графіка (оригінальна логіка з сучасною візуалізацією)"""
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

        w, h = int(self.canvas.winfo_width()) or 800, int(self.canvas.winfo_height()) or 400
        margin = 60
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

        # Масштабування (оригінальна логіка) з відладкою
        visible_points = [y for x, y in raw_points if abs(y) < 50]  # Збільшив ліміт з 20 до 50
        if not visible_points:
            messagebox.showerror("Помилка", "Значення функції виходять за межі графіку.")
            return

        ymin = min(visible_points)
        ymax = max(visible_points)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
            
        print(f"Побудова графіка: {len(raw_points)} точок, ymin={ymin:.2f}, ymax={ymax:.2f}")

        def to_canvas(x, y):
            cx = margin + (x - xmin) / (xmax - xmin) * pw
            cy = margin + (ymax - y) / (ymax - ymin) * ph
            return (cx, cy)

        # Сегментування (оригінальна логіка) з відладкою
        segments = []
        segment = []

        for i in range(len(raw_points)):
            x, y = raw_points[i]
            if segment:
                y_prev = segment[-1][1]
                if abs(y - y_prev) > 20:  # Збільшив поріг з 10 до 20
                    if len(segment) >= 2:
                        segments.append(segment)
                    segment = []
            segment.append((x, y))

        if len(segment) >= 2:
            segments.append(segment)
            
        print(f"Створено сегментів: {len(segments)}")

        # Сучасна сітка
        self.draw_modern_grid(w, h, margin, xmin, xmax, ymin, ymax)
        
        # Тестова лінія для перевірки роботи canvas
        self.canvas.create_line(margin, margin, margin + pw, margin + ph, 
                               fill="#FF0000", width=3, tags="test")

        # Малювання графіка з яскравими кольорами та відладкою
        for i, seg in enumerate(segments):
            coords = []
            for x, y in seg:
                coords.extend(to_canvas(x, y))
            if len(coords) >= 4:
                print(f"Малюю сегмент {i}: {len(coords)//2} точок")
                # Основна лінія - яскрава та добре видима
                self.canvas.create_line(coords, fill="#00BFFF", width=4, smooth=True, capstyle="round")
                
                # Додаткова обводка для кращої видимості
                self.canvas.create_line(coords, fill="#FFFFFF", width=2, smooth=True)
        
        # Видаляємо тестову лінію
        self.canvas.delete("test")

        # Заголовок функції
        self.canvas.create_text(w//2, 25, text=f"f(x) = {func}", 
                               font=("SF Pro Display", 16, "bold"), fill=COLORS['accent'])

    def draw_modern_grid(self, w, h, margin, xmin, xmax, ymin, ymax):
        """Сучасна сітка"""
        pw, ph = w - 2 * margin, h - 2 * margin
        
        # Сітка
        for i in range(11):
            x = margin + i * pw / 10
            val = xmin + i * (xmax - xmin) / 10
            
            # Вертикальні лінії
            self.canvas.create_line(x, margin, x, margin + ph, fill="#444444", width=1)
            self.canvas.create_text(x, margin + ph + 15, text=f"{val:.1f}", 
                                  font=("SF Pro Text", 10), fill=COLORS['text_secondary'])

            y = margin + i * ph / 10
            val = ymax - i * (ymax - ymin) / 10
            
            # Горизонтальні лінії
            self.canvas.create_line(margin, y, margin + pw, y, fill="#444444", width=1)
            self.canvas.create_text(margin - 25, y, text=f"{val:.1f}", 
                                  font=("SF Pro Text", 10), fill=COLORS['text_secondary'])

        # Головні осі
        if ymin < 0 < ymax:
            y0 = margin + (ymax - 0) / (ymax - ymin) * ph
            self.canvas.create_line(margin, y0, margin + pw, y0, fill=COLORS['text_primary'], width=2)

        if xmin < 0 < xmax:
            x0 = margin + (-xmin) / (xmax - xmin) * pw
            self.canvas.create_line(x0, margin, x0, margin + ph, fill=COLORS['text_primary'], width=2)

def main():
    root = ctk.CTk()
    app = Plotter(root)
    root.mainloop()

if __name__ == "__main__":
    # Перевірка CustomTkinter
    try:
        import customtkinter as ctk
    except ImportError:
        print("❌ Для роботи потрібно встановити CustomTkinter:")
        print("pip install customtkinter")
        exit(1)
        
    main()