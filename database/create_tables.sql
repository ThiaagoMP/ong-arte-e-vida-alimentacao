CREATE TABLE IF NOT EXISTS CATEGORIA (
    Nome TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS TABELA_NUTRICIONAL (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Valor_energetico_kcal REAL,
    Carboidratos_g REAL,
    Acucares_totais_g REAL,
    Acucares_adicionados_g REAL,
    Proteinas_g REAL,
    Gorduras_totais_g REAL,
    Gorduras_saturadas_g REAL,
    Gorduras_trans_g REAL,
    Fibras_alimentares_g REAL,
    Sodio_mg REAL,
    Calcio_mg REAL
);

CREATE TABLE IF NOT EXISTS ALIMENTO (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome TEXT NOT NULL,
    ID_Tabela_Nutricional INTEGER,
    FOREIGN KEY (ID_Tabela_Nutricional) REFERENCES TABELA_NUTRICIONAL(ID)
);

CREATE TABLE IF NOT EXISTS ALIMENTO_CATEGORIA (
    ID_Alimento INTEGER,
    Nome_Categoria TEXT,
    PRIMARY KEY (ID_Alimento, Nome_Categoria),
    FOREIGN KEY (ID_Alimento) REFERENCES ALIMENTO(ID),
    FOREIGN KEY (Nome_Categoria) REFERENCES CATEGORIA(Nome)
);

CREATE TABLE IF NOT EXISTS CARDAPIO (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Data TEXT,  -- YYYY-MM-DD, optional
    Descricao TEXT
);

CREATE TABLE IF NOT EXISTS ALIMENTO_CARDAPIO (
    ID_Alimento INTEGER,
    ID_Cardapio INTEGER,
    Quantidade REAL,
    PRIMARY KEY (ID_Alimento, ID_Cardapio),
    FOREIGN KEY (ID_Alimento) REFERENCES ALIMENTO(ID),
    FOREIGN KEY (ID_Cardapio) REFERENCES CARDAPIO(ID)
);

CREATE TABLE IF NOT EXISTS UNIDADE_DE_CONTAGEM (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Marca TEXT,
    Valor INTEGER NOT NULL,
    Unidade_de_medida TEXT(5),
    Data_de_validade TEXT NOT NULL,  -- YYYY-MM-DD
    Data_de_entrada TEXT NOT NULL,   -- DD/MM/YYYY
    Data_de_saida TEXT,              -- YYYY-MM-DD, optional
    Saiu INTEGER DEFAULT 0,          -- BOOLEAN as 0/1
    ID_Alimento INTEGER NOT NULL,
    FOREIGN KEY (ID_Alimento) REFERENCES ALIMENTO(ID)
);