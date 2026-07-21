import sqlite3
import os
from datetime import datetime, timedelta
from caminhos import obter_pasta_base

DATABASE_NAME = os.path.join(obter_pasta_base(), "autoeletrica.db")

def conectar():

    conn = sqlite3.connect(DATABASE_NAME)

    conn.execute("PRAGMA foreign_keys = ON")

    return conn

def criar_tabelas():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            modelo TEXT NOT NULL,
            placa TEXT NOT NULL,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_de_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            cliente_id INTEGER NOT NULL,

            veiculo_id INTEGER NOT NULL,

            descricao TEXT,

            mao_obra REAL NOT NULL,

            status TEXT NOT NULL,

            data_abertura TEXT,

            data_entrega TEXT,

            FOREIGN KEY(cliente_id)
                REFERENCES clientes(id),

            FOREIGN KEY(veiculo_id)
                REFERENCES veiculos(id)

        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_custo REAL NOT NULL,
            valor_venda REAL NOT NULL,
            estoque_minimo INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ordens_de_servico_pecas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_id INTEGER NOT NULL,
            peca_id INTEGER NOT NULL,
            nome_peca_momento TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            valor_custo_momento REAL NOT NULL,
            valor_venda_momento REAL NOT NULL,

            FOREIGN KEY (ordem_id)
                REFERENCES ordens_de_servico(id),

            FOREIGN KEY (peca_id)
                REFERENCES estoque(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria TEXT NOT NULL,
            descricao TEXT,
            valor REAL NOT NULL,
            forma_pagamento TEXT,
            data TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pagamentos_fiado (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ordem_id INTEGER NOT NULL,
            valor REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY(ordem_id)
                REFERENCES ordens_de_servico(id)
        )
    """)


    conn.commit()
    conn.close()

def inserir_cliente(nome, telefone):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes
        (nome, telefone)
        VALUES (?, ?)
    """, (nome, telefone))

    conn.commit()
    conn.close()

def listar_clientes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, telefone
        FROM clientes
        ORDER BY nome
    """)

    clientes = cursor.fetchall()

    conn.close()

    return clientes

def buscar_clientes(texto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, telefone
        FROM clientes
        WHERE nome LIKE ?
        ORDER BY nome
    """, (f"%{texto}%",))

    clientes = cursor.fetchall()

    conn.close()
    return clientes


def buscar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, telefone
        FROM clientes
        WHERE id = ?
    """, (id_cliente,))

    cliente = cursor.fetchone()

    conn.close()
    return cliente


def atualizar_cliente(id_cliente, nome, telefone):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes
        SET nome = ?, telefone = ?
        WHERE id = ?
    """, (nome, telefone, id_cliente))

    conn.commit()
    conn.close()


def apagar_cliente(id_cliente):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM clientes
            WHERE id = ?
        """, (id_cliente,))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()



def inserir_veiculo(cliente_id, modelo, placa):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO veiculos
        (cliente_id, modelo, placa)
        VALUES (?, ?, ?)
    """, (cliente_id, modelo, placa))

    conn.commit()
    conn.close()

def listar_veiculos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            veiculos.id,
            clientes.nome,
            veiculos.modelo,
            veiculos.placa
        FROM veiculos
        INNER JOIN clientes
            ON veiculos.cliente_id = clientes.id
        ORDER BY clientes.nome
    """)

    veiculos = cursor.fetchall()

    conn.close()

    return veiculos

def buscar_veiculos(texto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            veiculos.id,
            clientes.nome,
            veiculos.modelo,
            veiculos.placa
        FROM veiculos
        JOIN clientes
            ON clientes.id = veiculos.cliente_id
        WHERE veiculos.modelo LIKE ?
        OR veiculos.placa LIKE ?
        OR clientes.nome LIKE ?
        ORDER BY veiculos.id DESC
    """, (
        f"%{texto}%",
        f"%{texto}%",
        f"%{texto}%"
    ))

    veiculos = cursor.fetchall()

    conn.close()
    return veiculos


def buscar_veiculo(id_veiculo):
    """
    Diferente de listar_veiculos(), essa retorna cliente_id puro
    (não o nome), porque é usada pra pré-selecionar o combobox
    na tela de edição.
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cliente_id, modelo, placa
        FROM veiculos
        WHERE id = ?
    """, (id_veiculo,))

    veiculo = cursor.fetchone()

    conn.close()
    return veiculo


