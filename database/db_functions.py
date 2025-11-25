import sqlite3
from datetime import datetime, timedelta

DB_FILE = 'database/food_stock.db'

def get_menus():
    """Retorna uma lista de todos os cardápios com ID, data e descrição."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Data, Descricao FROM CARDAPIO")
    rows = cursor.fetchall()
    conn.close()
    menus = []
    for row in rows:
        data = datetime.strptime(row['Data'], '%Y-%m-%d').strftime('%d/%m/%Y') if row['Data'] else '-'
        menus.append({
            'ID': row['ID'],
            'Data': data,
            'Descricao': row['Descricao'] or '-'
        })
    return menus

def get_menu_foods(menu_id):
    """Retorna a lista de alimentos associados a um cardápio com suas quantidades."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.ID, a.Nome, ac.Quantidade
        FROM ALIMENTO_CARDAPIO ac
        JOIN ALIMENTO a ON ac.ID_Alimento = a.ID
        WHERE ac.ID_Cardapio = ?
    """, (menu_id,))
    foods = cursor.fetchall()
    conn.close()
    return [{'ID': food['ID'], 'Nome': food['Nome'], 'Quantidade': food['Quantidade']} for food in foods]

def delete_menu(menu_id):
    """Remove um cardápio e suas associações com alimentos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ALIMENTO_CARDAPIO WHERE ID_Cardapio = ?", (menu_id,))
        cursor.execute("DELETE FROM CARDAPIO WHERE ID = ?", (menu_id,))
        if cursor.rowcount == 0:
            conn.close()
            return False
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()


def add_category(nome):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO CATEGORIA (Nome) VALUES (?)", (nome,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_foods():
    """Retorna uma lista de alimentos (ID, Nome)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID, Nome FROM ALIMENTO")
    foods = cursor.fetchall()
    conn.close()
    return [(food['ID'], food['Nome']) for food in foods]

def get_categories():
    """Retorna uma lista de nomes de categorias."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Nome FROM CATEGORIA")
    categories = cursor.fetchall()
    conn.close()
    return [cat['Nome'] for cat in categories]

def get_menu_items_for_stock_out(menu_id):
    """
    Busca os IDs dos alimentos e suas quantidades necessárias para a baixa do cardápio.
    Retorna uma lista de tuplas: [(food_id, quantidade), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_Alimento, Quantidade 
            FROM ALIMENTO_CARDAPIO 
            WHERE ID_Cardapio = ?
        """, (menu_id,))
        items = cursor.fetchall()
        return items
    except Exception as e:
        print(f"Erro ao buscar itens do cardápio para baixa: {e}")
        return []
    finally:
        conn.close()

def add_nutritional_table(nut_data):
    """Adiciona uma tabela nutricional e retorna seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO TABELA_NUTRICIONAL (
            Valor_energetico_kcal, Carboidratos_g, Acucares_totais_g,
            Acucares_adicionados_g, Proteinas_g, Gorduras_totais_g,
            Gorduras_saturadas_g, Gorduras_trans_g, Fibras_alimentares_g,
            Sodio_mg, Calcio_mg
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, nut_data)
    id_nut = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_nut

def add_food(nome, id_nut, categories):
    """Adiciona um alimento e associa categorias, retornando seu ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ALIMENTO (Nome, ID_Tabela_Nutricional) VALUES (?, ?)", (nome, id_nut))
    food_id = cursor.lastrowid
    for cat in categories:
        cursor.execute("INSERT INTO ALIMENTO_CATEGORIA (ID_Alimento, Nome_Categoria) VALUES (?, ?)", (food_id, cat))
    conn.commit()
    conn.close()
    return food_id

def add_stock_unit(food_id, marca, valor, unidade, validade, entrada):
    """Adiciona uma unidade de estoque."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO UNIDADE_DE_CONTAGEM (
            Marca, Valor, Unidade_de_medida, Data_de_validade, Data_de_entrada, ID_Alimento
        ) VALUES (?, ?, ?, ?, ?, ?)
    """, (marca, valor, unidade, validade, entrada, food_id))
    conn.commit()
    conn.close()

