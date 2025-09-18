import tkinter as tk
from tkinter import messagebox
from dashboard import DashboardWindow

PREDEFINED_PASSWORD = "admin"  # Alterar em produção

class LoginWindow:
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Login - Sistema de Estoque")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#F5F5F5")
        self.window.resizable(False, False)

        # Estilo
        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        # Frame principal
        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(expand=True)

        # Título
        tk.Label(
            main_frame,
            text="Sistema de Estoque de Alimentos",
            font=font_title,
            fg="#800080",  # Roxo
            bg="#F5F5F5"
        ).pack(pady=20)

        # Campo de senha
        tk.Label(
            main_frame,
            text="Senha:",
            font=font_label,
            fg="#FFA500",  # Laranja
            bg="#F5F5F5"
        ).pack()
        self.password_entry = tk.Entry(
            main_frame,
            show="*",
            font=font_label,
            width=20,
            bd=2,
            relief="groove"
        )
        self.password_entry.pack(pady=10)

        # Botão de login
        tk.Button(
            main_frame,
            text="Entrar",
            command=self.login,
            bg="#800080",  # Roxo
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",  # Laranja ao clicar
            width=15
        ).pack(pady=20)

        self.window.mainloop()

    def login(self):
        if self.password_entry.get() == PREDEFINED_PASSWORD:
            self.window.destroy()
            DashboardWindow()
        else:
            messagebox.showerror("Erro", "Senha incorreta")