def atualizar_veiculo(id_veiculo, cliente_id, modelo, placa):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE veiculos
        SET cliente_id = ?, modelo = ?, placa = ?
        WHERE id = ?
    """, (cliente_id, modelo, placa, id_veiculo))

    conn.commit()
    conn.close()


def apagar_veiculo(id_veiculo):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM veiculos
            WHERE id = ?
        """, (id_veiculo,))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()



def listar_veiculos_por_cliente(cliente_id):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, cliente_id, modelo, placa
        FROM veiculos
        WHERE cliente_id = ?
    """, (cliente_id,))

    veiculos = cursor.fetchall()

    conn.close()

    return veiculos

def inserir_ordens_de_servico(
    cliente_id,
    veiculo_id,
    descricao,
    mao_obra,
    status,
    forma_pagamento=None,
    status_pagamento=None
):

    conn = conectar()
    cursor = conn.cursor()

    data_abertura = datetime.now().strftime("%d/%m/%Y %H:%M")

    mao_obra = float(str(mao_obra).replace(",", "."))

    cursor.execute("""
    INSERT INTO ordens_de_servico
    (
        cliente_id,
        veiculo_id,
        descricao,
        mao_obra,
        status,
        forma_pagamento,
        status_pagamento,
        data_abertura
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cliente_id,
        veiculo_id,
        descricao,
        mao_obra,
        status,
        forma_pagamento,
        status_pagamento,
        data_abertura
    ))

    id_ordem = cursor.lastrowid

    conn.commit()
    conn.close()

    return id_ordem

def listar_ordens_de_servico():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        ordens_de_servico.id,
        clientes.nome,
        veiculos.modelo,
        ordens_de_servico.descricao,
        ordens_de_servico.mao_obra,
        ordens_de_servico.status

    FROM ordens_de_servico

    JOIN clientes
        ON clientes.id = ordens_de_servico.cliente_id

    JOIN veiculos
        ON veiculos.id = ordens_de_servico.veiculo_id

    WHERE ordens_de_servico.status != 'Entregue'

    ORDER BY ordens_de_servico.id DESC
    """)

    os = cursor.fetchall()

    conn.close()

    return os

def atualizar_status_ordens_de_servico(
    id_ordem,
    novo_status,
    forma_pagamento,
    status_pagamento
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        status,
        status_pagamento,
        data_entrega,
        data_pagamento
    FROM ordens_de_servico
    WHERE id = ?
    """, (id_ordem,))

    status_atual, status_pagamento_atual, data_entrega, data_pagamento = cursor.fetchone()

    if (
        status_atual != "Entregue"
        and novo_status == "Entregue"
    ):
        data_entrega = datetime.now().strftime("%d/%m/%Y %H:%M")
        processar_entrega_ordem(id_ordem)

    if (
        status_pagamento_atual != "Pago"
        and status_pagamento == "Pago"
    ):
        data_pagamento = datetime.now().strftime("%d/%m/%Y %H:%M")

    cursor.execute("""
    UPDATE ordens_de_servico
    SET
        status = ?,
        forma_pagamento = ?,
        status_pagamento = ?,
        data_entrega = ?,
        data_pagamento = ?
    WHERE id = ?
    """, (
        novo_status,
        forma_pagamento,
        status_pagamento,
        data_entrega,
        data_pagamento,
        id_ordem
    ))

    conn.commit()
    conn.close()