def get_food_details(food_id):
    """Retorna detalhes do alimento: alimento, tabela nutricional, categorias e estoque."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ALIMENTO WHERE ID = ?", (food_id,))
    food = cursor.fetchone()
    cursor.execute("SELECT * FROM TABELA_NUTRICIONAL WHERE ID = ?", (food['ID_Tabela_Nutricional'],))
    nut = cursor.fetchone()
    cursor.execute("SELECT Nome_Categoria FROM ALIMENTO_CATEGORIA WHERE ID_Alimento = ?", (food_id,))
    cats = [row['Nome_Categoria'] for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM UNIDADE_DE_CONTAGEM WHERE ID_Alimento = ?", (food_id,))
    stocks = cursor.fetchall()
    conn.close()
    return food, nut, cats, stocks

def update_nutritional(nut_id, nut_data):
    """Atualiza a tabela nutricional."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE TABELA_NUTRICIONAL SET
            Valor_energetico_kcal = ?, Carboidratos_g = ?, Acucares_totais_g = ?,
            Acucares_adicionados_g = ?, Proteinas_g = ?, Gorduras_totais_g = ?,
            Gorduras_saturadas_g = ?, Gorduras_trans_g = ?, Fibras_alimentares_g = ?,
            Sodio_mg = ?, Calcio_mg = ?
        WHERE ID = ?
    """, nut_data + [nut_id])
    conn.commit()
    conn.close()

def update_food(food_id, nome, id_nut, categories):
    """Atualiza o alimento e suas categorias."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE ALIMENTO SET Nome = ?, ID_Tabela_Nutricional = ? WHERE ID = ?", (nome, id_nut, food_id))
    cursor.execute("DELETE FROM ALIMENTO_CATEGORIA WHERE ID_Alimento = ?", (food_id,))
    for cat in categories:
        cursor.execute("INSERT INTO ALIMENTO_CATEGORIA (ID_Alimento, Nome_Categoria) VALUES (?, ?)", (food_id, cat))
    conn.commit()
    conn.close()


def delete_food(food_id):
    """
    Marca unidades de estoque como 'Saiu' e remove o alimento, se não estiver em uso em cardápios.
    As unidades de estoque são preservadas (soft delete) para fins de histórico.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM ALIMENTO_CARDAPIO WHERE ID_Alimento = ?", (food_id,))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False

        today = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("""
                       UPDATE UNIDADE_DE_CONTAGEM
                       SET Saiu          = 1,
                           Data_de_saida = ?
                       WHERE ID_Alimento = ?
                         AND Saiu = 0
                       """, (today, food_id))

        cursor.execute("DELETE FROM ALIMENTO_CATEGORIA WHERE ID_Alimento = ?", (food_id,))

        cursor.execute("SELECT ID_Tabela_Nutricional FROM ALIMENTO WHERE ID = ?", (food_id,))
        nut_id_row = cursor.fetchone()

        if not nut_id_row:
            conn.commit()
            return True

        nut_id = nut_id_row['ID_Tabela_Nutricional']

        cursor.execute("DELETE FROM ALIMENTO WHERE ID = ?", (food_id,))

        if nut_id:
            cursor.execute("DELETE FROM TABELA_NUTRICIONAL WHERE ID = ?", (nut_id,))

        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()

def search_foods(name=None, category=None, near_expiry=False):
    """Busca alimentos por nome, categoria ou validade próxima."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT a.ID, a.Nome
        FROM ALIMENTO a
        LEFT JOIN ALIMENTO_CATEGORIA ac ON a.ID = ac.ID_Alimento
        LEFT JOIN UNIDADE_DE_CONTAGEM uc ON a.ID = uc.ID_Alimento
        WHERE 1=1
    """
    params = []
    if name:
        query += " AND a.Nome LIKE ?"
        params.append(f"%{name}%")
    if category:
        query += " AND ac.Nome_Categoria = ?"
        params.append(category)
    if near_expiry:
        query += " AND uc.Data_de_validade IS NOT NULL AND uc.Data_de_validade < ? AND uc.Saiu = 0"
        params.append((datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'))
    cursor.execute(query, params)
    foods = cursor.fetchall()
    conn.close()
    return [(food['ID'], food['Nome']) for food in foods]

def get_all_stock():
    """Retorna todas as unidades de estoque."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT uc.ID, a.Nome, uc.Marca, uc.Valor, uc.Unidade_de_medida,
               uc.Data_de_validade, uc.Data_de_entrada, uc.Data_de_saida, uc.Saiu, uc.ID_Alimento
        FROM UNIDADE_DE_CONTAGEM uc
        JOIN ALIMENTO a ON uc.ID_Alimento = a.ID
    """)
    stock = cursor.fetchall()
    conn.close()
    return stock

def update_stock_unit(unit_id, marca, valor, unidade, validade):
    """Atualiza uma unidade de estoque."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE UNIDADE_DE_CONTAGEM SET
            Marca = ?, Valor = ?, Unidade_de_medida = ?, Data_de_validade = ?
        WHERE ID = ?
    """, (marca, valor, unidade, validade, unit_id))
    conn.commit()
    conn.close()

def update_category(old_nome, new_nome):
    """
    Atualiza o nome de uma categoria e seu uso na tabela de relacionamento
    (ALIMENTO_CATEGORIA) de forma transacional.

    Args:
        old_nome (str): O nome atual da categoria.
        new_nome (str): O novo nome desejado para a categoria.

    Returns:
        bool: True se a atualização for bem-sucedida, False caso contrário.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM CATEGORIA WHERE Nome = ?", (new_nome,))
        if cursor.fetchone()[0] > 0:
            return False

        cursor.execute("UPDATE CATEGORIA SET Nome = ? WHERE Nome = ?", (new_nome, old_nome))

        cursor.execute("""
            UPDATE ALIMENTO_CATEGORIA 
            SET Nome_Categoria = ? 
            WHERE Nome_Categoria = ?
        """, (new_nome, old_nome))

        if cursor.rowcount == 0 and cursor.rowcount == 0:
             return False

        conn.commit()
        return True

    except Exception as e:
        print(f"Erro ao atualizar categoria de '{old_nome}' para '{new_nome}': {e}")
        conn.rollback()
        return False

    finally:
        conn.close()

