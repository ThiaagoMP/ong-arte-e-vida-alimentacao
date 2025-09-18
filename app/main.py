import tkinter as tk
import sqlite3
import os
from app.login import LoginWindow

# Definir caminhos absolutos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, '..', 'database', 'food_stock.db')
CREATE_TABLES_FILE = os.path.join(BASE_DIR, '..', 'database', 'create_tables.sql')


def init_db():
    # Criar diretório database/ se não existir
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Execute SQL commands from create_tables.sql
    try:
        with open(CREATE_TABLES_FILE, 'r') as sql_file:
            sql_script = sql_file.read()
        cursor.executescript(sql_script)
        conn.commit()
    except FileNotFoundError:
        print(f"Erro: Arquivo {CREATE_TABLES_FILE} não encontrado.")
        raise
    except sqlite3.Error as e:
        print(f"Erro ao executar o script SQL: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    root.withdraw()  # Hide root window
    login = LoginWindow()
    root.mainloop()