def listar_ordens_entregues():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        ordens_de_servico.id,
        clientes.nome,
        veiculos.modelo,
        ordens_de_servico.descricao,
        ordens_de_servico.mao_obra,
        ordens_de_servico.status

    FROM ordens_de_servico

    JOIN clientes
        ON clientes.id = ordens_de_servico.cliente_id

    JOIN veiculos
        ON veiculos.id = ordens_de_servico.veiculo_id

    WHERE ordens_de_servico.status = 'Entregue'

    ORDER BY ordens_de_servico.id DESC
    """)

    os = cursor.fetchall()

    conn.close()

    return os

def buscar_ordens_entregues(texto):
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
    SELECT
        ordens_de_servico.id,
        clientes.nome,
        veiculos.modelo,
        ordens_de_servico.descricao,
        ordens_de_servico.mao_obra,
        ordens_de_servico.status
 
    FROM ordens_de_servico
 
    JOIN clientes
        ON clientes.id = ordens_de_servico.cliente_id
 
    JOIN veiculos
        ON veiculos.id = ordens_de_servico.veiculo_id
 
    WHERE ordens_de_servico.status = 'Entregue'
    AND (
        clientes.nome LIKE ?
        OR veiculos.modelo LIKE ?
        OR veiculos.placa LIKE ?
        OR CAST(ordens_de_servico.id AS TEXT) LIKE ?
    )
 
    ORDER BY ordens_de_servico.id DESC
    """, (
        f"%{texto}%",
        f"%{texto}%",
        f"%{texto}%",
        f"%{texto}%"
    ))
 
    ordens = cursor.fetchall()
 
    conn.close()
    return ordens

def processar_entrega_ordem(
    id_ordem
):

    pecas = listar_pecas_baixa_estoque(
        id_ordem
    )

    for peca_id, quantidade in pecas:

        baixar_estoque(
            peca_id,
            quantidade
        )

def obter_ordem_por_id(id_ordem):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        ordens_de_servico.id,
        clientes.nome,
        veiculos.modelo,
        ordens_de_servico.descricao,
        ordens_de_servico.mao_obra,
        ordens_de_servico.status,
        ordens_de_servico.forma_pagamento,
        ordens_de_servico.status_pagamento,
        ordens_de_servico.data_abertura,
        ordens_de_servico.data_entrega,
        ordens_de_servico.data_pagamento
    FROM ordens_de_servico

    JOIN clientes
        ON clientes.id =
        ordens_de_servico.cliente_id

    JOIN veiculos
        ON veiculos.id =
        ordens_de_servico.veiculo_id

    WHERE ordens_de_servico.id = ?
    """, (
        id_ordem,
    ))

    os = cursor.fetchone()

    conn.close()

    return os

def atualizar_ordem_servico(id_ordem, descricao, mao_obra):
    conn = conectar()
    cursor = conn.cursor()
 
    try:
        mao_obra = float(str(mao_obra).replace(",", "."))
    except (ValueError, TypeError):
        mao_obra = 0.0
 
    cursor.execute("""
        UPDATE ordens_de_servico
        SET descricao = ?, mao_obra = ?
        WHERE id = ?
    """, (descricao, mao_obra, id_ordem))
 
    conn.commit()
    conn.close()
 
 
def listar_pecas_ordem_editavel(ordem_id):
    """
    Diferente de listar_pecas_ordem(), essa também traz o id
    da linha em ordens_de_servico_pecas e o peca_id - necessário
    pra poder remover uma peça específica ou checar estoque
    considerando o que já está nessa OS.
    """
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT id, peca_id, nome_peca_momento, quantidade, valor_venda_momento
        FROM ordens_de_servico_pecas
        WHERE ordem_id = ?
    """, (ordem_id,))
 
    pecas = cursor.fetchall()
 
    conn.close()
    return pecas
 
 
def remover_peca_da_ordem(id_relacao):
    """
    id_relacao é o id da linha em ordens_de_servico_pecas
    (não o id da peça no estoque). Como o estoque só é debitado
    na entrega, remover aqui não precisa devolver nada ao estoque.
    """
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
        DELETE FROM ordens_de_servico_pecas
        WHERE id = ?
    """, (id_relacao,))
 
    conn.commit()
    conn.close()
 


def contar_clientes():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM clientes
    """)

    quantidade = cursor.fetchone()[0]

    conn.close()

    return quantidade

def contar_veiculos():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM veiculos
    """)

    quantidade = cursor.fetchone()[0]

    conn.close()

    return quantidade

def contar_ordens_de_servico():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM ordens_de_servico
    WHERE status != 'Entregue'
    """)

    quantidade = cursor.fetchone()[0]

    conn.close()

    return quantidade

def contar_os_por_status(status):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM ordens_de_servico
        WHERE status = ?
    """, (status,))

    quantidade = cursor.fetchone()[0]

    conn.close()
    return quantidade


def contar_entregues_hoje():
    conn = conectar()
    cursor = conn.cursor()

    hoje = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        SELECT COUNT(*)
        FROM ordens_de_servico
        WHERE status = 'Entregue'
        AND data_entrega LIKE ?
    """, (f"{hoje}%",))

    quantidade = cursor.fetchone()[0]

    conn.close()
    return quantidade

