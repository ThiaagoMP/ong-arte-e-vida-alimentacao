import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from database import db_functions as db


class FoodManagerWindow:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.window = tk.Toplevel()
        self.window.title("Gerenciar Alimentos")

        # Define o que acontece ao fechar com o 'X'
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        try:
            self.window.state('zoomed')
        except tk.TclError:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f'{screen_width}x{screen_height}+0+0')

        self.window.configure(bg="#F5F5F5")
        self.window.resizable(True, True)

        self.window.grid_columnconfigure(0, weight=2)
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_rowconfigure(0, weight=1)

        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        left_column_frame = tk.Frame(self.window, bg="#F5F5F5", padx=10, pady=10)
        left_column_frame.grid(row=0, column=0, sticky="nsew")

        right_column_frame = tk.Frame(self.window, bg="#F5F5F5", padx=10, pady=10)
        right_column_frame.grid(row=0, column=1, sticky="nsew")

        # --- NOVO: Botão Voltar ---
        back_button_frame = tk.Frame(left_column_frame, bg="#F5F5F5")
        back_button_frame.pack(fill="x")

        tk.Button(
            back_button_frame,
            text="← Voltar",
            command=self.go_back,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=10
        ).pack(side="left", anchor="nw")
        # ---------------------------

        tk.Label(
            left_column_frame,
            text="Gerenciamento de Alimentos",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        add_frame = tk.LabelFrame(
            left_column_frame,
            text="Adicionar Alimento e Estoque Inicial",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        add_frame.pack(fill="both", expand=True, pady=10)

        add_frame.grid_columnconfigure(0, weight=1)
        add_frame.grid_columnconfigure(1, weight=1)
        add_frame.grid_columnconfigure(2, weight=1)

        nut_input_frame = tk.Frame(add_frame, bg="#F5F5F5")
        nut_input_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        tk.Label(
            add_frame, text="Nome: *", font=font_label, fg="#800080", bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.nome_entry = tk.Entry(add_frame, font=font_label, width=30, bd=2, relief="groove")
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        nut_labels = [
            "Valor Energético (kcal)", "Carboidratos (g)", "Açúcares Totais (g)",
            "Açúcares Adicionados (g)", "Proteínas (g)", "Gorduras Totais (g)",
            "Gorduras Saturadas (g)", "Gorduras Trans (g)", "Fibras (g)",
            "Sódio (mg)", "Cálcio (mg)"
        ]
        self.nut_entries = []
        for i, label in enumerate(nut_labels):
            tk.Label(
                nut_input_frame, text=label, font=font_label, fg="#800080", bg="#F5F5F5"
            ).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(nut_input_frame, font=font_label, width=20, bd=2, relief="groove")
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="w")
            self.nut_entries.append(entry)

        row_cat = len(nut_labels)
        tk.Label(
            nut_input_frame, text="Categoria: *", font=font_label, fg="#800080", bg="#F5F5F5"
        ).grid(row=row_cat, column=0, sticky="e", padx=5, pady=5)
        self.cats_combo = ttk.Combobox(nut_input_frame, font=font_label, width=30, state="readonly")
        self.cats_combo.grid(row=row_cat, column=1, padx=5, pady=5, sticky="w")
        self.load_categories_to_combo()

        tk.Button(
            nut_input_frame, text="Adicionar Categoria", command=self.add_category_to_list,
            bg="#800080", fg="#FFFFFF", font=font_button, activebackground="#FFA500", width=15
        ).grid(row=row_cat + 1, column=0, columnspan=2, pady=5)

        self.cats_listbox = tk.Listbox(nut_input_frame, font=font_label, width=30, height=5, bd=2, relief="groove")
        self.cats_listbox.grid(row=row_cat + 2, column=0, columnspan=2, pady=5)

        stock_section = tk.LabelFrame(
            add_frame, text="Estoque Inicial", font=font_label, fg="#800080",
            bg="#F5F5F5", padx=5, pady=5
        )
        stock_section.grid(row=0, column=2, rowspan=2, sticky="ns", padx=20, pady=5)

        tk.Label(stock_section, text="Marca:", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=0, column=0,
                                                                                                 sticky="e", padx=5,
                                                                                                 pady=5)
        self.marca_entry = tk.Entry(stock_section, font=font_label, width=20, bd=2, relief="groove")
        self.marca_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        tk.Label(stock_section, text="Quantidade:", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=1, column=0,
                                                                                                      sticky="e",
                                                                                                      padx=5, pady=5)
        self.valor_entry = tk.Entry(stock_section, font=font_label, width=10, bd=2, relief="groove")
        self.valor_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        tk.Label(stock_section, text="Unidade de medida (ex: kg):", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=2,
                                                                                                            column=0,
                                                                                                            sticky="e",
                                                                                                            padx=5,
                                                                                                            pady=5)
        self.unidade_entry = tk.Entry(stock_section, font=font_label, width=10, bd=2, relief="groove")
        self.unidade_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Label(stock_section, text="Validade (DD/MM/YYYY):", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=3,
                                                                                                                 column=0,
                                                                                                                 sticky="e",
                                                                                                                 padx=5,
                                                                                                                 pady=5)
        self.validade_entry = DateEntry(stock_section, font=font_label, width=15, date_pattern='dd/mm/yyyy',
                                        background="#800080", foreground="white", borderwidth=2)
        self.validade_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.entrada = datetime.now().strftime('%d/%m/%Y')

        tk.Button(
            add_frame, text="Adicionar Alimento e Estoque", command=self.add_food_with_stock,
            bg="#FFA500", fg="#FFFFFF", font=font_button, activebackground="#800080", width=25, height=2
        ).grid(row=len(nut_labels) + 4, column=0, columnspan=3, pady=15, sticky="ew")

        extra_stock_frame = tk.LabelFrame(
            right_column_frame,
            text="Adicionar Estoque a Alimento Existente",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        extra_stock_frame.pack(fill="x", pady=10)

        tk.Label(extra_stock_frame, text="Alimento:", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=0, column=0,
                                                                                                        sticky="e",
                                                                                                        padx=5, pady=5)
        self.foods_combo = ttk.Combobox(extra_stock_frame, font=font_label, width=30, state="readonly")
        self.foods_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.load_foods_to_combo()
        tk.Label(extra_stock_frame, text="Marca:", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=1, column=0,
                                                                                                     sticky="e", padx=5,
                                                                                                     pady=5)
        self.extra_marca_entry = tk.Entry(extra_stock_frame, font=font_label, width=20, bd=2, relief="groove")
        self.extra_marca_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        tk.Label(extra_stock_frame, text="Quantidade:", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=2,
                                                                                                          column=0,
                                                                                                          sticky="e",
                                                                                                          padx=5,
                                                                                                          pady=5)
        self.extra_valor_entry = tk.Entry(extra_stock_frame, font=font_label, width=10, bd=2, relief="groove")
        self.extra_valor_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tk.Label(extra_stock_frame, text="Unidade de medida (ex: kg):", font=font_label, fg="#800080", bg="#F5F5F5").grid(row=3,
                                                                                                                column=0,
                                                                                                                sticky="e",
                                                                                                                padx=5,
                                                                                                                pady=5)
        self.extra_unidade_entry = tk.Entry(extra_stock_frame, font=font_label, width=10, bd=2, relief="groove")
        self.extra_unidade_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        tk.Label(extra_stock_frame, text="Validade (DD/MM/YYYY):", font=font_label, fg="#800080", bg="#F5F5F5").grid(
            row=4, column=0, sticky="e", padx=5, pady=5)
        self.extra_validade_entry = DateEntry(extra_stock_frame, font=font_label, width=15, date_pattern='dd/mm/yyyy',
                                              background="#800080", foreground="white", borderwidth=2)
        self.extra_validade_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        tk.Button(
            extra_stock_frame, text="Adicionar Estoque Extra", command=self.add_extra_stock,
            bg="#FFA500", fg="#FFFFFF", font=font_button, activebackground="#800080", width=20, height=2
        ).grid(row=5, column=0, columnspan=2, pady=10, sticky="we")

        self.load_foods_to_combo()

        # O comando de fechar a janela pai foi removido do __init__
        # self.parent_window.destroy() <- REMOVIDO

    def go_back(self):
        """Fecha a janela atual e reexibe a Dashboard (janela pai)."""
        self.window.destroy()
        self.parent_window.deiconify()  # Reexibe a janela pai

    def load_foods_to_combo(self):
        foods = db.get_foods()
        self.foods_combo['values'] = [f"{food[1]} (ID: {food[0]})" for food in foods]
        self.foods_combo.food_ids = {f"{food[1]} (ID: {food[0]})": food[0] for food in foods}
        if foods:
            self.foods_combo.current(0)

    def load_categories_to_combo(self):
        categories = db.get_categories()
        self.cats_combo['values'] = categories
        if categories:
            self.cats_combo.current(0)

    def add_category_to_list(self):
        selected_cat = self.cats_combo.get()
        if not selected_cat:
            messagebox.showerror("Erro", "Selecione uma categoria")
            return
        if selected_cat not in self.cats_listbox.get(0, tk.END):
            self.cats_listbox.insert(tk.END, selected_cat)

    def add_food_with_stock(self):
        nome = self.nome_entry.get().strip()
        nut_data = []
        for entry in self.nut_entries:
            val = entry.get().strip()
            nut_data.append(float(val) if val else 0.0)
        cats = list(self.cats_listbox.get(0, tk.END))
        marca = self.marca_entry.get().strip()
        valor_str = self.valor_entry.get().strip()
        unidade = self.unidade_entry.get().strip()[:5]
        validade = self.validade_entry.get()

        if isinstance(unidade, (int, float)):
            messagebox.showerror("Erro", "Unidade de medida não pode conter números (ex: kg, l, ml):")
            return

        if not nome or not cats:
            messagebox.showerror("Erro", "Nome do alimento e pelo menos uma categoria são obrigatórios")
            return

        if not all(c in db.get_categories() for c in cats):
            messagebox.showerror("Erro", "Categorias inválidas")
            return

        if not marca or not valor_str or not unidade or not validade:
            messagebox.showerror("Erro", "Preencha os campos de estoque inicial")
            return

        try:
            valor = float(valor_str)
            validade_db = datetime.strptime(validade, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Erro", "Dados de estoque inválidos (quantidade numérica, data DD/MM/YYYY)")
            return

        id_nut = db.add_nutritional_table(nut_data)
        food_id = db.add_food(nome, id_nut, cats)
        db.add_stock_unit(food_id, marca, valor, unidade, validade_db, self.entrada)

        self.load_foods_to_combo()

        for entry in self.nut_entries + [self.nome_entry, self.marca_entry, self.valor_entry, self.unidade_entry]:
            entry.delete(0, tk.END)
        self.cats_listbox.delete(0, tk.END)
        self.validade_entry.set_date(datetime.now())
        messagebox.showinfo("Sucesso", "Alimento e estoque inicial adicionados")

    def add_extra_stock(self):
        try:
            selected_food = self.foods_combo.get()
            if not selected_food:
                messagebox.showerror("Erro", "Selecione um alimento")
                return
            food_id = self.foods_combo.food_ids.get(selected_food)
            marca = self.extra_marca_entry.get().strip()
            valor = float(self.extra_valor_entry.get())
            unidade = self.extra_unidade_entry.get()[:5]

            if isinstance(unidade, (int, float)):
                messagebox.showerror("Erro", "Unidade de medida não pode conter números (ex: kg, l, ml):")
                return

            validade = self.extra_validade_entry.get()
            validade_db = datetime.strptime(validade, '%d/%m/%Y').strftime('%Y-%m-%d')
            db.add_stock_unit(food_id, marca, valor, unidade, validade_db, self.entrada)

            self.extra_marca_entry.delete(0, tk.END)
            self.extra_valor_entry.delete(0, tk.END)
            self.extra_unidade_entry.delete(0, tk.END)
            self.extra_validade_entry.set_date(datetime.now())
            messagebox.showinfo("Sucesso", "Estoque adicional adicionado")
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos (quantidade numérica, data DD/MM/YYYY)")