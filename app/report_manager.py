import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

from database import db_functions as db
import csv


class ReportManagerWindow:
    def __init__(self, parent_window):
        self.parent_window = parent_window
        self.window = tk.Toplevel()
        self.window.title("Relatórios")

        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        try:
            self.window.state('zoomed')
        except tk.TclError:
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            self.window.geometry(f'{screen_width}x{screen_height}+0+0')

        self.window.configure(bg="#F5F5F5")
        self.window.resizable(True, True)

        font_title = ("Helvetica", 16, "bold")
        font_label = ("Helvetica", 12)
        font_button = ("Helvetica", 12, "bold")

        main_frame = tk.Frame(self.window, bg="#F5F5F5", padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

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

        tk.Label(
            main_frame,
            text="Relatórios de Estoque",
            font=font_title,
            fg="#800080",
            bg="#F5F5F5"
        ).pack(pady=20)

        history_frame = tk.LabelFrame(
            main_frame,
            text="Histórico de Entradas e Saídas",
            font=font_label,
            fg="#FFA500",
            bg="#F5F5F5",
            padx=10,
            pady=10
        )
        history_frame.pack(fill="both", expand=True, pady=10)

        tree_container = tk.Frame(history_frame)
        tree_container.pack(fill="both", expand=True, pady=10)

        self.history_list = ttk.Treeview(
            tree_container,
            columns=("ID", "Alimento", "Entrada", "Última Saída", "Quantidade", "Validade"),
            show="headings"
        )

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.history_list.yview)
        self.history_list.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.history_list.pack(side="left", fill="both", expand=True)

        columns = ("ID", "Alimento", "Entrada", "Última Saída", "Quantidade", "Validade")
        self.history_list.heading("ID", text="ID")
        self.history_list.heading("Alimento", text="Alimento")
        self.history_list.heading("Entrada", text="Entrada")
        self.history_list.heading("Última Saída", text="Última Saída")
        self.history_list.heading("Quantidade", text="Quantidade")
        self.history_list.heading("Validade", text="Validade")
        self.history_list.column("ID", width=50, anchor="center")
        self.history_list.column("Alimento", width=200, anchor="w")
        self.history_list.column("Entrada", width=100, anchor="center")
        self.history_list.column("Última Saída", width=100, anchor="center")
        self.history_list.column("Quantidade", width=80, anchor="center")
        self.history_list.column("Validade", width=100, anchor="center")

        self.load_history()

        export_button_frame = tk.Frame(main_frame, bg="#F5F5F5", pady=10)

        export_button_frame.pack(fill="x", side="bottom")

        tk.Button(
            export_button_frame,
            text="Exportar para PDF 📄",
            command=self.export_to_pdf,
            bg="#4CAF50",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#A5D6A7",
            width=20
        ).pack(side="left", padx=5)

        tk.Button(
            export_button_frame,
            text="Exportar para CSV 📊",
            command=self.export_to_csv,
            bg="#00BCD4",
            fg="#FFFFFF",
            font=font_button,
            activebackground="#80DEEA",
            width=20
        ).pack(side="left", padx=5)

    def go_back(self):
        """Fecha a janela atual e reexibe a Dashboard (janela pai)."""
        self.window.destroy()
        self.parent_window.deiconify()

    def load_history(self):
        self.all_data_for_export = []

        for i in self.history_list.get_children():
            self.history_list.delete(i)

        try:
            all_foods = db.get_foods()
            food_name_map = {food[0]: food[1] for food in all_foods}
        except Exception as e:
            messagebox.showerror("Erro de DB", f"Não foi possível carregar os nomes dos alimentos: {e}")
            food_name_map = {}

        try:
            history = db.get_stock_history()
        except Exception as e:
            messagebox.showerror("Erro de DB", f"Não foi possível carregar o histórico: {e}")
            return

        headers = ["ID", "Alimento", "Entrada", "Última Saída", "Quantidade", "Validade"]
        self.all_data_for_export.append(headers)

        for item in history:
            alimento_id = item[8]
            nome = food_name_map.get(alimento_id, "Alimento Desconhecido")

            validade_raw = item[4]
            entrada_raw = item[5]
            saida_raw = item[6]

            validade_display = validade_raw if validade_raw else "-"
            entrada_display = entrada_raw if entrada_raw else "-"
            saida_display = saida_raw if saida_raw else "-"

            validade_dt = None

            if validade_raw and validade_raw != '-':
                try:
                    validade_dt = datetime.strptime(validade_raw, '%Y-%m-%d')
                    validade_display = validade_dt.strftime('%d/%m/%Y')
                except ValueError:
                    try:
                        validade_dt = datetime.strptime(validade_raw, '%d/%m/%Y')
                        validade_display = validade_raw
                    except ValueError:
                        print(f"Aviso: Formato de data de validade inesperado: {validade_raw}")
                        validade_display = f"ERRO: {validade_raw}"
            if saida_raw and saida_raw != '-' and '-' in saida_raw:
                try:
                    saida_display = datetime.strptime(saida_raw, '%Y-%m-%d').strftime('%d/%m/%Y')
                except ValueError:
                    saida_display = saida_raw

            tree_values = (item[0], nome, entrada_display, saida_display, item[2], validade_display)
            self.history_list.insert("", "end", values=tree_values)

            export_data = [item[0], nome, entrada_display, saida_display, item[2], validade_display]
            self.all_data_for_export.append(export_data)

            if validade_dt:
                if validade_dt < datetime.now() + timedelta(days=7):
                    self.history_list.item(self.history_list.get_children()[-1], tags=('red',))

        self.history_list.tag_configure('red', foreground='red')

    def export_to_csv(self):
        """Exporta os dados da Treeview para um arquivo CSV."""
        if not self.all_data_for_export or len(self.all_data_for_export) <= 1:
            messagebox.showinfo("Exportar CSV", "Não há dados para exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv")],
            title="Salvar Relatório CSV",
            initialfile=f"Relatorio_Estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if file_path:
            try:
                with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerows(self.all_data_for_export)

                messagebox.showinfo("Sucesso", f"Relatório CSV exportado com sucesso para:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao exportar para CSV: {e}")

    def export_to_pdf(self):
        """Exporta os dados da Treeview para um arquivo PDF usando ReportLab."""
        if not self.all_data_for_export or len(self.all_data_for_export) <= 1:
            messagebox.showinfo("Exportar PDF", "Não há dados para exportar.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("Arquivos PDF", "*.pdf")],
            title="Salvar Relatório PDF",
            initialfile=f"Relatorio_Estoque_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        if file_path:
            try:
                doc = SimpleDocTemplate(file_path, pagesize=letter)
                elements = []

                data = self.all_data_for_export

                table = Table(data)

                style = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ])
                table.setStyle(style)

                elements.append(table)
                doc.build(elements)

                messagebox.showinfo("Sucesso", f"Relatório PDF exportado com sucesso para:\n{file_path}")
            except ImportError:
                messagebox.showerror("Erro de Dependência",
                                     "A biblioteca 'reportlab' não está instalada. Execute:\n'pip install reportlab'")
            except Exception as e:
                messagebox.showerror("Erro de Exportação", f"Ocorreu um erro ao exportar para PDF: {e}")