def listar_estoque_baixo():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, nome, quantidade, estoque_minimo
        FROM estoque
        WHERE quantidade <= estoque_minimo
        ORDER BY quantidade ASC
    """)

    itens = cursor.fetchall()

    conn.close()
    return itens

def listar_ultimas_ordens(limite=5):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ordens_de_servico.id,
            clientes.nome,
            veiculos.modelo,
            ordens_de_servico.status,
            ordens_de_servico.mao_obra,
            ordens_de_servico.data_abertura
        FROM ordens_de_servico
        JOIN clientes
            ON clientes.id = ordens_de_servico.cliente_id
        JOIN veiculos
            ON veiculos.id = ordens_de_servico.veiculo_id
        ORDER BY ordens_de_servico.id DESC
        LIMIT ?
    """, (limite,))

    ordens = cursor.fetchall()
    resultado = []

    for id_ordem, nome_cliente, modelo, status, mao_obra, data_abertura in ordens:
        cursor.execute("""
            SELECT COALESCE(SUM(valor_venda_momento * quantidade), 0)
            FROM ordens_de_servico_pecas
            WHERE ordem_id = ?
        """, (id_ordem,))

        valor_pecas = cursor.fetchone()[0]

        total = 0.0
        try:
            total += float(str(mao_obra).replace(",", "."))
        except (ValueError, TypeError):
            pass
        total += valor_pecas

        resultado.append((
            id_ordem,
            nome_cliente,
            modelo,
            status,
            data_abertura,
            total
        ))

    conn.close()
    return resultado

def inserir_estoque(
    nome,
    quantidade,
    valor_custo,
    valor_venda,
    estoque_minimo
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO estoque
        (
            nome,
            quantidade,
            valor_custo,
            valor_venda,
            estoque_minimo
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        nome,
        quantidade,
        valor_custo,
        valor_venda,
        estoque_minimo
    ))

    conn.commit()
    conn.close()

def listar_estoque():

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            quantidade,
            valor_custo,
            valor_venda,
            estoque_minimo
        FROM estoque
    """)

    estoque = cursor.fetchall()

    conn.close()

    return estoque

def buscar_peca(id_peca):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            quantidade,
            valor_custo,
            valor_venda,
            estoque_minimo
        FROM estoque
        WHERE id = ?
    """, (id_peca,))

    peca = cursor.fetchone()

    conn.close()

    return peca

def buscar_pecas(texto):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            quantidade,
            valor_custo,
             valor_venda,
            estoque_minimo
        FROM estoque
        WHERE nome LIKE ?
    """, (f"%{texto}%",))

    peca = cursor.fetchall()

    conn.close()

    return peca

def atualizar_quantidade_estoque(id_peca, nova_quantidade):

    conn = conectar()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE estoque
        SET quantidade = ?
        WHERE id = ?
    """, (
        nova_quantidade,
        id_peca
    ))

    conn.commit()

    conn.close()

def apagar_peca_estoque(id_peca):

    conn = conectar()

    cursor = conn.cursor()

    try:

        cursor.execute("""
            DELETE FROM estoque
            WHERE id = ?
        """, (id_peca,))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


def inserir_ordem_peca(
    ordem_id,
    peca_id,
    nome_peca,
    quantidade,
    valor_custo,
    valor_venda
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO ordens_de_servico_pecas
    (
        ordem_id,
        peca_id,
        nome_peca_momento,
        quantidade,
        valor_custo_momento,
        valor_venda_momento
    )
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ordem_id,
        peca_id,
        nome_peca,
        quantidade,
        valor_custo,
        valor_venda
    ))

    conn.commit()

    conn.close()

def listar_pecas_ordem(
    ordem_id
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        nome_peca_momento,
        quantidade,
        valor_venda_momento
    FROM ordens_de_servico_pecas
    WHERE ordem_id = ?
    """, (
        ordem_id,
    ))

    pecas = cursor.fetchall()

    conn.close()

    return pecas

def baixar_estoque(
    peca_id,
    quantidade
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE estoque
        SET quantidade = quantidade - ?
        WHERE id = ?
    """, (
        quantidade,
        peca_id
    ))

    conn.commit()
    conn.close()

