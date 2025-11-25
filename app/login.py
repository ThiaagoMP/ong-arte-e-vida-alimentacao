import tkinter as tk
from tkinter import messagebox

from app.dashboard import DashboardWindow

PREDEFINED_PASSWORD = "admin"


class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Login - Sistema de Estoque")

        self.center_window(400, 350)

        self.window.configure(bg="#F5F5F5")
        self.window.resizable(False, False)

        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(expand=True)

        tk.Label(
            main_frame,
            text="Sistema de Estoque de Alimentos",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        tk.Label(
            main_frame,
            text="Senha:",
            font=font_label,
            fg="#FFA500",
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
        self.password_entry.pack(pady=10, ipady=5)
        self.password_entry.focus_set()

        tk.Button(
            main_frame,
            text="Entrar",
            command=self.login,
            bg="#800080",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#FFA500",
            width=15
        ).pack(pady=20)

        self.window.bind('<Return>', lambda event: self.login())

        self.window.mainloop()

    def center_window(self, width, height):
        """Calcula a posição para centralizar a janela na tela."""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.window.geometry(f'{width}x{height}+{x}+{y}')

    def login(self):
        if self.password_entry.get() == PREDEFINED_PASSWORD:
            self.window.destroy()
            DashboardWindow()
        else:
            messagebox.showerror("Erro", "Senha incorreta")