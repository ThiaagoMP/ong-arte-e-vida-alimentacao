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

        try:
            self.window.state('zoomed')
        except tk.TclError:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f'{screen_width}x{screen_height}+0+0')

        self.window.resizable(True, True)
        self.window.configure(bg="#F5F5F5")

        self.window.protocol("WM_DELETE_WINDOW", self.close_app)

        font_title = ("Helvetica", 18, "bold")
        font_button = ("Helvetica", 12, "bold")

        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=30, pady=30)
        main_frame.pack(expand=True)

        tk.Label(
            main_frame,
            text="Painel de Controle",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=30)

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
                bg="#FFA500",
                fg="#FFFFFF",
                font=font_button,
                activebackground="#800080",
                width=20,
                height=2
            ).pack(pady=15)

        self.window.mainloop()

    def close_app(self):
        """Fecha a janela e encerra o loop principal do Tkinter, finalizando o processo."""
        self.window.destroy()
        self.window.quit()

    def open_food(self):
        FoodManagerWindow(self.window)

    def open_category(self):
        CategoryManagerWindow(self.window)

    def open_menu(self):
        MenuManagerWindow(self.window)

    def open_stock_viewer(self):
        StockViewerWindow(self.window)

    def open_report(self):
        ReportManagerWindow(self.window)


if __name__ == '__main__':
    DashboardWindow()