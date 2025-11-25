import tkinter as tk
from tkinter import ttk, messagebox
from database import db_functions as db


# Importe a classe da Dashboard aqui para poder reabri-la.
# Exemplo: from dashboard import DashboardWindow
# **OBSERVAÇÃO:** Mantenha a importação comentada ou ajuste o caminho conforme sua estrutura.
# Se a DashboardWindow estiver no mesmo arquivo ou já tiver sido importada no ponto de chamada, não há problema.


class CategoryManagerWindow:
    # 1. Adicionado 'parent_window' ao construtor
    def __init__(self, parent_window):
        self.parent_window = parent_window  # Armazena a janela pai (DashboardWindow)
        self.window = tk.Toplevel()
        self.window.title("Gerenciar Categorias")

        # Configura o que acontece quando a janela é fechada pelo "X"
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        # 2. Lógica de maximização (Cross-platform)
        try:
            self.window.state('zoomed')
        except tk.TclError:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f'{screen_width}x{screen_height}+0+0')

        self.window.configure(bg="#F5F5F5")
        self.window.resizable(True, True)  # Permitir redimensionar

        # Estilo
        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        # Frame principal
        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        # --- NOVO: Botão Voltar ---
        back_button_frame = tk.Frame(main_frame, bg="#F5F5F5")
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

        # Título
        tk.Label(
            main_frame,
            text="Gerenciamento de Categorias",
            font=font_title,
            fg="#800080",  # Roxo
            bg="#F5F5F5"
        ).pack(pady=20)

        # Adicionar categoria
        tk.Label(
            main_frame,
            text="Nova Categoria:",
            font=font_label,
            fg="#FFA500",  # Laranja
            bg="#F5F5F5"
        ).pack()
        self.new_cat_entry = tk.Entry(
            main_frame,
            font=font_label,
            width=30,
            bd=2,
            relief="groove"
        )
        self.new_cat_entry.pack(pady=10)
        tk.Button(
            main_frame,
            text="Adicionar",
            command=self.add_category,
            bg="#FFA500",  # Laranja
            fg="#FFFFFF",
            font=font_button,
            activebackground="#800080",
            width=15
        ).pack(pady=10)

        # Lista de categorias
        tk.Label(
            main_frame,
            text="Categorias Existentes:",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5"
        ).pack(pady=10)

        # Frame para a Treeview e Scrollbar (para melhor layout)
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(pady=10, fill="both", expand=True)  # Alterado para preencher o espaço

        self.cat_list = ttk.Treeview(
            tree_frame,
            columns=("Nome",),
            show="headings"
        )
        self.cat_list.heading("Nome", text="Nome")
        self.cat_list.column("Nome", anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.cat_list.yview)
        self.cat_list.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.cat_list.pack(side="left", fill="both", expand=True)

        self.load_categories()

        # Botões de edição e exclusão
        button_frame = tk.Frame(main_frame, bg="#F5F5F5")
        button_frame.pack(pady=20)
        tk.Button(
            button_frame,
            text="Editar",
            command=self.edit_category,
            bg="#800080",  # Roxo
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=12
        ).pack(side="left", padx=10)
        tk.Button(
            button_frame,
            text="Remover",
            command=self.delete_category,
            bg="#800080",  # Roxo
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=12
        ).pack(side="left", padx=10)

        # 3. A janela pai não é mais destruída aqui, mas sim no ponto de chamada,
        # para que possamos reabri-la
        # self.parent_window.destroy()  <-- REMOVIDO DAQUI

    def go_back(self):
        """Fecha a janela atual e reabre a Dashboard."""
        self.window.destroy()
        self.parent_window.deiconify()  # Assumindo que a Dashboard foi minimizada (ou é reaberta)

    def load_categories(self):
        # ... (Mantido) ...
        for i in self.cat_list.get_children():
            self.cat_list.delete(i)
        categories = db.get_categories()
        for cat in categories:
            self.cat_list.insert("", "end", values=(cat,))

    def add_category(self):
        # ... (Mantido) ...
        nome = self.new_cat_entry.get().strip()
        if nome:
            if db.add_category(nome):
                self.load_categories()
                self.new_cat_entry.delete(0, tk.END)
                messagebox.showinfo("Sucesso", "Categoria adicionada")
            else:
                messagebox.showerror("Erro", "Categoria já existe")
        else:
            messagebox.showerror("Erro", "Nome vazio")

    def edit_category(self):
        # ... (Mantido) ...
        selected = self.cat_list.selection()
        if selected:
            old_nome = self.cat_list.item(selected)["values"][0]
            edit_window = tk.Toplevel()
            edit_window.title("Editar Categoria")

            # (Bônus) Ajuste na geometria da janela de edição
            edit_window.geometry("400x200")

            edit_window.configure(bg="#F5F5F5")
            tk.Label(
                edit_window,
                text="Novo Nome:",
                font=("Helvetica", 12),
                fg="#FFA500",
                bg="#F5F5F5"
            ).pack(pady=10)
            entry = tk.Entry(edit_window, font=("Helvetica", 12), width=30)
            entry.insert(0, old_nome)
            entry.pack(pady=10)

            def save():
                new_nome = entry.get().strip()
                if new_nome:
                    if db.update_category(old_nome, new_nome):
                        self.load_categories()
                        edit_window.destroy()
                        messagebox.showinfo("Sucesso", "Categoria atualizada")
                    else:
                        messagebox.showerror("Erro", "Falha ao atualizar categoria")
                else:
                    messagebox.showerror("Erro", "Nome vazio")

            tk.Button(
                edit_window,
                text="Salvar",
                command=save,
                bg="#FFA500",
                fg="#FFFFFF",
                font=("Helvetica", 12, "bold"),
                activebackground="#800080",
                width=10
            ).pack(pady=10)

    def delete_category(self):
        # ... (Mantido) ...
        selected = self.cat_list.selection()
        if not selected:
            messagebox.showerror("Erro", "Selecione uma categoria para remover")
            return
        nome = self.cat_list.item(selected)["values"][0]
        if messagebox.askyesno("Confirmação", f"Deseja remover a categoria '{nome}'?"):
            if db.delete_category(nome):
                self.load_categories()
                messagebox.showinfo("Sucesso", "Categoria removida")
            else:
                messagebox.showerror("Erro", "Categoria em uso ou falha ao remover")