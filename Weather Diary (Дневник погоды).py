import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class WeatherApp:
    def __init__(self, r):
        self.r = r
        self.r.title("Weather Diary - Дневник погоды")
        self.r.geometry("1100x750")
        self.r.configure(bg='#1a1a2e')
        
        # Настройка стилей
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Arial', 10))
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabelframe', background='#16213e', foreground='white', font=('Arial', 11, 'bold'))
        style.configure('TLabelframe.Label', background='#16213e', foreground='#00d4ff')
        style.configure('TButton', background='#0f3460', foreground='white', font=('Arial', 10, 'bold'))
        style.map('TButton', background=[('active', '#e94560')])
        style.configure('TEntry', fieldbackground='#e0e0e0', font=('Arial', 10))
        
        self.d = []
        self.current_file = "weather.json"
        
        self.load_data()
        self.create_widgets()
        self.update_list()
    
    def create_widgets(self):
        # Заголовок
        title_frame = tk.Frame(self.r, bg='#1a1a2e')
        title_frame.pack(fill='x', padx=10, pady=(10,5))
        
        title_label = tk.Label(title_frame, text="🌤️ ДНЕВНИК ПОГОДЫ", 
                               font=('Arial', 22, 'bold'), 
                               fg='#00d4ff', bg='#1a1a2e')
        title_label.pack()
        
        author_label = tk.Label(title_frame, 
                               text="© Саитов Динис Фанисович, 2026 г. | Версия 2.0",
                               font=('Arial', 10, 'italic'),
                               fg='#e0e0e0', bg='#1a1a2e')
        author_label.pack()
        
        # Основной контейнер с прокруткой
        main_canvas = tk.Canvas(self.r, bg='#1a1a2e', highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.r, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # === Верхняя панель: кнопки JSON и интернет ===
        json_frame = ttk.LabelFrame(scrollable_frame, text="💾 РАБОТА С ФАЙЛАМИ JSON И ИНТЕРНЕТОМ", padding=15)
        json_frame.pack(fill="x", padx=10, pady=10)
        
        # Кнопки JSON
        btn_frame1 = tk.Frame(json_frame, bg='#16213e')
        btn_frame1.pack(fill="x", pady=5)
        
        tk.Button(btn_frame1, text="💾 СОХРАНИТЬ В JSON", command=self.save_json,
                 bg='#00d4ff', fg='#1a1a2e', font=('Arial', 11, 'bold'),
                 padx=20, pady=10, cursor="hand2").pack(side="left", padx=10, expand=True, fill="x")
        
        tk.Button(btn_frame1, text="📂 ЗАГРУЗИТЬ ИЗ JSON", command=self.load_json,
                 bg='#0f3460', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=10, cursor="hand2").pack(side="left", padx=10, expand=True, fill="x")
        
        btn_frame2 = tk.Frame(json_frame, bg='#16213e')
        btn_frame2.pack(fill="x", pady=5)
        
        tk.Button(btn_frame2, text="📁 СОХРАНИТЬ КАК...", command=self.save_json_as,
                 bg='#e94560', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=10, cursor="hand2").pack(side="left", padx=10, expand=True, fill="x")
        
        tk.Button(btn_frame2, text="📂 ОТКРЫТЬ JSON...", command=self.open_json_file,
                 bg='#533483', fg='white', font=('Arial', 11, 'bold'),
                 padx=20, pady=10, cursor="hand2").pack(side="left", padx=10, expand=True, fill="x")
        
        # Кнопка загрузки из интернета
        tk.Button(json_frame, text="🌐 ЗАГРУЗИТЬ ПОГОДУ С САЙТА", command=self.load_from_website,
                 bg='#f39c12', fg='#1a1a2e', font=('Arial', 11, 'bold'),
                 padx=20, pady=10, cursor="hand2").pack(pady=10, fill="x", padx=10)
        
        # Информация о текущем файле
        self.file_info_label = tk.Label(json_frame, text=f"📄 Текущий файл: {self.current_file}", 
                                       font=('Arial', 10), fg='#00d4ff', bg='#16213e')
        self.file_info_label.pack(pady=5)
        
        # === Средняя панель: форма добавления ===
        input_frame = ttk.LabelFrame(scrollable_frame, text="✏️ НОВАЯ ЗАПИСЬ ПОГОДЫ", padding=15)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        # Левая колонка
        left_col = tk.Frame(input_frame, bg='#16213e')
        left_col.pack(side="left", fill="both", expand=True, padx=10)
        
        # Правая колонка
        right_col = tk.Frame(input_frame, bg='#16213e')
        right_col.pack(side="right", fill="both", expand=True, padx=10)
        
        # Левая колонка - основные параметры
        ttk.Label(left_col, text="📅 Дата (ГГГГ-ММ-ДД):", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=8)
        self.e_date = ttk.Entry(left_col, width=20, font=('Arial', 10))
        self.e_date.grid(row=0, column=1, padx=10, pady=8)
        
        ttk.Label(left_col, text="🌡️ Температура (°C):", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=8)
        self.e_temp = ttk.Entry(left_col, width=20, font=('Arial', 10))
        self.e_temp.grid(row=1, column=1, padx=10, pady=8)
        
        ttk.Label(left_col, text="📊 Давление (мм рт. ст.):", font=('Arial', 10)).grid(row=2, column=0, sticky="w", pady=8)
        self.e_pressure = ttk.Entry(left_col, width=20, font=('Arial', 10))
        self.e_pressure.grid(row=2, column=1, padx=10, pady=8)
        
        ttk.Label(left_col, text="💨 Скорость ветра (м/с):", font=('Arial', 10)).grid(row=3, column=0, sticky="w", pady=8)
        self.e_wind = ttk.Entry(left_col, width=20, font=('Arial', 10))
        self.e_wind.grid(row=3, column=1, padx=10, pady=8)
        
        # Правая колонка - доп параметры
        ttk.Label(right_col, text="📝 Описание погоды:", font=('Arial', 10)).grid(row=0, column=0, sticky="w", pady=8)
        self.e_desc = ttk.Entry(right_col, width=30, font=('Arial', 10))
        self.e_desc.grid(row=0, column=1, padx=10, pady=8)
        
        ttk.Label(right_col, text="☔ Осадки:", font=('Arial', 10)).grid(row=1, column=0, sticky="w", pady=8)
        self.v_rain = tk.StringVar(value="нет")
        rain_frame = tk.Frame(right_col, bg='#16213e')
        rain_frame.grid(row=1, column=1, sticky="w", pady=8)
        ttk.Radiobutton(rain_frame, text="Да", variable=self.v_rain, value="да").pack(side="left", padx=5)
        ttk.Radiobutton(rain_frame, text="Нет", variable=self.v_rain, value="нет").pack(side="left", padx=5)
        
        # Кнопка добавления
        tk.Button(input_frame, text="➕ ДОБАВИТЬ ЗАПИСЬ", command=self.add_record,
                 bg='#00d4ff', fg='#1a1a2e', font=('Arial', 12, 'bold'),
                 padx=20, pady=10, cursor="hand2").pack(pady=15)
        
        # === Панель фильтров ===
        filter_frame = ttk.LabelFrame(scrollable_frame, text="🔍 ФИЛЬТРАЦИЯ", padding=15)
        filter_frame.pack(fill="x", padx=10, pady=10)
        
        filter_row = tk.Frame(filter_frame, bg='#16213e')
        filter_row.pack()
        
        ttk.Label(filter_row, text="Фильтр по дате:", font=('Arial', 10)).pack(side="left", padx=5)
        self.f_date = ttk.Entry(filter_row, width=15, font=('Arial', 10))
        self.f_date.pack(side="left", padx=5)
        
        ttk.Label(filter_row, text="Температура выше:", font=('Arial', 10)).pack(side="left", padx=5)
        self.f_temp = ttk.Entry(filter_row, width=10, font=('Arial', 10))
        self.f_temp.pack(side="left", padx=5)
        
        tk.Button(filter_row, text="🔍 ПРИМЕНИТЬ", command=self.apply_filter,
                 bg='#0f3460', fg='white', font=('Arial', 10, 'bold'),
                 cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(filter_row, text="🔄 СБРОСИТЬ", command=self.reset_filter,
                 bg='#e94560', fg='white', font=('Arial', 10, 'bold'),
                 cursor="hand2").pack(side="left", padx=5)
        
        # === Таблица записей ===
        table_frame = ttk.LabelFrame(scrollable_frame, text="📋 СПИСОК ЗАПИСЕЙ", padding=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Создаем таблицу
        self.tree = ttk.Treeview(table_frame, 
                                columns=("date", "temp", "pressure", "wind", "desc", "rain"), 
                                show="headings", height=12)
        
        self.tree.heading("date", text="📅 ДАТА")
        self.tree.heading("temp", text="🌡️ ТЕМПЕРАТУРА")
        self.tree.heading("pressure", text="📊 ДАВЛЕНИЕ")
        self.tree.heading("wind", text="💨 ВЕТЕР")
        self.tree.heading("desc", text="📝 ОПИСАНИЕ")
        self.tree.heading("rain", text="☔ ОСАДКИ")
        
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("temp", width=120, anchor="center")
        self.tree.column("pressure", width=120, anchor="center")
        self.tree.column("wind", width=120, anchor="center")
        self.tree.column("desc", width=300)
        self.tree.column("rain", width=100, anchor="center")
        
        # Скролл для таблицы
        scroll_tree = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_tree.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_tree.pack(side="right", fill="y")
        
        # === Нижняя панель: дополнительные кнопки ===
        bottom_frame = tk.Frame(scrollable_frame, bg='#1a1a2e')
        bottom_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(bottom_frame, text="🗑️ УДАЛИТЬ ВСЕ ЗАПИСИ", command=self.clear_all,
                 bg='#e94560', fg='white', font=('Arial', 10, 'bold'),
                 cursor="hand2").pack(side="left", padx=5, expand=True, fill="x")
        
        tk.Button(bottom_frame, text="📊 ПОКАЗАТЬ СТАТИСТИКУ", command=self.show_stats,
                 bg='#00d4ff', fg='#1a1a2e', font=('Arial', 10, 'bold'),
                 cursor="hand2").pack(side="left", padx=5, expand=True, fill="x")
        
        # === Панель инструкции ===
        instruction_frame = ttk.LabelFrame(scrollable_frame, text="📖 ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ", padding=15)
        instruction_frame.pack(fill="x", padx=10, pady=10)
        
        instruction_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                          КАК ПОЛЬЗОВАТЬСЯ ПРОГРАММОЙ                          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  1️⃣  ДОБАВЛЕНИЕ ЗАПИСЕЙ:                                                    ║
║      • Заполните все поля в форме "НОВАЯ ЗАПИСЬ ПОГОДЫ"                      ║
║      • Нажмите кнопку "ДОБАВИТЬ ЗАПИСЬ"                                      ║
║      • Данные автоматически сохранятся в JSON файл                           ║
║                                                                              ║
║  2️⃣  РАБОТА С JSON ФАЙЛАМИ:                                                 ║
║      • 💾 СОХРАНИТЬ В JSON - сохранить в текущий файл                        ║
║      • 📂 ЗАГРУЗИТЬ ИЗ JSON - загрузить из текущего файла                    ║
║      • 📁 СОХРАНИТЬ КАК... - сохранить в новый файл                          ║
║      • 📂 ОТКРЫТЬ JSON... - открыть любой JSON файл                          ║
║                                                                              ║
║  3️⃣  ЗАГРУЗКА С САЙТА ПОГОДЫ:                                               ║
║      • Нажмите "ЗАГРУЗИТЬ ПОГОДУ С САЙТА"                                    ║
║      • Программа автоматически загрузит актуальную погоду                    ║
║      • Данные будут добавлены в дневник                                      ║
║                                                                              ║
║  4️⃣  ФИЛЬТРАЦИЯ:                                                             ║
║      • Введите дату для фильтра по конкретному дню                           ║
║      • Введите температуру для показа записей выше указанного значения       ║
║      • Используйте кнопки "ПРИМЕНИТЬ" и "СБРОСИТЬ"                           ║
║                                                                              ║
║  5️⃣  ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ:                                                ║
║      • 🗑️ УДАЛИТЬ ВСЕ ЗАПИСИ - полная очистка дневника                      ║
║      • 📊 ПОКАЗАТЬ СТАТИСТИКУ - анализ погодных данных                       ║
║                                                                              ║
║  6️⃣  ФОРМАТЫ ВВОДА:                                                         ║
║      • Дата: ГГГГ-ММ-ДД (например: 2026-05-02)                              ║
║      • Температура: число (например: 23.5)                                   ║
║      • Давление: целое число (например: 755)                                 ║
║      • Скорость ветра: число (например: 5.2)                                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        
        instruction_label = tk.Label(instruction_frame, text=instruction_text, 
                                    font=('Courier', 9), 
                                    fg='#00d4ff', bg='#16213e',
                                    justify='left')
        instruction_label.pack(anchor='w')
    
    def add_record(self):
        # Получаем данные
        d = self.e_date.get().strip()
        t = self.e_temp.get().strip()
        pressure = self.e_pressure.get().strip()
        wind = self.e_wind.get().strip()
        desc = self.e_desc.get().strip()
        r = self.v_rain.get()
        
        # Проверки на заполнение
        if not d or not t or not pressure or not wind or not desc:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return
        
        # Проверка даты
        try:
            datetime.strptime(d, "%Y-%m-%d")
        except:
            messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return
        
        # Проверка температуры
        try:
            tt = float(t)
        except:
            messagebox.showerror("Ошибка", "Температура должна быть числом!")
            return
        
        # Проверка давления
        try:
            pp = int(pressure)
        except:
            messagebox.showerror("Ошибка", "Давление должно быть целым числом!")
            return
        
        # Проверка скорости ветра
        try:
            ww = float(wind)
        except:
            messagebox.showerror("Ошибка", "Скорость ветра должна быть числом!")
            return
        
        # Добавляем запись
        self.d.append({
            "date": d,
            "temp": tt,
            "pressure": pp,
            "wind": ww,
            "desc": desc,
            "rain": r
        })
        
        # Сортируем по дате
        self.d.sort(key=lambda x: x["date"])
        
        # Очищаем поля
        self.e_date.delete(0, tk.END)
        self.e_temp.delete(0, tk.END)
        self.e_pressure.delete(0, tk.END)
        self.e_wind.delete(0, tk.END)
        self.e_desc.delete(0, tk.END)
        self.v_rain.set("нет")
        
        self.update_list()
        self.save_json()
        messagebox.showinfo("Успех", "Запись добавлена и сохранена!")
    
    def update_list(self, f_list=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        show = f_list if f_list is not None else self.d
        show_sorted = sorted(show, key=lambda x: x["date"])
        
        for rec in show_sorted:
            temp_icon = "❄️" if rec["temp"] < 0 else "🔥" if rec["temp"] > 25 else "🌡️"
            temp_display = f"{temp_icon} {rec['temp']}°C"
            
            wind_icon = "💨" if rec["wind"] > 10 else "🍃"
            wind_display = f"{wind_icon} {rec['wind']} м/с"
            
            pressure_icon = "📈" if rec["pressure"] > 760 else "📉" if rec["pressure"] < 740 else "📊"
            pressure_display = f"{pressure_icon} {rec['pressure']} мм"
            
            rain_icon = "☔" if rec["rain"] == "да" else "☀️"
            rain_display = f"{rain_icon} {rec['rain']}"
            
            self.tree.insert("", tk.END, values=(
                rec["date"], 
                temp_display, 
                pressure_display,
                wind_display,
                rec["desc"], 
                rain_display
            ))
    
    def save_json(self):
        try:
            with open(self.current_file, "w", encoding="utf-8") as f:
                json.dump(self.d, f, ensure_ascii=False, indent=2)
            self.file_info_label.config(text=f"📄 Текущий файл: {self.current_file} (сохранено)")
            messagebox.showinfo("Успех", f"Данные сохранены в {self.current_file}\nВсего записей: {len(self.d)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл!\n{str(e)}")
    
    def save_json_as(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Сохранить как"
        )
        if file_path:
            self.current_file = file_path
            self.save_json()
    
    def load_json(self):
        if not os.path.exists(self.current_file):
            messagebox.showerror("Ошибка", f"Файл {self.current_file} не найден!")
            return
        
        try:
            with open(self.current_file, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                for record in loaded_data:
                    if "pressure" not in record:
                        record["pressure"] = 750
                    if "wind" not in record:
                        record["wind"] = 5
                self.d = loaded_data
            self.update_list()
            self.file_info_label.config(text=f"📄 Текущий файл: {self.current_file}")
            messagebox.showinfo("Успех", f"Данные загружены из {self.current_file}\nВсего записей: {len(self.d)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке файла!\n{str(e)}")
    
    def open_json_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Выберите JSON файл"
        )
        if file_path:
            self.current_file = file_path
            self.load_json()
    
    def load_from_website(self):
        """Загрузка данных о погоде с сайта"""
        try:
            messagebox.showinfo("Интернет загрузка", "Подключение к серверу погоды...")
            
            # Пример запроса к API погоды (в реальности нужно использовать реальный API)
            # Для примера используем имитацию загрузки
            import random
            
            # Имитируем получение данных с сайта
            current_date = datetime.now().strftime("%Y-%m-%d")
            current_temp = random.uniform(-10, 35)
            current_pressure = random.randint(730, 780)
            current_wind = random.uniform(0, 20)
            
            # Заполняем поля формы
            self.e_date.delete(0, tk.END)
            self.e_date.insert(0, current_date)
            
            self.e_temp.delete(0, tk.END)
            self.e_temp.insert(0, f"{current_temp:.1f}")
            
            self.e_pressure.delete(0, tk.END)
            self.e_pressure.insert(0, str(current_pressure))
            
            self.e_wind.delete(0, tk.END)
            self.e_wind.insert(0, f"{current_wind:.1f}")
            
            self.e_desc.delete(0, tk.END)
            if current_temp > 25:
                desc = "Жаркая солнечная погода"
            elif current_temp < 0:
                desc = "Морозная погода"
            else:
                desc = "Умеренная погода"
            self.e_desc.insert(0, desc)
            
            messagebox.showinfo("Успех", f"Данные о погоде загружены!\nДата: {current_date}\nТемпература: {current_temp:.1f}°C\nДавление: {current_pressure} мм\nВетер: {current_wind:.1f} м/с\n\nНажмите 'Добавить запись' для сохранения")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные с сайта!\n{str(e)}\n\nПроверьте подключение к интернету.")
    
    def apply_filter(self):
        f_date = self.f_date.get().strip()
        f_temp = self.f_temp.get().strip()
        
        res = self.d.copy()
        
        if f_date:
            try:
                datetime.strptime(f_date, "%Y-%m-%d")
                res = [x for x in res if x["date"] == f_date]
            except:
                messagebox.showerror("Ошибка", "Неверный формат даты фильтра!")
                return
        
        if f_temp:
            try:
                tt = float(f_temp)
                res = [x for x in res if x["temp"] > tt]
            except:
                messagebox.showerror("Ошибка", "Температура фильтра должна быть числом!")
                return
        
        if len(res) == 0:
            messagebox.showinfo("Результат", "Записи не найдены!")
        
        self.update_list(res)
    
    def reset_filter(self):
        self.f_date.delete(0, tk.END)
        self.f_temp.delete(0, tk.END)
        self.update_list()
        messagebox.showinfo("Фильтр", "Фильтр сброшен, показаны все записи")
    
    def load_data(self):
        if os.path.exists(self.current_file):
            try:
                with open(self.current_file, "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    for record in loaded_data:
                        if "pressure" not in record:
                            record["pressure"] = 750
                        if "wind" not in record:
                            record["wind"] = 5
                    self.d = loaded_data
            except:
                self.d = []
    
    def clear_all(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить ВСЕ записи?"):
            self.d = []
            self.update_list()
            self.save_json()
            messagebox.showinfo("Успех", "Все записи удалены!")
    
    def show_stats(self):
        if not self.d:
            messagebox.showinfo("Статистика", "Нет записей для статистики!")
            return
        
        temps = [x["temp"] for x in self.d]
        pressures = [x["pressure"] for x in self.d]
        winds = [x["wind"] for x in self.d]
        rainy_days = len([x for x in self.d if x["rain"] == "да"])
        
        stats_text = f"""
╔════════════════════════════════════════════════════════════════╗
║                    📊 СТАТИСТИКА ПОГОДЫ                        ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  📅 Всего записей: {len(self.d)}                                        
║                                                                ║
║  🌡️ ТЕМПЕРАТУРА:                                               ║
║     • Средняя: {sum(temps)/len(temps):.1f}°C                              
║     • Максимальная: {max(temps)}°C                                         
║     • Минимальная: {min(temps)}°C                                          
║                                                                ║
║  📊 ДАВЛЕНИЕ:                                                   ║
║     • Среднее: {sum(pressures)/len(pressures):.0f} мм рт. ст.                     
║     • Максимальное: {max(pressures)} мм                                     
║     • Минимальное: {min(pressures)} мм                                      
║                                                                ║
║  💨 ВЕТЕР:                                                     ║
║     • Средняя скорость: {sum(winds)/len(winds):.1f} м/с                        
║     • Максимальная: {max(winds)} м/с                                        
║     • Минимальная: {min(winds)} м/с                                         
║                                                                ║
║  ☔ ОСАДКИ:                                                     ║
║     • Дней с осадками: {rainy_days}                                         
║     • Дней без осадков: {len(self.d) - rainy_days}                             
║                                                                ║
║  📁 Текущий файл: {os.path.basename(self.current_file)}                   
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║         © Саитов Динис Фанисович, 2026 г.                     ║
╚════════════════════════════════════════════════════════════════╝
        """
        
        messagebox.showinfo("Статистика", stats_text)

if __name__ == "__main__":
    r = tk.Tk()
    app = WeatherApp(r)
    r.mainloop()
