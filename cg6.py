from sqlalchemy import create_engine
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc

# Подключение через SQLAlchemy
engine = create_engine("mssql+pyodbc://User055:User055%5D16@192.168.112.103/db22205?driver=SQL+Server")

# Если всё ещё нужно для execute
conn = pyodbc.connect(driver='{SQL Server}',
                      server='192.168.112.103',
                      database='db22205',
                      user='User055',
                      password='User055]16')

# Главная форма
root = tk.Tk()
root.title("Главная форма")

def open_meters_form():
    meters_form = tk.Toplevel(root)
    meters_form.title("Счетчики")

    # Получаем все данные из таблицы "Счетчики"
    df = pd.read_sql("SELECT * FROM Счетчики", engine)

    # Создаём таблицу для отображения
    tree = ttk.Treeview(meters_form, columns=list(df.columns), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    for row in df.itertuples(index=False):
        tree.insert('', 'end', values=row)

    tree.pack(fill='both', expand=True)

    def on_double_click(event):
        item = tree.selection()
        if not item:
            return
        selected = tree.item(item[0], 'values')
        meter_id = selected[0]
        open_check_form(meter_id)

    tree.bind("<Double-1>", on_double_click)

    add_meter_btn = ttk.Button(meters_form, text="Добавить счетчик", command=open_new_meter_form)
    add_meter_btn.pack(side='bottom')

    add_check_btn = ttk.Button(meters_form, text="Добавить проверку", command=lambda: open_add_check_form(tree))
    add_check_btn.pack(side='bottom')

def open_new_meter_form():
    form = tk.Toplevel(root)
    form.title("Новый счетчик")

    tk.Label(form, text="Введите адрес:").pack()
    address_entry = tk.Entry(form)
    address_entry.pack()

    def save_meter():
        address = address_entry.get()
        if not address:
            messagebox.showwarning("Ошибка", "Адрес не может быть пустым!")
            return
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Счетчики (Адрес) VALUES (?)", address)
        conn.commit()
        form.destroy()
        messagebox.showinfo("Успех", "Счетчик успешно добавлен!")

    tk.Button(form, text="Сохранить", command=save_meter).pack()

def open_check_form(meter_id):
    form = tk.Toplevel(root)
    form.title(f"Проверки счетчика № {meter_id}")

    # Получаем все данные о счетчике
    meter_data = pd.read_sql(f"SELECT * FROM Счетчики WHERE [Номер счетчика] = ?", conn, params=[meter_id])

    # Создаём таблицу с результатами
    tree = ttk.Treeview(form, columns=list(meter_data.columns), show='headings')
    for col in meter_data.columns:
        tree.heading(col, text=col)
        tree.column(col, anchor='center')

    for row in meter_data.itertuples(index=False):
        tree.insert('', 'end', values=row)

    tree.pack(fill='both', expand=True)

    # Добавление информации о проверках
    checks_data = pd.read_sql(f"SELECT * FROM tblCheck WHERE intMeterID = ?", conn, params=[meter_id])
    checks_tree = ttk.Treeview(form, columns=list(checks_data.columns), show='headings')
    for col in checks_data.columns:
        checks_tree.heading(col, text=col)
        checks_tree.column(col, anchor='center')

    for row in checks_data.itertuples(index=False):
        checks_tree.insert('', 'end', values=row)

    checks_tree.pack(fill='both', expand=True)

def open_add_check_form(tree):
    try:
        item = tree.selection()[0]
        selected = tree.item(item, 'values')
        meter_id = selected[0]
    except IndexError:
        messagebox.showwarning("Ошибка", "Выберите счетчик для добавления проверки.")
        return

    form = tk.Toplevel(root)
    form.title("Добавить проверку")

    tk.Label(form, text=f"Номер счетчика: {meter_id}").pack()

    inspectors = pd.read_sql("SELECT intInspectorID, txtInspectorName FROM tblInspector", engine)

    tk.Label(form, text="ФИО контролера:").pack()
    inspector_var = tk.StringVar()
    inspector_menu = ttk.Combobox(form, textvariable=inspector_var, values=list(inspectors['txtInspectorName']))
    inspector_menu.pack()

    tk.Label(form, text="Дата проверки (ГГГГ-ММ-ДД):").pack()
    date_entry = tk.Entry(form)
    date_entry.pack()

    tk.Label(form, text="Показания счетчика:").pack()
    meter_value_entry = tk.Entry(form)
    meter_value_entry.pack()

    def save_check():
        inspector_name = inspector_var.get()
        date = date_entry.get()
        meter_value = meter_value_entry.get()

        if not inspector_name or not date or not meter_value:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return

        try:
            inspector_id = int(inspectors.loc[inspectors['txtInspectorName'] == inspector_name, 'intInspectorID'].values[0])
        except IndexError:
            messagebox.showerror("Ошибка", "Контролер не найден.")
            return

        # Заполнить fltCheckSum каким-либо значением, например 0
        flt_check_sum = 0  # или любое другое значение, которое имеет смысл

        cursor = conn.cursor()
        cursor.execute(""" 
            INSERT INTO tblCheck (intMeterId, intInspectorID, datCheckPaid, txtCheckMeterValue, fltCheckSum) 
            VALUES (?, ?, ?, ?, ?)
        """, (int(meter_id), inspector_id, date, meter_value, flt_check_sum))
        conn.commit()
        form.destroy()
        messagebox.showinfo("Успех", "Проверка добавлена!")
        open_check_form(meter_id)

    tk.Button(form, text="Сохранить проверку", command=save_check).pack()

def report1():
    messagebox.showinfo("Отчет 1", "Здесь будет первый отчет.")

def report2():
    messagebox.showinfo("Отчет 2", "Здесь будет второй отчет.")

def report3():
    report_form = tk.Toplevel(root)
    report_form.title("Отчет по контролеру")

    inspectors = pd.read_sql("SELECT intInspectorID, txtInspectorName FROM tblInspector", engine)

    tk.Label(report_form, text="Выберите ФИО контролера:").pack()

    inspector_var = tk.StringVar()
    inspector_menu = ttk.Combobox(report_form, textvariable=inspector_var, values=list(inspectors['txtInspectorName']))
    inspector_menu.pack()

    def generate_report():
        selected_name = inspector_var.get()
        if not selected_name:
            messagebox.showwarning("Ошибка", "Выберите контролера!")
            return
        try:
            inspector_id = inspectors.loc[inspectors['txtInspectorName'] == selected_name, 'intInspectorID'].values[0]
        except IndexError:
            messagebox.showerror("Ошибка", "Контролер не найден.")
            return

        query = "SELECT * FROM tblCheck WHERE intInspectorID = ?"
        df = pd.read_sql(query, conn, params=[inspector_id])
        messagebox.showinfo("Результат", f"Найдено проверок: {len(df)}")

    tk.Button(report_form, text="Сформировать отчет", command=generate_report).pack()

# Главное меню
ttk.Button(root, text="Открыть форму Счетчики", command=open_meters_form).pack(pady=5)
ttk.Button(root, text="Отчет 1", command=report1).pack(pady=5)
ttk.Button(root, text="Отчет 2", command=report2).pack(pady=5)
ttk.Button(root, text="Отчет по контролеру", command=report3).pack(pady=5)

root.mainloop()
