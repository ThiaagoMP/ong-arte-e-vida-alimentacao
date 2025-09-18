import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from database import db_functions as db


class ReportManagerWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Relatórios")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#F5F5F5")
        self.window.resizable(False, False)

        # Estilo
        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)

        # Frame principal
        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Título
        tk.Label(
            main_frame,
            text="Relatórios de Estoque",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        # Frame de histórico
        history_frame = tk.LabelFrame(
            main_frame,
            text="Histórico de Entradas e Saídas",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        history_frame.pack(fill="both", expand=True, pady=10)

        self.history_list = ttk.Treeview(
            history_frame,
            columns=("ID", "Alimento", "Entrada", "Saída", "Quantidade", "Validade"),
            show="headings",
            height=15
        )
        self.history_list.heading("ID", text="ID")
        self.history_list.heading("Alimento", text="Alimento")
        self.history_list.heading("Entrada", text="Data de Entrada")
        self.history_list.heading("Saída", text="Data de Saída")
        self.history_list.heading("Quantidade", text="Quantidade")
        self.history_list.heading("Validade", text="Validade")
        self.history_list.column("ID", width=50, anchor="center")
        self.history_list.column("Alimento", width=200, anchor="w")
        self.history_list.column("Entrada", width=100, anchor="center")
        self.history_list.column("Saída", width=100, anchor="center")
        self.history_list.column("Quantidade", width=100, anchor="center")
        self.history_list.column("Validade", width=100, anchor="center")
        self.history_list.pack(pady=10)
        self.load_history()

    def load_history(self):
        for i in self.history_list.get_children():
            self.history_list.delete(i)
        history = db.get_stock_history()
        for item in history:
            conn = db.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Nome FROM ALIMENTO WHERE ID = ?", (item[8],))
            result = cursor.fetchone()
            nome = result[0] if result else "Desconhecido"
            conn.close()
            # Converter datas para DD/MM/YYYY
            validade = datetime.strptime(item[4], '%Y-%m-%d').strftime('%d/%m/%Y') if item[4] else "-"
            entrada = datetime.strptime(item[5], '%d/%m/%Y').strftime('%d/%m/%Y') if item[5] else "-"
            saida = datetime.strptime(item[6], '%Y-%m-%d').strftime('%d/%m/%Y') if item[6] else "-"
            self.history_list.insert("", "end", values=(item[0], nome, entrada, saida, item[2], validade))
            if item[4] and datetime.strptime(item[4], '%Y-%m-%d') < datetime.now() + timedelta(days=7):
                self.history_list.item(self.history_list.get_children()[-1], tags=('red',))
        self.history_list.tag_configure('red', foreground='red')