def listar_pecas_baixa_estoque(
    ordem_id
):

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        peca_id,
        quantidade
    FROM ordens_de_servico_pecas
    WHERE ordem_id = ?
    """, (
        ordem_id,
    ))

    pecas = cursor.fetchall()

    conn.close()

    return pecas

def migrar_colunas_ordens_de_servico():
    """
    Seu banco de teste já existe e pode não ter as colunas
    forma_pagamento, status_pagamento e data_pagamento.
    Esta função adiciona só o que estiver faltando, sem apagar nada.
    Chame ela uma vez ao iniciar o sistema (ex: junto de criar_tabelas()).
    Quando o banco for criado do zero (entrega limpa), essas colunas já
    vêm no CREATE TABLE original e essa função não faz nada.
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(ordens_de_servico)")
    colunas_existentes = [linha[1] for linha in cursor.fetchall()]

    colunas_necessarias = {
        "forma_pagamento": "TEXT",
        "status_pagamento": "TEXT",
        "data_pagamento": "TEXT",
    }

    for coluna, tipo in colunas_necessarias.items():
        if coluna not in colunas_existentes:
            cursor.execute(f"""
                ALTER TABLE ordens_de_servico ADD COLUMN {coluna} {tipo}
            """)

    conn.commit()
    conn.close()

def migrar_colunas_pagamentos_fiado():
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("PRAGMA table_info(pagamentos_fiado)")
    colunas_existentes = [linha[1] for linha in cursor.fetchall()]
 
    if "forma_pagamento" not in colunas_existentes:
        cursor.execute("""
            ALTER TABLE pagamentos_fiado ADD COLUMN forma_pagamento TEXT
        """)
 
    conn.commit()
    conn.close()

# ------------------------------------------------------------
# DESPESAS
# ------------------------------------------------------------

def inserir_despesa(categoria, descricao, valor, forma_pagamento, data=None):
    """
    categoria: texto fixo escolhido no combobox (ex: "Fornecedor", "Aluguel"...)
    descricao: texto livre complementar
    data: se None, usa a data de hoje. Formato "%d/%m/%Y" (mesmo padrão do resto do sistema)
    """
    conn = conectar()
    cursor = conn.cursor()

    if data is None:
        data = datetime.now().strftime("%d/%m/%Y")

    cursor.execute("""
        INSERT INTO despesas
        (categoria, descricao, valor, forma_pagamento, data)
        VALUES (?, ?, ?, ?, ?)
    """, (categoria, descricao, valor, forma_pagamento, data))

    conn.commit()
    conn.close()


def listar_despesas(data_inicio=None, data_fim=None):
    """
    Retorna todas as despesas. Se data_inicio/data_fim forem passadas
    (objetos date ou datetime), filtra pelo período.
    O filtro é feito em Python porque a data é salva como texto
    dd/mm/aaaa (não ordena certo direto no SQL).
    """
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, categoria, descricao, valor, forma_pagamento, data
        FROM despesas
        ORDER BY id DESC
    """)

    despesas = cursor.fetchall()
    conn.close()

    if data_inicio is None and data_fim is None:
        return despesas

    despesas_filtradas = []
    for despesa in despesas:
        data_despesa = datetime.strptime(despesa[5], "%d/%m/%Y").date()

        if data_inicio and data_despesa < data_inicio:
            continue
        if data_fim and data_despesa > data_fim:
            continue

        despesas_filtradas.append(despesa)

    return despesas_filtradas

def inserir_pagamento_fiado(ordem_id, valor, forma_pagamento, data=None):
    conn = conectar()
    cursor = conn.cursor()
 
    if data is None:
        data = datetime.now().strftime("%d/%m/%Y")
 
    cursor.execute("""
        INSERT INTO pagamentos_fiado (ordem_id, valor, forma_pagamento, data)
        VALUES (?, ?, ?, ?)
    """, (ordem_id, valor, forma_pagamento, data))
 
    conn.commit()
    conn.close()
 
def listar_pagamentos_fiado(ordem_id):
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT id, valor, forma_pagamento, data
        FROM pagamentos_fiado
        WHERE ordem_id = ?
        ORDER BY id ASC
    """, (ordem_id,))
 
    pagamentos = cursor.fetchall()
 
    conn.close()
    return pagamentos

