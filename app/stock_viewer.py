import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from tkcalendar import DateEntry
from database import db_functions as db


class StockViewerWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Visualizar e Editar Estoque")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#F5F5F5")
        self.window.resizable(False, False)

        # Estilo
        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        # Frame principal
        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # Título
        tk.Label(
            main_frame,
            text="Estoque de Alimentos",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        # Lista de estoque
        self.stock_list = ttk.Treeview(
            main_frame,
            columns=("ID", "Alimento", "Marca", "Quantidade", "Unidade", "Validade", "Entrada", "Saída", "Saiu"),
            show="headings",
            height=15
        )
        self.stock_list.heading("ID", text="ID")
        self.stock_list.heading("Alimento", text="Alimento")
        self.stock_list.heading("Marca", text="Marca")
        self.stock_list.heading("Quantidade", text="Quantidade")
        self.stock_list.heading("Unidade", text="Unidade")
        self.stock_list.heading("Validade", text="Validade")
        self.stock_list.heading("Entrada", text="Entrada")
        self.stock_list.heading("Saída", text="Saída")
        self.stock_list.heading("Saiu", text="Saiu")
        self.stock_list.column("ID", width=50, anchor="center")
        self.stock_list.column("Alimento", width=150, anchor="w")
        self.stock_list.column("Marca", width=100, anchor="w")
        self.stock_list.column("Quantidade", width=80, anchor="center")
        self.stock_list.column("Unidade", width=60, anchor="center")
        self.stock_list.column("Validade", width=100, anchor="center")
        self.stock_list.column("Entrada", width=100, anchor="center")
        self.stock_list.column("Saída", width=100, anchor="center")
        self.stock_list.column("Saiu", width=50, anchor="center")
        self.stock_list.pack(pady=10, fill="x")
        self.load_stock()

        # Botões
        button_frame = tk.Frame(main_frame, bg="#F5F5F5")
        button_frame.pack(pady=20)
        tk.Button(
            button_frame,
            text="Editar Unidade",
            command=self.edit_stock,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=15
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Remover Unidade",
            command=self.delete_stock,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=15
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Atualizar",
            command=self.load_stock,
            bg="#FFA500",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#800080",
            width=15
        ).pack(side="left", padx=10)

    def load_stock(self):
        for i in self.stock_list.get_children():
            self.stock_list.delete(i)
        stock = db.get_all_stock()
        for item in stock:
            # Converter datas para DD/MM/YYYY, se existirem
            validade = datetime.strptime(item[5], '%Y-%m-%d').strftime('%d/%m/%Y') if item[5] else "-"
            entrada = datetime.strptime(item[6], '%d/%m/%Y').strftime('%d/%m/%Y') if item[6] else "-"
            saida = datetime.strptime(item[7], '%Y-%m-%d').strftime('%d/%m/%Y') if item[7] else "-"
            saiu = "Sim" if item[8] else "Não"
            self.stock_list.insert("", "end", values=(item[0], item[1], item[2], item[3], item[4], validade, entrada, saida, saiu))
            if item[5] and datetime.strptime(item[5], '%Y-%m-%d') < datetime.now() + timedelta(days=7) and not item[8]:
                self.stock_list.item(self.stock_list.get_children()[-1], tags=('red',))
        self.stock_list.tag_configure('red', foreground='red')

    def edit_stock(self):
        selected = self.stock_list.selection()
        if selected:
            unit_id = self.stock_list.item(selected)["values"][0]
            item = next((s for s in db.get_all_stock() if s[0] == unit_id), None)
            if item:
                edit_window = tk.Toplevel()
                edit_window.title("Editar Unidade de Estoque")
                edit_window.geometry("1920x1080")
                edit_window.configure(bg="#F5F5F5")
                edit_frame = tk.Frame(edit_window, bg="#F5F5F5", padx=20, pady=20)
                edit_frame.pack(fill="both", expand=True)

                tk.Label(edit_frame, text="Marca:", font=("Helvetica", 12), fg="#800080", bg="#F5F5F5").grid(row=0, column=0, sticky="e", padx=5, pady=5)
                marca_entry = tk.Entry(edit_frame, font=("Helvetica", 12), width=20, bd=2, relief="groove")
                marca_entry.insert(0, item[2])
                marca_entry.grid(row=0, column=1, padx=5, pady=5)

                tk.Label(edit_frame, text="Quantidade:", font=("Helvetica", 12), fg="#800080", bg="#F5F5F5").grid(row=1, column=0, sticky="e", padx=5, pady=5)
                valor_entry = tk.Entry(edit_frame, font=("Helvetica", 12), width=10, bd=2, relief="groove")
                valor_entry.insert(0, str(item[3]))
                valor_entry.grid(row=1, column=1, padx=5, pady=5)

                tk.Label(edit_frame, text="Unidade:", font=("Helvetica", 12), fg="#800080", bg="#F5F5F5").grid(row=2, column=0, sticky="e", padx=5, pady=5)
                unidade_entry = tk.Entry(edit_frame, font=("Helvetica", 12), width=10, bd=2, relief="groove")
                unidade_entry.insert(0, item[4])
                unidade_entry.grid(row=2, column=1, padx=5, pady=5)

                tk.Label(edit_frame, text="Validade (DD/MM/YYYY):", font=("Helvetica", 12), fg="#800080", bg="#F5F5F5").grid(row=3, column=0, sticky="e", padx=5, pady=5)
                validade_entry = DateEntry(
                    edit_frame,
                    font=("Helvetica", 12),
                    width=15,
                    date_pattern='dd/mm/yyyy',
                    background="#800080",
                    foreground="white",
                    borderwidth=2
                )
                if item[5]:
                    validade_entry.set_date(datetime.strptime(item[5], '%Y-%m-%d'))
                validade_entry.grid(row=3, column=1, padx=5, pady=5)

                def save():
                    try:
                        new_marca = marca_entry.get().strip()
                        new_valor = int(valor_entry.get().strip())
                        new_unidade = unidade_entry.get().strip()[:5]
                        new_validade = validade_entry.get().strip()
                        new_validade_db = datetime.strptime(new_validade, '%d/%m/%Y').strftime('%Y-%m-%d')
                        db.update_stock_unit(unit_id, new_marca, new_valor, new_unidade, new_validade_db)
                        self.load_stock()
                        edit_window.destroy()
                        messagebox.showinfo("Sucesso", "Unidade atualizada")
                    except ValueError:
                        messagebox.showerror("Erro", "Dados inválidos (quantidade inteira, data DD/MM/YYYY)")
                tk.Button(
                    edit_frame,
                    text="Salvar",
                    command=save,
                    bg="#FFA500",
                    fg="#FFFFFF",
                    font=("Helvetica", 12, "bold"),
                    activebackground="#800080",
                    width=15
                ).grid(row=4, column=0, columnspan=2, pady=10, sticky="we")

    def delete_stock(self):
        selected = self.stock_list.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma unidade de estoque para remover")
            return
        unit_id = self.stock_list.item(selected)["values"][0]
        if messagebox.askyesno("Confirmação", "Deseja remover esta unidade de estoque?"):
            if db.delete_stock_unit(unit_id):
                self.load_stock()
                messagebox.showinfo("Sucesso", "Unidade de estoque removida")
            else:
                messagebox.showerror("Erro", "Falha ao remover unidade de estoque")