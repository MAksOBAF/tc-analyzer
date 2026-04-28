import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import analyzer, charts

# Цветовая палитра
APP_BG = "#0f0f12"
SIDEBAR_BG = "#16161a"
CARD_BG = "#1e1e26"
ACCENT = "#bb86fc"

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value, subtext="", icon="📊"):
        super().__init__(master, fg_color=CARD_BG, corner_radius=15)
        self.pack(side="left", expand=True, fill="both", padx=10)
        
        ctk.CTkLabel(self, text=f"{icon}  {title}", font=("Segoe UI", 13), text_color="#aaaaaa").pack(pady=(15, 0), padx=20, anchor="w")
        self.val_lbl = ctk.CTkLabel(self, text=value, font=("Segoe UI", 26, "bold"))
        self.val_lbl.pack(pady=(5, 0), padx=20, anchor="w")
        self.sub_lbl = ctk.CTkLabel(self, text=subtext, font=("Segoe UI", 11), text_color=ACCENT)
        self.sub_lbl.pack(pady=(0, 15), padx=20, anchor="w")

class CustomProgressBar(ctk.CTkFrame):
    def __init__(self, master, title, value_str, pct, color):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="x", pady=8, padx=20)
        
        # Текст над баром
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x")
        ctk.CTkLabel(top_frame, text=title, font=("Segoe UI", 12), text_color="#dddddd").pack(side="left")
        ctk.CTkLabel(top_frame, text=value_str, font=("Segoe UI", 12, "bold"), text_color=color).pack(side="right")
        
        # Сам бар
        bar = ctk.CTkProgressBar(self, height=8, progress_color=color, fg_color="#2a2a35")
        bar.pack(fill="x", pady=(5,0))
        bar.set(pct)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Telegram Analyzer Pro")
        self.geometry("1400x900")
        ctk.set_appearance_mode("dark")
        
        self.data_global = None
        
        # Главная сетка (Sidebar + Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === SIDEBAR ===
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SIDEBAR_BG)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="TC ANALYZER", font=("Segoe UI", 22, "bold"), text_color=ACCENT).pack(pady=35)

        ctk.CTkButton(self.sidebar, text="📂 Загрузить JSON", font=("Segoe UI", 14), height=45, fg_color="#3700b3", hover_color="#6200ea", command=self.load_file).pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(self.sidebar, text="Пользователь:", text_color="#777777").pack(pady=(20,0), anchor="w", padx=25)
        self.user_selector = ctk.CTkOptionMenu(self.sidebar, values=["Все"], command=self.update_ui, fg_color="#2c2c35", button_color="#3700b3")
        self.user_selector.pack(pady=5, padx=20, fill="x")

        # === MAIN CONTENT ===
        self.main_view = ctk.CTkScrollableFrame(self, fg_color=APP_BG, corner_radius=0)
        self.main_view.grid(row=0, column=1, sticky="nsew")

        # Header
        ctk.CTkLabel(self.main_view, text="Привет! 👋", font=("Segoe UI", 32, "bold")).pack(anchor="w", padx=30, pady=(30, 0))
        ctk.CTkLabel(self.main_view, text="Вот статистика вашей переписки", text_color="#777777").pack(anchor="w", padx=30, pady=(0, 20))

        # ROW 1: Стат-карточки
        self.row1 = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.row1.pack(fill="x", padx=20, pady=10)
        
        self.c_msgs = StatCard(self.row1, "Всего сообщений", "0", "---", "💬")
        self.c_time = StatCard(self.row1, "Общее время", "0 ч", "---", "⏱")
        self.c_actd = StatCard(self.row1, "Самый активный", "--", "---", "📅")
        self.c_maxm = StatCard(self.row1, "Максимум в день", "0", "---", "⚡")

        # ROW 2: Графики (Линейный 65% ширины, Бублик 35% ширины)
        self.row2 = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.row2.pack(fill="x", padx=20, pady=10)
        
        self.line_card = ctk.CTkFrame(self.row2, fg_color=CARD_BG, corner_radius=15)
        self.line_card.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(self.line_card, text="Активность по дням (Часы)", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(15,0))
        self.line_canvas_frame = ctk.CTkFrame(self.line_card, fg_color="transparent")
        self.line_canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.pie_card = ctk.CTkFrame(self.row2, fg_color=CARD_BG, corner_radius=15)
        self.pie_card.pack(side="right", fill="both", padx=10)
        ctk.CTkLabel(self.pie_card, text="Доли сообщений", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(15,0))
        self.pie_canvas_frame = ctk.CTkFrame(self.pie_card, fg_color="transparent")
        self.pie_canvas_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ROW 3: Топ дней и Периоды
        self.row3 = ctk.CTkFrame(self.main_view, fg_color="transparent")
        self.row3.pack(fill="x", padx=20, pady=10)

        self.top_card = ctk.CTkFrame(self.row3, fg_color=CARD_BG, corner_radius=15)
        self.top_card.pack(side="left", fill="both", expand=True, padx=10)
        ctk.CTkLabel(self.top_card, text="Топ дней (по времени)", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=15)
        self.top_container = ctk.CTkFrame(self.top_card, fg_color="transparent")
        self.top_container.pack(fill="both", expand=True, pady=(0, 15))

        self.periods_card = ctk.CTkFrame(self.row3, fg_color=CARD_BG, corner_radius=15)
        self.periods_card.pack(side="right", fill="both", expand=True, padx=10)
        ctk.CTkLabel(self.periods_card, text="Самые активные периоды", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=15)
        self.periods_container = ctk.CTkFrame(self.periods_card, fg_color="transparent")
        self.periods_container.pack(fill="both", expand=True, pady=(0, 15))

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.data_global = json.load(f)["messages"]
                self.user_selector.configure(values=["Все"] + analyzer.get_users(self.data_global))
                self.user_selector.set("Все")
                self.update_ui()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Файл не прочитан: {e}")

    def update_ui(self, _=None):
        if not self.data_global: return
        sel = self.user_selector.get()
        
        # Получаем данные
        stats, daily, total_h, extra = analyzer.analyze(self.data_global, sel)
        if not daily: return

        # 1. Заполняем Карточки сверху
        self.c_msgs.val_lbl.configure(text=f"{extra['total_msgs']:,}".replace(',', ' '))
        self.c_msgs.sub_lbl.configure(text="Всего за период")
        
        h, m = int(total_h), int((total_h % 1) * 60)
        self.c_time.val_lbl.configure(text=f"{h}ч {m}м")
        
        act_date, act_h = extra['max_hours_day']
        self.c_actd.val_lbl.configure(text=act_date.strftime('%d.%m.%Y'))
        self.c_actd.sub_lbl.configure(text=f"{act_h:.1f} ч за день")
        
        msg_date, msg_count = extra['max_msgs_day']
        self.c_maxm.val_lbl.configure(text=f"{msg_count}")
        self.c_maxm.sub_lbl.configure(text=msg_date.strftime('%d %b %Y'))

        # 2. Обновляем виджеты "Топ дней" (Очищаем старые и рисуем новые)
        for w in self.top_container.winfo_children(): w.destroy()
        top_h = extra['top_days'][0][1]['hours'] if extra['top_days'] else 1
        colors = ["#bb86fc", "#9965f4", "#7744ec", "#5522e4"]
        for i, (date, data) in enumerate(extra['top_days']):
            CustomProgressBar(self.top_container, date.strftime('%d %B %Y'), f"{data['hours']:.1f} ч", data['hours']/top_h, colors[i])

        # 3. Обновляем виджеты "Периоды"
        for w in self.periods_container.winfo_children(): w.destroy()
        p_colors = {"День (12-18)": "#cf6679", "Вечер (18-00)": "#3700b3", "Ночь (00-06)": "#03dac6", "Утро (06-12)": "#f1c40f"}
        # Сортируем периоды по убыванию процентов
        sorted_periods = sorted(extra['time_periods'].items(), key=lambda x: x[1], reverse=True)
        for name, pct in sorted_periods:
            CustomProgressBar(self.periods_container, name, f"{pct:.1f}%", pct/100, p_colors.get(name, "#bb86fc"))

        # 4. Рисуем графики Matplotlib
        for w in self.line_canvas_frame.winfo_children(): w.destroy()
        fig_line = charts.draw_line_chart(daily)
        canvas_line = FigureCanvasTkAgg(fig_line, master=self.line_canvas_frame)
        canvas_line.draw()
        canvas_line.get_tk_widget().pack(fill="both", expand=True)

        for w in self.pie_canvas_frame.winfo_children(): w.destroy()
        fig_pie = charts.draw_pie_chart(stats)
        canvas_pie = FigureCanvasTkAgg(fig_pie, master=self.pie_canvas_frame)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    App().mainloop()