def calcular_valor_pago_fiado(ordem_id):
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT COALESCE(SUM(valor), 0)
        FROM pagamentos_fiado
        WHERE ordem_id = ?
    """, (ordem_id,))
 
    total = cursor.fetchone()[0]
 
    conn.close()
    return total
 
def registrar_pagamento_fiado(ordem_id, valor_pagamento, forma_pagamento, data=None):
    inserir_pagamento_fiado(ordem_id, valor_pagamento, forma_pagamento, data)
 
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT status, mao_obra
        FROM ordens_de_servico
        WHERE id = ?
    """, (ordem_id,))
 
    status_atual, mao_obra = cursor.fetchone()
 
    cursor.execute("""
        SELECT COALESCE(SUM(valor_venda_momento * quantidade), 0)
        FROM ordens_de_servico_pecas
        WHERE ordem_id = ?
    """, (ordem_id,))
 
    valor_pecas = cursor.fetchone()[0]
 
    conn.close()
 
    try:
        valor_total = float(str(mao_obra).replace(",", ".")) + valor_pecas
    except (ValueError, TypeError):
        valor_total = valor_pecas
 
    valor_pago = calcular_valor_pago_fiado(ordem_id)
 
    if valor_pago >= valor_total - 0.01:
        atualizar_status_ordens_de_servico(
            ordem_id,
            status_atual,
            forma_pagamento,
            "Pago"
        )
        return True
 
    return False

def calcular_receita(data_inicio, data_fim):
    conn = conectar()
    cursor = conn.cursor()
 
    total = 0.0
 
    cursor.execute("""
        SELECT
            ordens_de_servico.id,
            ordens_de_servico.mao_obra,
            ordens_de_servico.data_pagamento
        FROM ordens_de_servico
        WHERE ordens_de_servico.status_pagamento = 'Pago'
        AND ordens_de_servico.data_pagamento IS NOT NULL
        AND ordens_de_servico.id NOT IN (
            SELECT DISTINCT ordem_id FROM pagamentos_fiado
        )
    """)
 
    for id_ordem, mao_obra, data_pagamento in cursor.fetchall():
        data_pag = datetime.strptime(
            data_pagamento, "%d/%m/%Y %H:%M"
        ).date()
 
        if data_pag < data_inicio or data_pag > data_fim:
            continue
 
        try:
            total += float(str(mao_obra).replace(",", "."))
        except (ValueError, TypeError):
            pass
 
        cursor.execute("""
            SELECT COALESCE(SUM(valor_venda_momento * quantidade), 0)
            FROM ordens_de_servico_pecas
            WHERE ordem_id = ?
        """, (id_ordem,))
 
        total += cursor.fetchone()[0]
 
    cursor.execute("""
        SELECT valor, data
        FROM pagamentos_fiado
    """)
 
    for valor, data in cursor.fetchall():
        data_pag = datetime.strptime(data, "%d/%m/%Y").date()
 
        if data_pag < data_inicio or data_pag > data_fim:
            continue
 
        total += valor
 
    conn.close()
    return total

def resumo_formas_pagamento(data_inicio, data_fim):
    conn = conectar()
    cursor = conn.cursor()
 
    resumo = {}
 
    cursor.execute("""
        SELECT
            ordens_de_servico.id,
            ordens_de_servico.mao_obra,
            ordens_de_servico.forma_pagamento,
            ordens_de_servico.data_pagamento
        FROM ordens_de_servico
        WHERE ordens_de_servico.status_pagamento = 'Pago'
        AND ordens_de_servico.data_pagamento IS NOT NULL
        AND ordens_de_servico.id NOT IN (
            SELECT DISTINCT ordem_id FROM pagamentos_fiado
        )
    """)
 
    for id_ordem, mao_obra, forma_pagamento, data_pagamento in cursor.fetchall():
        data_pag = datetime.strptime(
            data_pagamento, "%d/%m/%Y %H:%M"
        ).date()
 
        if data_pag < data_inicio or data_pag > data_fim:
            continue
 
        cursor.execute("""
            SELECT COALESCE(SUM(valor_venda_momento * quantidade), 0)
            FROM ordens_de_servico_pecas
            WHERE ordem_id = ?
        """, (id_ordem,))
 
        valor_pecas = cursor.fetchone()[0]
 
        total = 0.0
        try:
            total += float(str(mao_obra).replace(",", "."))
        except (ValueError, TypeError):
            pass
        total += valor_pecas
 
        forma = forma_pagamento or "Não informado"
        resumo[forma] = resumo.get(forma, 0.0) + total
 
    cursor.execute("""
        SELECT valor, forma_pagamento, data
        FROM pagamentos_fiado
    """)
 
    for valor, forma_pagamento, data in cursor.fetchall():
        data_pag = datetime.strptime(data, "%d/%m/%Y").date()
 
        if data_pag < data_inicio or data_pag > data_fim:
            continue
 
        forma = forma_pagamento or "Não informado"
        resumo[forma] = resumo.get(forma, 0.0) + valor
 
    conn.close()
    return resumo


