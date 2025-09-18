import tkinter as tk
from food_manager import FoodManagerWindow
from category_manager import CategoryManagerWindow
from menu_manager import MenuManagerWindow
from report_manager import ReportManagerWindow
from stock_viewer import StockViewerWindow

class DashboardWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Dashboard - Sistema de Estoque")
        self.window.geometry("1920x1080")
        self.window.configure(bg="#F5F5F5")
        self.window.resizable(False, False)

        # Estilo
        font_title = ("Helvetica", 18, "bold")
        font_button = ("Helvetica", 12, "bold")

        # Frame principal
        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=30, pady=30)
        main_frame.pack(expand=True)

        # Título
        tk.Label(
            main_frame,
            text="Painel de Controle",
            font=font_title,
            fg="#800080",  # Roxo
            bg="#F5F5F5"
        ).pack(pady=30)

        # Botões
        buttons = [
            ("Gerenciar Alimentos", self.open_food),
            ("Gerenciar Categorias", self.open_category),
            ("Gerenciar Cardápios", self.open_menu),
            ("Visualizar Estoque", self.open_stock_viewer),
            ("Relatórios", self.open_report)
        ]

        for text, command in buttons:
            tk.Button(
                main_frame,
                text=text,
                command=command,
                bg="#FFA500",  # Laranja
                fg="#FFFFFF",
                font=font_button,
                activebackground="#800080",  # Roxo ao clicar
                width=20,
                height=2
            ).pack(pady=15)

        self.window.mainloop()

    def open_food(self):
        FoodManagerWindow()

    def open_category(self):
        CategoryManagerWindow()

    def open_menu(self):
        MenuManagerWindow()

    def open_stock_viewer(self):
        StockViewerWindow()

    def open_report(self):
        ReportManagerWindow()