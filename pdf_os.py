import os
import re
import subprocess
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from database import obter_ordem_por_id, listar_pecas_ordem
from caminhos import obter_pasta_base
PASTA_PDFS = os.path.join(obter_pasta_base(), "OS_PDFs")


def limpar_nome_arquivo(texto):
    texto = texto.strip().replace(" ", "_")
    texto = re.sub(r"[^a-zA-Z0-9_]", "", texto)
    return texto


def gerar_pdf_os(id_ordem):
    dados = obter_ordem_por_id(id_ordem)

    (
        id_os,
        cliente,
        veiculo,
        descricao,
        mao_obra,
        status,
        forma_pagamento,
        status_pagamento,
        data_abertura,
        data_entrega,
        data_pagamento
    ) = dados
 
    try:
        mao_obra = float(str(mao_obra).replace(",", "."))
    except (ValueError, TypeError):
        mao_obra = 0.0
 
    pecas = listar_pecas_ordem(id_ordem)
 
    total_pecas = 0.0
    linhas_pecas = [["Peça", "Qtd", "Valor Unit.", "Subtotal"]]
 
    for nome_peca, quantidade, valor_venda in pecas:
        subtotal = float(quantidade) * float(valor_venda)
        total_pecas += subtotal
        linhas_pecas.append([
            nome_peca,
            str(quantidade),
            f"R$ {float(valor_venda):.2f}",
            f"R$ {subtotal:.2f}"
        ])
 
    total = total_pecas + mao_obra
 
    os.makedirs(PASTA_PDFS, exist_ok=True)
 
    nome_arquivo = f"OS_{id_os}_{limpar_nome_arquivo(cliente)}.pdf"
    caminho = os.path.join(PASTA_PDFS, nome_arquivo)
 
    doc = SimpleDocTemplate(
        caminho,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2 * cm,
        rightMargin=2 * cm
    )
 
    estilos = getSampleStyleSheet()
 
    estilo_titulo = ParagraphStyle(
        "TituloEmpresa",
        parent=estilos["Title"],
        fontSize=20,
        textColor=colors.HexColor("#0d1117"),
        spaceAfter=0
    )
 
    estilo_subtitulo = ParagraphStyle(
        "Subtitulo",
        parent=estilos["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#444444"),
        spaceAfter=10
    )
 
    estilo_secao = ParagraphStyle(
        "Secao",
        parent=estilos["Heading2"],
        fontSize=13,
        textColor=colors.HexColor("#0d1117"),
        spaceBefore=14,
        spaceAfter=6
    )
 
    estilo_normal = ParagraphStyle(
        "NormalPreto",
        parent=estilos["Normal"],
        fontSize=11,
        textColor=colors.black,
        leading=16
    )
 
    estilo_rodape = ParagraphStyle(
        "Rodape",
        parent=estilos["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#666666"),
        alignment=1
    )
 
    elementos = []
 
    elementos.append(Paragraph("Auto Elétrica Emerson", estilo_titulo))
    elementos.append(Paragraph("Tel: (67) 98157-7324", estilo_subtitulo))
 
    linha_vermelha = Table(
        [[""]],
        colWidths=[17 * cm],
        rowHeights=[0.08 * cm]
    )
    linha_vermelha.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#c0392b"))
    ]))
    elementos.append(linha_vermelha)
    elementos.append(Spacer(1, 14))
 
    elementos.append(Paragraph(f"Ordem de Serviço #{id_os}", estilo_secao))
    elementos.append(Paragraph(
        f"Cliente: {cliente}<br/>"
        f"Veículo: {veiculo}<br/>"
        f"Status: {status}",
        estilo_normal
    ))
 
    elementos.append(Paragraph("Serviço realizado", estilo_secao))
    elementos.append(Paragraph(
        f"Descrição: {descricao or '-'}<br/><br/>"
        f"Data de abertura: {data_abertura or '-'}<br/>"
        f"Data de entrega: {data_entrega or 'Ainda não entregue'}<br/>"
        f"Forma de pagamento: {forma_pagamento or 'Não informado'}<br/>"
        f"Status do pagamento: {status_pagamento or 'Não informado'}<br/>"
        f"Data do pagamento: {data_pagamento or 'Ainda não recebido'}",
        estilo_normal
    ))
 
    if pecas:
        elementos.append(Paragraph("Peças utilizadas", estilo_secao))
 
        tabela_pecas = Table(
            linhas_pecas,
            colWidths=[7 * cm, 2 * cm, 4 * cm, 4 * cm]
        )
        tabela_pecas.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d1117")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabela_pecas)
 
    elementos.append(Spacer(1, 16))
 
    tabela_totais = Table(
        [
            ["Total das peças", f"R$ {total_pecas:.2f}"],
            ["Mão de obra", f"R$ {mao_obra:.2f}"],
            ["TOTAL", f"R$ {total:.2f}"]
        ],
        colWidths=[13 * cm, 4 * cm]
    )
    tabela_totais.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 2), (-1, 2), 13),
        ("LINEABOVE", (0, 2), (-1, 2), 1, colors.HexColor("#0d1117")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabela_totais)
 
    elementos.append(Spacer(1, 30))
    elementos.append(Paragraph("Obrigado pela preferência!", estilo_rodape))
 
    doc.build(elementos)
 
    return caminho

def abrir_pdf(caminho):
    if sys.platform == "win32":
        os.startfile(caminho)
    else:
        try:
            subprocess.run(["xdg-open", caminho], check=False)
        except FileNotFoundError:
            pass

