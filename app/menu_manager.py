import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry
from database import db_functions as db
import re  # Necessário para a função edit_menu corrigida


class MenuManagerWindow:
    def __init__(self, parent_window):
        # ... (código __init__ mantido) ...
        self.parent_window = parent_window
        self.editing_menu_id = None

        self.window = tk.Toplevel()
        self.window.title("Gerenciar Cardápios")
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        # ... (Configurações de layout e frames mantidas) ...

        # Configurações de fonte
        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # ---------------- VOLTAR --------------------
        back_button_frame = tk.Frame(main_frame, bg="#F5F5F5")
        back_button_frame.pack(fill="x")

        tk.Button(
            back_button_frame, text="← Voltar", command=self.go_back, bg="#800080",
            fg="#FFFFFF", font=font_button, activebackground="#FFA500", width=10
        ).pack(side="left", anchor="nw")

        # Título
        tk.Label(main_frame, text="Gerenciamento de Cardápios",
                 font=font_title, fg="#800080", bg="#F5F5F5").pack(pady=20)

        # ---------------- ADD FRAME ----------------
        add_frame = tk.LabelFrame(
            main_frame, text="Adicionar/Editar Cardápio", font=font_label,
            fg="#FFA500", bg="#F5F5F5", padx=10, pady=10
        )
        add_frame.pack(fill="x", pady=10)

        tk.Label(add_frame, text="Data (DD/MM/YYYY, opcional):",
                 font=font_label, fg="#800080", bg="#F5F5F5"
                 ).grid(row=0, column=0, sticky="e", padx=5, pady=5)

        self.data_entry = DateEntry(
            add_frame, font=font_label, width=20, date_pattern='dd/mm/yyyy',
            background="#800080", foreground="white", borderwidth=2
        )
        self.data_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Descrição:", font=font_label,
                 fg="#800080", bg="#F5F5F5"
                 ).grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.desc_entry = tk.Entry(add_frame, font=font_label,
                                   width=30, bd=2, relief="groove")
        self.desc_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_frame, text="Alimento:", font=font_label,
                 fg="#800080", bg="#F5F5F5"
                 ).grid(row=2, column=0, sticky="e", padx=5, pady=5)

        self.foods_combo = ttk.Combobox(add_frame, font=font_label,
                                        width=30, state="readonly")
        self.foods_combo.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.load_foods_to_combo()

        tk.Label(add_frame, text="Quantidade:", font=font_label,
                 fg="#800080", bg="#F5F5F5"
                 ).grid(row=3, column=0, sticky="e", padx=5, pady=5)

        self.food_qty_entry = tk.Entry(add_frame, font=font_label,
                                       width=10, bd=2, relief="groove")
        self.food_qty_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        tk.Button(add_frame, text="Adicionar Alimento",
                  command=self.add_food_to_list, bg="#800080", fg="#FFFFFF",
                  font=font_button, activebackground="#FFA500", width=15
                  ).grid(row=4, column=0, columnspan=2, pady=5)

        self.food_listbox = tk.Listbox(add_frame, font=font_label,
                                       width=40, height=5, bd=2, relief="groove")
        self.food_listbox.grid(row=5, column=0, columnspan=2, pady=5)

        # BOTÃO: Remover Alimento
        tk.Button(add_frame, text="Remover Alimento Selecionado",
                  command=self.remove_selected_food,
                  bg="#FF0000", fg="#FFFFFF", font=font_button,
                  activebackground="#AA0000", width=25
                  ).grid(row=6, column=0, columnspan=2, pady=5)

        # BOTÃO PRINCIPAL: Adicionar/Salvar
        self.btn_save = tk.Button(
            add_frame, text="Adicionar Cardápio",
            command=self.save_menu, bg="#FFA500", fg="#FFFFFF",
            font=font_button, activebackground="#800080", width=20, height=2
        )
        self.btn_save.grid(row=7, column=0, columnspan=2, pady=10, sticky="we")

        # ---------------- LISTAGEM -----------------
        list_frame = tk.LabelFrame(main_frame, text="Cardápios Existentes",
                                   font=font_label, fg="#FFA500", bg="#F5F5F5",
                                   padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, pady=10)

        tree_frame = tk.Frame(list_frame)
        tree_frame.pack(fill="both", expand=True, pady=10)

        self.menu_list = ttk.Treeview(
            tree_frame, columns=("ID", "Data", "Descrição"), show="headings"
        )
        self.menu_list.heading("ID", text="ID")
        self.menu_list.heading("Data", text="Data")
        self.menu_list.heading("Descrição", text="Descrição")
        self.menu_list.column("ID", width=50, anchor="center")
        self.menu_list.column("Data", width=100, anchor="center")
        self.menu_list.column("Descrição", width=300, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical",
                                  command=self.menu_list.yview)
        self.menu_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.menu_list.pack(side="left", fill="both", expand=True)

        self.load_menus()

        # Botões editar/remover/BAIXA NO ESTOQUE
        button_frame = tk.Frame(list_frame, bg="#F5F5F5")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Editar", command=self.edit_menu,
                  bg="#800080", fg="#FFFFFF", font=font_button,
                  activebackground="#FFA500", width=12
                  ).pack(side="left", padx=10)

        tk.Button(button_frame, text="Remover", command=self.delete_menu,
                  bg="#800080", fg="#FFFFFF", font=font_button,
                  activebackground="#FFA500", width=12
                  ).pack(side="left", padx=10)

        # 🔥 NOVO BOTÃO: BAIXA NO ESTOQUE 🔥
        tk.Button(button_frame, text="Baixa no Estoque", command=self.give_stock_out,
                  bg="#00AA00", fg="#FFFFFF", font=font_button,
                  activebackground="#008800", width=18
                  ).pack(side="left", padx=20)

    # =================== FUNÇÕES ====================
    # ... (go_back, load_foods_to_combo, load_menus, add_food_to_list,
    # remove_selected_food, _parse_food_item, save_menu, reset_form, edit_menu, delete_menu)

    def go_back(self):
        self.window.destroy()
        self.parent_window.deiconify()

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
            data_db = menu.get("Data")
            data_display = "-"
            if data_db:
                try:
                    if "/" in data_db:
                        data_display = datetime.strptime(data_db, "%d/%m/%Y").strftime("%d/%m/%Y")
                    else:
                        data_display = datetime.strptime(data_db, "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    data_display = f"Erro ({data_db})"

            # show ID, Data, Descrição
            self.menu_list.insert("", "end", values=(menu['ID'], data_display, menu['Descricao']))

    def add_food_to_list(self):
        selected_food = self.foods_combo.get()
        qty = self.food_qty_entry.get().strip()
        if not selected_food:
            messagebox.showerror("Erro", "Selecione um alimento")
            return
        try:
            qty_val = float(qty)
            if qty_val <= 0:
                raise ValueError()
            self.food_listbox.insert(tk.END, f"{selected_food}: {qty_val}")
            self.food_qty_entry.delete(0, tk.END)
        except Exception:
            messagebox.showerror("Erro", "Quantidade inválida")

    def remove_selected_food(self):
        selected = self.food_listbox.curselection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um alimento para remover.")
            return
        self.food_listbox.delete(selected[0])

    def _parse_food_item(self, item_str):
        """
        Espera item_str no formato: "Name (ID: X): qty"
        Retorna (food_id, qty) ou (None, None) se falhar.
        """
        try:
            food_part, qty_str = item_str.rsplit(": ", 1)
            qty = float(qty_str)
        except Exception:
            return None, None

        id_start = food_part.rfind("(ID:")
        if id_start != -1:
            try:
                start = id_start + len("(ID:")
                end = food_part.rfind(")")
                fid = int(food_part[start:end].strip())
                return fid, qty
            except Exception:
                return None, None

        mapping = getattr(self.foods_combo, "food_ids", {})
        fid = mapping.get(food_part)
        if fid:
            return fid, qty
        for key, v in mapping.items():
            if key.startswith(food_part):
                return v, qty

        return None, None

    def save_menu(self):
        data = self.data_entry.get().strip() or None
        desc = self.desc_entry.get().strip()
        foods_quantities = []

        if not desc:
            messagebox.showerror("Erro", "Descrição é obrigatória")
            return

        for item in self.food_listbox.get(0, tk.END):
            food_id, qty = self._parse_food_item(item)
            if food_id is None:
                messagebox.showerror("Erro", f"Não foi possível identificar o alimento na linha: '{item}'")
                return
            foods_quantities.append((food_id, qty))

        if self.editing_menu_id is None:
            menu_id = db.add_menu(data, desc, foods_quantities)
            if menu_id:
                messagebox.showinfo("Sucesso", "Cardápio adicionado!")
                self.load_menus()
                self.reset_form()
            else:
                messagebox.showerror("Erro", "Falha ao adicionar cardápio")
            return

        success = db.update_menu(self.editing_menu_id, data, desc, foods_quantities)
        if success:
            messagebox.showinfo("Sucesso", "Cardápio atualizado!")
            self.load_menus()
            self.reset_form()
        else:
            messagebox.showerror("Erro", "Falha ao salvar alterações")

    def reset_form(self):
        self.editing_menu_id = None
        try:
            self.data_entry.set_date(datetime.now())
        except Exception:
            pass
        self.desc_entry.delete(0, tk.END)
        self.food_listbox.delete(0, tk.END)
        self.btn_save.config(text="Adicionar Cardápio")

    def edit_menu(self):
        selected = self.menu_list.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um cardápio.")
            return

        selected_id = selected[0]
        item = self.menu_list.item(selected_id)
        menu_id = item["values"][0]

        menu_list = db.get_menu(menu_id)
        if not menu_list:
            messagebox.showerror("Erro", "Cardápio não encontrado.")
            return

        menu = menu_list[0]
        data = menu.get("Data", "")
        desc = menu.get("Descricao", "")
        alimentos = menu.get("Alimentos", [])

        try:
            if data and "-" in data:
                self.data_entry.set_date(datetime.strptime(data, "%Y-%m-%d").strftime("%d/%m/%Y"))
            else:
                self.data_entry.set_date(data if data else datetime.now())
        except Exception:
            try:
                self.data_entry.set_date(datetime.now())
            except Exception:
                pass

        self.desc_entry.delete(0, tk.END)
        self.desc_entry.insert(0, desc)

        self.food_listbox.delete(0, tk.END)
        for a in alimentos:
            fid = a.get('ID_Alimento') or a.get('ID') or a.get('id') or a.get('Id')
            nome = a.get('Nome') or a.get('nome') or a.get('Name') or "?"
            qty = a.get('Quantidade') or a.get('quantidade') or a.get('Qtd') or 0

            if fid is not None:
                display_food = f"{nome} (ID: {fid}): {qty}"
            else:
                display_food = f"{nome}: {qty}"
            self.food_listbox.insert(tk.END, display_food)

        self.editing_menu_id = menu_id
        self.btn_save.config(text="Salvar alterações")
        messagebox.showinfo("Modo edição", "Cardápio carregado para edição.")

    def delete_menu(self):
        selected = self.menu_list.selection()
        if not selected:
            return
        selected_id = selected[0]
        menu_id = self.menu_list.item(selected_id)["values"][0]
        if messagebox.askyesno("Confirmação", "Deseja realmente remover este cardápio?"):
            if db.delete_menu(menu_id):
                self.load_menus()
                messagebox.showinfo("Removido", "Cardápio removido.")
            else:
                messagebox.showerror("Erro", "Falha ao remover.")

    # 🔥 NOVO MÉTODO: DAR BAIXA NO ESTOQUE 🔥
    def give_stock_out(self):
        selected = self.menu_list.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um cardápio para dar baixa no estoque.")
            return

        selected_id = selected[0]
        menu_id = self.menu_list.item(selected_id)["values"][0]
        menu_desc = self.menu_list.item(selected_id)["values"][2]

        # Confirmação
        confirm = messagebox.askyesno(
            "Confirmação de Baixa",
            f"Você confirma que deseja dar baixa no estoque para todos os itens do cardápio '{menu_desc}' (ID: {menu_id})?"
        )
        if not confirm:
            return

        # 1. Busca os itens e quantidades do cardápio selecionado
        food_items = db.get_menu_items_for_stock_out(menu_id)

        if not food_items:
            messagebox.showerror("Erro", "Nenhum alimento encontrado neste cardápio ou falha na busca.")
            return

        # 2. Chama a função do banco de dados para executar a baixa
        # db.give_stock_out deve:
        # a) Checar estoque (opcional, mas recomendado)
        # b) Subtrair quantidades da tabela ALIMENTO (Estoque)
        # c) Registrar a baixa em uma tabela de histórico, se houver.

        success, message = db.give_stock_out(menu_id, food_items)

        if success:
            messagebox.showinfo("Sucesso", f"Baixa de estoque realizada com sucesso para o cardápio '{menu_desc}'.")
        else:
            # A mensagem de erro deve vir da função db.give_stock_out (e.g., estoque insuficiente)
            messagebox.showerror("Erro", f"Falha ao dar baixa no estoque: {message}")