def delete_stock_unit(unit_id):
    """
    Marca uma unidade de estoque como 'Saiu' (soft delete) com a data de saída atual.
    Isso preserva o histórico de estoque.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        cursor.execute("""
            UPDATE UNIDADE_DE_CONTAGEM
            SET Saiu = 1, Data_de_saida = ?
            WHERE ID = ?
        """, (today, unit_id))
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_stock_history():
    """Retorna o histórico de entradas e saídas do estoque."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ID, Marca, Valor, Unidade_de_medida, Data_de_validade,
               Data_de_entrada, Data_de_saida, Saiu, ID_Alimento
        FROM UNIDADE_DE_CONTAGEM
    """)
    history = cursor.fetchall()
    conn.close()
    return history

def food_exists(food_id):
    """Verifica se um alimento existe pelo ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ALIMENTO WHERE ID = ?", (food_id,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists


def get_available_stock(food_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
                       SELECT SUM(Valor)
                       FROM UNIDADE_DE_CONTAGEM
                       WHERE ID_Alimento = ?
                         AND Saiu = 0
                       """, (food_id,))

        result = cursor.fetchone()
        return float(result[0]) if result and result[0] is not None else 0.0
    except Exception as e:
        print(f"Erro ao buscar estoque para o ID {food_id}: {e}")
        return 0.0
    finally:
        conn.close()

def get_menu_items_for_stock_out(menu_id):
    """
    Busca os IDs dos alimentos e suas quantidades necessárias para a baixa do cardápio.
    Retorna uma lista de tuplas: [(ID_Alimento, Quantidade), ...]
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_Alimento, Quantidade 
            FROM ALIMENTO_CARDAPIO 
            WHERE ID_Cardapio = ?
        """, (menu_id,))
        items = cursor.fetchall()
        return items
    except Exception as e:
        print(f"Erro ao buscar itens do cardápio para baixa: {e}")
        return []
    finally:
        conn.close()

def update_stock_on_menu(menu_id, food_id, quantity):
    """Atualiza o estoque com base na quantidade usada em um cardápio."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ID, Valor
        FROM UNIDADE_DE_CONTAGEM
        WHERE ID_Alimento = ? AND Saiu = 0
        ORDER BY Data_de_validade ASC
    """, (food_id,))
    units = cursor.fetchall()
    remaining = quantity
    today = datetime.now().strftime('%Y-%m-%d')
    for unit in units:
        if remaining <= 0:
            break
        unit_id, valor = unit['ID'], unit['Valor']
        if valor <= remaining:
            cursor.execute("""
                UPDATE UNIDADE_DE_CONTAGEM
                SET Saiu = 1, Data_de_saida = ?
                WHERE ID = ?
            """, (today, unit_id))
            remaining -= valor
        else:
            cursor.execute("""
                UPDATE UNIDADE_DE_CONTAGEM
                SET Valor = Valor - ?, Data_de_saida = ?
                WHERE ID = ?
            """, (remaining, today, unit_id))
            remaining = 0
    if remaining > 0:
        conn.close()
        return False
    cursor.execute("""
        INSERT OR REPLACE INTO ALIMENTO_CARDAPIO (ID_Alimento, ID_Cardapio, Quantidade)
        VALUES (?, ?, ?)
    """, (food_id, menu_id, quantity))
    conn.commit()
    conn.close()
    return True

def get_menu(menu_id=None):
    """Retorna detalhes de um ou todos os cardápios."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if menu_id:
        cursor.execute("""
            SELECT 
                c.ID,
                c.Data,
                c.Descricao,
                a.ID AS ID_Alimento,
                a.Nome,
                ac.Quantidade
            FROM CARDAPIO c
            LEFT JOIN ALIMENTO_CARDAPIO ac ON c.ID = ac.ID_Cardapio
            LEFT JOIN ALIMENTO a ON ac.ID_Alimento = a.ID
            WHERE c.ID = ?
        """, (menu_id,))
    else:
        cursor.execute("""
            SELECT 
                c.ID,
                c.Data,
                c.Descricao,
                a.ID AS ID_Alimento,
                a.Nome,
                ac.Quantidade
            FROM CARDAPIO c
            LEFT JOIN ALIMENTO_CARDAPIO ac ON c.ID = ac.ID_Cardapio
            LEFT JOIN ALIMENTO a ON ac.ID_Alimento = a.ID
        """)

    rows = cursor.fetchall()
    conn.close()

    menus = {}
    for row in rows:
        mid = row["ID"]
        if mid not in menus:
            menus[mid] = {
                "ID": mid,
                "Data": row["Data"] or "-",
                "Descricao": row["Descricao"] or "-",
                "Alimentos": []
            }

        if row["Nome"]:
            menus[mid]["Alimentos"].append({
                "ID_Alimento": row["ID_Alimento"],
                "Nome": row["Nome"],
                "Quantidade": row["Quantidade"]
            })

    return list(menus.values())


def add_menu(data, descricao, alimentos):
    print("\n--- INÍCIO: add_menu ---")
    print(f"Parâmetros de entrada: data='{data}', descricao='{descricao}', alimentos={alimentos}")

    conn = get_db_connection()
    cursor = conn.cursor()

    data_db = None
    if data:
        if '/' in data:
            try:
                data_db = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d')
                print(f"DEBUG: Data formatada de DD/MM/YYYY para DB: {data_db}")
            except ValueError as ve:
                print(f"ERRO DE DEBUG (Data): Falha ao formatar DD/MM/YYYY. Erro: {ve}")
                data_db = None
        else:
            data_db = data
            print(f"DEBUG: Data recebida no formato DB ou literal: {data_db}")

    try:
        print("DEBUG: Tentando inserir CARDAPIO...")
        cursor.execute("INSERT INTO CARDAPIO (Data, Descricao) VALUES (?, ?)", (data_db, descricao))
        menu_id = cursor.lastrowid
        print(f"DEBUG: Inserido CARDAPIO. ID gerado: {menu_id}")

        if menu_id is None:
            print("ERRO: Falha ao obter ID do CARDAPIO. Rollback.")
            conn.rollback()
            return None

        print("DEBUG: Iniciando loop de checagem de existência dos Alimentos.")
        for food_id, quantidade in alimentos:
            if not food_exists(food_id):
                print(f"ERRO: Alimento ID {food_id} não existe. Rollback.")
                conn.rollback()
                return None
            print(f"DEBUG: Alimento ID {food_id} existe.")

        print("DEBUG: Iniciando inserção em ALIMENTO_CARDAPIO.")
        for food_id, quantidade in alimentos:
            print(
                f"DEBUG: Inserindo ALIMENTO_CARDAPIO: (Alimento: {food_id}, Cardapio: {menu_id}, Quantidade: {quantidade})")
            cursor.execute(
                "INSERT INTO ALIMENTO_CARDAPIO (ID_Alimento, ID_Cardapio, Quantidade) VALUES (?, ?, ?)",
                (food_id, menu_id, quantidade)
            )

        print("DEBUG: Todas as operações realizadas com sucesso. Executando COMMIT.")
        conn.commit()
        print(f"--- FIM: add_menu (SUCESSO) - Retornando ID: {menu_id} ---")
        return menu_id

    except ValueError as ve:
        print(f"ERRO FATAL (ValueError): {ve}. Executando ROLLBACK.")
        conn.rollback()
        return None

    except sqlite3.Error as se:
        print(f"ERRO FATAL (SQLiteError - Chave Estrangeira/SQL): {se}. Executando ROLLBACK.")
        conn.rollback()
        return None

    finally:
        print("DEBUG: Fechando conexão com o DB.")
        conn.close()


def delete_category(nome_categoria):
    """
    Remove uma categoria do banco de dados, SE ela não estiver vinculada a NENHUM alimento
    na tabela ALIMENTO_CATEGORIA.

    Args:
        nome_categoria (str): O nome (chave primária) da categoria a ser removida.

    Returns:
        bool: True se a remoção for bem-sucedida, False caso contrário (incluindo se estiver em uso).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM ALIMENTO_CATEGORIA
                       WHERE Nome_Categoria = ?
                       """, (nome_categoria,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False
        cursor.execute("DELETE FROM CATEGORIA WHERE Nome = ?", (nome_categoria,))

        if cursor.rowcount == 0:
            return False

        conn.commit()
        return True

    except Exception as e:
        print(f"Erro ao deletar categoria '{nome_categoria}': {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def update_menu(menu_id, data, descricao, alimentos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        data_db = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d') if data else None

        cursor.execute("UPDATE CARDAPIO SET Data = ?, Descricao = ? WHERE ID = ?",
                       (data_db, descricao, menu_id))

        cursor.execute("DELETE FROM ALIMENTO_CARDAPIO WHERE ID_Cardapio = ?", (menu_id,))

        for food_id, quantidade in alimentos:
            cursor.execute("""
                INSERT INTO ALIMENTO_CARDAPIO (ID_Cardapio, ID_Alimento, Quantidade)
                VALUES (?, ?, ?)
            """, (menu_id, food_id, quantidade))

        conn.commit()
        return True
    except Exception as e:
        print("Erro update_menu:", e)
        conn.rollback()
        return False
    finally:
        conn.close()


def give_stock_out(menu_id, food_items):
    """
    Executa a transação de baixa de estoque consumindo e marcando as unidades
    em UNIDADE_DE_CONTAGEM. Prioriza unidades com Data_de_validade mais antiga (FEFO).
    Retorna (True, "Sucesso") ou (False, "Mensagem de Erro").
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        for food_id, required_qty in food_items:
            available_qty = get_available_stock(food_id)
            if available_qty < required_qty:
                return False, f"Estoque insuficiente para o Alimento ID {food_id}. Disponível: {available_qty}, Necessário: {required_qty}."

        for food_id, required_qty in food_items:
            cursor.execute("""
                           SELECT ID, Valor
                           FROM UNIDADE_DE_CONTAGEM
                           WHERE ID_Alimento = ?
                             AND Saiu = 0
                           ORDER BY Data_de_validade ASC, Data_de_entrada ASC
                           """, (food_id,))
            available_units = cursor.fetchall()

            remaining_qty = required_qty

            for unit_id, unit_value in available_units:
                if remaining_qty <= 0:
                    break

                if remaining_qty >= unit_value:
                    cursor.execute("""
                                   UPDATE UNIDADE_DE_CONTAGEM
                                   SET Saiu          = 1,
                                       Data_de_saida = ?
                                   WHERE ID = ?
                                   """, (current_date, unit_id))
                    remaining_qty -= unit_value

                else:

                    cursor.execute("""
                                   UPDATE UNIDADE_DE_CONTAGEM
                                   SET Valor         = Valor - ?,
                                       Data_de_saida = ?
                                   WHERE ID = ?
                                   """, (remaining_qty, current_date, unit_id))
                    remaining_qty = 0
                    break
        conn.commit()
        return True, "Baixa de estoque concluída com sucesso."

    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Erro de banco de dados ao executar a baixa: {e}"

    except Exception as e:
        conn.rollback()
        return False, f"Erro inesperado: {e}"

    finally:
        conn.close()