def calcular_despesa(data_inicio, data_fim):
    despesas = listar_despesas(data_inicio, data_fim)
    return sum(despesa[3] for despesa in despesas)

def calcular_lucro_dia():
    hoje = datetime.now().date()
    receita = calcular_receita(hoje, hoje)
    despesa = calcular_despesa(hoje, hoje)
    return receita - despesa


def calcular_lucro_mes():
    hoje = datetime.now().date()
    primeiro_dia_mes = hoje.replace(day=1)
    receita = calcular_receita(primeiro_dia_mes, hoje)
    despesa = calcular_despesa(primeiro_dia_mes, hoje)
    return receita - despesa


# ------------------------------------------------------------
# FIADO / CONTAS A RECEBER
# ------------------------------------------------------------

def listar_os_pendentes_fiado():
    conn = conectar()
    cursor = conn.cursor()
 
    cursor.execute("""
        SELECT
            ordens_de_servico.id,
            clientes.nome,
            ordens_de_servico.mao_obra,
            ordens_de_servico.data_entrega
        FROM ordens_de_servico
        JOIN clientes
            ON clientes.id = ordens_de_servico.cliente_id
        WHERE ordens_de_servico.status_pagamento = 'Pendente'
        ORDER BY ordens_de_servico.data_entrega ASC
    """)
 
    ordens = cursor.fetchall()
    resultado = []
    hoje = datetime.now().date()
 
    for id_ordem, nome_cliente, mao_obra, data_entrega in ordens:
        cursor.execute("""
            SELECT COALESCE(SUM(valor_venda_momento * quantidade), 0)
            FROM ordens_de_servico_pecas
            WHERE ordem_id = ?
        """, (id_ordem,))
 
        valor_pecas = cursor.fetchone()[0]
 
        try:
            valor_total = float(str(mao_obra).replace(",", ".")) + valor_pecas
        except (ValueError, TypeError):
            valor_total = valor_pecas
 
        cursor.execute("""
            SELECT COALESCE(SUM(valor), 0)
            FROM pagamentos_fiado
            WHERE ordem_id = ?
        """, (id_ordem,))
 
        valor_pago = cursor.fetchone()[0]
        valor_restante = valor_total - valor_pago
 
        if data_entrega:
            data_ent = datetime.strptime(
                data_entrega, "%d/%m/%Y %H:%M"
            ).date()
            dias_pendente = (hoje - data_ent).days
        else:
            dias_pendente = None
 
        resultado.append((
            id_ordem,
            nome_cliente,
            valor_total,
            valor_pago,
            valor_restante,
            dias_pendente
        ))
 
    conn.close()
    return resultado


# ------------------------------------------------------------
# FLUXO DE CAIXA
# ------------------------------------------------------------

def calcular_fluxo_caixa(data_inicio, data_fim):
    """
    Retorna lista de dicts, um por dia no período:
    [{"data": date, "entradas": float, "saidas": float, "saldo": float}, ...]
    """
    fluxo = []
    dia_atual = data_inicio

    while dia_atual <= data_fim:
        entradas = calcular_receita(dia_atual, dia_atual)
        saidas = calcular_despesa(dia_atual, dia_atual)

        fluxo.append({
            "data": dia_atual,
            "entradas": entradas,
            "saidas": saidas,
            "saldo": entradas - saidas
        })

        dia_atual += timedelta(days=1)

    return fluxo
