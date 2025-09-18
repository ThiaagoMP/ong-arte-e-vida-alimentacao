import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from database import db_functions as db


class MenuManagerWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Gerenciar Cardápios")
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
            text="Gerenciamento de Cardápios",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        # Frame de adição
        add_frame = tk.LabelFrame(
            main_frame,
            text="Adicionar Cardápio",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        add_frame.pack(fill="x", pady=10)

        tk.Label(
            add_frame,
            text="Data (DD/MM/YYYY, opcional):",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.data_entry = DateEntry(
            add_frame,
            font=font_label,
            width=20,
            date_pattern='dd/mm/yyyy',
            background="#800080",
            foreground="white",
            borderwidth=2
        )
        self.data_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(
            add_frame,
            text="Descrição:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.desc_entry = tk.Entry(
            add_frame,
            font=font_label,
            width=30,
            bd=2,
            relief="groove"
        )
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        # Seleção de alimentos
        tk.Label(
            add_frame,
            text="Alimento:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.foods_combo = ttk.Combobox(
            add_frame,
            font=font_label,
            width=30,
            state="readonly"
        )
        self.foods_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.load_foods_to_combo()

        tk.Label(
            add_frame,
            text="Quantidade:",
            font=font_label,
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.food_qty_entry = tk.Entry(
            add_frame,
            font=font_label,
            width=10,
            bd=2,
            relief="groove"
        )
        self.food_qty_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Button(
            add_frame,
            text="Adicionar Alimento",
            command=self.add_food_to_list,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=15
        ).grid(row=4, column=0, columnspan=2, pady=5)

        self.food_listbox = tk.Listbox(
            add_frame,
            font=font_label,
            width=40,
            height=5,
            bd=2,
            relief="groove"
        )
        self.food_listbox.grid(row=5, column=0, columnspan=2, pady=5)

        tk.Button(
            add_frame,
            text="Adicionar Cardápio",
            command=self.add_menu,
            bg="#FFA500",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#800080",
            width=20,
            height=2
        ).grid(row=6, column=0, columnspan=2, pady=10, sticky="we")

        # Lista de cardápios
        list_frame = tk.LabelFrame(
            main_frame,
            text="Cardápios Existentes",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        list_frame.pack(fill="both", expand=True, pady=10)

        self.menu_list = ttk.Treeview(
            list_frame,
            columns=("ID", "Data", "Descrição"),
            show="headings",
            height=10
        )
        self.menu_list.heading("ID", text="ID")
        self.menu_list.heading("Data", text="Data")
        self.menu_list.heading("Descrição", text="Descrição")
        self.menu_list.column("ID", width=50, anchor="center")
        self.menu_list.column("Data", width=100, anchor="center")
        self.menu_list.column("Descrição", width=300, anchor="w")
        self.menu_list.pack(pady=10, fill="x")
        self.load_menus()

        # Botões de edição e exclusão
        button_frame = tk.Frame(list_frame, bg="#F5F5F5")
        button_frame.pack(pady=10)
        tk.Button(
            button_frame,
            text="Editar",
            command=self.edit_menu,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=12
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Remover",
            command=self.delete_menu,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=12
        ).pack(side="left", padx=10)

    def load_foods_to_combo(self):
        foods = db.get_foods()
        self.foods_combo['values'] = [f"{food[1]} (ID: {food[0]})" for food in foods]
        self.foods_combo.food_ids = {f"{food[1]} (ID: {food[0]})": food[0] for food in foods}
        if foods:
            self.foods_combo.current(0)

    def load_menus(self):
        for i in self.menu_list.get_children():
            self.menu_list.delete(i)
        menus = db.get_menus()
        for menu in menus:
            data_display = datetime.strptime(menu[1], '%Y-%m-%d').strftime('%d/%m/%Y') if menu[1] else "-"
            self.menu_list.insert("", "end", values=(menu[0], data_display, menu[2]))

    def add_food_to_list(self):
        selected_food = self.foods_combo.get()
        qty = self.food_qty_entry.get().strip()
        if not selected_food:
            messagebox.showerror("Erro", "Selecione um alimento")
            return
        try:
            qty = float(qty)
            if qty <= 0:
                raise ValueError("Quantidade deve ser maior que zero")
            food_id = self.foods_combo.food_ids.get(selected_food)
            self.food_listbox.insert(tk.END, f"{selected_food}: {qty}")
            self.food_qty_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Erro", "Quantidade inválida (use um número maior que zero)")

    def add_menu(self):
        data = self.data_entry.get().strip() or None
        desc = self.desc_entry.get().strip()
        foods_quantities = []

        if data:
            try:
                datetime.strptime(data, '%d/%m/%Y')
            except ValueError:
                messagebox.showerror("Erro", "Data inválida (use DD/MM/YYYY)")
                return

        if not desc:
            messagebox.showerror("Erro", "Descrição é obrigatória")
            return

        for item in self.food_listbox.get(0, tk.END):
            try:
                food_str, qty = item.rsplit(": ", 1)
                food_id = self.foods_combo.food_ids.get(food_str)
                qty = float(qty)
                foods_quantities.append((food_id, qty))
            except ValueError:
                messagebox.showerror("Erro", "Erro ao processar alimentos selecionados")
                return

        if not foods_quantities:
            messagebox.showerror("Erro", "Pelo menos um alimento deve ser informado")
            return

        for fid, qty in foods_quantities:
            if not db.food_exists(fid):
                messagebox.showerror("Erro", f"Alimento ID {fid} não existe")
                return
            available_stock = db.get_available_stock(fid)
            if available_stock < qty:
                messagebox.showerror("Erro", f"Estoque insuficiente para alimento ID {fid}")
                return

        data_db = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d') if data else None
        menu_id = db.add_menu(data_db, desc, foods_quantities)
        if menu_id:
            for fid, qty in foods_quantities:
                db.update_stock_on_menu(fid, qty, datetime.now().strftime('%Y-%m-%d'))
            self.load_menus()
            self.data_entry.set_date(datetime.now())
            self.desc_entry.delete(0, tk.END)
            self.food_listbox.delete(0, tk.END)
            messagebox.showinfo("Sucesso", "Cardápio adicionado com sucesso")
        else:
            messagebox.showerror("Erro", "Falha ao adicionar cardápio")

    def edit_menu(self):
        selected = self.menu_list.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione um cardápio para editar")
            return

        menu_id = self.menu_list.item(selected)["values"][0]
        menu = db.get_menu(menu_id)
        if not menu:
            messagebox.showerror("Erro", "Cardápio não encontrado")
            return

        foods = db.get_menu_foods(menu_id)
        edit_window = tk.Toplevel()
        edit_window.title("Editar Cardápio")
        edit_window.geometry("1920x1080")
        edit_window.configure(bg="#F5F5F5")
        edit_frame = tk.Frame(edit_window, bg="#F5F5F5", padx=20, pady=20)
        edit_frame.pack(fill="both", expand=True)

        tk.Label(
            edit_frame,
            text="Data (DD/MM/YYYY, opcional):",
            font=("Helvetica", 12),
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)
        data_entry = DateEntry(
            edit_frame,
            font=("Helvetica", 12),
            width=20,
            date_pattern='dd/mm/yyyy',
            background="#800080",
            foreground="white",
            borderwidth=2
        )
        if menu[1]:
            data_entry.set_date(datetime.strptime(menu[1], '%Y-%m-%d'))
        data_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(
            edit_frame,
            text="Descrição:",
            font=("Helvetica", 12),
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=1, column=0, sticky="e", padx=5, pady=5)
        desc_entry = tk.Entry(
            edit_frame,
            font=("Helvetica", 12),
            width=30,
            bd=2,
            relief="groove"
        )
        desc_entry.insert(0, menu[2])
        desc_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(
            edit_frame,
            text="Alimento:",
            font=("Helvetica", 12),
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=2, column=0, sticky="e", padx=5, pady=5)
        foods_combo = ttk.Combobox(
            edit_frame,
            font=("Helvetica", 12),
            width=30,
            state="readonly"
        )
        foods_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        foods = db.get_foods()
        foods_combo['values'] = [f"{food[1]} (ID: {food[0]})" for food in foods]
        foods_combo.food_ids = {f"{food[1]} (ID: {food[0]})": food[0] for food in foods}
        if foods:
            foods_combo.current(0)

        tk.Label(
            edit_frame,
            text="Quantidade:",
            font=("Helvetica", 12),
            fg="#800080",
            bg="#F5F5F5"
        ).grid(row=3, column=0, sticky="e", padx=5, pady=5)
        food_qty_entry = tk.Entry(
            edit_frame,
            font=("Helvetica", 12),
            width=10,
            bd=2,
            relief="groove"
        )
        food_qty_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        food_listbox = tk.Listbox(
            edit_frame,
            font=("Helvetica", 12),
            width=40,
            height=5,
            bd=2,
            relief="groove"
        )
        food_listbox.grid(row=4, column=0, columnspan=2, pady=5)
        for f in db.get_menu_foods(menu_id):
            food_name = next((food[1] for food in foods if food[0] == f[0]), f"ID: {f[0]}")
            food_listbox.insert(tk.END, f"{food_name} (ID: {f[0]}): {f[1]}")

        def add_food_to_list():
            selected_food = foods_combo.get()
            qty = food_qty_entry.get().strip()
            if not selected_food:
                messagebox.showerror("Erro", "Selecione um alimento")
                return
            try:
                qty = float(qty)
                if qty <= 0:
                    raise ValueError("Quantidade deve ser maior que zero")
                food_listbox.insert(tk.END, f"{selected_food}: {qty}")
                food_qty_entry.delete(0, tk.END)
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida (use um número maior que zero)")

        tk.Button(
            edit_frame,
            text="Adicionar Alimento",
            command=add_food_to_list,
            bg="#800080",
            fg="#FFFFFF",
            font=("Helvetica", 12, "bold"),
            activebackground="#FFA500",
            width=15
        ).grid(row=5, column=0, columnspan=2, pady=5)

        def save():
            new_data = data_entry.get().strip() or None
            new_desc = desc_entry.get().strip()
            new_foods = []

            if new_data:
                try:
                    datetime.strptime(new_data, '%d/%m/%Y')
                except ValueError:
                    messagebox.showerror("Erro", "Data inválida (use DD/MM/YYYY)")
                    return

            if not new_desc:
                messagebox.showerror("Erro", "Descrição é obrigatória")
                return

            for item in food_listbox.get(0, tk.END):
                try:
                    food_str, qty = item.rsplit(": ", 1)
                    fid = foods_combo.food_ids.get(food_str)
                    qty = float(qty)
                    if qty <= 0:
                        raise ValueError("Quantidade deve ser maior que zero")
                    new_foods.append((fid, qty))
                except ValueError:
                    messagebox.showerror("Erro", "Erro ao processar alimentos selecionados")
                    return

            if not new_foods:
                messagebox.showerror("Erro", "Pelo menos um alimento deve ser informado")
                return

            for fid, qty in new_foods:
                if not db.food_exists(fid):
                    messagebox.showerror("Erro", f"Alimento ID {fid} não existe")
                    return
                available_stock = db.get_available_stock(fid)
                if available_stock < qty:
                    messagebox.showerror("Erro", f"Estoque insuficiente para alimento ID {fid}")
                    return

            new_data_db = datetime.strptime(new_data, '%d/%m/%Y').strftime('%Y-%m-%d') if new_data else None
            if db.update_menu(menu_id, new_data_db, new_desc, new_foods):
                for fid, qty in new_foods:
                    db.update_stock_on_menu(fid, qty, datetime.now().strftime('%Y-%m-%d'))
                self.load_menus()
                edit_window.destroy()
                messagebox.showinfo("Sucesso", "Cardápio atualizado com sucesso")
            else:
                messagebox.showerror("Erro", "Falha ao atualizar cardápio")

        tk.Button(
            edit_frame,
            text="Salvar",
            command=save,
            bg="#FFA500",
            fg="#FFFFFF",
            font=("Helvetica", 12, "bold"),
            activebackground="#800080",
            width=15
        ).grid(row=6, column=0, columnspan=2, pady=10, sticky="we")

    def delete_menu(self):
        selected = self.menu_list.selection()
        if selected:
            menu_id = self.menu_list.item(selected)["values"][0]
            if messagebox.askyesno("Confirmação", "Deseja remover este cardápio?"):
                if db.delete_menu(menu_id):
                    self.load_menus()
                    messagebox.showinfo("Sucesso", "Cardápio removido")
                else:
                    messagebox.showerror("Erro", "Falha ao remover cardápio")