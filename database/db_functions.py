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
        # Converter data para DD/MM/YYYY, se existir
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
        # Remover associações em ALIMENTO_CARDAPIO
        cursor.execute("DELETE FROM ALIMENTO_CARDAPIO WHERE ID_Cardapio = ?", (menu_id,))
        # Remover o cardápio
        cursor.execute("DELETE FROM CARDAPIO WHERE ID = ?", (menu_id,))
        # Verificar se o cardápio existia
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
        # Categoria já existe (violação de chave primária)
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
    """Remove um alimento, se não estiver em uso em cardápios."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ALIMENTO_CARDAPIO WHERE ID_Alimento = ?", (food_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        return False
    cursor.execute("DELETE FROM ALIMENTO_CATEGORIA WHERE ID_Alimento = ?", (food_id,))
    cursor.execute("DELETE FROM UNIDADE_DE_CONTAGEM WHERE ID_Alimento = ?", (food_id,))
    cursor.execute("SELECT ID_Tabela_Nutricional FROM ALIMENTO WHERE ID = ?", (food_id,))
    nut_id = cursor.fetchone()['ID_Tabela_Nutricional']
    cursor.execute("DELETE FROM ALIMENTO WHERE ID = ?", (food_id,))
    cursor.execute("DELETE FROM TABELA_NUTRICIONAL WHERE ID = ?", (nut_id,))
    conn.commit()
    conn.close()
    return True

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

def delete_stock_unit(unit_id):
    """Remove uma unidade de estoque."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM UNIDADE_DE_CONTAGEM WHERE ID = ?", (unit_id,))
    conn.commit()
    conn.close()
    return True

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
    """Retorna a soma do estoque disponível (Saiu = 0) para um alimento."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(Valor) as total
        FROM UNIDADE_DE_CONTAGEM
        WHERE ID_Alimento = ? AND Saiu = 0
    """, (food_id,))
    total = cursor.fetchone()['total'] or 0
    conn.close()
    return total

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
        return False  # Estoque insuficiente
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
            SELECT c.ID, c.Data, c.Descricao, a.Nome, ac.Quantidade
            FROM CARDAPIO c
            LEFT JOIN ALIMENTO_CARDAPIO ac ON c.ID = ac.ID_Cardapio
            LEFT JOIN ALIMENTO a ON ac.ID_Alimento = a.ID
            WHERE c.ID = ?
        """, (menu_id,))
    else:
        cursor.execute("""
            SELECT c.ID, c.Data, c.Descricao, a.Nome, ac.Quantidade
            FROM CARDAPIO c
            LEFT JOIN ALIMENTO_CARDAPIO ac ON c.ID = ac.ID_Cardapio
            LEFT JOIN ALIMENTO a ON ac.ID_Alimento = a.ID
        """)
    rows = cursor.fetchall()
    conn.close()
    # Organiza os dados em um formato mais útil
    menus = {}
    for row in rows:
        menu_id = row['ID']
        if menu_id not in menus:
            menus[menu_id] = {
                'ID': menu_id,
                'Data': row['Data'] or '-',
                'Descricao': row['Descricao'] or '-',
                'Alimentos': []
            }
        if row['Nome']:
            menus[menu_id]['Alimentos'].append({
                'Nome': row['Nome'],
                'Quantidade': row['Quantidade']
            })
    return list(menus.values())

def add_menu(data, descricao, alimentos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Converter data para YYYY-MM-DD, se fornecida
        data_db = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d') if data else None
        # Inserir cardápio
        cursor.execute("INSERT INTO CARDAPIO (Data, Descricao) VALUES (?, ?)", (data_db, descricao))
        menu_id = cursor.lastrowid
        # Verificar alimentos e estoque
        for food_id, quantidade in alimentos:
            if not food_exists(food_id):
                conn.rollback()
                return None
            if get_available_stock(food_id) < quantidade:
                conn.rollback()
                return None
            # Atualizar estoque
            if not update_stock_on_menu(menu_id, food_id, quantidade):
                conn.rollback()
                return None
        conn.commit()
        return menu_id
    except (sqlite3.Error, ValueError):
        conn.rollback()
        return None
    finally:
        conn.close()


def update_menu(menu_id, data, descricao, alimentos):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Converter data para YYYY-MM-DD, se fornecida
        data_db = datetime.strptime(data, '%d/%m/%Y').strftime('%Y-%m-%d') if data else None
        # Atualizar cardápio
        cursor.execute("UPDATE CARDAPIO SET Data = ?, Descricao = ? WHERE ID = ?", (data_db, descricao, menu_id))
        # Remover associações antigas de alimentos
        cursor.execute("DELETE FROM ALIMENTO_CARDAPIO WHERE ID_Cardapio = ?", (menu_id,))
        # Verificar alimentos e estoque
        for food_id, quantidade in alimentos:
            if not food_exists(food_id):
                conn.rollback()
                return False
            if get_available_stock(food_id) < quantidade:
                conn.rollback()
                return False
            # Atualizar estoque
            if not update_stock_on_menu(menu_id, food_id, quantidade):
                conn.rollback()
                return False
        conn.commit()
        return True
    except (sqlite3.Error, ValueError):
        conn.rollback()
        return False
    finally:
        conn.close()