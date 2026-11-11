import customtkinter as ctk
import datetime
import os
import math
from PIL import Image
from tkinter import messagebox
from pdf_os import gerar_pdf_os, abrir_pdf
from caminhos import obter_pasta_recursos
from database import (
    criar_tabelas,
    inserir_cliente,
    listar_clientes,
    inserir_veiculo,
    listar_veiculos,
    buscar_veiculos,
    buscar_veiculo,
    atualizar_veiculo,
    apagar_veiculo,
    listar_veiculos_por_cliente,
    inserir_ordens_de_servico,
    listar_ordens_de_servico,
    buscar_ordens_entregues,
    atualizar_status_ordens_de_servico,
    atualizar_ordem_servico,
    listar_pecas_ordem_editavel,
    remover_peca_da_ordem,
    contar_clientes,
    contar_veiculos,
    contar_ordens_de_servico,
    listar_estoque,
    inserir_estoque,
    inserir_ordem_peca,
    listar_pecas_ordem,
    listar_ordens_entregues,
    obter_ordem_por_id,
    baixar_estoque,
    buscar_peca,
    atualizar_quantidade_estoque,
    apagar_peca_estoque,
    buscar_pecas,
    inserir_despesa,
    listar_despesas,
    calcular_receita,
    calcular_despesa,
    calcular_lucro_dia,
    calcular_lucro_mes,
    resumo_formas_pagamento,
    listar_os_pendentes_fiado,
    migrar_colunas_ordens_de_servico,
    migrar_colunas_pagamentos_fiado,
    calcular_fluxo_caixa,
    contar_os_por_status,
    contar_entregues_hoje,
    listar_estoque_baixo,
    listar_ultimas_ordens,
    buscar_clientes,
    buscar_cliente,
    atualizar_cliente,
    apagar_cliente,
    registrar_pagamento_fiado,
    listar_pagamentos_fiado,
    contar_clientes_busca,
    listar_clientes_paginado,
    contar_veiculos_busca,
    listar_veiculos_paginado,
    contar_ordens_entregues_busca,
    buscar_ordens_entregues_paginado,
    listar_ordens_de_servico_paginado,
    contar_pecas_busca,
    listar_pecas_paginado

)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CATEGORIAS_DESPESA = [
    "Fornecedor",
    "Aluguel",
    "Salário",
    "Conta de Luz/Água",
    "Peça Avulsa",
    "Outros"
]

FORMAS_PAGAMENTO_DESPESA = [
    "Dinheiro",
    "Pix",
    "Débito",
    "Crédito"
]

COR_FUNDO = "#0d1117"
COR_FUNDO_MENU = "#161b22"
COR_AZUL_ATIVO = "#1f6feb"
COR_TEXTO = "#e6edf3"
COR_TEXTO_SECUNDARIO = "#8b949e"
COR_POSITIVO = "#3fb950"
COR_ALERTA = "#f85149"

ITENS_POR_PAGINA = 20

STATUS_CORES = {
    "Aberta": "#8b949e",
    "Em diagnóstico": "#d29922",
    "Aguardando peça": "#a371f7",
    "Em execução": "#d29922",
    "Finalizada": "#3fb950",
    "Entregue": "#3fb950",
}


class AutoEletricaApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        criar_tabelas()
        migrar_colunas_ordens_de_servico()
        migrar_colunas_pagamentos_fiado()

        self.title("Auto Elétrica Emerson")
        self.geometry("1400x900")

        self.paginas = {}
        self.criar_layout()

    def preparar_janela(self, janela):
        janela.lift()
        janela.focus_force()
        janela.attributes("-topmost", True)
        janela.after(
            100,
            lambda: janela.attributes("-topmost", False)
        )
        janela.after(
            150,
            janela.grab_set
        )

    def criar_layout(self):
        ctk.set_appearance_mode("dark")

        self.configure(fg_color=COR_FUNDO)

        # MENU LATERAL
        self.menu_frame = ctk.CTkFrame(
            self,
            width=250,
            corner_radius=0,
            fg_color=COR_FUNDO_MENU
        )
        self.menu_frame.pack(
            side="left",
            fill="y"
        )

        # ÁREA PRINCIPAL
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=COR_FUNDO
        )
        self.content_frame.pack(
            side="right",
            fill="both",
            expand=True
        )

        # LOGO
        caminho_logo = os.path.join(
            obter_pasta_recursos(),
            "assets",
            "logo_emerson_sidebar.png"
        )
 
        logo_imagem = ctk.CTkImage(
            light_image=Image.open(caminho_logo),
            dark_image=Image.open(caminho_logo),
            size=(220, 129)
        )

        logo_label = ctk.CTkLabel(
            self.menu_frame,
            image=logo_imagem,
            text=""
        )
        logo_label.pack(
            pady=25
        )

        # BOTÕES
        botoes = [
            ("Dashboard", self.mostrar_dashboard),
            ("Clientes", self.mostrar_clientes),
            ("Veículos", self.mostrar_veiculos),
            ("Ordens de Serviço", self.mostrar_ordens_de_servico),
            ("Histórico OS", self.mostrar_historico_ordens),
            ("Estoque", self.mostrar_estoque),
            ("Financeiro", self.mostrar_financeiro)
        ]

        self.botoes_sidebar = {}

        for texto, comando in botoes:
            def comando_wrapper(comando=comando, texto=texto):
                self.selecionar_botao_sidebar(texto)
                comando()

            btn = ctk.CTkButton(
                self.menu_frame,
                text=texto,
                fg_color="transparent",
                text_color=COR_TEXTO,
                hover_color=COR_FUNDO,
                anchor="w",
                command=comando_wrapper
            )
            btn.pack(
                fill="x",
                padx=15,
                pady=6
            )

            self.botoes_sidebar[texto] = btn

        self.selecionar_botao_sidebar("Dashboard")
        self.mostrar_dashboard()


    def selecionar_botao_sidebar(self, texto_selecionado):
        for texto, botao in self.botoes_sidebar.items():
            if texto == texto_selecionado:
                botao.configure(
                    fg_color=COR_AZUL_ATIVO,
                    text_color="#ffffff"
                )
            else:
                botao.configure(
                    fg_color="transparent",
                    text_color=COR_TEXTO
                )

            self.mostrar_dashboard()

    def limpar_tela(self):

        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def criar_paginacao(self, parent, pagina_atual, total_paginas, total_itens, ao_mudar):
        btn_anterior = ctk.CTkButton(
            parent,
            text="◀ Anterior",
            width=110,
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            state="normal" if pagina_atual > 1 else "disabled",
            command=lambda: ao_mudar(pagina_atual - 1)
        )
        btn_anterior.pack(
            side="left",
            padx=10
        )

        info_label = ctk.CTkLabel(
            parent,
            text=f"Página {pagina_atual} de {total_paginas}  ({total_itens} itens)",
            text_color=COR_TEXTO_SECUNDARIO
        )
        info_label.pack(
            side="left",
            padx=10
        )

        btn_proxima = ctk.CTkButton(
            parent,
            text="Próxima ▶",
            width=110,
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            state="normal" if pagina_atual < total_paginas else "disabled",
            command=lambda: ao_mudar(pagina_atual + 1)
        )
        btn_proxima.pack(
            side="left",
            padx=10
        )

    def atualizar_lista_paginada(
        self,
        chave,
        texto,
        contar,
        listar,
        carregar,
        scroll,
        frame_paginacao
    ):
        total = contar(texto)
        total_paginas = max(1, math.ceil(total / ITENS_POR_PAGINA))

        pagina = min(self.paginas.get(chave, 1), total_paginas)
        self.paginas[chave] = pagina

        offset = (pagina - 1) * ITENS_POR_PAGINA
        itens = listar(texto, ITENS_POR_PAGINA, offset)

        for widget in scroll.winfo_children():
            widget.destroy()

        if not itens:
            vazio = ctk.CTkLabel(
                scroll,
                text="Nenhum item encontrado.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio.pack(
                pady=20
            )
        else:
            carregar(itens, scroll)

        try:
            scroll._parent_canvas.yview_moveto(0)
        except Exception:
            pass

        for widget in frame_paginacao.winfo_children():
            widget.destroy()

        def ao_mudar(nova_pagina):
            self.paginas[chave] = nova_pagina
            self.atualizar_lista_paginada(
                chave,
                texto,
                contar,
                listar,
                carregar,
                scroll,
                frame_paginacao
            )

        self.criar_paginacao(
            frame_paginacao,
            pagina,
            total_paginas,
            total,
            ao_mudar
        )

    # DASHBOARD

    def mostrar_dashboard(self):
        self.limpar_tela()
        self.criar_titulo_dashboard()
        self.criar_cards_dashboard()
        self.criar_corpo_dashboard()
        self.criar_painel_financeiro()
        self.criar_painel_estoque()
        self.criar_tabela_ultimas_os()


    def criar_titulo_dashboard(self):


        titulo = ctk.CTkLabel(
            self.content_frame,
            text="Dashboard",
            font=("Arial", 32, "bold")
        )

        titulo.pack(
            pady=20
        )

    def criar_cards_dashboard(self):
        os_abertas = contar_os_por_status("Aberta")
        os_execucao = contar_os_por_status("Em execução")
        finalizadas_hoje = contar_entregues_hoje()

        cards_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        cards_frame.pack(
            padx=20,
            pady=20,
            fill="x"
        )

        self.criar_card(
            cards_frame,
            "OS Abertas",
            str(os_abertas)
        )
        self.criar_card(
            cards_frame,
            "Em Execução",
            str(os_execucao)
        )
        self.criar_card(
            cards_frame,
            "Finalizadas Hoje",
            str(finalizadas_hoje),
            cor_valor=COR_POSITIVO
        )



    def criar_corpo_dashboard(self):
        self.corpo_dashboard = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.corpo_dashboard.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.linha_superior = ctk.CTkFrame(
            self.corpo_dashboard,
            fg_color="transparent"
        )
        self.linha_superior.pack(
            fill="x",
            pady=10
        )

        self.financeiro_frame = ctk.CTkFrame(
            self.linha_superior,
            corner_radius=15,
            fg_color=COR_FUNDO_MENU
        )
        self.financeiro_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 10)
        )

        self.estoque_frame = ctk.CTkFrame(
            self.linha_superior,
            corner_radius=15,
            fg_color=COR_FUNDO_MENU
        )
        self.estoque_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(10, 0)
        )

        self.tabela_ultimas_os = ctk.CTkFrame(
            self.corpo_dashboard,
            corner_radius=15,
            fg_color=COR_FUNDO_MENU
        )
        self.tabela_ultimas_os.pack(
            fill="both",
            expand=True,
            pady=(10, 0)
        )


    def criar_painel_financeiro(self):
        titulo = ctk.CTkLabel(
            self.financeiro_frame,
            text="📈 Financeiro",
            font=("Arial", 22, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(20, 5)
        )

        subtitulo = ctk.CTkLabel(
            self.financeiro_frame,
            text="Faturamento",
            font=("Arial", 14),
            text_color=COR_TEXTO_SECUNDARIO
        )
        subtitulo.pack()

        hoje = datetime.datetime.now().date()
        primeiro_dia_mes = hoje.replace(day=1)

        faturamento_hoje = calcular_receita(hoje, hoje)
        faturamento_mes = calcular_receita(primeiro_dia_mes, hoje)

        def formatar(valor):
            return (
                f"R$ {valor:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

        frame_valores = ctk.CTkFrame(
            self.financeiro_frame,
            fg_color="transparent"
        )
        frame_valores.pack(
            pady=15
        )

        bloco_hoje = ctk.CTkFrame(
            frame_valores,
            fg_color="transparent"
        )
        bloco_hoje.pack(
            side="left",
            padx=20
        )

        label_hoje_titulo = ctk.CTkLabel(
            bloco_hoje,
            text="Hoje",
            font=("Arial", 13),
            text_color=COR_TEXTO_SECUNDARIO
        )
        label_hoje_titulo.pack()

        label_hoje_valor = ctk.CTkLabel(
            bloco_hoje,
            text=formatar(faturamento_hoje),
            font=("Arial", 22, "bold"),
            text_color=COR_POSITIVO
        )
        label_hoje_valor.pack()

        bloco_mes = ctk.CTkFrame(
            frame_valores,
            fg_color="transparent"
        )
        bloco_mes.pack(
            side="left",
            padx=20
        )

        label_mes_titulo = ctk.CTkLabel(
            bloco_mes,
            text="Mês",
            font=("Arial", 13),
            text_color=COR_TEXTO_SECUNDARIO
        )
        label_mes_titulo.pack()

        label_mes_valor = ctk.CTkLabel(
            bloco_mes,
            text=formatar(faturamento_mes),
            font=("Arial", 22, "bold"),
            text_color=COR_POSITIVO
        )
        label_mes_valor.pack()



    def criar_painel_estoque(self):
        titulo = ctk.CTkLabel(
            self.estoque_frame,
            text="📦 Estoque Baixo",
            font=("Arial", 22, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(20, 5)
        )

        subtitulo = ctk.CTkLabel(
            self.estoque_frame,
            text="Itens que precisam de reposição",
            font=("Arial", 14),
            text_color=COR_TEXTO_SECUNDARIO
        )
        subtitulo.pack(
            pady=(0, 10)
        )

        itens = listar_estoque_baixo()

        if not itens:
            vazio = ctk.CTkLabel(
                self.estoque_frame,
                text="Nenhum item em estoque baixo.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio.pack(
                pady=15
            )
            return

        for id_item, nome, quantidade, estoque_minimo in itens:
            linha = ctk.CTkFrame(
                self.estoque_frame,
                fg_color="transparent"
            )
            linha.pack(
                fill="x",
                padx=20,
                pady=4
            )

            nome_label = ctk.CTkLabel(
                linha,
                text=nome,
                text_color=COR_TEXTO,
                anchor="w"
            )
            nome_label.pack(
                side="left"
            )

            quantidade_label = ctk.CTkLabel(
                linha,
                text=f"{quantidade} un.",
                text_color=COR_ALERTA
            )
            quantidade_label.pack(
                side="right"
            )


    def criar_tabela_ultimas_os(self):
        titulo = ctk.CTkLabel(
            self.tabela_ultimas_os,
            text="Últimas Ordens de Serviço",
            font=("Arial", 20, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        colunas_frame = ctk.CTkFrame(
            self.tabela_ultimas_os,
            fg_color="transparent"
        )
        colunas_frame.pack(
            fill="x",
            padx=20
        )

        cabecalhos = [
            "Nº OS",
            "Cliente",
            "Veículo",
            "Status",
            "Data Abertura",
            "Total"
        ]

        for texto in cabecalhos:
            label = ctk.CTkLabel(
                colunas_frame,
                text=texto,
                font=("Arial", 13, "bold"),
                text_color=COR_TEXTO_SECUNDARIO,
                width=150,
                anchor="w"
            )
            label.pack(
                side="left"
            )

        ordens = listar_ultimas_ordens(5)

        if not ordens:
            vazio = ctk.CTkLabel(
                self.tabela_ultimas_os,
                text="Nenhuma ordem de serviço registrada.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio.pack(
                pady=20
            )
            return

        for id_ordem, nome_cliente, modelo, status, data_abertura, total in ordens:
            linha = ctk.CTkFrame(
                self.tabela_ultimas_os,
                fg_color="transparent"
            )
            linha.pack(
                fill="x",
                padx=20,
                pady=6
            )

            total_formatado = (
                f"R$ {total:,.2f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
            )

            valores = [
                f"#{id_ordem}",
                nome_cliente,
                modelo,
                status,
                data_abertura,
                total_formatado
            ]

            for valor in valores:
                label = ctk.CTkLabel(
                    linha,
                    text=valor,
                    text_color=COR_TEXTO,
                    width=150,
                    anchor="w"
                )
                label.pack(
                    side="left"
                )


    def criar_card(self, parent, titulo, valor, cor_valor=None):
        card = ctk.CTkFrame(
            parent,
            width=220,
            height=110,
            corner_radius=15,
            fg_color=COR_FUNDO_MENU,
            border_width=1,
            border_color=COR_TEXTO_SECUNDARIO
        )
        card.pack(
            side="left",
            padx=10,
            pady=10
        )
        card.pack_propagate(False)
 
        texto = ctk.CTkLabel(
            card,
            text=titulo,
            font=("Arial", 14),
            text_color=COR_TEXTO_SECUNDARIO
        )
        texto.pack(
            pady=(20, 5)
        )
 
        numero = ctk.CTkLabel(
            card,
            text=valor,
            font=("Arial", 26, "bold"),
            text_color=cor_valor or COR_TEXTO
        )
        numero.pack()

    def configurar_combobox_pesquisavel(self, combo, valores_completos):
        """
        Faz o combobox filtrar as opções conforme o usuário digita.
        valores_completos é a lista ORIGINAL (sem filtro) - guarde
        ela numa variável antes de chamar essa função, porque o
        combo.configure(values=...) vai sobrescrever a lista visível.
        """
        entry_widget = getattr(combo, "_entry", None)
 
        if entry_widget is None:
            for widget in combo.winfo_children():
                if isinstance(widget, ctk.CTkEntry):
                    entry_widget = widget
                    break
 
        if entry_widget is None:
            return
 
        def filtrar(event=None):
            texto_digitado = combo.get().lower()
 
            if texto_digitado == "":
                filtrados = valores_completos
            else:
                filtrados = [
                    valor for valor in valores_completos
                    if texto_digitado in valor.lower()
                ]
 
            combo.configure(values=filtrados)
 
        entry_widget.bind("<KeyRelease>", filtrar)


    # TELAS

    def mostrar_clientes(self):
        self.limpar_tela()

        titulo = ctk.CTkLabel(
            self.content_frame,
            text="Cadastro de Clientes",
            font=("Arial", 28, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(30, 20)
        )

        card_formulario = ctk.CTkFrame(
            self.content_frame,
            corner_radius=15,
            border_width=1,
            fg_color=COR_FUNDO_MENU
        )
        card_formulario.pack(
            padx=20,
            pady=10
        )

        nome_entry = ctk.CTkEntry(
            card_formulario,
            width=300,
            placeholder_text="Nome",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        nome_entry.pack(
            padx=30,
            pady=(25, 10)
        )

        telefone_entry = ctk.CTkEntry(
            card_formulario,
            width=300,
            placeholder_text="Telefone",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        telefone_entry.pack(
            padx=30,
            pady=10
        )

        def salvar_cliente():
            nome = nome_entry.get()
            telefone = telefone_entry.get()

            if not nome.strip():
                messagebox.showerror(
                    "Erro",
                    "Digite o nome do cliente."
                )
                return

            inserir_cliente(nome, telefone)

            self.mostrar_clientes()

        btn_salvar = ctk.CTkButton(
            card_formulario,
            text="Salvar cliente",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_cliente
        )
        btn_salvar.pack(
            pady=(15, 25)
        )

        titulo_lista = ctk.CTkLabel(
            self.content_frame,
            text="Clientes Cadastrados",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo_lista.pack(
            pady=(20, 10)
        )

        frame_pesquisa = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        frame_pesquisa.pack(
            pady=10
        )

        self.pesquisa_cliente_entry = ctk.CTkEntry(
            frame_pesquisa,
            width=300,
            placeholder_text="🔍 Pesquisar cliente...",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        self.pesquisa_cliente_entry.pack(
            side="left",
            padx=(0, 10)
        )
        self.pesquisa_cliente_entry.bind(
            "<KeyRelease>",
            self.pesquisar_cliente
        )

        btn_pesquisa_cliente = ctk.CTkButton(
            frame_pesquisa,
            text="Pesquisar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=self.pesquisar_cliente
        )
        btn_pesquisa_cliente.pack(
            side="left"
        )

        self.paginas["clientes"] = 1

        self.frame_paginacao_clientes = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.frame_paginacao_clientes.pack(
            side="bottom",
            pady=10
        )

        self.scroll_clientes = ctk.CTkScrollableFrame(
            self.content_frame,
            width=600,
            height=350,
            fg_color="transparent"
        )
        self.scroll_clientes.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(10, 20)
        )

        self.atualizar_lista_clientes()

    def carregar_lista_clientes(self, clientes, scroll):
        for widget in scroll.winfo_children():
            widget.destroy()

        if not clientes:
            vazio = ctk.CTkLabel(
                scroll,
                text="Nenhum cliente encontrado.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio.pack(
                pady=20
            )
            return

        for cliente in clientes:
            id_cliente, nome, telefone = cliente

            card_cliente = ctk.CTkFrame(
                scroll,
                corner_radius=10,
                fg_color=COR_FUNDO_MENU
            )
            card_cliente.pack(
                fill="x",
                padx=5,
                pady=6
            )

            info_frame = ctk.CTkFrame(
                card_cliente,
                fg_color="transparent"
            )
            info_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=20,
                pady=12
            )

            nome_label = ctk.CTkLabel(
                info_frame,
                text=nome,
                font=("Arial", 15, "bold"),
                text_color=COR_TEXTO,
                anchor="w"
            )
            nome_label.pack(
                anchor="w"
            )

            telefone_label = ctk.CTkLabel(
                info_frame,
                text=telefone or "Sem telefone",
                font=("Arial", 13),
                text_color=COR_TEXTO_SECUNDARIO,
                anchor="w"
            )
            telefone_label.pack(
                anchor="w"
            )

            botoes_frame = ctk.CTkFrame(
                card_cliente,
                fg_color="transparent"
            )
            botoes_frame.pack(
                side="right",
                padx=15,
                pady=12
            )

            btn_alterar = ctk.CTkButton(
                botoes_frame,
                text="Alterar",
                width=90,
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                command=lambda id=id_cliente: self.editar_cliente(id)
            )
            btn_alterar.pack(
                side="left",
                padx=(0, 8)
            )

            btn_apagar = ctk.CTkButton(
                botoes_frame,
                text="Apagar",
                width=90,
                fg_color=COR_ALERTA,
                hover_color="#c93c36",
                command=lambda id=id_cliente: self.apagar_cliente_click(id)
            )
            btn_apagar.pack(
                side="left"
            )

    def atualizar_lista_clientes(self):
        self.atualizar_lista_paginada(
            "clientes",
            self.pesquisa_cliente_entry.get(),
            contar_clientes_busca,
            listar_clientes_paginado,
            self.carregar_lista_clientes,
            self.scroll_clientes,
            self.frame_paginacao_clientes
        )

    def pesquisar_cliente(self, event=None):
        self.paginas["clientes"] = 1
        self.atualizar_lista_clientes()

    def editar_cliente(self, id_cliente):
        janela = ctk.CTkToplevel(self)
        janela.title("Editar Cliente")
        janela.geometry("400x350")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        cliente = buscar_cliente(id_cliente)
        nome_atual = cliente[1]
        telefone_atual = cliente[2]

        titulo = ctk.CTkLabel(
            janela,
            text="Editar Cliente",
            font=("Arial", 20, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=20
        )

        nome_entry = ctk.CTkEntry(
            janela,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        nome_entry.insert(0, nome_atual)
        nome_entry.pack(
            pady=10
        )

        telefone_entry = ctk.CTkEntry(
            janela,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        telefone_entry.insert(0, telefone_atual or "")
        telefone_entry.pack(
            pady=10
        )

        def salvar():
            novo_nome = nome_entry.get()
            novo_telefone = telefone_entry.get()

            if not novo_nome.strip():
                messagebox.showerror(
                    "Erro",
                    "Digite o nome do cliente."
                )
                return

            atualizar_cliente(
                id_cliente,
                novo_nome,
                novo_telefone
            )

            messagebox.showinfo(
                "Sucesso",
                "Cliente atualizado com sucesso!"
            )

            janela.destroy()
            self.mostrar_clientes()

        btn_salvar = ctk.CTkButton(
            janela,
            text="Salvar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar
        )
        btn_salvar.pack(
            pady=20
        )

    def apagar_cliente_click(self, id_cliente):
        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir este cliente?\n\n"
            "Esta ação não poderá ser desfeita."
        )

        if not confirmar:
            return

        resultado = apagar_cliente(id_cliente)

        if resultado:
            messagebox.showinfo(
                "Cliente apagado",
                "Cliente removido com sucesso!"
            )
            self.mostrar_clientes()
        else:
            messagebox.showerror(
                "Não foi possível excluir este cliente.",
                "Ele possui veículos ou ordens de serviço vinculados."
            )

    def mostrar_veiculos(self):
        self.limpar_tela()

        titulo = ctk.CTkLabel(
            self.content_frame,
            text="Cadastro de Veículos",
            font=("Arial", 28, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(30, 20)
        )

        card_formulario = ctk.CTkFrame(
            self.content_frame,
            corner_radius=15,
            fg_color=COR_FUNDO_MENU
        )
        card_formulario.pack(
            padx=20,
            pady=10
        )

        clientes = listar_clientes()
        nomes_clientes = [cliente[1] for cliente in clientes]

        cliente_label = ctk.CTkLabel(
            card_formulario,
            text="Cliente",
            text_color=COR_TEXTO_SECUNDARIO
        )
        cliente_label.pack(
            pady=(25, 0)
        )

        cliente_combo = ctk.CTkComboBox(
            card_formulario,
            values=nomes_clientes,
            width=300,
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        cliente_combo.pack(
            pady=10
        )

        self.configurar_combobox_pesquisavel(
            cliente_combo,
            nomes_clientes
        )

        dica_pesquisa_label = ctk.CTkLabel(
            card_formulario,
            text="💡 Digite para filtrar a lista",
            font=("Arial", 11),
            text_color=COR_TEXTO_SECUNDARIO
        )
        dica_pesquisa_label.pack(
            pady=(0, 10)
        )


        modelo_entry = ctk.CTkEntry(
            card_formulario,
            width=300,
            placeholder_text="Modelo",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        modelo_entry.pack(
            pady=10
        )

        placa_entry = ctk.CTkEntry(
            card_formulario,
            width=300,
            placeholder_text="Placa",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        placa_entry.pack(
            pady=10
        )

        def salvar_veiculo():
            nome_cliente = cliente_combo.get()
            modelo = modelo_entry.get()
            placa = placa_entry.get()

            if not nome_cliente or not modelo.strip():
                messagebox.showerror(
                    "Erro",
                    "Selecione o cliente e digite o modelo."
                )
                return

            cliente_id = None
            for cliente in clientes:
                if cliente[1] == nome_cliente:
                    cliente_id = cliente[0]
                    break

            inserir_veiculo(
                cliente_id,
                modelo,
                placa
            )

            self.mostrar_veiculos()

        btn_salvar = ctk.CTkButton(
            card_formulario,
            text="Salvar veículo",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_veiculo
        )
        btn_salvar.pack(
            pady=(15, 25)
        )

        titulo_lista = ctk.CTkLabel(
            self.content_frame,
            text="Veículos Cadastrados",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo_lista.pack(
            pady=(20, 10)
        )

        frame_pesquisa = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        frame_pesquisa.pack(
            pady=10
        )

        self.pesquisa_veiculo_entry = ctk.CTkEntry(
            frame_pesquisa,
            width=300,
            placeholder_text="🔍 Pesquisar por cliente, modelo ou placa...",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        self.pesquisa_veiculo_entry.pack(
            side="left",
            padx=(0, 10)
        )
        self.pesquisa_veiculo_entry.bind(
            "<KeyRelease>",
            self.pesquisar_veiculo
        )

        btn_pesquisa_veiculo = ctk.CTkButton(
            frame_pesquisa,
            text="Pesquisar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=self.pesquisar_veiculo
        )
        btn_pesquisa_veiculo.pack(
            side="left"
        )

        self.paginas["veiculos"] = 1

        self.frame_paginacao_veiculos = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.frame_paginacao_veiculos.pack(
            side="bottom",
            pady=10
        )

        self.scroll_veiculos = ctk.CTkScrollableFrame(
            self.content_frame,
            width=650,
            height=400,
            fg_color="transparent"
        )
        self.scroll_veiculos.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(10, 20)
        )

        self.atualizar_lista_veiculos()

    def carregar_lista_veiculos(self, veiculos, scroll):
        for widget in scroll.winfo_children():
            widget.destroy()

        if not veiculos:
            vazio = ctk.CTkLabel(
                scroll,
                text="Nenhum veículo encontrado.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio.pack(
                pady=20
            )
            return

        for veiculo in veiculos:
            id_veiculo, nome_cliente, modelo, placa = veiculo

            card_veiculo = ctk.CTkFrame(
                scroll,
                corner_radius=10,
                fg_color=COR_FUNDO_MENU
            )
            card_veiculo.pack(
                fill="x",
                padx=5,
                pady=6
            )

            info_frame = ctk.CTkFrame(
                card_veiculo,
                fg_color="transparent"
            )
            info_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=20,
                pady=12
            )

            modelo_label = ctk.CTkLabel(
                info_frame,
                text=f"{modelo} / {placa}",
                font=("Arial", 15, "bold"),
                text_color=COR_TEXTO,
                anchor="w"
            )
            modelo_label.pack(
                anchor="w"
            )

            cliente_label = ctk.CTkLabel(
                info_frame,
                text=nome_cliente,
                font=("Arial", 13),
                text_color=COR_TEXTO_SECUNDARIO,
                anchor="w"
            )
            cliente_label.pack(
                anchor="w"
            )

            botoes_frame = ctk.CTkFrame(
                card_veiculo,
                fg_color="transparent"
            )
            botoes_frame.pack(
                side="right",
                padx=15,
                pady=12
            )

            btn_alterar = ctk.CTkButton(
                botoes_frame,
                text="Alterar",
                width=90,
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                command=lambda id=id_veiculo: self.editar_veiculo(id)
            )
            btn_alterar.pack(
                side="left",
                padx=(0, 8)
            )

            btn_apagar = ctk.CTkButton(
                botoes_frame,
                text="Apagar",
                width=90,
                fg_color=COR_ALERTA,
                hover_color="#c93c36",
                command=lambda id=id_veiculo: self.apagar_veiculo_click(id)
            )
            btn_apagar.pack(
                side="left"
            )

    def atualizar_lista_veiculos(self):
        self.atualizar_lista_paginada(
            "veiculos",
            self.pesquisa_veiculo_entry.get(),
            contar_veiculos_busca,
            listar_veiculos_paginado,
            self.carregar_lista_veiculos,
            self.scroll_veiculos,
            self.frame_paginacao_veiculos
        )

    def pesquisar_veiculo(self, event=None):
        self.paginas["veiculos"] = 1
        self.atualizar_lista_veiculos()

    def editar_veiculo(self, id_veiculo):
        janela = ctk.CTkToplevel(self)
        janela.title("Editar Veículo")
        janela.geometry("400x420")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        veiculo = buscar_veiculo(id_veiculo)
        cliente_id_atual = veiculo[1]
        modelo_atual = veiculo[2]
        placa_atual = veiculo[3]

        clientes = listar_clientes()
        nomes_clientes = [cliente[1] for cliente in clientes]

        nome_cliente_atual = ""
        for cliente in clientes:
            if cliente[0] == cliente_id_atual:
                nome_cliente_atual = cliente[1]
                break

        titulo = ctk.CTkLabel(
            janela,
            text="Editar Veículo",
            font=("Arial", 20, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=20
        )

        cliente_combo = ctk.CTkComboBox(
            janela,
            values=nomes_clientes,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        cliente_combo.set(nome_cliente_atual)
        cliente_combo.pack(
            pady=10
        )

        self.configurar_combobox_pesquisavel(
            cliente_combo,
            nomes_clientes
        )

        dica_pesquisa_label = ctk.CTkLabel(
            janela,
            text="💡 Digite para filtrar a lista",
            font=("Arial", 11),
            text_color=COR_TEXTO_SECUNDARIO
        )
        dica_pesquisa_label.pack(
            pady=(0, 10)
        )


        modelo_entry = ctk.CTkEntry(
            janela,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        modelo_entry.insert(0, modelo_atual)
        modelo_entry.pack(
            pady=10
        )

        placa_entry = ctk.CTkEntry(
            janela,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        placa_entry.insert(0, placa_atual)
        placa_entry.pack(
            pady=10
        )

        def salvar():
            nome_cliente = cliente_combo.get()
            novo_modelo = modelo_entry.get()
            nova_placa = placa_entry.get()

            if not nome_cliente or not novo_modelo.strip():
                messagebox.showerror(
                    "Erro",
                    "Selecione o cliente e digite o modelo."
                )
                return

            novo_cliente_id = None
            for cliente in clientes:
                if cliente[1] == nome_cliente:
                    novo_cliente_id = cliente[0]
                    break

            atualizar_veiculo(
                id_veiculo,
                novo_cliente_id,
                novo_modelo,
                nova_placa
            )

            messagebox.showinfo(
                "Sucesso",
                "Veículo atualizado com sucesso!"
            )

            janela.destroy()
            self.mostrar_veiculos()

        btn_salvar = ctk.CTkButton(
            janela,
            text="Salvar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar
        )
        btn_salvar.pack(
            pady=20
        )

    def apagar_veiculo_click(self, id_veiculo):
        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir este veículo?\n\n"
            "Esta ação não poderá ser desfeita."
        )

        if not confirmar:
            return

        resultado = apagar_veiculo(id_veiculo)

        if resultado:
            messagebox.showinfo(
                "Veículo apagado",
                "Veículo removido com sucesso!"
            )
            self.mostrar_veiculos()
        else:
            messagebox.showerror(
                "Não foi possível excluir este veículo.",
                "Ele possui ordens de serviço vinculadas."
            )

    def mostrar_ordens_de_servico(self):
        self.limpar_tela()

        titulo = ctk.CTkLabel(
            self.content_frame,
            text="Ordens de Serviço",
            font=("Arial", 28, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(30, 10)
        )

        btn_nova_os = ctk.CTkButton(
            self.content_frame,
            text="+ Nova Ordem de Serviço",
            width=250,
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=self.abrir_janela_nova_os
        )
        btn_nova_os.pack(
            pady=10
        )

        titulo_lista = ctk.CTkLabel(
            self.content_frame,
            text="Ordens de Serviço Cadastradas",
            font=("Arial", 20, "bold"),
            text_color=COR_TEXTO
        )
        titulo_lista.pack(
            pady=(20, 5)
        )

        def abrir_janela_status(id_ordem):
            janela = ctk.CTkToplevel(self)
            janela.title("Alterar Status")
            janela.geometry("700x400")
            janela.configure(fg_color=COR_FUNDO)
            self.preparar_janela(janela)

            dados_atuais = obter_ordem_por_id(id_ordem)
            status_atual = dados_atuais[5]
            forma_pagamento_atual = dados_atuais[6]
            status_pagamento_atual = dados_atuais[7]
 
            label = ctk.CTkLabel(
                janela,
                text=f"OS #{id_ordem}",
                font=("Arial", 18, "bold"),
                text_color=COR_TEXTO
            )
            label.pack(
                pady=10
            )
 
            status_combo = ctk.CTkComboBox(
                janela,
                values=[
                    "Aberta",
                    "Em diagnóstico",
                    "Aguardando peça",
                    "Em execução",
                    "Finalizada",
                    "Entregue"
                ],
                width=250,
                fg_color=COR_FUNDO_MENU,
                border_color=COR_TEXTO_SECUNDARIO,
                button_color=COR_AZUL_ATIVO,
                text_color=COR_TEXTO
            )
            status_combo.set(status_atual or "Aberta")
            status_combo.pack(
                pady=20
            )
 
            forma_label = ctk.CTkLabel(
                janela,
                text="Forma de pagamento",
                text_color=COR_TEXTO_SECUNDARIO
            )
            forma_label.pack(
                pady=(10, 5)
            )
 
            forma_combo = ctk.CTkComboBox(
                janela,
                values=[
                    "Pix",
                    "Dinheiro",
                    "Débito",
                    "Crédito",
                    "Fiado"
                ],
                width=250,
                fg_color=COR_FUNDO_MENU,
                border_color=COR_TEXTO_SECUNDARIO,
                button_color=COR_AZUL_ATIVO,
                text_color=COR_TEXTO
            )
            forma_combo.pack(
                pady=5
            )
 
            status_pagamento_label = ctk.CTkLabel(
                janela,
                text="Status do pagamento",
                text_color=COR_TEXTO_SECUNDARIO
            )
            status_pagamento_label.pack(
                pady=(10, 5)
            )
 
            status_pagamento_combo = ctk.CTkComboBox(
                janela,
                values=[
                    "Pago",
                    "Pendente"
                ],
                width=250,
                fg_color=COR_FUNDO_MENU,
                border_color=COR_TEXTO_SECUNDARIO,
                button_color=COR_AZUL_ATIVO,
                text_color=COR_TEXTO
            )
            status_pagamento_combo.pack(
                pady=5
            )
 
            def atualizar_status_pagamento(escolha):
                if escolha == "Fiado":
                    status_pagamento_combo.set("Pendente")
                else:
                    status_pagamento_combo.set("Pago")
 
            forma_combo.configure(
                command=atualizar_status_pagamento
            )

            forma_combo.set(forma_pagamento_atual or "Pix")
            status_pagamento_combo.set(status_pagamento_atual or "Pago")
 
            def salvar_status():
                novo_status = status_combo.get()
                forma_pagamento = forma_combo.get()
                status_pagamento = status_pagamento_combo.get()
 
                atualizar_status_ordens_de_servico(
                    id_ordem,
                    novo_status,
                    forma_pagamento,
                    status_pagamento
                )
 
                janela.destroy()
                self.mostrar_ordens_de_servico()
 
            btn_salvar = ctk.CTkButton(
                janela,
                text="Salvar",
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                command=salvar_status
            )
            btn_salvar.pack(
                pady=20
            )


        ordens = listar_ordens_de_servico()
        quantidade = len(ordens)

        contador_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Ordens Ativas: {quantidade}",
            font=("Arial", 16, "bold"),
            text_color=COR_TEXTO_SECUNDARIO
        )
        contador_label.pack(
            pady=10
        )

        lista_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=1000,
            height=650,
            fg_color="transparent"
        )
        lista_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        for ordem in ordens:
            frame_os = ctk.CTkFrame(
                lista_frame,
                corner_radius=12,
                fg_color=COR_FUNDO_MENU
            )
            frame_os.pack(
                fill="x",
                padx=5,
                pady=10,
                ipadx=10,
                ipady=10
            )

            pecas = listar_pecas_ordem(ordem[0])

            texto_pecas = ""
            total_pecas = 0

            if pecas:
                texto_pecas = "\nPeças:\n"
                for nome_peca, qtd_peca, valor_venda in pecas:
                    subtotal = float(qtd_peca) * float(valor_venda)
                    total_pecas += subtotal
                    texto_pecas += (
                        f"- {nome_peca}\n"
                        f"  Qtd: {qtd_peca}\n"
                        f"  Valor Unit.: R$ {valor_venda:.2f}\n"
                        f"  Subtotal: R$ {subtotal:.2f}\n\n"
                    )

            try:
                mao_obra = float(str(ordem[4] or 0).replace(",", "."))
            except ValueError:
                mao_obra = 0

            total = total_pecas + mao_obra

            texto = (
                f"OS #{ordem[0]}\n"
                f"Cliente: {ordem[1]}\n"
                f"Veículo: {ordem[2]}\n"
                f"Descrição: {ordem[3]}\n"
                f"{texto_pecas}"
                f"\nTotal das peças: R$ {total_pecas:.2f}\n"
                f"Mão de obra: R$ {mao_obra:.2f}\n"
                f"--------------------------------\n"
                f"TOTAL: R$ {total:.2f}\n"
            )

            ordem_label = ctk.CTkLabel(
                frame_os,
                text=texto,
                justify="left",
                text_color=COR_TEXTO
            )
            ordem_label.pack(
                anchor="w",
                padx=10,
                pady=2
            )

            status_frame = ctk.CTkFrame(
                frame_os,
                fg_color="transparent"
            )
            status_frame.pack(
                fill="x",
                padx=10,
                pady=5
            )

            cor_status = STATUS_CORES.get(ordem[5], COR_TEXTO_SECUNDARIO)

            badge_status = ctk.CTkLabel(
                status_frame,
                text=f" {ordem[5]} ",
                font=("Arial", 13, "bold"),
                fg_color=cor_status,
                text_color="#0d1117",
                corner_radius=8
            )
            badge_status.pack(
                side="left",
                padx=5
            )

            btn_alterar = ctk.CTkButton(
                status_frame,
                text="Alterar Status",
                width=140,
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                command=lambda id_ordem=ordem[0]: abrir_janela_status(id_ordem)
            )
            btn_alterar.pack(
                side="left",
                padx=10
            )

            if ordem[5] != "Entregue":
                btn_editar = ctk.CTkButton(
                    status_frame,
                    text="Editar OS",
                    width=120,
                    fg_color=COR_FUNDO,
                    hover_color="#21262d",
                    command=lambda id_ordem=ordem[0]: self.abrir_janela_editar_os(id_ordem)
                )
                btn_editar.pack(
                    side="left",
                    padx=10
                )

    def abrir_janela_editar_os(self, id_ordem):
        janela = ctk.CTkToplevel(self)
        janela.title(f"Editar OS #{id_ordem}")
        janela.geometry("700x750")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        scroll = ctk.CTkScrollableFrame(
            janela,
            fg_color="transparent"
        )
        scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )
 
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
 
        titulo = ctk.CTkLabel(
            scroll,
            text=f"Editando OS #{id_os}",
            font=("Arial", 22, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(0, 5)
        )
 
        info_label = ctk.CTkLabel(
            scroll,
            text=f"Cliente: {cliente}   |   Veículo: {veiculo}",
            text_color=COR_TEXTO_SECUNDARIO
        )
        info_label.pack(
            pady=(0, 20)
        )
 
        descricao_entry = ctk.CTkEntry(
            scroll,
            width=400,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        descricao_entry.insert(0, descricao or "")
        descricao_entry.pack(
            pady=10
        )
 
        mao_obra_entry = ctk.CTkEntry(
            scroll,
            width=400,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        mao_obra_entry.insert(0, str(mao_obra))
        mao_obra_entry.pack(
            pady=10
        )
 
        def salvar_dados_os():
            nova_descricao = descricao_entry.get().strip()
            nova_mao_obra = mao_obra_entry.get().strip()
 
            if nova_descricao == "":
                messagebox.showerror(
                    "Erro",
                    "Digite a descrição do serviço."
                )
                return
 
            atualizar_ordem_servico(
                id_ordem,
                nova_descricao,
                nova_mao_obra or "0"
            )
 
            messagebox.showinfo(
                "Sucesso",
                "Dados da OS atualizados!"
            )
 
        btn_salvar_dados = ctk.CTkButton(
            scroll,
            text="Salvar Descrição/Mão de Obra",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_dados_os
        )
        btn_salvar_dados.pack(
            pady=(5, 25)
        )
 
        titulo_pecas = ctk.CTkLabel(
            scroll,
            text="Peças da OS",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo_pecas.pack(
            pady=(10, 10)
        )
 
        scroll_pecas = ctk.CTkScrollableFrame(
            scroll,
            height=200,
            fg_color="transparent"
        )
        scroll_pecas.pack(
            fill="x",
            pady=(0, 15)
        )
 
        def carregar_pecas_editaveis():
            for widget in scroll_pecas.winfo_children():
                widget.destroy()
 
            pecas = listar_pecas_ordem_editavel(id_ordem)
 
            if not pecas:
                vazio = ctk.CTkLabel(
                    scroll_pecas,
                    text="Nenhuma peça nesta OS.",
                    text_color=COR_TEXTO_SECUNDARIO
                )
                vazio.pack(
                    pady=10
                )
                return
 
            for id_relacao, peca_id, nome_peca, quantidade, valor_venda in pecas:
                linha = ctk.CTkFrame(
                    scroll_pecas,
                    corner_radius=8,
                    fg_color=COR_FUNDO_MENU
                )
                linha.pack(
                    fill="x",
                    padx=5,
                    pady=4
                )
 
                subtotal = float(quantidade) * float(valor_venda)
 
                texto_label = ctk.CTkLabel(
                    linha,
                    text=(
                        f"{nome_peca} | Qtd: {quantidade} | "
                        f"R$ {valor_venda:.2f} un. | Subtotal: R$ {subtotal:.2f}"
                    ),
                    text_color=COR_TEXTO,
                    anchor="w"
                )
                texto_label.pack(
                    side="left",
                    padx=10,
                    pady=8
                )
 
                def remover(id_relacao=id_relacao):
                    confirmar = messagebox.askyesno(
                        "Remover peça",
                        "Remover essa peça da OS?"
                    )
                    if not confirmar:
                        return
 
                    remover_peca_da_ordem(id_relacao)
                    carregar_pecas_editaveis()
 
                btn_remover = ctk.CTkButton(
                    linha,
                    text="Remover",
                    width=90,
                    fg_color=COR_ALERTA,
                    hover_color="#c93c36",
                    command=remover
                )
                btn_remover.pack(
                    side="right",
                    padx=10,
                    pady=8
                )
 
        carregar_pecas_editaveis()
 
        titulo_add = ctk.CTkLabel(
            scroll,
            text="Adicionar Peça",
            font=("Arial", 16, "bold"),
            text_color=COR_TEXTO
        )
        titulo_add.pack(
            pady=(10, 10)
        )
 
        estoque = listar_estoque()
        nomes_pecas = [item[1] for item in estoque]
 
        peca_combo = ctk.CTkComboBox(
            scroll,
            values=nomes_pecas,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        peca_combo.pack(
            pady=10
        )
 
        self.configurar_combobox_pesquisavel(
            peca_combo,
            nomes_pecas
        )
 
        quantidade_peca_entry = ctk.CTkEntry(
            scroll,
            width=300,
            placeholder_text="Quantidade",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        quantidade_peca_entry.pack(
            pady=10
        )
 
        def adicionar_peca_editar():
            nome_peca = peca_combo.get()
            quantidade_texto = quantidade_peca_entry.get().strip()
 
            if not nome_peca:
                messagebox.showerror(
                    "Erro",
                    "Selecione uma peça."
                )
                return
 
            try:
                quantidade = int(quantidade_texto)
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Digite uma quantidade válida (número inteiro)."
                )
                return
 
            if quantidade <= 0:
                messagebox.showerror(
                    "Erro",
                    "A quantidade deve ser maior que zero."
                )
                return
 
            peca_id = None
            valor_custo = 0
            valor_venda = 0
            estoque_disponivel = 0
 
            for item in estoque:
                if item[1] == nome_peca:
                    peca_id = item[0]
                    estoque_disponivel = item[2]
                    valor_custo = item[3]
                    valor_venda = item[4]
                    break
 
            if peca_id is None:
                messagebox.showerror(
                    "Erro",
                    "Peça não encontrada no estoque."
                )
                return
 
            pecas_atuais = listar_pecas_ordem_editavel(id_ordem)
            quantidade_ja_na_os = sum(
                qtd for _, p_id, _, qtd, _ in pecas_atuais if p_id == peca_id
            )
 
            if quantidade_ja_na_os + quantidade > estoque_disponivel:
                disponivel_restante = estoque_disponivel - quantidade_ja_na_os
                messagebox.showerror(
                    "Estoque insuficiente",
                    f"Só há {disponivel_restante} unidade(s) disponível(is) "
                    f"de \"{nome_peca}\"."
                )
                return
 
            inserir_ordem_peca(
                id_ordem,
                peca_id,
                nome_peca,
                quantidade,
                valor_custo,
                valor_venda
            )
 
            quantidade_peca_entry.delete(0, "end")
            carregar_pecas_editaveis()
 
        btn_adicionar = ctk.CTkButton(
            scroll,
            text="Adicionar Peça",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=adicionar_peca_editar
        )
        btn_adicionar.pack(
            pady=(10, 20)
        )
 
        def fechar():
            janela.destroy()
            self.mostrar_ordens_de_servico()
 
        btn_fechar = ctk.CTkButton(
            scroll,
            text="Fechar",
            fg_color=COR_FUNDO,
            hover_color="#21262d",
            command=fechar
        )
        btn_fechar.pack(
            pady=10
        )

        janela.protocol("WM_DELETE_WINDOW", fechar)

    def abrir_janela_nova_os(self):
        janela = ctk.CTkToplevel(self)
        janela.title("Nova Ordem de Serviço")
        janela.geometry("700x800")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        scroll = ctk.CTkScrollableFrame(
            janela,
            fg_color="transparent"
        )
        scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20
        )

        clientes = listar_clientes()
        clientes_dict = {}
        veiculos_dict = {}
        nomes_clientes = []

        for cliente in clientes:
            clientes_dict[cliente[1]] = cliente[0]
            nomes_clientes.append(cliente[1])

        cliente_label = ctk.CTkLabel(
            scroll,
            text="Cliente",
            text_color=COR_TEXTO_SECUNDARIO
        )
        cliente_label.pack(
            pady=(0, 0)
        )

        dica_pesquisa_label = ctk.CTkLabel(
            scroll,
            text="💡 Nos campos de Cliente, Veículo e Peça, digite para filtrar a lista",
            font=("Arial", 11),
            text_color=COR_TEXTO_SECUNDARIO
        )

        dica_pesquisa_label.pack(
            pady=(0, 15)
        )

        cliente_combo = ctk.CTkComboBox(
            scroll,
            values=nomes_clientes,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        cliente_combo.pack(
            pady=10
        )

        self.configurar_combobox_pesquisavel(
            cliente_combo,
            nomes_clientes
        )

        veiculo_label = ctk.CTkLabel(
            scroll,
            text="Veículo",
            text_color=COR_TEXTO_SECUNDARIO
        )
        veiculo_label.pack()

        veiculo_combo = ctk.CTkComboBox(
            scroll,
            values=[],
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        veiculo_combo.pack(
            pady=10
        )

        def atualizar_veiculos(nome_cliente):
            cliente_id = None
            for cliente in clientes:
                if cliente[1] == nome_cliente:
                    cliente_id = cliente[0]
                    break

            veiculos_cliente = listar_veiculos_por_cliente(cliente_id)

            veiculos_dict.clear()
            lista_veiculos = []

            for veiculo in veiculos_cliente:
                veiculos_dict[veiculo[2]] = veiculo[0]
                lista_veiculos.append(veiculo[2])

            veiculo_combo.configure(values=lista_veiculos)

            if lista_veiculos:
                veiculo_combo.set(lista_veiculos[0])
            else:
                veiculo_combo.set("")

            self.configurar_combobox_pesquisavel(
                veiculo_combo,
                lista_veiculos
            )


        cliente_combo.configure(
            command=atualizar_veiculos
        )

        if nomes_clientes:
            atualizar_veiculos(nomes_clientes[0])

        descricao_entry = ctk.CTkEntry(
            scroll,
            width=300,
            placeholder_text="Descrição de serviço",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        descricao_entry.pack(
            pady=10
        )

        estoque = listar_estoque()
        nomes_pecas = [item[1] for item in estoque]
        pecas_adicionadas = []

        peca_combo = ctk.CTkComboBox(
            scroll,
            values=nomes_pecas,
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        peca_combo.pack(
            pady=10
        )

        self.configurar_combobox_pesquisavel(
            peca_combo,
            nomes_pecas
        )


        quantidade_peca_entry = ctk.CTkEntry(
            scroll,
            width=300,
            placeholder_text="Quantidade da peça",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        quantidade_peca_entry.pack(
            pady=10
        )

        pecas_textbox = ctk.CTkTextbox(
            scroll,
            width=500,
            height=180,
            fg_color=COR_FUNDO_MENU,
            text_color=COR_TEXTO
        )

        mao_obra_entry = ctk.CTkEntry(
            scroll,
            width=300,
            placeholder_text="Mão de obra",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )

        def atualizar_resumo():
            texto = "Peças adicionadas:\n\n"
            total_pecas = 0

            for (
                peca_id,
                nome_peca,
                quantidade,
                valor_custo,
                valor_venda
            ) in pecas_adicionadas:
                subtotal = float(quantidade) * float(valor_venda)
                total_pecas += subtotal
                texto += (
                    f"- {nome_peca}\n"
                    f"  Qtd: {quantidade}\n"
                    f"  Valor Unitário: R$ {valor_venda:.2f}\n"
                    f"  Subtotal: R$ {subtotal:.2f}\n\n"
                )

            mao_obra_texto = mao_obra_entry.get().strip()
            try:
                mao_obra = (
                    float(mao_obra_texto.replace(",", "."))
                    if mao_obra_texto else 0.0
                )
            except ValueError:
                mao_obra = 0.0

            valor_total = total_pecas + mao_obra

            texto += (
                f"\nTotal das peças: R$ {total_pecas:.2f}"
                f"\n\nTOTAL: R$ {valor_total:.2f}"
            )

            pecas_textbox.configure(state="normal")
            pecas_textbox.delete("1.0", "end")
            pecas_textbox.insert("1.0", texto)
            pecas_textbox.configure(state="disabled")

        def adicionar_peca():
            nome_peca = peca_combo.get()
            quantidade_texto = quantidade_peca_entry.get().strip()

            if not nome_peca:
                messagebox.showerror(
                    "Erro",
                    "Selecione uma peça."
                )
                return

            if quantidade_texto == "":
                messagebox.showerror(
                    "Erro",
                    "Digite a quantidade da peça."
                )
                return

            try:
                quantidade = int(quantidade_texto)
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Digite uma quantidade válida (número inteiro)."
                )
                return

            if quantidade <= 0:
                messagebox.showerror(
                    "Erro",
                    "A quantidade deve ser maior que zero."
                )
                return

            peca_id = None
            valor_custo = 0
            valor_venda = 0
            estoque_disponivel = 0

            for item in estoque:
                if item[1] == nome_peca:
                    peca_id = item[0]
                    estoque_disponivel = item[2]
                    valor_custo = item[3]
                    valor_venda = item[4]
                    break

            if peca_id is None:
                messagebox.showerror(
                    "Erro",
                    "Peça não encontrada no estoque."
                )
                return

            quantidade_ja_adicionada = 0
            for item_adicionado in pecas_adicionadas:
                if item_adicionado[0] == peca_id:
                    quantidade_ja_adicionada += item_adicionado[2]

            if quantidade_ja_adicionada + quantidade > estoque_disponivel:
                disponivel_restante = estoque_disponivel - quantidade_ja_adicionada
                messagebox.showerror(
                    "Estoque insuficiente",
                    f"Só há {disponivel_restante} unidade(s) disponível(is) "
                    f"de \"{nome_peca}\" no estoque."
                )
                return

            pecas_adicionadas.append((
                peca_id,
                nome_peca,
                quantidade,
                valor_custo,
                valor_venda
            ))

            atualizar_resumo()

            quantidade_peca_entry.delete(0, "end")

        btn_adicionar_peca = ctk.CTkButton(
            scroll,
            text="Adicionar Peça",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=adicionar_peca
        )
        btn_adicionar_peca.pack(
            pady=10
        )

        pecas_textbox.pack(
            pady=5
        )
        pecas_textbox.insert("1.0", "Peças adicionadas:")
        pecas_textbox.configure(state="disabled")

        mao_obra_entry.pack(
            pady=10
        )

        status_combo_cadastro = ctk.CTkComboBox(
            scroll,
            values=[
                "Aberta",
                "Em diagnóstico",
                "Aguardando peça",
                "Em execução",
                "Finalizada",
                "Entregue"
            ],
            width=300,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        status_combo_cadastro.pack(
            pady=10
        )
        status_combo_cadastro.set("Aberta")

        def salvar_ordens_de_servico():
            cliente = cliente_combo.get()
            veiculo = veiculo_combo.get()
            descricao = descricao_entry.get().strip()

            if cliente not in clientes_dict:
                messagebox.showerror(
                    "Erro",
                    "Selecione um cliente."
                )
                return

            if veiculo not in veiculos_dict:
                messagebox.showerror(
                    "Erro",
                    "Selecione um veículo."
                )
                return

            if descricao == "":
                messagebox.showerror(
                    "Erro",
                    "Digite a descrição do serviço."
                )
                return

            cliente_id = clientes_dict[cliente]
            veiculo_id = veiculos_dict[veiculo]

            mao_obra_texto = mao_obra_entry.get().strip()
            mao_obra = mao_obra_texto if mao_obra_texto else "0"

            status = status_combo_cadastro.get()

            id_ordem = inserir_ordens_de_servico(
                cliente_id,
                veiculo_id,
                descricao,
                mao_obra,
                status
            )

            for (
                peca_id,
                nome_peca,
                quantidade,
                valor_custo,
                valor_venda
            ) in pecas_adicionadas:
                inserir_ordem_peca(
                    id_ordem,
                    peca_id,
                    nome_peca,
                    quantidade,
                    valor_custo,
                    valor_venda
                )

            messagebox.showinfo(
                "Sucesso",
                "Ordem cadastrada com sucesso!"
            )

            janela.destroy()
            self.mostrar_ordens_de_servico()

        btn_salvar = ctk.CTkButton(
            scroll,
            text="Salvar OS",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_ordens_de_servico
        )
        btn_salvar.pack(
            pady=20
        )

    def mostrar_historico_ordens(self):
        self.limpar_tela()
 
        titulo = ctk.CTkLabel(
            self.content_frame,
            text="Histórico de Ordens de Serviço",
            font=("Arial", 28, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(30, 15)
        )
 
        frame_pesquisa = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        frame_pesquisa.pack(
            pady=10
        )
 
        self.pesquisa_historico_entry = ctk.CTkEntry(
            frame_pesquisa,
            width=350,
            placeholder_text="🔍 Pesquisar por cliente, veículo, placa ou nº da OS...",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        self.pesquisa_historico_entry.pack(
            side="left",
            padx=(0, 10)
        )
        self.pesquisa_historico_entry.bind(
            "<KeyRelease>",
            self.pesquisar_historico
        )
 
        btn_pesquisa_historico = ctk.CTkButton(
            frame_pesquisa,
            text="Pesquisar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=self.pesquisar_historico
        )
        btn_pesquisa_historico.pack(
            side="left"
        )

        self.paginas["historico"] = 1

        self.frame_paginacao_historico = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.frame_paginacao_historico.pack(
            side="bottom",
            pady=10
        )

        self.scroll_historico = ctk.CTkScrollableFrame(
            self.content_frame,
            width=1000,
            height=650,
            fg_color="transparent"
        )
        self.scroll_historico.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.atualizar_lista_historico()

    def carregar_lista_historico(self, ordens, scroll):
        for widget in scroll.winfo_children():
            widget.destroy()
 
        if not ordens:
            vazio = ctk.CTkLabel(
                scroll,
                text="Nenhuma ordem de serviço encontrada.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio.pack(
                pady=20
            )
            return
 
        for ordem in ordens:
            frame_os = ctk.CTkFrame(
                scroll,
                corner_radius=12,
                fg_color=COR_FUNDO_MENU
            )
            frame_os.pack(
                fill="x",
                padx=5,
                pady=10,
                ipadx=10,
                ipady=10
            )
 
            pecas = listar_pecas_ordem(ordem[0])
 
            texto_pecas = ""
            total_pecas = 0
 
            if pecas:
                texto_pecas = "\nPeças:\n"
                for nome_peca, qtd_peca, valor_venda in pecas:
                    subtotal = float(qtd_peca) * float(valor_venda)
                    total_pecas += subtotal
                    texto_pecas += (
                        f"- {nome_peca}\n"
                        f"  Qtd: {qtd_peca}\n"
                        f"  Valor Unit.: R$ {valor_venda:.2f}\n"
                        f"  Subtotal: R$ {subtotal:.2f}\n\n"
                    )
 
            try:
                mao_obra = float(str(ordem[4] or 0).replace(",", "."))
            except ValueError:
                mao_obra = 0
 
            total = total_pecas + mao_obra
 
            texto = (
                f"OS #{ordem[0]}\n"
                f"Cliente: {ordem[1]}\n"
                f"Veículo: {ordem[2]}\n"
                f"Descrição: {ordem[3]}\n"
                f"{texto_pecas}"
                f"\nTotal das peças: R$ {total_pecas:.2f}\n"
                f"Mão de obra: R$ {mao_obra:.2f}\n"
                f"--------------------------------\n"
                f"TOTAL: R$ {total:.2f}\n"
            )
 
            ordem_label = ctk.CTkLabel(
                frame_os,
                text=texto,
                justify="left",
                text_color=COR_TEXTO
            )
            ordem_label.pack(
                anchor="w",
                padx=10,
                pady=2
            )
 
            status_label = ctk.CTkLabel(
                frame_os,
                text="Status: Entregue",
                font=("Arial", 16, "bold"),
                text_color=COR_POSITIVO
            )
            status_label.pack(
                anchor="w",
                padx=10,
                pady=(5, 5)
            )
 
            botoes_frame = ctk.CTkFrame(
                frame_os,
                fg_color="transparent"
            )
            botoes_frame.pack(
                anchor="w",
                padx=10,
                pady=(5, 0)
            )
 
            btn_detalhes = ctk.CTkButton(
                botoes_frame,
                text="Ver Detalhes",
                width=140,
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                command=lambda id_ordem=ordem[0]: self.abrir_janela_detalhes(id_ordem)
            )
            btn_detalhes.pack(
                side="left",
                padx=(0, 8)
            )
 
            btn_pdf = ctk.CTkButton(
                botoes_frame,
                text="📄 Baixar PDF",
                width=140,
                fg_color=COR_FUNDO,
                hover_color="#21262d",
                command=lambda id_ordem=ordem[0]: self.baixar_pdf_os(id_ordem)
            )
            btn_pdf.pack(
                side="left",
                padx=(0, 8)
            )
 
            btn_imprimir = ctk.CTkButton(
                botoes_frame,
                text="🖨️ Imprimir",
                width=140,
                fg_color=COR_FUNDO,
                hover_color="#21262d",
                command=lambda id_ordem=ordem[0]: self.imprimir_os(id_ordem)
            )
            btn_imprimir.pack(
                side="left"
            )

    def atualizar_lista_historico(self):
        self.atualizar_lista_paginada(
            "historico",
            self.pesquisa_historico_entry.get(),
            contar_ordens_entregues_busca,
            buscar_ordens_entregues_paginado,
            self.carregar_lista_historico,
            self.scroll_historico,
            self.frame_paginacao_historico
        )

    def pesquisar_historico(self, event=None):
        self.paginas["historico"] = 1
        self.atualizar_lista_historico()

    def baixar_pdf_os(self, id_ordem):
        try:
            caminho = gerar_pdf_os(id_ordem)
        except Exception as erro:
            messagebox.showerror(
                "Erro ao gerar PDF",
                f"Não foi possível gerar o PDF.\n\n{erro}"
            )
            return

        messagebox.showinfo(
            "PDF gerado",
            f"PDF salvo em:\n{caminho}"
        )

        abrir_pdf(caminho)

    def imprimir_os(self, id_ordem):
        try:
            caminho = gerar_pdf_os(id_ordem)
        except Exception as erro:
            messagebox.showerror(
                "Erro ao gerar PDF",
                f"Não foi possível gerar o PDF.\n\n{erro}"
            )
            return

        abrir_pdf(caminho)

    def abrir_janela_detalhes(self, id_ordem):
        janela = ctk.CTkToplevel(self)
        janela.title(f"OS #{id_ordem}")
        janela.geometry("700x650")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        scroll = ctk.CTkScrollableFrame(
            janela,
            width=650,
            height=550,
            fg_color="transparent"
        )
        scroll.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=15
        )
 
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
            mao_obra = float(str(mao_obra or 0).replace(",", "."))
        except ValueError:
            mao_obra = 0.0
 
        pecas = listar_pecas_ordem(id_ordem)
 
        total_pecas = 0
 
        for _, quantidade, valor_venda in pecas:
            subtotal = float(quantidade) * float(valor_venda)
            total_pecas += subtotal
 
        total = total_pecas + mao_obra
 
        titulo = ctk.CTkLabel(
            scroll,
            text=f"Detalhes da OS #{id_os}",
            font=("Arial", 24, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=20
        )
 
        frame_info = ctk.CTkLabel(
            scroll,
            text=(
                f"Auto Elétrica Emerson\n"
                f"Tel: 📱 (67) 98157-7324"
            ),
            justify="left",
            font=("Arial", 16),
            text_color=COR_TEXTO_SECUNDARIO
        )
        frame_info.pack(
            padx=15,
            pady=15
        )
 
        frame_cliente = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            fg_color=COR_FUNDO_MENU
        )
        frame_cliente.pack(
            fill="x",
            padx=20,
            pady=10
        )
 
        cliente_label = ctk.CTkLabel(
            frame_cliente,
            text=(
                f"Cliente: {cliente}\n"
                f"Veículo: {veiculo}"
            ),
            justify="left",
            font=("Arial", 16),
            text_color=COR_TEXTO
        )
        cliente_label.pack(
            anchor="w",
            padx=15,
            pady=15
        )
 
        frame_servico = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            fg_color=COR_FUNDO_MENU
        )
        frame_servico.pack(
            fill="x",
            padx=20,
            pady=10
        )
 
        titulo_servico = ctk.CTkLabel(
            frame_servico,
            text="Serviço realizado",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo_servico.pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )
 
        descricao_label = ctk.CTkLabel(
            frame_servico,
            text=(
                f"Descrição:\n{descricao}\n\n"
                f"Status: {status}\n\n"
                f"Forma de pagamento: {forma_pagamento or 'Não informado'}\n"
                f"Status do pagamento: {status_pagamento or 'Não informado'}\n\n"
                f"Data de abertura: {data_abertura}\n"
                f"Data de entrega: {data_entrega or 'Ainda não entregue'}\n"
                f"Data do pagamento: {data_pagamento or 'Ainda não recebido'}"
            ),
            justify="left",
            text_color=COR_TEXTO
        )
        descricao_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 10)
        )
 
        frame_pecas = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            fg_color=COR_FUNDO_MENU
        )
        frame_pecas.pack(
            fill="x",
            padx=20,
            pady=10
        )
 
        titulo_pecas = ctk.CTkLabel(
            frame_pecas,
            text="Peças utilizadas",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo_pecas.pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )
 
        if not pecas:
            sem_pecas_label = ctk.CTkLabel(
                frame_pecas,
                text="Nenhuma peça utilizada nesta OS.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            sem_pecas_label.pack(
                anchor="w",
                padx=15,
                pady=(0, 10)
            )
        else:
            for nome_peca, quantidade, valor_venda in pecas:
                subtotal = float(quantidade) * float(valor_venda)
 
                peca_label = ctk.CTkLabel(
                    frame_pecas,
                    text=(
                        f"{nome_peca}\n"
                        f"Qtd: {quantidade}\n"
                        f"Valor Unit.: R$ {valor_venda:.2f}\n"
                        f"Subtotal: R$ {subtotal:.2f}"
                    ),
                    justify="left",
                    text_color=COR_TEXTO
                )
                peca_label.pack(
                    anchor="w",
                    padx=15,
                    pady=5
                )
 
        frame_valores = ctk.CTkFrame(
            scroll,
            corner_radius=12,
            fg_color=COR_FUNDO_MENU
        )
        frame_valores.pack(
            fill="x",
            padx=20,
            pady=10
        )
 
        titulo_valores = ctk.CTkLabel(
            frame_valores,
            text="Valores",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo_valores.pack(
            anchor="w",
            padx=15,
            pady=(10, 5)
        )
 
        valores_label = ctk.CTkLabel(
            frame_valores,
            text=(
                f"Total das peças: R$ {total_pecas:.2f}\n\n"
                f"Mão de obra: R$ {mao_obra:.2f}\n\n"
                f"TOTAL: R$ {total:.2f}"
            ),
            justify="left",
            font=("Arial", 15, "bold"),
            text_color=COR_POSITIVO
        )
        valores_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 15)
        )
 
        botoes_frame = ctk.CTkFrame(
            scroll,
            fg_color="transparent"
        )
        botoes_frame.pack(
            pady=20
        )
 
        btn_pdf = ctk.CTkButton(
            botoes_frame,
            text="📄 Baixar PDF",
            width=150,
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=lambda: self.baixar_pdf_os(id_ordem)
        )
        btn_pdf.pack(
            side="left",
            padx=(0, 10)
        )
 
        btn_imprimir = ctk.CTkButton(
            botoes_frame,
            text="🖨️ Imprimir",
            width=150,
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=lambda: self.imprimir_os(id_ordem)
        )
        btn_imprimir.pack(
            side="left"
        )

    def mostrar_estoque(self):

        self.limpar_tela()

        label = ctk.CTkLabel(
            self.content_frame,
            text="Controle de Estoque",
            font=("Arial", 30, "bold")
        )

        label.pack(
            pady=40
        )

        nome_entry = ctk.CTkEntry(
            self.content_frame,
            width=300,
            placeholder_text="Nome da peça",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )


        nome_entry.pack(pady=10)

        quantidade_entry = ctk.CTkEntry(
            self.content_frame,
            width=300,
            placeholder_text="Quantidade",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )


        quantidade_entry.pack(pady=10)

        valor_custo_entry = ctk.CTkEntry(
            self.content_frame,
            width=300,
            placeholder_text="Valor de custo",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )


        valor_custo_entry.pack(pady=10)


        valor_venda_entry = ctk.CTkEntry(
            self.content_frame,
            width=300,
            placeholder_text="Valor de venda",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )


        valor_venda_entry.pack(pady=10)


        estoque_minimo_entry = ctk.CTkEntry(
            self.content_frame,
            width=300,
            placeholder_text="Estoque mínimo",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )


        estoque_minimo_entry.pack(pady=10)


        def salvar_estoque():

            nome = nome_entry.get()

            quantidade = quantidade_entry.get()

            valor_custo = valor_custo_entry.get().replace(",", ".")

            valor_venda = valor_venda_entry.get().replace(",", ".")

            estoque_minimo = estoque_minimo_entry.get()

            inserir_estoque(
                nome,
                quantidade,
                valor_custo,
                valor_venda,
                estoque_minimo
            )

            nome_entry.delete(0, "end")
            quantidade_entry.delete(0, "end")
            valor_custo_entry.delete(0, "end")
            valor_venda_entry.delete(0, "end")
            estoque_minimo_entry.delete(0, "end")

            self.mostrar_estoque()


        btn_salvar = ctk.CTkButton(
            self.content_frame,
            text="Salvar peça",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_estoque
        )

        btn_salvar.pack(pady=20)

        titulo_lista = ctk.CTkLabel(
            self.content_frame,
            text="Peças Cadastradas",
            font=("Arial", 20, "bold")
        )

        titulo_lista.pack(pady=20)

        frame_pesquisa = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )

        frame_pesquisa.pack(pady=10)

        self.pesquisa_peca_entry = ctk.CTkEntry(
            frame_pesquisa,
            width=300,
            placeholder_text="🔍 Pesquisar peça...",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )

        self.pesquisa_peca_entry.pack(
            side="left",
            padx=(0, 10)
        )

        self.pesquisa_peca_entry.bind(
            "<KeyRelease>",
            self.pesquisar_peca
        )

        btn_pesquisa_peca = ctk.CTkButton(
            frame_pesquisa,
            text="Pesquisar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=self.pesquisar_peca
        )

        btn_pesquisa_peca.pack(
            side="left"
        )

        self.paginas["estoque"] = 1

        self.frame_paginacao_estoque = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.frame_paginacao_estoque.pack(
            side="bottom",
            pady=10
        )

        self.scroll = ctk.CTkScrollableFrame(
            self.content_frame,
            width=1000,
            height=800,
            fg_color="transparent"
        )

        self.scroll.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        self.atualizar_lista_estoque()

    def carregar_lista_estoque(self, estoque, scroll):

        for item in estoque:

            valor_formatado = f"{float(item[3]):.2f}".replace(".", ",")

            texto = (
                f"{item[1]}\n"
                f"Quantidade: {item[2]}\n"
                f"Valor custo: R$ {valor_formatado}"
            )

            card = ctk.CTkFrame(
                scroll,
                fg_color=COR_FUNDO_MENU,
                corner_radius=12,
                border_width=1,
                border_color="#444444"
            )

            card.pack(
                fill="x",
                padx=10,
                pady=8
            )

            info_frame = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            info_frame.pack(
                side="left",
                fill="both",
                expand=True,
                padx=20,
                pady=12
            )

            texto_label = ctk.CTkLabel(
                info_frame,
                text=texto,
                justify="left"
            )

            texto_label.pack(anchor="w")

            botoes_frame = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            botoes_frame.pack(
                side="right",
                pady=(0,15)
            )

            btn_alterar = ctk.CTkButton(
                botoes_frame,
                text="Alterar",
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                width=150,
                command=lambda id=item[0]: self.adicionar_estoque(id)
            )

            btn_alterar.pack(
                side="left",
                padx=20,
                pady=(0,10)
            )

            btn_apagar = ctk.CTkButton(
                botoes_frame,
                text="Apagar",
                fg_color=COR_ALERTA,
                hover_color="#c93c36",
                width=150,
                command=lambda id=item[0]: self.apagar_peca(id)
            )

            btn_apagar.pack(
                side="left",
                padx=20,
                pady=(0,10),
            )


    def adicionar_estoque(self, id_peca):

        janela = ctk.CTkToplevel(self)
        janela.title("Movimentar Estoque")
        janela.geometry("700x350")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        peca = buscar_peca(id_peca)

        nome = peca[1]

        quantidade_atual = int(peca[2])

        tipo_movimentacao = ctk.StringVar(
            value="Entrada"
        )

        titulo = ctk.CTkLabel(
            janela,
            text=f"Movimentar Estoque\n\n{nome}",
            font=("Arial", 20, "bold")
        )

        titulo.pack(pady=20)

        quantidade_label = ctk.CTkLabel(
            janela,
            text=f"Quantidade atual: {quantidade_atual}"
        )

        quantidade_label.pack(pady=5)

        radio_entrada = ctk.CTkRadioButton(
            janela,
            text="Entrada",
            variable=tipo_movimentacao,
            value="Entrada"
        )

        radio_entrada.pack(
            pady=10
        )

        radio_saida = ctk.CTkRadioButton(
            janela,
            text="Saída",
            variable=tipo_movimentacao,
            value="Saída"
        )

        radio_saida.pack(
            pady=10
        )

        quantidade_entry = ctk.CTkEntry(
            janela,
            width=300,
            placeholder_text="Quantidade a Movimentar",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )

        quantidade_entry.pack(pady=10)


        def salvar():

            tipo = tipo_movimentacao.get()

            try:

                quantidade_recebida = int(
                    quantidade_entry.get()
                )

            except ValueError:

                messagebox.showerror(
                    "Erro",
                    "Digite uma quantidade válida."
                )

                return

            if tipo == "Entrada":
                nova_quantidade = (
                    quantidade_atual +
                    quantidade_recebida
                )

            else:

                if quantidade_recebida > quantidade_atual:

                    messagebox.showerror(
                        "Erro",
                        "Estoque insuficiente."
                    )


                    return

                nova_quantidade = (
                    quantidade_atual -
                    quantidade_recebida
                )

            atualizar_quantidade_estoque(
                id_peca,
                nova_quantidade
            )

            messagebox.showinfo(
               "Sucesso",
               "Estoque atualizado com sucesso!"
            )

            janela.destroy()

            self.mostrar_estoque()

        btn_salvar = ctk.CTkButton(
            janela,
            text="Salvar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar
        )

        btn_salvar.pack(pady=20)

    def apagar_peca(self, id_peca):

        confirmar = messagebox.askyesno(
            "Confirmar exclusão",
            "Deseja realmente excluir esta peça do estoque?\n\n"
            "Esta ação não poderá ser desfeita."
        )

        if not confirmar:

            return

        resultado = apagar_peca_estoque(id_peca)

        if resultado:

            messagebox.showinfo(
                "Peça apagada",
                "Peça removida com sucesso!"

            )

            self.mostrar_estoque()

        else:

            messagebox.showerror(
               "Não foi possível excluir esta peça.",
               "Ela já foi utilizada em uma Ordem de Serviço."
            )

    def atualizar_lista_estoque(self):
        self.atualizar_lista_paginada(
            "estoque",
            self.pesquisa_peca_entry.get(),
            contar_pecas_busca,
            listar_pecas_paginado,
            self.carregar_lista_estoque,
            self.scroll,
            self.frame_paginacao_estoque
        )

    def pesquisar_peca(self, event=None):
        self.paginas["estoque"] = 1
        self.atualizar_lista_estoque()

    def mostrar_financeiro(self, aba_inicial="Resumo"):
        self.limpar_tela()
 
        label = ctk.CTkLabel(
            self.content_frame,
            text="Financeiro",
            font=("Arial", 30, "bold"),
            text_color=COR_TEXTO
        )
        label.pack(
            pady=30
        )
 
        tabview = ctk.CTkTabview(
            self.content_frame,
            width=1100,
            height=750,
            fg_color=COR_FUNDO_MENU,
            segmented_button_fg_color=COR_FUNDO,
            segmented_button_selected_color=COR_AZUL_ATIVO,
            segmented_button_selected_hover_color="#1a5fc4",
            segmented_button_unselected_color=COR_FUNDO,
            text_color=COR_TEXTO
        )
        tabview.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )
 
        tabview.add("Resumo")
        tabview.add("Despesas")
        tabview.add("Fiados")
        tabview.add("Fluxo de Caixa")
 
        self.construir_aba_resumo(
            tabview.tab("Resumo")
        )
        self.construir_aba_despesas(
            tabview.tab("Despesas")
        )
        self.construir_aba_fiados(
            tabview.tab("Fiados")
        )
        self.construir_aba_fluxo_caixa(
            tabview.tab("Fluxo de Caixa")
        )
 
        tabview.set(aba_inicial)

    # ------------------------------------------------------------
    # ABA RESUMO
    # ------------------------------------------------------------
    def construir_aba_resumo(self, aba):
        hoje = datetime.datetime.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
 
        lucro_dia = calcular_lucro_dia()
        lucro_mes = calcular_lucro_mes()
        receita_dia = calcular_receita(hoje, hoje)
        despesa_dia = calcular_despesa(hoje, hoje)
        receita_mes = calcular_receita(primeiro_dia_mes, hoje)
        despesa_mes = calcular_despesa(primeiro_dia_mes, hoje)
        formas_mes = resumo_formas_pagamento(primeiro_dia_mes, hoje)
 
        frame_cards = ctk.CTkFrame(
            aba,
            fg_color="transparent"
        )
        frame_cards.pack(
            pady=20
        )
 
        self.criar_card(
            frame_cards,
            "Lucro do Dia",
            f"R$ {lucro_dia:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            cor_valor=COR_POSITIVO if lucro_dia >= 0 else COR_ALERTA
        )
        self.criar_card(
            frame_cards,
            "Lucro do Mês",
            f"R$ {lucro_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            cor_valor=COR_POSITIVO if lucro_mes >= 0 else COR_ALERTA
        )
        self.criar_card(
            frame_cards,
            "Receita do Dia",
            f"R$ {receita_dia:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        self.criar_card(
            frame_cards,
            "Despesa do Dia",
            f"R$ {despesa_dia:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
 
        frame_cards_2 = ctk.CTkFrame(
            aba,
            fg_color="transparent"
        )
        frame_cards_2.pack(
            pady=10
        )
 
        self.criar_card(
            frame_cards_2,
            "Receita do Mês",
            f"R$ {receita_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        self.criar_card(
            frame_cards_2,
            "Despesa do Mês",
            f"R$ {despesa_mes:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        titulo_formas = ctk.CTkLabel(
            aba,
            text="Recebimentos do mês por forma de pagamento",
            font=("Arial", 16, "bold"),
            text_color=COR_TEXTO
        )
        titulo_formas.pack(
            pady=(30, 10)
        )
 
        if not formas_mes:
            vazio_label = ctk.CTkLabel(
                aba,
                text="Nenhum recebimento registrado neste mês.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio_label.pack(
                pady=10
            )
        else:
            frame_formas = ctk.CTkScrollableFrame(
                aba,
                fg_color="transparent"
            )

            frame_formas.pack(
                fill="both",
                expand=True,
                padx=20,
                pady=10
            )

            for forma, valor in formas_mes.items():
                if forma == "Não informado":
                    continue

                valor_formatado = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                item_forma = ctk.CTkFrame(
                    frame_formas,
                    corner_radius=12,
                    fg_color=COR_FUNDO_MENU,
                    border_width=1,
                    border_color=COR_TEXTO_SECUNDARIO
                )
                item_forma.pack(
                    fill="x",
                    padx=5,
                    pady=6
                )
 
                forma_label = ctk.CTkLabel(
                    item_forma,
                    text=forma,
                    text_color=COR_TEXTO,
                    anchor="w"
                )
                forma_label.pack(
                    side="left",
                    padx=15,
                    pady=12
                )
 
                valor_label = ctk.CTkLabel(
                    item_forma,
                    text=valor_formatado,
                    font=("Arial", 13, "bold"),
                    text_color=COR_TEXTO,
                    anchor="e"
                )
                valor_label.pack(
                    side="right",
                    padx=15,
                    pady=12
                )


    # ------------------------------------------------------------
    # ABA DESPESAS
    # ------------------------------------------------------------
    def construir_aba_despesas(self, aba):
        card_formulario = ctk.CTkFrame(
            aba,
            corner_radius=15,
            fg_color=COR_FUNDO_MENU
        )
        card_formulario.pack(
            padx=10,
            pady=15,
            fill="x"
        )
 
        categoria_combo = ctk.CTkComboBox(
            card_formulario,
            width=300,
            values=CATEGORIAS_DESPESA,
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        categoria_combo.set("Fornecedor")
        categoria_combo.pack(
            pady=(20, 10)
        )
 
        descricao_entry = ctk.CTkEntry(
            card_formulario,
            width=300,
            placeholder_text="Descrição (opcional)",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        descricao_entry.pack(
            pady=10
        )
 
        valor_entry = ctk.CTkEntry(
            card_formulario,
            width=300,
            placeholder_text="Valor",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        valor_entry.pack(
            pady=10
        )
 
        forma_pagamento_combo = ctk.CTkComboBox(
            card_formulario,
            width=300,
            values=FORMAS_PAGAMENTO_DESPESA,
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        forma_pagamento_combo.set("Dinheiro")
        forma_pagamento_combo.pack(
            pady=10
        )
 
        def salvar_despesa():
            categoria = categoria_combo.get()
            descricao = descricao_entry.get()
            forma_pagamento = forma_pagamento_combo.get()
 
            try:
                valor = float(
                    valor_entry.get().replace(",", ".")
                )
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Digite um valor válido."
                )
                return
 
            if valor <= 0:
                messagebox.showerror(
                    "Erro",
                    "O valor deve ser maior que zero."
                )
                return
 
            inserir_despesa(
                categoria,
                descricao,
                valor,
                forma_pagamento
            )
 
            descricao_entry.delete(0, "end")
            valor_entry.delete(0, "end")
 
            messagebox.showinfo(
                "Sucesso",
                "Despesa lançada com sucesso!"
            )
 
            carregar_lista_despesas()
 
        btn_salvar = ctk.CTkButton(
            card_formulario,
            text="Lançar Despesa",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_despesa
        )
        btn_salvar.pack(
            pady=(15, 25)
        )
 
        titulo_lista = ctk.CTkLabel(
            aba,
            text="Despesas Lançadas",
            font=("Arial", 16, "bold"),
            text_color=COR_TEXTO
        )
        titulo_lista.pack(
            pady=(10, 10)
        )
 
        scroll_despesas = ctk.CTkScrollableFrame(
            aba,
            fg_color="transparent"
        )
        scroll_despesas.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )
 
        def carregar_lista_despesas():
            for widget in scroll_despesas.winfo_children():
                widget.destroy()
 
            despesas = listar_despesas()
 
            if not despesas:
                vazio_label = ctk.CTkLabel(
                    scroll_despesas,
                    text="Nenhuma despesa lançada ainda.",
                    text_color=COR_TEXTO_SECUNDARIO
                )
                vazio_label.pack(
                    pady=20
                )
                return
 
            for despesa in despesas:
                id_despesa, categoria, descricao, valor, forma_pagamento, data = despesa
 
                card_despesa = ctk.CTkFrame(
                    scroll_despesas,
                    corner_radius=10,
                    fg_color=COR_FUNDO_MENU
                )
                card_despesa.pack(
                    fill="x",
                    padx=5,
                    pady=6
                )
 
                valor_formatado = f"{valor:.2f}".replace(".", ",")
 
                categoria_label = ctk.CTkLabel(
                    card_despesa,
                    text=f"{categoria} - R$ {valor_formatado}",
                    font=("Arial", 14, "bold"),
                    text_color=COR_ALERTA,
                    anchor="w"
                )
                categoria_label.pack(
                    anchor="w",
                    padx=20,
                    pady=(12, 0)
                )
 
                descricao_label = ctk.CTkLabel(
                    card_despesa,
                    text=descricao or "-",
                    font=("Arial", 12),
                    text_color=COR_TEXTO,
                    anchor="w"
                )
                descricao_label.pack(
                    anchor="w",
                    padx=20
                )
 
                info_label = ctk.CTkLabel(
                    card_despesa,
                    text=f"Forma: {forma_pagamento} | Data: {data}",
                    font=("Arial", 12),
                    text_color=COR_TEXTO_SECUNDARIO,
                    anchor="w"
                )
                info_label.pack(
                    anchor="w",
                    padx=20,
                    pady=(0, 12)
                )
 
        carregar_lista_despesas()

    def construir_aba_fiados(self, aba):
        titulo = ctk.CTkLabel(
            aba,
            text="Ordens de Serviço em Fiado",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=(20, 5)
        )
 
        fiados = listar_os_pendentes_fiado()
 
        total_a_receber = sum(item[4] for item in fiados)
        total_fmt = f"R$ {total_a_receber:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
 
        total_label = ctk.CTkLabel(
            aba,
            text=f"Total a Receber: {total_fmt}",
            font=("Arial", 16, "bold"),
            text_color=COR_ALERTA
        )
        total_label.pack(
            pady=(0, 15)
        )
 
        scroll_fiados = ctk.CTkScrollableFrame(
            aba,
            fg_color="transparent"
        )
        scroll_fiados.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )
 
        if not fiados:
            vazio_label = ctk.CTkLabel(
                scroll_fiados,
                text="Nenhuma OS pendente em fiado.",
                text_color=COR_TEXTO_SECUNDARIO
            )
            vazio_label.pack(
                pady=20
            )
            return
 
        for id_ordem, nome_cliente, valor_total, valor_pago, valor_restante, dias_pendente in fiados:
            card = ctk.CTkFrame(
                scroll_fiados,
                corner_radius=12,
                fg_color=COR_FUNDO
            )
            card.pack(
                fill="x",
                padx=5,
                pady=8
            )
 
            valor_total_fmt = f"{valor_total:.2f}".replace(".", ",")
            valor_pago_fmt = f"{valor_pago:.2f}".replace(".", ",")
            valor_restante_fmt = f"{valor_restante:.2f}".replace(".", ",")
 
            if dias_pendente is None:
                dias_texto = "Data de entrega não registrada"
            else:
                dias_texto = f"{dias_pendente} dia(s) pendente"
 
            cabecalho_label = ctk.CTkLabel(
                card,
                text=f"OS #{id_ordem} - {nome_cliente}",
                font=("Arial", 15, "bold"),
                text_color=COR_TEXTO,
                anchor="w"
            )
            cabecalho_label.pack(
                anchor="w",
                padx=20,
                pady=(15, 0)
            )
 
            dias_label = ctk.CTkLabel(
                card,
                text=dias_texto,
                font=("Arial", 12),
                text_color=COR_TEXTO_SECUNDARIO,
                anchor="w"
            )
            dias_label.pack(
                anchor="w",
                padx=20
            )
 
            valores_label = ctk.CTkLabel(
                card,
                text=(
                    f"Total: R$ {valor_total_fmt}   |   "
                    f"Pago: R$ {valor_pago_fmt}   |   "
                    f"Restante: R$ {valor_restante_fmt}"
                ),
                font=("Arial", 13, "bold"),
                text_color=COR_ALERTA,
                anchor="w"
            )
            valores_label.pack(
                anchor="w",
                padx=20,
                pady=(6, 0)
            )
 
            if valor_total > 0:
                progresso = ctk.CTkProgressBar(
                    card,
                    width=400,
                    progress_color=COR_POSITIVO,
                    fg_color=COR_FUNDO_MENU
                )
                progresso.set(min(valor_pago / valor_total, 1.0))
                progresso.pack(
                    anchor="w",
                    padx=20,
                    pady=(10, 5)
                )
 
            pagamentos = listar_pagamentos_fiado(id_ordem)
 
            if pagamentos:
                linhas_historico = []
                for _, valor, forma, data in pagamentos:
                    valor_fmt = f"{valor:.2f}".replace(".", ",")
                    linhas_historico.append(
                        f"  R$ {valor_fmt} ({forma or '-'}) em {data}"
                    )
 
                historico_texto = "Pagamentos registrados:\n" + "\n".join(linhas_historico)
 
                historico_label = ctk.CTkLabel(
                    card,
                    text=historico_texto,
                    font=("Arial", 11),
                    text_color=COR_TEXTO_SECUNDARIO,
                    justify="left",
                    anchor="w"
                )
                historico_label.pack(
                    anchor="w",
                    padx=20,
                    pady=(5, 0)
                )
 
            botoes_frame = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            botoes_frame.pack(
                anchor="w",
                padx=20,
                pady=15
            )
 
            btn_pagamento = ctk.CTkButton(
                botoes_frame,
                text="Registrar Pagamento",
                width=170,
                fg_color=COR_AZUL_ATIVO,
                hover_color="#1a5fc4",
                command=lambda id_ordem=id_ordem, restante=valor_restante:
                    self.abrir_janela_pagamento_fiado(id_ordem, restante)
            )
            btn_pagamento.pack(
                side="left",
                padx=(0, 10)
            )
 
            btn_quitar = ctk.CTkButton(
                botoes_frame,
                text="Quitar Tudo",
                width=140,
                fg_color=COR_POSITIVO,
                hover_color="#2ea043",
                command=lambda id_ordem=id_ordem, restante=valor_restante:
                    self.abrir_janela_pagamento_fiado(id_ordem, restante, valor_inicial=restante)
            )
            btn_quitar.pack(
                side="left"
            )

    def abrir_janela_pagamento_fiado(self, id_ordem, valor_restante, valor_inicial=None):
        janela = ctk.CTkToplevel(self)
        janela.title("Registrar Pagamento")
        janela.geometry("400x420")
        janela.configure(fg_color=COR_FUNDO)
        self.preparar_janela(janela)

        titulo = ctk.CTkLabel(
            janela,
            text=f"OS #{id_ordem}",
            font=("Arial", 18, "bold"),
            text_color=COR_TEXTO
        )
        titulo.pack(
            pady=20
        )
 
        restante_fmt = f"{valor_restante:.2f}".replace(".", ",")
        restante_label = ctk.CTkLabel(
            janela,
            text=f"Valor restante: R$ {restante_fmt}",
            font=("Arial", 14),
            text_color=COR_ALERTA
        )
        restante_label.pack(
            pady=(0, 15)
        )
 
        valor_entry = ctk.CTkEntry(
            janela,
            width=250,
            placeholder_text="Valor pago agora",
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        if valor_inicial is not None:
            valor_entry.insert(0, f"{valor_inicial:.2f}".replace(".", ","))
        valor_entry.pack(
            pady=10
        )
 
        forma_label = ctk.CTkLabel(
            janela,
            text="Forma de pagamento",
            text_color=COR_TEXTO_SECUNDARIO
        )
        forma_label.pack(
            pady=(10, 5)
        )
 
        forma_combo = ctk.CTkComboBox(
            janela,
            width=250,
            values=FORMAS_PAGAMENTO_DESPESA,
            fg_color=COR_FUNDO_MENU,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_AZUL_ATIVO,
            text_color=COR_TEXTO
        )
        forma_combo.set("Dinheiro")
        forma_combo.pack(
            pady=5
        )
 
        def salvar_pagamento():
            valor_texto = valor_entry.get().strip()
            forma_pagamento = forma_combo.get()
 
            try:
                valor = float(valor_texto.replace(",", "."))
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Digite um valor válido."
                )
                return
 
            if valor <= 0:
                messagebox.showerror(
                    "Erro",
                    "O valor deve ser maior que zero."
                )
                return
 
            if valor > valor_restante + 0.01:
                messagebox.showerror(
                    "Erro",
                    f"O valor não pode ser maior que o restante "
                    f"(R$ {restante_fmt})."
                )
                return
 
            quitado = registrar_pagamento_fiado(
                id_ordem,
                valor,
                forma_pagamento
            )
 
            janela.destroy()
 
            if quitado:
                messagebox.showinfo(
                    "OS quitada!",
                    "Pagamento registrado e a OS foi totalmente quitada!"
                )
            else:
                messagebox.showinfo(
                    "Pagamento registrado",
                    "Pagamento parcial registrado com sucesso."
                )
 
            self.mostrar_financeiro(aba_inicial="Fiados")
 
        btn_salvar = ctk.CTkButton(
            janela,
            text="Salvar Pagamento",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=salvar_pagamento
        )
        btn_salvar.pack(
            pady=20
        )

    def construir_aba_fluxo_caixa(self, aba):
        frame_filtro = ctk.CTkFrame(
            aba,
            fg_color="transparent"
        )
        frame_filtro.pack(
            pady=20
        )
 
        hoje = datetime.datetime.now().date()
        primeiro_dia_mes = hoje.replace(day=1)
 
        data_inicio_entry = ctk.CTkEntry(
            frame_filtro,
            width=150,
            placeholder_text="Início (dd/mm/aaaa)",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        data_inicio_entry.insert(0, primeiro_dia_mes.strftime("%d/%m/%Y"))
        data_inicio_entry.pack(
            side="left",
            padx=10
        )
 
        data_fim_entry = ctk.CTkEntry(
            frame_filtro,
            width=150,
            placeholder_text="Fim (dd/mm/aaaa)",
            fg_color=COR_FUNDO,
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        data_fim_entry.insert(0, hoje.strftime("%d/%m/%Y"))
        data_fim_entry.pack(
            side="left",
            padx=10
        )
 
        scroll_fluxo = ctk.CTkScrollableFrame(
            aba,
            fg_color="transparent"
        )
 
        def consultar_fluxo():
            try:
                data_inicio = datetime.datetime.strptime(
                    data_inicio_entry.get(),
                    "%d/%m/%Y"
                ).date()
                data_fim = datetime.datetime.strptime(
                    data_fim_entry.get(),
                    "%d/%m/%Y"
                ).date()
            except ValueError:
                messagebox.showerror(
                    "Erro",
                    "Digite as datas no formato dd/mm/aaaa."
                )
                return
 
            if data_inicio > data_fim:
                messagebox.showerror(
                    "Erro",
                    "A data de início não pode ser depois da data de fim."
                )
                return
 
            for widget in scroll_fluxo.winfo_children():
                widget.destroy()
 
            fluxo = calcular_fluxo_caixa(data_inicio, data_fim)
 
            if not fluxo:
                vazio = ctk.CTkLabel(
                    scroll_fluxo,
                    text="Nenhum dado no período selecionado.",
                    text_color=COR_TEXTO_SECUNDARIO
                )
                vazio.pack(
                    pady=20
                )
                return
 
            for dia in fluxo:
                card_dia = ctk.CTkFrame(
                    scroll_fluxo,
                    corner_radius=10,
                    fg_color=COR_FUNDO
                )
                card_dia.pack(
                    fill="x",
                    padx=5,
                    pady=5
                )
 
                data_formatada = dia["data"].strftime("%d/%m/%Y")
 
                data_label = ctk.CTkLabel(
                    card_dia,
                    text=data_formatada,
                    font=("Arial", 13, "bold"),
                    text_color=COR_TEXTO,
                    width=110,
                    anchor="w"
                )
                data_label.pack(
                    side="left",
                    padx=15,
                    pady=10
                )
 
                entradas_fmt = f"R$ {dia['entradas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                saidas_fmt = f"R$ {dia['saidas']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
                saldo_fmt = f"R$ {dia['saldo']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
 
                entradas_label = ctk.CTkLabel(
                    card_dia,
                    text=f"Entradas: {entradas_fmt}",
                    text_color=COR_POSITIVO,
                    width=200,
                    anchor="w"
                )
                entradas_label.pack(
                    side="left",
                    padx=10
                )
 
                saidas_label = ctk.CTkLabel(
                    card_dia,
                    text=f"Saídas: {saidas_fmt}",
                    text_color=COR_ALERTA,
                    width=180,
                    anchor="w"
                )
                saidas_label.pack(
                    side="left",
                    padx=10
                )
 
                cor_saldo = COR_POSITIVO if dia["saldo"] >= 0 else COR_ALERTA

                saldo_label = ctk.CTkLabel(
                    card_dia,
                    text=f"Saldo: {saldo_fmt}",
                    font=("Arial", 12, "bold"),
                    text_color=cor_saldo,
                    width=180,
                    anchor="w"
                )
                saldo_label.pack(
                    side="left",
                    padx=10
                )

        btn_consultar = ctk.CTkButton(
            frame_filtro,
            text="Consultar",
            fg_color=COR_AZUL_ATIVO,
            hover_color="#1a5fc4",
            command=consultar_fluxo
        )
        btn_consultar.pack(
            side="left",
            padx=10
        )

        scroll_fluxo.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        consultar_fluxo()


if __name__ == "__main__":
    app = AutoEletricaApp()
    app.mainloop()

