import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from database import db_functions as db


class FoodManagerWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Gerenciar Alimentos")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#F5F5F5")
        self.window.resizable(False, False)

        # Estilo
        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        # Canvas e Scrollbar
        canvas = tk.Canvas(self.window, bg="#F5F5F5")
        scrollbar = tk.Scrollbar(self.window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#F5F5F5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        # Título
        tk.Label(
            scrollable_frame,
            text="Gerenciamento de Alimentos",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        # Frame de adição de alimento
        add_frame = tk.LabelFrame(
            scrollable_frame,
            text="Adicionar Alimento",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        add_frame.pack(fill="x", pady=10)

        # Nome do alimento
        tk.Label(
            add_frame,
            text="Nome:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.nome_entry = tk.Entry(
            add_frame,
            font=font_label,
            width=30,
            bd=2,
            relief="groove"
        )
        self.nome_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Tabela nutricional
        nut_labels = [
            "Valor Energético (kcal)", "Carboidratos (g)", "Açúcares Totais (g)",
            "Açúcares Adicionados (g)", "Proteínas (g)", "Gorduras Totais (g)",
            "Gorduras Saturadas (g)", "Gorduras Trans (g)", "Fibras (g)",
            "Sódio (mg)", "Cálcio (mg)"
        ]
        self.nut_entries = []
        for i, label in enumerate(nut_labels):
            tk.Label(
                add_frame,
                text=label,
                font=font_label,
                fg="#800080",
                bg="#F5F5F5"
            ).grid(row=i+1, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(
                add_frame,
                font=font_label,
                width=20,
                bd=2,
                relief="groove"
            )
            entry.grid(row=i+1, column=1, padx=5, pady=5, sticky="w")
            self.nut_entries.append(entry)

        # Categorias
        tk.Label(
            add_frame,
            text="Categoria:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=len(nut_labels)+1, column=0, sticky="e", padx=5, pady=5)
        self.cats_combo = ttk.Combobox(
            add_frame,
            font=font_label,
            width=30,
            state="readonly"
        )
        self.cats_combo.grid(row=len(nut_labels)+1, column=1, padx=5, pady=5, sticky="w")
        self.load_categories_to_combo()

        tk.Button(
            add_frame,
            text="Adicionar Categoria",
            command=self.add_category_to_list,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=15
        ).grid(row=len(nut_labels)+2, column=0, columnspan=2, pady=5)

        self.cats_listbox = tk.Listbox(
            add_frame,
            font=font_label,
            width=30,
            height=5,
            bd=2,
            relief="groove"
        )
        self.cats_listbox.grid(row=len(nut_labels)+3, column=0, columnspan=2, pady=5)

        # Campos para estoque inicial
        stock_section = tk.LabelFrame(
            add_frame,
            text="Estoque Inicial",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5",
            padx=5,
            pady=5
        )
        stock_section.grid(row=0, column=2, rowspan=len(nut_labels)+4, sticky="ns", padx=20, pady=5)

        tk.Label(
            stock_section,
            text="Marca:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.marca_entry = tk.Entry(
            stock_section,
            font=font_label,
            width=20,
            bd=2,
            relief="groove"
        )
        self.marca_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            stock_section,
            text="Quantidade:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.valor_entry = tk.Entry(
            stock_section,
            font=font_label,
            width=10,
            bd=2,
            relief="groove"
        )
        self.valor_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            stock_section,
            text="Unidade (ex: kg):",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.unidade_entry = tk.Entry(
            stock_section,
            font=font_label,
            width=10,
            bd=2,
            relief="groove"
        )
        self.unidade_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            stock_section,
            text="Validade (DD/MM/YYYY):",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.validade_entry = DateEntry(
            stock_section,
            font=font_label,
            width=15,
            date_pattern='dd/mm/yyyy',
            background="#800080",
            foreground="white",
            borderwidth=2
        )
        self.validade_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        self.entrada = datetime.now().strftime('%d/%m/%Y')

        # Botão de adicionar alimento
        button_frame = tk.Frame(add_frame, bg="#F5F5F5")
        button_frame.grid(row=len(nut_labels)+4, column=0, columnspan=3, pady=15, sticky="we")
        tk.Button(
            button_frame,
            text="Adicionar Alimento e Estoque",
            command=self.add_food_with_stock,
            bg="#FFA500",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#800080",
            width=25,
            height=2
        ).pack(pady=5, fill="x")

        # Frame de adição de estoque extra
        extra_stock_frame = tk.LabelFrame(
            scrollable_frame,
            text="Adicionar Estoque a Alimento Existente",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        extra_stock_frame.pack(fill="x", pady=10)

        tk.Label(
            extra_stock_frame,
            text="Alimento:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.foods_combo = ttk.Combobox(
            extra_stock_frame,
            font=font_label,
            width=30,
            state="readonly"
        )
        self.foods_combo.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.load_foods_to_combo()

        tk.Label(
            extra_stock_frame,
            text="Marca:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.extra_marca_entry = tk.Entry(
            extra_stock_frame,
            font=font_label,
            width=20,
            bd=2,
            relief="groove"
        )
        self.extra_marca_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            extra_stock_frame,
            text="Quantidade:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.extra_valor_entry = tk.Entry(
            extra_stock_frame,
            font=font_label,
            width=10,
            bd=2,
            relief="groove"
        )
        self.extra_valor_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            extra_stock_frame,
            text="Unidade (ex: kg):",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.extra_unidade_entry = tk.Entry(
            extra_stock_frame,
            font=font_label,
            width=10,
            bd=2,
            relief="groove"
        )
        self.extra_unidade_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            extra_stock_frame,
            text="Validade (DD/MM/YYYY):",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.extra_validade_entry = DateEntry(
            extra_stock_frame,
            font=font_label,
            width=15,
            date_pattern='dd/mm/yyyy',
            background="#800080",
            foreground="white",
            borderwidth=2
        )
        self.extra_validade_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        tk.Button(
            extra_stock_frame,
            text="Adicionar Estoque Extra",
            command=self.add_extra_stock,
            bg="#FFA500",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#800080",
            width=20,
            height=2
        ).grid(row=5, column=0, columnspan=2, pady=10, sticky="we")

        # Frame de lista e busca
        list_frame = tk.LabelFrame(
            scrollable_frame,
            text="Lista de Alimentos",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        list_frame.pack(fill="both", expand=True, pady=10)

        self.food_list = ttk.Treeview(
            list_frame,
            columns=("ID", "Nome"),
            show="headings",
            height=8
        )
        self.food_list.heading("ID", text="ID")
        self.food_list.heading("Nome", text="Nome")
        self.food_list.column("ID", width=50, anchor="center")
        self.food_list.column("Nome", width=300, anchor="w")
        self.food_list.pack(pady=10, fill="x")
        self.load_foods()

        # Botões de edição e exclusão
        button_frame = tk.Frame(list_frame, bg="#F5F5F5")
        button_frame.pack(pady=10)
        tk.Button(
            button_frame,
            text="Editar",
            command=self.edit_food,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=12
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Remover",
            command=self.delete_food,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=12
        ).pack(side="left", padx=10)

        # Frame de busca
        search_frame = tk.LabelFrame(
            scrollable_frame,
            text="Buscar Alimentos",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        search_frame.pack(fill="x", pady=10)

        tk.Label(
            search_frame,
            text="Nome:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.search_name = tk.Entry(
            search_frame,
            font=font_label,
            width=20,
            bd=2,
            relief="groove"
        )
        self.search_name.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(
            search_frame,
            text="Categoria:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.search_cat = tk.Entry(
            search_frame,
            font=font_label,
            width=20,
            bd=2,
            relief="groove"
        )
        self.search_cat.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.near_expiry_var = tk.BooleanVar()
        tk.Checkbutton(
            search_frame,
            text="Próximos da Validade (< 7 dias)",
            variable=self.near_expiry_var,
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=2, column=0, columnspan=2, pady=5)

        tk.Button(
            search_frame,
            text="Buscar",
            command=self.search,
            bg="#FFA500",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#800080",
            width=15,
            height=2
        ).grid(row=3, column=0, columnspan=2, pady=10, sticky="we")

        self.load_foods()

    def load_foods(self):
        for i in self.food_list.get_children():
            self.food_list.delete(i)
        foods = db.get_foods()
        for food in foods:
            self.food_list.insert("", "end", values=(food[0], food[1]))

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
            valor = int(valor_str)
            validade_db = datetime.strptime(validade, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Erro", "Dados de estoque inválidos (quantidade inteira, data DD/MM/YYYY)")
            return

        id_nut = db.add_nutritional_table(nut_data)
        food_id = db.add_food(nome, id_nut, cats)
        db.add_stock_unit(food_id, marca, valor, unidade, validade_db, self.entrada)

        self.load_foods()
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
            valor = int(self.extra_valor_entry.get())
            unidade = self.extra_unidade_entry.get()[:5]
            validade = self.extra_validade_entry.get()
            validade_db = datetime.strptime(validade, '%d/%m/%Y').strftime('%Y-%m-%d')
            db.add_stock_unit(food_id, marca, valor, unidade, validade_db, self.entrada)
            self.extra_marca_entry.delete(0, tk.END)
            self.extra_valor_entry.delete(0, tk.END)
            self.extra_unidade_entry.delete(0, tk.END)
            self.extra_validade_entry.set_date(datetime.now())
            messagebox.showinfo("Sucesso", "Estoque adicional adicionado")
        except ValueError:
            messagebox.showerror("Erro", "Dados inválidos (quantidade inteira, data DD/MM/YYYY)")

    def edit_food(self):
        selected = self.food_list.selection()
        if selected:
            food_id = self.food_list.item(selected)["values"][0]
            food, nut, cats, stocks = db.get_food_details(food_id)
            edit_window = tk.Toplevel()
            edit_window.title("Editar Alimento")
            edit_window.geometry("1920x1080")
            edit_window.configure(bg="#F5F5F5")
            edit_frame = tk.Frame(edit_window, bg="#F5F5F5", padx=20, pady=20)
            edit_frame.pack(fill="both", expand=True)
            tk.Label(
                edit_frame,
                text="Nome:",
                font=("Helvetica", 12),
                fg="#800080",
                bg="#F5F5F5"
            ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
            nome_entry = tk.Entry(
                edit_frame,
                font=("Helvetica", 12),
                width=30,
                bd=2,
                relief="groove"
            )
            nome_entry.insert(0, food[1])
            nome_entry.grid(row=0, column=1, padx=5, pady=5)
            nut_entries = []
            for i, val in enumerate(nut[1:]):
                tk.Label(
                    edit_frame,
                    text=f"Nutriente {i+1}:",
                    font=("Helvetica", 12),
                    fg="#800080",
                    bg="#F5F5F5"
                ).grid(row=i+1, column=0, sticky="e", padx=5, pady=5)
                entry = tk.Entry(
                    edit_frame,
                    font=("Helvetica", 12),
                    width=20,
                    bd=2,
                    relief="groove"
                )
                entry.insert(0, str(val))
                entry.grid(row=i+1, column=1, padx=5, pady=5)
                nut_entries.append(entry)
            tk.Label(
                edit_frame,
                text="Categoria:",
                font=("Helvetica", 12),
                fg="#800080",
                bg="#F5F5F5"
            ).grid(row=len(nut[1:])+1, column=0, sticky="e", padx=5, pady=5)
            cats_combo = ttk.Combobox(
                edit_frame,
                font=("Helvetica", 12),
                width=30,
                state="readonly"
            )
            cats_combo.grid(row=len(nut[1:])+1, column=1, padx=5, pady=5, sticky="w")
            cats_combo['values'] = db.get_categories()
            if cats_combo['values']:
                cats_combo.current(0)
            cats_listbox = tk.Listbox(
                edit_frame,
                font=("Helvetica", 12),
                width=30,
                height=5,
                bd=2,
                relief="groove"
            )
            cats_listbox.grid(row=len(nut[1:])+2, column=0, columnspan=2, pady=5)
            for cat in cats:
                cats_listbox.insert(tk.END, cat)
            def add_category_to_list():
                selected_cat = cats_combo.get()
                if selected_cat and selected_cat not in cats_listbox.get(0, tk.END):
                    cats_listbox.insert(tk.END, selected_cat)
            tk.Button(
                edit_frame,
                text="Adicionar Categoria",
                command=add_category_to_list,
                bg="#800080",
                fg="#FFFFFF",
                font=("Helvetica", 12, "bold"),
                activebackground="#FFA500",
                width=15
            ).grid(row=len(nut[1:])+3, column=0, columnspan=2, pady=5)
            def save():
                new_nome = nome_entry.get().strip()
                new_nut = [float(e.get() or 0) for e in nut_entries]
                new_cats = list(cats_listbox.get(0, tk.END))
                if new_nome and new_cats:
                    if all(c in db.get_categories() for c in new_cats):
                        db.update_nutritional(nut[0], new_nut)
                        db.update_food(food_id, new_nome, nut[0], new_cats)
                        self.load_foods()
                        self.load_foods_to_combo()
                        edit_window.destroy()
                        messagebox.showinfo("Sucesso", "Alimento atualizado")
                    else:
                        messagebox.showerror("Erro", "Categorias inválidas")
                else:
                    messagebox.showerror("Erro", "Nome e pelo menos uma categoria são obrigatórios")
            tk.Button(
                edit_frame,
                text="Salvar",
                command=save,
                bg="#FFA500",
                fg="#FFFFFF",
                font=("Helvetica", 12, "bold"),
                activebackground="#800080",
                width=15
            ).grid(row=len(nut[1:])+4, column=0, columnspan=2, pady=10)

    def delete_food(self):
        selected = self.food_list.selection()
        if selected:
            food_id = self.food_list.item(selected)["values"][0]
            if db.delete_food(food_id):
                self.load_foods()
                self.load_foods_to_combo()
                messagebox.showinfo("Sucesso", "Alimento removido")
            else:
                messagebox.showerror("Erro", "Alimento em uso em cardápios")

    def search(self):
        name = self.search_name.get().strip() or None
        cat = self.search_cat.get().strip() or None
        near = self.near_expiry_var.get()
        foods = db.search_foods(name, cat, near)
        for i in self.food_list.get_children():
            self.food_list.delete(i)
        for food in foods:
            self.food_list.insert("", "end", values=food)
            if near:
                self.food_list.item(self.food_list.get_children()[-1], tags=('red',))
        self.food_list.tag_configure('red', foreground='red')