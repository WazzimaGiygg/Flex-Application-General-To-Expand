import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance, ImageWin
import os
import json
import pickle
import tempfile
import datetime
import math

# Para impressão (Windows)
try:
    import win32print
    import win32ui
    from PIL import ImageWin
    IMPRESSAO_DISPONIVEL = True
except ImportError:
    IMPRESSAO_DISPONIVEL = False
    print("Bibliotecas de impressão não disponíveis. Instale pywin32 para suporte à impressão.")

class EditorImagem:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imagens Python - PaintWazzima")
        self.root.geometry("1200x800")
        
        # Tamanho máximo de imagem (em pixels) para evitar sobrecarga de memória
        self.MAX_LARGURA = 5000
        self.MAX_ALTURA = 5000
        self.MAX_MEGAPIXELS = 20  # Limite de 20 megapixels
        
        # Variáveis para armazenar as imagens
        self.imagem_original = None
        self.imagem_editada = None
        self.imagem_tk = None
        self.current_file = None
        self.project_file = None  # Arquivo de projeto .paintwazzima
        self.houve_alteracao = False  # Flag para controle de alterações não salvas
        
        # Histórico para desfazer/refazer
        self.historico = []
        self.historico_index = -1
        self.MAX_HISTORICO = 20
        
        # Metadados do projeto
        self.project_metadata = {
            "nome": "Novo Projeto",
            "data_criacao": None,
            "data_modificacao": None,
            "autor": "Usuário",
            "descricao": "",
            "versoes": []  # Histórico de versões
        }
        
        # Variáveis para ferramentas de desenho
        self.ferramenta_atual = "selecao"
        self.cor_atual = "#000000"
        self.tamanho_pincel = 5
        self.ultimo_x = None
        self.ultimo_y = None
        self.desenho_ativo = False
        
        # Variáveis para seleção
        self.selecao_ativa = False
        self.selecao_inicio = None
        self.selecao_fim = None
        self.area_selecionada = None
        self.rect_selecao = None
        
        # Variáveis para zoom
        self.fator_zoom = 1.0
        self.zoom_minimo = 0.1
        self.zoom_maximo = 5.0
        self.offset_x = 0
        self.offset_y = 0
        self.arrastando = False
        self.ultimo_pan_x = 0
        self.ultimo_pan_y = 0
        
        # Configurações da ferramenta
        self.configuracoes = {
            "ultima_pasta": os.path.expanduser("~"),
            "qualidade_impressao": 300,  # DPI
            "formato_papel": "A4",
            "orientacao": "Retrato",
            "margens": (1, 1, 1, 1)  # cm: esquerda, direita, topo, base
        }
        
        # Variável para cor de fundo
        self.fundo_cor = "#FFFFFF"
        
        self.setup_ui()
        self.setup_bindings()
        self.protocolo_janela()
    
    def protocolo_janela(self):
        """Configurar protocolo de fechamento da janela"""
        self.root.protocol("WM_DELETE_WINDOW", self.sair_aplicacao)
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barra de menu
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Submenu Novo
        novo_menu = tk.Menu(file_menu, tearoff=0)
        novo_menu.add_command(label="Nova Imagem", command=self.nova_imagem, accelerator="Ctrl+N")
        novo_menu.add_command(label="Novo Projeto", command=self.novo_projeto)
        file_menu.add_cascade(label="Novo", menu=novo_menu)
        
        file_menu.add_command(label="Abrir Imagem...", command=self.abrir_imagem, accelerator="Ctrl+O")
        file_menu.add_command(label="Abrir Projeto...", command=self.abrir_projeto, accelerator="Ctrl+Shift+O")
        file_menu.add_separator()
        file_menu.add_command(label="Salvar", command=self.salvar_imagem, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Como...", command=self.salvar_imagem_como)
        file_menu.add_command(label="Salvar Projeto", command=self.salvar_projeto, accelerator="Ctrl+Shift+S")
        file_menu.add_command(label="Salvar Projeto Como...", command=self.salvar_projeto_como)
        file_menu.add_separator()
        file_menu.add_command(label="Importar...", command=self.importar_imagem)
        file_menu.add_command(label="Exportar Como...", command=self.exportar_imagem)
        file_menu.add_separator()
        
        # Submenu Imprimir
        imprimir_menu = tk.Menu(file_menu, tearoff=0)
        imprimir_menu.add_command(label="Imprimir...", command=self.imprimir, accelerator="Ctrl+P")
        imprimir_menu.add_command(label="Configurar Página...", command=self.configurar_pagina)
        imprimir_menu.add_command(label="Visualizar Impressão...", command=self.visualizar_impressao)
        file_menu.add_cascade(label="Imprimir", menu=imprimir_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Propriedades", command=self.mostrar_propriedades)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.sair_aplicacao, accelerator="Ctrl+Q")
        
        # Menu Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", command=self.desfazer, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Refazer", command=self.refazer, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", command=self.recortar_selecao, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copiar", command=self.copiar_selecao, accelerator="Ctrl+C")
        edit_menu.add_command(label="Colar", command=self.colar_selecao, accelerator="Ctrl+V")
        edit_menu.add_command(label="Duplicar", command=self.duplicar_selecao, accelerator="Ctrl+D")
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", command=self.selecionar_tudo, accelerator="Ctrl+A")
        edit_menu.add_command(label="Limpar Seleção", command=self.limpar_selecao)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reset", command=self.reset_imagem)
        
        # Menu Visualizar
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizar", menu=view_menu)
        view_menu.add_command(label="Zoom +", command=self.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom -", command=self.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Zoom 100%", command=self.zoom_100, accelerator="Ctrl+0")
        view_menu.add_command(label="Ajustar à tela", command=self.ajustar_tela)
        view_menu.add_command(label="Tamanho Real", command=self.zoom_100)
        view_menu.add_separator()
        view_menu.add_command(label="Mostrar Grade", command=self.toggle_grade)
        view_menu.add_command(label="Mostrar Régua", command=self.toggle_regua)
        view_menu.add_separator()
        view_menu.add_command(label="Modo Tela Cheia", command=self.toggle_fullscreen, accelerator="F11")
        
        # ========== MENU EFEITOS (NOVO) ==========
        efeitos_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Efeitos", menu=efeitos_menu)
        
        # Submenu de Cores
        cores_menu = tk.Menu(efeitos_menu, tearoff=0)
        efeitos_menu.add_cascade(label="Cores", menu=cores_menu)
        cores_menu.add_command(label="Inverter Cores", command=self.efeito_inverter_cores)
        cores_menu.add_command(label="Escala de Cinza", command=self.efeito_escala_cinza)
        cores_menu.add_command(label="Sépia", command=self.efeito_sepia)
        cores_menu.add_command(label="P&B (Limiar)", command=self.efeito_preto_branco)
        cores_menu.add_separator()
        cores_menu.add_command(label="Ajustar Brilho...", command=self.efeito_ajustar_brilho)
        cores_menu.add_command(label="Ajustar Contraste...", command=self.efeito_ajustar_contraste)
        cores_menu.add_command(label="Ajustar Saturação...", command=self.efeito_ajustar_saturacao)
        
        # Submenu de Filtros
        filtros_menu = tk.Menu(efeitos_menu, tearoff=0)
        efeitos_menu.add_cascade(label="Filtros", menu=filtros_menu)
        filtros_menu.add_command(label="Desfoque (Blur)", command=self.efeito_desfoque)
        filtros_menu.add_command(label="Desfoque Gaussiano", command=self.efeito_desfoque_gaussiano)
        filtros_menu.add_command(label="Detecção de Bordas", command=self.efeito_bordas)
        filtros_menu.add_command(label="Realce (Sharpen)", command=self.efeito_realce)
        filtros_menu.add_command(label="Suavizar (Smooth)", command=self.efeito_suavizar)
        filtros_menu.add_command(label="Efeito Pintura (Emboss)", command=self.efeito_emboss)
        filtros_menu.add_command(label="Contorno (Contour)", command=self.efeito_contorno)
        filtros_menu.add_command(label="Detalhes (Detail)", command=self.efeito_detalhes)
        
        # Submenu de Transformações
        transformar_menu = tk.Menu(efeitos_menu, tearoff=0)
        efeitos_menu.add_cascade(label="Transformar", menu=transformar_menu)
        transformar_menu.add_command(label="Rotacionar 90°", command=lambda: self.efeito_rotacionar(90))
        transformar_menu.add_command(label="Rotacionar 180°", command=lambda: self.efeito_rotacionar(180))
        transformar_menu.add_command(label="Rotacionar 270°", command=lambda: self.efeito_rotacionar(270))
        transformar_menu.add_separator()
        transformar_menu.add_command(label="Espelhar Horizontal", command=lambda: self.efeito_espelhar('horizontal'))
        transformar_menu.add_command(label="Espelhar Vertical", command=lambda: self.efeito_espelhar('vertical'))
        transformar_menu.add_separator()
        transformar_menu.add_command(label="Redimensionar...", command=self.efeito_redimensionar)
        transformar_menu.add_command(label="Cortar...", command=self.efeito_cortar)
        
        # Submenu de Efeitos Especiais
        especiais_menu = tk.Menu(efeitos_menu, tearoff=0)
        efeitos_menu.add_cascade(label="Especiais", menu=especiais_menu)
        especiais_menu.add_command(label="Deixar Transparente...", command=self.efeito_deixar_transparente)
        especiais_menu.add_command(label="Pixelizar...", command=self.efeito_pixelizar)
        especiais_menu.add_command(label="Efeito Mosaico...", command=self.efeito_mosaico)
        especiais_menu.add_separator()
        especiais_menu.add_command(label="Adicionar Ruído...", command=self.efeito_ruido)
        especiais_menu.add_command(label="Efeito Solarizar...", command=self.efeito_solarizar)
        especiais_menu.add_command(label="Efeito Negativo", command=self.efeito_inverter_cores)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Configurar Ferramentas...", command=self.configurar_ferramentas)
        tools_menu.add_command(label="Gerenciar Cores...", command=self.gerenciar_cores)
        tools_menu.add_separator()
        tools_menu.add_command(label="Exportar Configurações...", command=self.exportar_configuracoes)
        tools_menu.add_command(label="Importar Configurações...", command=self.importar_configuracoes)
        
        # Menu Projeto
        project_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Projeto", menu=project_menu)
        project_menu.add_command(label="Propriedades do Projeto...", command=self.propriedades_projeto)
        project_menu.add_command(label="Histórico de Versões...", command=self.historico_versoes)
        project_menu.add_command(label="Exportar como Modelo...", command=self.exportar_modelo)
        project_menu.add_separator()
        project_menu.add_command(label="Combinar Projetos...", command=self.combinar_projetos)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        help_menu.add_command(label="Limites do Editor", command=self.mostrar_limites)
        help_menu.add_command(label="Atalhos de Teclado", command=self.mostrar_atalhos)
        help_menu.add_command(label="Tutoriais", command=self.mostrar_tutoriais)
        
        # Toolbar principal
        toolbar = tk.Frame(main_frame, bg='#e0e0e0', height=120)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Primeira linha da toolbar
        linha1 = tk.Frame(toolbar, bg='#e0e0e0')
        linha1.pack(fill=tk.X, pady=2)
        
        # Botões de arquivo
        btn_novo = tk.Button(linha1, text="📄 Nova Imagem", command=self.nova_imagem, bg='#e0e0e0')
        btn_novo.pack(side=tk.LEFT, padx=2)
        
        btn_novo_projeto = tk.Button(linha1, text="📁 Novo Projeto", command=self.novo_projeto, bg='#e0e0e0')
        btn_novo_projeto.pack(side=tk.LEFT, padx=2)
        
        btn_abrir = tk.Button(linha1, text="📂 Abrir", command=self.abrir_imagem, bg='#e0e0e0')
        btn_abrir.pack(side=tk.LEFT, padx=2)
        
        btn_abrir_projeto = tk.Button(linha1, text="📂 Abrir Projeto", command=self.abrir_projeto, bg='#e0e0e0')
        btn_abrir_projeto.pack(side=tk.LEFT, padx=2)
        
        btn_salvar = tk.Button(linha1, text="💾 Salvar", command=self.salvar_imagem, bg='#e0e0e0')
        btn_salvar.pack(side=tk.LEFT, padx=2)
        
        btn_salvar_projeto = tk.Button(linha1, text="💾 Salvar Projeto", command=self.salvar_projeto, bg='#e0e0e0')
        btn_salvar_projeto.pack(side=tk.LEFT, padx=2)
        
        btn_imprimir = tk.Button(linha1, text="🖨️ Imprimir", command=self.imprimir, bg='#e0e0e0')
        btn_imprimir.pack(side=tk.LEFT, padx=2)
        
        # Separador
        tk.Frame(linha1, width=2, bg='#a0a0a0', height=25).pack(side=tk.LEFT, padx=10)
        
        # Controles de zoom
        tk.Label(linha1, text="Zoom:", bg='#e0e0e0').pack(side=tk.LEFT)
        btn_zoom_menos = tk.Button(linha1, text="−", command=self.zoom_out, bg='#e0e0e0', width=3)
        btn_zoom_menos.pack(side=tk.LEFT, padx=2)
        
        self.zoom_label = tk.Label(linha1, text="100%", bg='#e0e0e0', width=6)
        self.zoom_label.pack(side=tk.LEFT)
        
        btn_zoom_mais = tk.Button(linha1, text="+", command=self.zoom_in, bg='#e0e0e0', width=3)
        btn_zoom_mais.pack(side=tk.LEFT, padx=2)
        
        btn_ajustar = tk.Button(linha1, text="↺ Ajustar", command=self.ajustar_tela, bg='#e0e0e0')
        btn_ajustar.pack(side=tk.LEFT, padx=5)
        
        # Segunda linha da toolbar
        linha2 = tk.Frame(toolbar, bg='#e0e0e0')
        linha2.pack(fill=tk.X, pady=2)
        
        # Frame de ferramentas
        tools_frame = tk.Frame(linha2, bg='#e0e0e0')
        tools_frame.pack(side=tk.LEFT, padx=5)
        
        # Botões de ferramentas
        self.btn_selecao = tk.Button(tools_frame, text="🖱️ Seleção", bg='#c0c0c0',
                                     command=lambda: self.selecionar_ferramenta("selecao"))
        self.btn_selecao.pack(side=tk.LEFT, padx=2)
        
        self.btn_caneta = tk.Button(tools_frame, text="✏️ Caneta", 
                                    command=lambda: self.selecionar_ferramenta("caneta"))
        self.btn_caneta.pack(side=tk.LEFT, padx=2)
        
        self.btn_borracha = tk.Button(tools_frame, text="🧽 Borracha", 
                                      command=lambda: self.selecionar_ferramenta("borracha"))
        self.btn_borracha.pack(side=tk.LEFT, padx=2)
        
        # Botão de cor
        self.btn_cor = tk.Button(tools_frame, text="🎨 Cor", bg='black', fg='white',
                                 command=self.escolher_cor, width=5)
        self.btn_cor.pack(side=tk.LEFT, padx=(10,2))
        
        # Tamanho do pincel
        tk.Label(tools_frame, text="Tamanho:", bg='#e0e0e0').pack(side=tk.LEFT, padx=(10,2))
        self.tamanho_scale = tk.Scale(tools_frame, from_=1, to=50, orient=tk.HORIZONTAL,
                                      command=self.ajustar_tamanho, bg='#e0e0e0', length=100)
        self.tamanho_scale.set(self.tamanho_pincel)
        self.tamanho_scale.pack(side=tk.LEFT)
        
        # Botão de limpar seleção
        self.btn_limpar_selecao = tk.Button(tools_frame, text="✖️ Limpar Seleção",
                                           command=self.limpar_selecao,
                                           state=tk.DISABLED)
        self.btn_limpar_selecao.pack(side=tk.LEFT, padx=10)
        
        # Frame de transformações
        transform_frame = tk.Frame(linha2, bg='#e0e0e0')
        transform_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(transform_frame, text="Transformar:", bg='#e0e0e0').pack(side=tk.LEFT)
        tk.Button(transform_frame, text="Recortar", command=self.recortar_selecao).pack(side=tk.LEFT, padx=2)
        tk.Button(transform_frame, text="Copiar", command=self.copiar_selecao).pack(side=tk.LEFT, padx=2)
        tk.Button(transform_frame, text="Colar", command=self.colar_selecao).pack(side=tk.LEFT, padx=2)
        
        # Frame principal de edição
        edit_frame = tk.Frame(main_frame)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para a imagem
        self.canvas = tk.Canvas(edit_frame, bg='#505050', highlightthickness=0, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_label = tk.Label(self.root, text="Pronto | Ferramenta: Seleção | Sem imagem", 
                                     bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame de coordenadas e info
        info_frame = tk.Frame(self.status_label)
        info_frame.pack(side=tk.RIGHT)
        
        self.coord_label = tk.Label(info_frame, text="", bd=1, relief=tk.SUNKEN, width=20)
        self.coord_label.pack(side=tk.LEFT)
        
        self.size_label = tk.Label(info_frame, text="", bd=1, relief=tk.SUNKEN, width=25)
        self.size_label.pack(side=tk.LEFT)
        
        self.modified_label = tk.Label(info_frame, text="", bd=1, relief=tk.SUNKEN, width=10, fg='red')
        self.modified_label.pack(side=tk.LEFT)
        
        self.project_label = tk.Label(info_frame, text="", bd=1, relief=tk.SUNKEN, width=15, fg='blue')
        self.project_label.pack(side=tk.LEFT)
    
    def setup_bindings(self):
        # Bindings do mouse
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<Motion>", self.on_mouse_over)
        
        # Bindings para pan (arrastar com botão direito)
        self.canvas.bind("<Button-3>", self.iniciar_pan)
        self.canvas.bind("<B3-Motion>", self.fazer_pan)
        self.canvas.bind("<ButtonRelease-3>", self.parar_pan)
        
        # Bindings para zoom com roda do mouse
        self.canvas.bind("<MouseWheel>", self.zoom_roda)  # Windows
        self.canvas.bind("<Button-4>", self.zoom_roda)    # Linux (scroll up)
        self.canvas.bind("<Button-5>", self.zoom_roda)    # Linux (scroll down)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.nova_imagem())
        self.root.bind("<Control-N>", lambda e: self.novo_projeto())
        self.root.bind("<Control-o>", lambda e: self.abrir_imagem())
        self.root.bind("<Control-O>", lambda e: self.abrir_projeto())
        self.root.bind("<Control-s>", lambda e: self.salvar_imagem())
        self.root.bind("<Control-S>", lambda e: self.salvar_projeto())
        self.root.bind("<Control-p>", lambda e: self.imprimir())
        self.root.bind("<Control-q>", lambda e: self.sair_aplicacao())
        self.root.bind("<Control-z>", lambda e: self.desfazer())
        self.root.bind("<Control-y>", lambda e: self.refazer())
        self.root.bind("<Control-x>", lambda e: self.recortar_selecao())
        self.root.bind("<Control-c>", lambda e: self.copiar_selecao())
        self.root.bind("<Control-v>", lambda e: self.colar_selecao())
        self.root.bind("<Control-d>", lambda e: self.duplicar_selecao())
        self.root.bind("<Control-a>", lambda e: self.selecionar_tudo())
        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        
        # Atalhos de zoom
        self.root.bind("<Control-plus>", lambda e: self.zoom_in())
        self.root.bind("<Control-KP_Add>", lambda e: self.zoom_in())
        self.root.bind("<Control-minus>", lambda e: self.zoom_out())
        self.root.bind("<Control-KP_Subtract>", lambda e: self.zoom_out())
        self.root.bind("<Control-0>", lambda e: self.zoom_100())
    
    # ========== FUNÇÕES DE HISTÓRICO ==========
    
    def salvar_no_historico(self):
        """Salvar estado atual no histórico para desfazer/refazer"""
        if self.imagem_editada:
            # Criar cópia do estado atual
            estado_atual = self.imagem_editada.copy()
            
            # Se estamos em um ponto diferente do final do histórico, remover estados futuros
            if self.historico_index < len(self.historico) - 1:
                self.historico = self.historico[:self.historico_index + 1]
            
            # Adicionar estado atual
            self.historico.append(estado_atual)
            
            # Limitar tamanho do histórico
            if len(self.historico) > self.MAX_HISTORICO:
                self.historico.pop(0)
            
            # Atualizar índice
            self.historico_index = len(self.historico) - 1
    
    def desfazer(self):
        """Desfazer última ação"""
        if self.historico_index > 0:
            self.historico_index -= 1
            self.imagem_editada = self.historico[self.historico_index].copy()
            self.marcar_alteracao()
            self.atualizar_visualizacao()
            self.status_label.config(text="Desfazer")
    
    def refazer(self):
        """Refazer ação desfeita"""
        if self.historico_index < len(self.historico) - 1:
            self.historico_index += 1
            self.imagem_editada = self.historico[self.historico_index].copy()
            self.marcar_alteracao()
            self.atualizar_visualizacao()
            self.status_label.config(text="Refazer")
    
    def aplicar_efeito(self, funcao_efeito, *args):
        """Aplicar um efeito com salvamento no histórico"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhuma imagem carregada!")
            return
        
        # Salvar estado atual no histórico
        self.salvar_no_historico()
        
        # Aplicar o efeito
        try:
            funcao_efeito(*args)
            self.marcar_alteracao()
            self.atualizar_visualizacao()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao aplicar efeito: {str(e)}")
    
    # ========== FUNÇÕES DE EFEITOS ==========
    
    def efeito_inverter_cores(self):
        """Inverter cores da imagem"""
        if self.imagem_editada:
            # Converter para RGB se necessário
            if self.imagem_editada.mode == 'RGBA':
                r, g, b, a = self.imagem_editada.split()
                rgb = Image.merge('RGB', (r, g, b))
                rgb_invertido = Image.eval(rgb, lambda x: 255 - x)
                self.imagem_editada = Image.merge('RGBA', (*rgb_invertido.split(), a))
            else:
                self.imagem_editada = Image.eval(self.imagem_editada, lambda x: 255 - x)
            self.status_label.config(text="Efeito: Inverter Cores aplicado")
    
    def efeito_escala_cinza(self):
        """Converter para escala de cinza"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.convert('L').convert(self.imagem_editada.mode)
            self.status_label.config(text="Efeito: Escala de Cinza aplicado")
    
    def efeito_sepia(self):
        """Aplicar efeito sépia"""
        if self.imagem_editada:
            # Converter para RGB se for RGBA
            if self.imagem_editada.mode == 'RGBA':
                img_rgb = self.imagem_editada.convert('RGB')
                img_sepia = self._aplicar_sepia(img_rgb)
                # Manter canal alpha
                a = self.imagem_editada.split()[3]
                r, g, b = img_sepia.split()
                self.imagem_editada = Image.merge('RGBA', (r, g, b, a))
            else:
                self.imagem_editada = self._aplicar_sepia(self.imagem_editada)
            self.status_label.config(text="Efeito: Sépia aplicado")
    
    def _aplicar_sepia(self, img):
        """Aplicar filtro sépia em uma imagem RGB"""
        width, height = img.size
        pixels = img.load()
        
        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]
                # Fórmula do sépia
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                pixels[x, y] = (min(255, tr), min(255, tg), min(255, tb))
        
        return img
    
    def efeito_preto_branco(self):
        """Converter para preto e branco com limiar ajustável"""
        if self.imagem_editada:
            limiar = simpledialog.askinteger("Limiar", 
                                            "Valor do limiar (0-255):\nValores baixos = mais escuro",
                                            minvalue=0, maxvalue=255, initialvalue=128)
            if limiar is not None:
                # Converter para escala de cinza
                img_gray = self.imagem_editada.convert('L')
                # Aplicar limiar
                img_bw = img_gray.point(lambda x: 0 if x < limiar else 255, '1')
                # Converter de volta para o modo original
                self.imagem_editada = img_bw.convert(self.imagem_editada.mode)
                self.status_label.config(text=f"Efeito: Preto e Branco (limiar={limiar}) aplicado")
    
    def efeito_ajustar_brilho(self):
        """Ajustar brilho da imagem"""
        if self.imagem_editada:
            fator = simpledialog.askfloat("Brilho", 
                                         "Fator de brilho (0.0 - 2.0):\n1.0 = original\n<1.0 = mais escuro\n>1.0 = mais claro",
                                         minvalue=0.0, maxvalue=2.0, initialvalue=1.0)
            if fator is not None:
                enhancer = ImageEnhance.Brightness(self.imagem_editada)
                self.imagem_editada = enhancer.enhance(fator)
                self.status_label.config(text=f"Efeito: Brilho ajustado ({fator:.2f})")
    
    def efeito_ajustar_contraste(self):
        """Ajustar contraste da imagem"""
        if self.imagem_editada:
            fator = simpledialog.askfloat("Contraste", 
                                         "Fator de contraste (0.0 - 2.0):\n1.0 = original\n<1.0 = menos contraste\n>1.0 = mais contraste",
                                         minvalue=0.0, maxvalue=2.0, initialvalue=1.0)
            if fator is not None:
                enhancer = ImageEnhance.Contrast(self.imagem_editada)
                self.imagem_editada = enhancer.enhance(fator)
                self.status_label.config(text=f"Efeito: Contraste ajustado ({fator:.2f})")
    
    def efeito_ajustar_saturacao(self):
        """Ajustar saturação da imagem"""
        if self.imagem_editada:
            fator = simpledialog.askfloat("Saturação", 
                                         "Fator de saturação (0.0 - 2.0):\n1.0 = original\n0.0 = preto e branco\n>1.0 = mais saturado",
                                         minvalue=0.0, maxvalue=2.0, initialvalue=1.0)
            if fator is not None:
                enhancer = ImageEnhance.Color(self.imagem_editada)
                self.imagem_editada = enhancer.enhance(fator)
                self.status_label.config(text=f"Efeito: Saturação ajustada ({fator:.2f})")
    
    def efeito_desfoque(self):
        """Aplicar desfoque simples"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.BLUR)
            self.status_label.config(text="Efeito: Desfoque aplicado")
    
    def efeito_desfoque_gaussiano(self):
        """Aplicar desfoque gaussiano com raio ajustável"""
        if self.imagem_editada:
            raio = simpledialog.askinteger("Desfoque Gaussiano", 
                                          "Raio do desfoque (1-10):\nMaior raio = mais desfocado",
                                          minvalue=1, maxvalue=10, initialvalue=2)
            if raio is not None:
                self.imagem_editada = self.imagem_editada.filter(ImageFilter.GaussianBlur(radius=raio))
                self.status_label.config(text=f"Efeito: Desfoque Gaussiano (raio={raio}) aplicado")
    
    def efeito_bordas(self):
        """Detectar bordas na imagem"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.FIND_EDGES)
            self.status_label.config(text="Efeito: Detecção de Bordas aplicado")
    
    def efeito_realce(self):
        """Aplicar realce (sharpen)"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.SHARPEN)
            self.status_label.config(text="Efeito: Realce aplicado")
    
    def efeito_suavizar(self):
        """Aplicar suavização (smooth)"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.SMOOTH)
            self.status_label.config(text="Efeito: Suavizar aplicado")
    
    def efeito_emboss(self):
        """Aplicar efeito de relevo (emboss)"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.EMBOSS)
            self.status_label.config(text="Efeito: Relevo (Emboss) aplicado")
    
    def efeito_contorno(self):
        """Aplicar efeito de contorno"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.CONTOUR)
            self.status_label.config(text="Efeito: Contorno aplicado")
    
    def efeito_detalhes(self):
        """Aplicar efeito de detalhes"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.filter(ImageFilter.DETAIL)
            self.status_label.config(text="Efeito: Detalhes aplicado")
    
    def efeito_rotacionar(self, angulo):
        """Rotacionar a imagem"""
        if self.imagem_editada:
            self.imagem_editada = self.imagem_editada.rotate(angulo, expand=True)
            self.status_label.config(text=f"Efeito: Rotacionado {angulo}°")
    
    def efeito_espelhar(self, direcao):
        """Espelhar a imagem"""
        if self.imagem_editada:
            if direcao == 'horizontal':
                self.imagem_editada = self.imagem_editada.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                self.imagem_editada = self.imagem_editada.transpose(Image.FLIP_TOP_BOTTOM)
            self.status_label.config(text=f"Efeito: Espelhar {direcao}")
    
    def efeito_redimensionar(self):
        """Redimensionar a imagem"""
        if self.imagem_editada:
            dialog = tk.Toplevel(self.root)
            dialog.title("Redimensionar Imagem")
            dialog.geometry("400x250")
            dialog.transient(self.root)
            dialog.grab_set()
            
            frame = tk.Frame(dialog, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            largura_atual, altura_atual = self.imagem_editada.size
            
            tk.Label(frame, text=f"Dimensões atuais: {largura_atual} x {altura_atual}").pack(pady=5)
            
            largura_frame = tk.Frame(frame)
            largura_frame.pack(fill=tk.X, pady=5)
            tk.Label(largura_frame, text="Nova Largura:").pack(side=tk.LEFT)
            largura_entry = tk.Entry(largura_frame, width=10)
            largura_entry.pack(side=tk.LEFT, padx=5)
            largura_entry.insert(0, str(largura_atual))
            
            altura_frame = tk.Frame(frame)
            altura_frame.pack(fill=tk.X, pady=5)
            tk.Label(altura_frame, text="Nova Altura:").pack(side=tk.LEFT)
            altura_entry = tk.Entry(altura_frame, width=10)
            altura_entry.pack(side=tk.LEFT, padx=5)
            altura_entry.insert(0, str(altura_atual))
            
            manter_proporcao = tk.BooleanVar(value=True)
            tk.Checkbutton(frame, text="Manter proporção", variable=manter_proporcao).pack(pady=5)
            
            def aplicar_redimensionamento():
                try:
                    nova_largura = int(largura_entry.get())
                    nova_altura = int(altura_entry.get())
                    
                    if manter_proporcao.get():
                        # Calcular proporção
                        proporcao = altura_atual / largura_atual
                        nova_altura = int(nova_largura * proporcao)
                        altura_entry.delete(0, tk.END)
                        altura_entry.insert(0, str(nova_altura))
                    
                    self.imagem_editada = self.imagem_editada.resize((nova_largura, nova_altura), 
                                                                     Image.Resampling.LANCZOS)
                    self.marcar_alteracao()
                    self.atualizar_visualizacao()
                    dialog.destroy()
                    self.status_label.config(text=f"Imagem redimensionada para {nova_largura}x{nova_altura}")
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira números válidos!")
            
            tk.Button(frame, text="Aplicar", command=aplicar_redimensionamento).pack(pady=10)
            tk.Button(frame, text="Cancelar", command=dialog.destroy).pack()
    
    def efeito_cortar(self):
        """Cortar a imagem (usar seleção atual ou pedir dimensões)"""
        if self.area_selecionada:
            # Usar a seleção atual
            self.imagem_editada = self.area_selecionada.copy()
            self.limpar_selecao()
            self.status_label.config(text="Imagem cortada para a seleção")
        else:
            # Pedir coordenadas
            dialog = tk.Toplevel(self.root)
            dialog.title("Cortar Imagem")
            dialog.geometry("400x250")
            dialog.transient(self.root)
            dialog.grab_set()
            
            frame = tk.Frame(dialog, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            largura, altura = self.imagem_editada.size
            
            tk.Label(frame, text=f"Imagem atual: {largura} x {altura}").pack()
            
            # Coordenadas
            coords_frame = tk.Frame(frame)
            coords_frame.pack(pady=10)
            
            tk.Label(coords_frame, text="X:").grid(row=0, column=0)
            x_entry = tk.Entry(coords_frame, width=8)
            x_entry.grid(row=0, column=1)
            x_entry.insert(0, "0")
            
            tk.Label(coords_frame, text="Y:").grid(row=0, column=2)
            y_entry = tk.Entry(coords_frame, width=8)
            y_entry.grid(row=0, column=3)
            y_entry.insert(0, "0")
            
            tk.Label(coords_frame, text="Largura:").grid(row=1, column=0)
            w_entry = tk.Entry(coords_frame, width=8)
            w_entry.grid(row=1, column=1)
            w_entry.insert(0, str(largura))
            
            tk.Label(coords_frame, text="Altura:").grid(row=1, column=2)
            h_entry = tk.Entry(coords_frame, width=8)
            h_entry.grid(row=1, column=3)
            h_entry.insert(0, str(altura))
            
            def aplicar_corte():
                try:
                    x = int(x_entry.get())
                    y = int(y_entry.get())
                    w = int(w_entry.get())
                    h = int(h_entry.get())
                    
                    if w > 0 and h > 0:
                        self.imagem_editada = self.imagem_editada.crop((x, y, x + w, y + h))
                        self.marcar_alteracao()
                        self.atualizar_visualizacao()
                        dialog.destroy()
                        self.status_label.config(text=f"Imagem cortada para {w}x{h}")
                    else:
                        messagebox.showerror("Erro", "Largura e altura devem ser maiores que zero!")
                except ValueError:
                    messagebox.showerror("Erro", "Por favor, insira números válidos!")
            
            tk.Button(frame, text="Aplicar", command=aplicar_corte).pack(pady=10)
            tk.Button(frame, text="Cancelar", command=dialog.destroy).pack()
    
    def efeito_deixar_transparente(self):
        """Tornar uma cor específica transparente"""
        if self.imagem_editada:
            if self.imagem_editada.mode != 'RGBA':
                resposta = messagebox.askyesno("Transparência", 
                                              "A imagem não possui canal alpha. Converter para RGBA?")
                if resposta:
                    self.imagem_editada = self.imagem_editada.convert('RGBA')
                else:
                    return
            
            # Escolher cor para tornar transparente
            cor = colorchooser.askcolor(title="Escolha a cor para tornar transparente")
            if cor[1]:
                cor_rgb = cor[0]
                # Limiar de tolerância
                tolerancia = simpledialog.askinteger("Tolerância", 
                                                     "Tolerância de cor (0-100):\n0 = exata\n100 = ampla",
                                                     minvalue=0, maxvalue=100, initialvalue=10)
                if tolerancia is not None:
                    self._tornar_cor_transparente(cor_rgb, tolerancia)
                    self.status_label.config(text=f"Efeito: Cor {cor[1]} tornada transparente")
    
    def _tornar_cor_transparente(self, cor_alvo, tolerancia):
        """Tornar uma cor específica transparente"""
        dados = self.imagem_editada.getdata()
        novos_dados = []
        
        for pixel in dados:
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel
                a = 255
            
            # Calcular diferença de cor
            diff = math.sqrt((r - cor_alvo[0])**2 + 
                           (g - cor_alvo[1])**2 + 
                           (b - cor_alvo[2])**2)
            
            if diff <= tolerancia * 2.55:  # Escala 0-100 para 0-255
                novos_dados.append((r, g, b, 0))  # Transparente
            else:
                if len(pixel) == 4:
                    novos_dados.append((r, g, b, a))
                else:
                    novos_dados.append((r, g, b, 255))
        
        self.imagem_editada.putdata(novos_dados)
    
    def efeito_pixelizar(self):
        """Aplicar efeito pixelizado"""
        if self.imagem_editada:
            tamanho = simpledialog.askinteger("Pixelizar", 
                                             "Tamanho do pixel (2-50):\nMaior = mais pixelizado",
                                             minvalue=2, maxvalue=50, initialvalue=5)
            if tamanho is not None:
                largura, altura = self.imagem_editada.size
                # Reduzir e depois ampliar
                nova_largura = max(1, largura // tamanho)
                nova_altura = max(1, altura // tamanho)
                
                img_pequena = self.imagem_editada.resize((nova_largura, nova_altura), 
                                                         Image.Resampling.NEAREST)
                self.imagem_editada = img_pequena.resize((largura, altura), 
                                                         Image.Resampling.NEAREST)
                self.status_label.config(text=f"Efeito: Pixelizado (tamanho={tamanho})")
    
    def efeito_mosaico(self):
        """Aplicar efeito de mosaico"""
        if self.imagem_editada:
            tamanho = simpledialog.askinteger("Mosaico", 
                                             "Tamanho do bloco (5-100):\nMaior = mais blocos",
                                             minvalue=5, maxvalue=100, initialvalue=20)
            if tamanho is not None:
                largura, altura = self.imagem_editada.size
                img_copy = self.imagem_editada.copy()
                
                for x in range(0, largura, tamanho):
                    for y in range(0, altura, tamanho):
                        # Calcular média da região
                        regiao = img_copy.crop((x, y, min(x + tamanho, largura), 
                                               min(y + tamanho, altura)))
                        if regiao.size[0] > 0 and regiao.size[1] > 0:
                            # Redimensionar para um pixel e depois ampliar
                            cor_media = regiao.resize((1, 1), Image.Resampling.BOX)
                            cor_media = cor_media.resize((regiao.size[0], regiao.size[1]), 
                                                        Image.Resampling.NEAREST)
                            self.imagem_editada.paste(cor_media, (x, y))
                
                self.status_label.config(text=f"Efeito: Mosaico (tamanho={tamanho})")
    
    def efeito_ruido(self):
        """Adicionar ruído à imagem"""
        if self.imagem_editada:
            intensidade = simpledialog.askinteger("Ruído", 
                                                 "Intensidade do ruído (1-50):\nMaior = mais ruído",
                                                 minvalue=1, maxvalue=50, initialvalue=10)
            if intensidade is not None:
                import random
                dados = list(self.imagem_editada.getdata())
                novos_dados = []
                
                for pixel in dados:
                    if len(pixel) == 4:  # RGBA
                        r, g, b, a = pixel
                        r = min(255, max(0, r + random.randint(-intensidade, intensidade)))
                        g = min(255, max(0, g + random.randint(-intensidade, intensidade)))
                        b = min(255, max(0, b + random.randint(-intensidade, intensidade)))
                        novos_dados.append((r, g, b, a))
                    else:  # RGB
                        r, g, b = pixel
                        r = min(255, max(0, r + random.randint(-intensidade, intensidade)))
                        g = min(255, max(0, g + random.randint(-intensidade, intensidade)))
                        b = min(255, max(0, b + random.randint(-intensidade, intensidade)))
                        novos_dados.append((r, g, b))
                
                self.imagem_editada.putdata(novos_dados)
                self.status_label.config(text=f"Efeito: Ruído adicionado (intensidade={intensidade})")
    
    def efeito_solarizar(self):
        """Aplicar efeito de solarização"""
        if self.imagem_editada:
            limiar = simpledialog.askinteger("Solarizar", 
                                            "Limiar (0-255):\nValores menores = mais solarizado",
                                            minvalue=0, maxvalue=255, initialvalue=128)
            if limiar is not None:
                # Converter para escala de cinza e solarizar
                img_gray = self.imagem_editada.convert('L')
                img_solarized = img_gray.point(lambda x: 255 - x if x < limiar else x)
                self.imagem_editada = img_solarized.convert(self.imagem_editada.mode)
                self.status_label.config(text=f"Efeito: Solarizado (limiar={limiar})")
    
    # ========== FUNÇÕES DE PROJETO (existentes) ==========
    
    def novo_projeto(self):
        """Criar um novo projeto PaintWazzima"""
        if not self.verificar_alteracoes_nao_salvas():
            return
        
        # Diálogo para configuração do projeto
        dialog = tk.Toplevel(self.root)
        dialog.title("Novo Projeto PaintWazzima")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar o diálogo
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (500 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(frame, text="Criar Novo Projeto", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Nome do projeto
        nome_frame = tk.Frame(frame)
        nome_frame.pack(fill=tk.X, pady=5)
        tk.Label(nome_frame, text="Nome do Projeto:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        nome_entry = tk.Entry(nome_frame, width=30)
        nome_entry.pack(side=tk.LEFT)
        nome_entry.insert(0, "Meu Projeto PaintWazzima")
        
        # Autor
        autor_frame = tk.Frame(frame)
        autor_frame.pack(fill=tk.X, pady=5)
        tk.Label(autor_frame, text="Autor:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        autor_entry = tk.Entry(autor_frame, width=30)
        autor_entry.pack(side=tk.LEFT)
        autor_entry.insert(0, "Usuário")
        
        # Descrição
        tk.Label(frame, text="Descrição:", anchor=tk.W).pack(anchor=tk.W, pady=(10, 0))
        descricao_text = tk.Text(frame, height=4, width=50)
        descricao_text.pack(fill=tk.X, pady=5)
        
        # Tamanho da imagem
        tamanho_frame = tk.LabelFrame(frame, text="Tamanho da Imagem", padx=10, pady=10)
        tamanho_frame.pack(fill=tk.X, pady=10)
        
        largura_frame = tk.Frame(tamanho_frame)
        largura_frame.pack(fill=tk.X, pady=2)
        tk.Label(largura_frame, text="Largura (px):", width=12, anchor=tk.W).pack(side=tk.LEFT)
        largura_entry = tk.Entry(largura_frame, width=15)
        largura_entry.pack(side=tk.LEFT)
        largura_entry.insert(0, "800")
        
        altura_frame = tk.Frame(tamanho_frame)
        altura_frame.pack(fill=tk.X, pady=2)
        tk.Label(altura_frame, text="Altura (px):", width=12, anchor=tk.W).pack(side=tk.LEFT)
        altura_entry = tk.Entry(altura_frame, width=15)
        altura_entry.pack(side=tk.LEFT)
        altura_entry.insert(0, "600")
        
        # Cor de fundo
        cor_frame = tk.Frame(tamanho_frame)
        cor_frame.pack(fill=tk.X, pady=2)
        tk.Label(cor_frame, text="Cor de fundo:", width=12, anchor=tk.W).pack(side=tk.LEFT)
        
        fundo_cor = "#FFFFFF"
        btn_cor_fundo = tk.Button(cor_frame, text="  ", bg=fundo_cor, 
                                  command=lambda: self.escolher_cor_projeto(btn_cor_fundo))
        btn_cor_fundo.pack(side=tk.LEFT)
        
        transparente_var = tk.BooleanVar()
        tk.Checkbutton(cor_frame, text="Transparente", variable=transparente_var).pack(side=tk.LEFT, padx=(10,0))
        
        # Botões
        botoes_frame = tk.Frame(frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(botoes_frame, text="Criar Projeto", 
                 command=lambda: self.criar_novo_projeto(
                     nome_entry.get(), autor_entry.get(), descricao_text.get("1.0", tk.END).strip(),
                     largura_entry.get(), altura_entry.get(), 
                     btn_cor_fundo.cget('bg'), transparente_var.get(), dialog
                 )).pack(side=tk.LEFT, padx=5)
        
        tk.Button(botoes_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def escolher_cor_projeto(self, botao):
        """Escolher cor de fundo para o projeto"""
        cor = colorchooser.askcolor(title="Cor de Fundo")
        if cor[1]:
            botao.config(bg=cor[1])
    
    def criar_novo_projeto(self, nome, autor, descricao, largura_str, altura_str, cor_fundo, transparente, dialog):
        """Criar o novo projeto com as configurações especificadas"""
        try:
            largura = int(largura_str)
            altura = int(altura_str)
            
            # Validações
            if largura <= 0 or altura <= 0:
                messagebox.showerror("Erro", "Largura e altura devem ser maiores que zero!")
                return
            
            if largura > self.MAX_LARGURA or altura > self.MAX_ALTURA:
                messagebox.showerror("Erro", f"Dimensões máximas: {self.MAX_LARGURA}x{self.MAX_ALTURA}")
                return
            
            # Verificar megapixels
            megapixels = (largura * altura) / 1_000_000
            if megapixels > self.MAX_MEGAPIXELS:
                resposta = messagebox.askyesno(
                    "Aviso de Memória",
                    f"Esta imagem terá {megapixels:.1f} megapixels, o que pode consumir muita memória.\n"
                    f"Limite recomendado: {self.MAX_MEGAPIXELS} megapixels.\n\n"
                    f"Deseja continuar mesmo assim?"
                )
                if not resposta:
                    return
            
            # Criar imagem base
            if transparente:
                self.imagem_original = Image.new('RGBA', (largura, altura), (0, 0, 0, 0))
            else:
                cor_rgb = self.hex_para_rgb(cor_fundo)
                self.imagem_original = Image.new('RGB', (largura, altura), cor_rgb)
            
            self.imagem_editada = self.imagem_original.copy()
            
            # Limpar histórico
            self.historico = []
            self.salvar_no_historico()
            
            # Configurar metadados do projeto
            agora = datetime.datetime.now().isoformat()
            self.project_metadata = {
                "nome": nome if nome.strip() else "Projeto sem nome",
                "autor": autor if autor.strip() else "Usuário",
                "descricao": descricao,
                "data_criacao": agora,
                "data_modificacao": agora,
                "versoes": [{
                    "data": agora,
                    "descricao": "Versão inicial",
                    "arquivo": None
                }]
            }
            
            self.project_file = None
            self.current_file = None
            self.limpar_selecao()
            self.limpar_marcador_alteracao()
            self.ajustar_tela()
            
            # Atualizar interface
            self.project_label.config(text=f" Projeto: {self.project_metadata['nome']}")
            self.status_label.config(text=f"Projeto criado: {self.project_metadata['nome']}")
            
            # Fechar diálogo
            dialog.destroy()
            
            # Mostrar mensagem de sucesso
            messagebox.showinfo("Sucesso", 
                f"Projeto '{self.project_metadata['nome']}' criado com sucesso!\n\n"
                f"Dimensões: {largura}x{altura}\n"
                f"Modo: {'Transparente' if transparente else 'Opaco'}\n\n"
                f"Não esqueça de salvar seu projeto em Arquivo > Salvar Projeto.")
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira números válidos para largura e altura!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar projeto: {str(e)}")
    
    def salvar_projeto(self):
        """Salvar o projeto atual no formato .paintwazzima"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhum projeto para salvar!")
            return
        
        if self.project_file:
            self._salvar_projeto_arquivo(self.project_file)
        else:
            self.salvar_projeto_como()

    def salvar_projeto_como(self):
        """Salvar o projeto em um novo arquivo .paintwazzima"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhum projeto para salvar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Salvar Projeto Como",
            defaultextension=".paintwazzima",
            filetypes=[("PaintWazzima Project", "*.paintwazzima"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self._salvar_projeto_arquivo(file_path)
            self.project_file = file_path
            self.project_label.config(text=f" Projeto: {self.project_metadata.get('nome', 'Projeto')}")
            self.status_label.config(text=f"Projeto salvo: {os.path.basename(file_path)}")

    def _salvar_projeto_arquivo(self, file_path):
        """Salvar os dados do projeto em arquivo"""
        try:
            # Atualizar metadados
            self.project_metadata["data_modificacao"] = datetime.datetime.now().isoformat()
            
            # Preparar dados do projeto
            project_data = {
                "metadata": self.project_metadata,
                "imagem": self.imagem_editada,
                "configuracoes": {
                    "ferramenta_atual": self.ferramenta_atual,
                    "cor_atual": self.cor_atual,
                    "tamanho_pincel": self.tamanho_pincel,
                    "fator_zoom": self.fator_zoom,
                    "offset_x": self.offset_x,
                    "offset_y": self.offset_y
                },
                "versao": "1.0"
            }
            
            # Salvar usando pickle
            with open(file_path, 'wb') as f:
                pickle.dump(project_data, f)
            
            self.limpar_marcador_alteracao()
            messagebox.showinfo("Sucesso", f"Projeto salvo com sucesso em:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar o projeto: {str(e)}")
    
    def abrir_projeto(self):
        """Abrir um projeto .paintwazzima"""
        if not self.verificar_alteracoes_nao_salvas():
            return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("PaintWazzima Project", "*.paintwazzima"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    project_data = pickle.load(f)
                
                # Carregar dados
                self.imagem_editada = project_data["imagem"]
                self.imagem_original = self.imagem_editada.copy()
                self.project_metadata = project_data.get("metadata", {
                    "nome": os.path.basename(file_path),
                    "data_criacao": datetime.datetime.now().isoformat()
                })
                
                # Carregar configurações
                config = project_data.get("configuracoes", {})
                self.ferramenta_atual = config.get("ferramenta_atual", "selecao")
                self.cor_atual = config.get("cor_atual", "#000000")
                self.tamanho_pincel = config.get("tamanho_pincel", 5)
                self.fator_zoom = config.get("fator_zoom", 1.0)
                self.offset_x = config.get("offset_x", 0)
                self.offset_y = config.get("offset_y", 0)
                
                # Limpar histórico e salvar estado atual
                self.historico = []
                self.salvar_no_historico()
                
                self.project_file = file_path
                self.current_file = None
                self.limpar_selecao()
                self.limpar_marcador_alteracao()
                self.atualizar_visualizacao()
                
                # Atualizar interface
                self.project_label.config(text=f" Projeto: {self.project_metadata.get('nome', 'Sem nome')}")
                self.status_label.config(text=f"Projeto carregado: {os.path.basename(file_path)}")
                
                # Atualizar botões de ferramenta
                self.selecionar_ferramenta(self.ferramenta_atual)
                self.btn_cor.config(bg=self.cor_atual)
                self.tamanho_scale.set(self.tamanho_pincel)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o projeto: {str(e)}")
    
    def propriedades_projeto(self):
        """Mostrar/editar propriedades do projeto"""
        if not self.imagem_editada:
            messagebox.showinfo("Propriedades", "Nenhum projeto aberto.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Propriedades do Projeto")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Propriedades do Projeto", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Nome
        nome_frame = tk.Frame(frame)
        nome_frame.pack(fill=tk.X, pady=5)
        tk.Label(nome_frame, text="Nome:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        nome_entry = tk.Entry(nome_frame, width=30)
        nome_entry.pack(side=tk.LEFT)
        nome_entry.insert(0, self.project_metadata.get("nome", ""))
        
        # Autor
        autor_frame = tk.Frame(frame)
        autor_frame.pack(fill=tk.X, pady=5)
        tk.Label(autor_frame, text="Autor:", width=10, anchor=tk.W).pack(side=tk.LEFT)
        autor_entry = tk.Entry(autor_frame, width=30)
        autor_entry.pack(side=tk.LEFT)
        autor_entry.insert(0, self.project_metadata.get("autor", ""))
        
        # Datas
        info_frame = tk.LabelFrame(frame, text="Informações", padx=10, pady=10)
        info_frame.pack(fill=tk.X, pady=10)
        
        criacao = self.project_metadata.get("data_criacao", "Desconhecido")
        if criacao and criacao != "Desconhecido":
            try:
                criacao = datetime.datetime.fromisoformat(criacao).strftime("%d/%m/%Y %H:%M")
            except:
                pass
        
        modificacao = self.project_metadata.get("data_modificacao", "Desconhecido")
        if modificacao and modificacao != "Desconhecido":
            try:
                modificacao = datetime.datetime.fromisoformat(modificacao).strftime("%d/%m/%Y %H:%M")
            except:
                pass
        
        tk.Label(info_frame, text=f"Criado em: {criacao}").pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Modificado em: {modificacao}").pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Tamanho: {self.imagem_editada.width} x {self.imagem_editada.height} pixels").pack(anchor=tk.W)
        tk.Label(info_frame, text=f"Modo de cor: {self.imagem_editada.mode}").pack(anchor=tk.W)
        
        # Descrição
        tk.Label(frame, text="Descrição:", anchor=tk.W).pack(anchor=tk.W, pady=(10, 0))
        descricao_text = tk.Text(frame, height=4, width=50)
        descricao_text.pack(fill=tk.X, pady=5)
        descricao_text.insert("1.0", self.project_metadata.get("descricao", ""))
        
        # Botões
        botoes_frame = tk.Frame(frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        def salvar_propriedades():
            self.project_metadata["nome"] = nome_entry.get()
            self.project_metadata["autor"] = autor_entry.get()
            self.project_metadata["descricao"] = descricao_text.get("1.0", tk.END).strip()
            self.project_label.config(text=f" Projeto: {nome_entry.get()}")
            self.marcar_alteracao()
            dialog.destroy()
        
        tk.Button(botoes_frame, text="Salvar", command=salvar_propriedades).pack(side=tk.LEFT, padx=5)
        tk.Button(botoes_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def historico_versoes(self):
        """Mostrar histórico de versões do projeto"""
        if not self.imagem_editada:
            messagebox.showinfo("Histórico", "Nenhum projeto aberto.")
            return
        
        versoes = self.project_metadata.get("versoes", [])
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Histórico de Versões")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Histórico de Versões", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Lista de versões
        list_frame = tk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        versoes_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        versoes_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=versoes_listbox.yview)
        
        for i, versao in enumerate(versoes):
            data = versao.get("data", "Desconhecida")
            desc = versao.get("descricao", "Sem descrição")
            try:
                data = datetime.datetime.fromisoformat(data).strftime("%d/%m/%Y %H:%M")
            except:
                pass
            versoes_listbox.insert(tk.END, f"Versão {i+1}: {data} - {desc}")
        
        if not versoes:
            versoes_listbox.insert(tk.END, "Nenhuma versão salva")
        
        # Botões
        botoes_frame = tk.Frame(frame)
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
        def nova_versao():
            desc = simpledialog.askstring("Nova Versão", "Descrição da versão:")
            if desc:
                versao = {
                    "data": datetime.datetime.now().isoformat(),
                    "descricao": desc,
                    "arquivo": self.project_file
                }
                versoes.append(versao)
                versoes_listbox.insert(tk.END, f"Versão {len(versoes)}: {desc}")
                self.marcar_alteracao()
        
        tk.Button(botoes_frame, text="Nova Versão", command=nova_versao).pack(side=tk.LEFT, padx=5)
        tk.Button(botoes_frame, text="Fechar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def exportar_modelo(self):
        """Exportar projeto como modelo"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhum projeto para exportar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".paintwazzima_template",
            filetypes=[("PaintWazzima Template", "*.paintwazzima_template"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Preparar modelo (sem dados específicos de edição)
                template_data = {
                    "metadata": {
                        "nome": self.project_metadata.get("nome", "Modelo"),
                        "autor": self.project_metadata.get("autor", ""),
                        "descricao": self.project_metadata.get("descricao", ""),
                        "tipo": "template"
                    },
                    "imagem_base": self.imagem_original,
                    "configuracoes_padrao": {
                        "ferramenta_padrao": "selecao",
                        "cor_padrao": "#000000",
                        "tamanho_pincel_padrao": 5
                    },
                    "versao": "1.0"
                }
                
                with open(file_path, 'wb') as f:
                    pickle.dump(template_data, f)
                
                messagebox.showinfo("Sucesso", "Modelo exportado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exportar modelo: {str(e)}")
    
    def combinar_projetos(self):
        """Combinar dois ou mais projetos"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Abra um projeto primeiro!")
            return
        
        file_paths = filedialog.askopenfilenames(
            title="Selecione projetos para combinar",
            filetypes=[("PaintWazzima Project", "*.paintwazzima"), ("Todos os arquivos", "*.*")]
        )
        
        if file_paths:
            try:
                # Carregar todos os projetos
                projetos = []
                for path in file_paths:
                    with open(path, 'rb') as f:
                        projetos.append(pickle.load(f))
                
                # Criar nova imagem combinada
                largura_total = max(p["imagem"].width for p in projetos)
                altura_total = max(p["imagem"].height for p in projetos)
                
                nova_imagem = Image.new('RGBA', (largura_total, altura_total), (255, 255, 255, 0))
                
                # Combinar imagens
                y_offset = 0
                for projeto in projetos:
                    img = projeto["imagem"]
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    nova_imagem.paste(img, (0, y_offset), img if img.mode == 'RGBA' else None)
                    y_offset += img.height
                
                self.imagem_editada = nova_imagem
                self.imagem_original = nova_imagem.copy()
                self.project_metadata["nome"] = "Projeto Combinado"
                self.marcar_alteracao()
                self.ajustar_tela()
                self.atualizar_visualizacao()
                
                messagebox.showinfo("Sucesso", "Projetos combinados com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao combinar projetos: {str(e)}")
    
    # ========== FUNÇÕES DE IMPRESSÃO (existentes) ==========
    
    def imprimir(self):
        """Imprimir a imagem atual"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhuma imagem para imprimir!")
            return
        
        if not IMPRESSAO_DISPONIVEL:
            messagebox.showinfo("Impressão", 
                "A impressão direta requer a biblioteca pywin32.\n\n"
                "Você pode exportar a imagem e imprimir com outro programa.")
            return
        
        try:
            # Configurações de impressão
            printer_name = win32print.GetDefaultPrinter()
            
            # Diálogo de configuração de impressão
            config_dialog = tk.Toplevel(self.root)
            config_dialog.title("Configurar Impressão")
            config_dialog.geometry("400x300")
            config_dialog.transient(self.root)
            config_dialog.grab_set()
            
            frame = tk.Frame(config_dialog, padx=20, pady=20)
            frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(frame, text="Configurações de Impressão", font=("Arial", 12, "bold")).pack(pady=(0, 15))
            
            # Qualidade (DPI)
            dpi_frame = tk.Frame(frame)
            dpi_frame.pack(fill=tk.X, pady=5)
            tk.Label(dpi_frame, text="Qualidade (DPI):", width=15, anchor=tk.W).pack(side=tk.LEFT)
            dpi_spinbox = tk.Spinbox(dpi_frame, from_=72, to=1200, increment=1, width=10)
            dpi_spinbox.pack(side=tk.LEFT)
            dpi_spinbox.delete(0, tk.END)
            dpi_spinbox.insert(0, str(self.configuracoes["qualidade_impressao"]))
            
            # Orientação
            orient_frame = tk.Frame(frame)
            orient_frame.pack(fill=tk.X, pady=5)
            tk.Label(orient_frame, text="Orientação:", width=15, anchor=tk.W).pack(side=tk.LEFT)
            orient_combo = ttk.Combobox(orient_frame, values=["Retrato", "Paisagem"], width=10)
            orient_combo.pack(side=tk.LEFT)
            orient_combo.set(self.configuracoes["orientacao"])
            
            # Margens
            margens_frame = tk.LabelFrame(frame, text="Margens (cm)", padx=10, pady=10)
            margens_frame.pack(fill=tk.X, pady=10)
            
            margens_grid = tk.Frame(margens_frame)
            margens_grid.pack()
            
            # Layout das margens
            tk.Label(margens_grid, text="Esquerda:").grid(row=0, column=0, padx=5)
            esq_entry = tk.Entry(margens_grid, width=8)
            esq_entry.grid(row=0, column=1, padx=5)
            esq_entry.insert(0, str(self.configuracoes["margens"][0]))
            
            tk.Label(margens_grid, text="Direita:").grid(row=0, column=2, padx=5)
            dir_entry = tk.Entry(margens_grid, width=8)
            dir_entry.grid(row=0, column=3, padx=5)
            dir_entry.insert(0, str(self.configuracoes["margens"][1]))
            
            tk.Label(margens_grid, text="Topo:").grid(row=1, column=0, padx=5)
            topo_entry = tk.Entry(margens_grid, width=8)
            topo_entry.grid(row=1, column=1, padx=5)
            topo_entry.insert(0, str(self.configuracoes["margens"][2]))
            
            tk.Label(margens_grid, text="Base:").grid(row=1, column=2, padx=5)
            base_entry = tk.Entry(margens_grid, width=8)
            base_entry.grid(row=1, column=3, padx=5)
            base_entry.insert(0, str(self.configuracoes["margens"][3]))
            
            def iniciar_impressao():
                # Salvar configurações
                self.configuracoes["qualidade_impressao"] = int(dpi_spinbox.get())
                self.configuracoes["orientacao"] = orient_combo.get()
                self.configuracoes["margens"] = (
                    float(esq_entry.get()),
                    float(dir_entry.get()),
                    float(topo_entry.get()),
                    float(base_entry.get())
                )
                
                config_dialog.destroy()
                self._executar_impressao()
            
            # Botões
            botoes_frame = tk.Frame(frame)
            botoes_frame.pack(fill=tk.X, pady=(20, 0))
            
            tk.Button(botoes_frame, text="Imprimir", command=iniciar_impressao).pack(side=tk.LEFT, padx=5)
            tk.Button(botoes_frame, text="Cancelar", command=config_dialog.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao configurar impressão: {str(e)}")
    
    def _executar_impressao(self):
        """Executar a impressão com as configurações atuais"""
        try:
            # Preparar imagem para impressão
            dpi = self.configuracoes["qualidade_impressao"]
            
            # Criar DC da impressora
            printer_name = win32print.GetDefaultPrinter()
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_name)
            
            # Iniciar documento
            hdc.StartDoc('PaintWazzima - Impressão')
            hdc.StartPage()
            
            # Converter imagem para formato compatível
            if self.imagem_editada.mode != 'RGB':
                img_impressao = self.imagem_editada.convert('RGB')
            else:
                img_impressao = self.imagem_editada
            
            # Calcular dimensões em pixels para o DPI desejado
            largura_px = img_impressao.width
            altura_px = img_impressao.height
            
            # Calcular dimensões em polegadas
            largura_pol = largura_px / dpi
            altura_pol = altura_px / dpi
            
            # Converter para unidades da impressora (geralmente 0.01mm)
            # 1 polegada = 2540 unidades (0.01mm)
            largura_unidades = int(largura_pol * 2540)
            altura_unidades = int(altura_pol * 2540)
            
            # Aplicar margens
            margem_esq = int(self.configuracoes["margens"][0] * 0.3937 * 2540)  # cm para polegadas * 2540
            margem_topo = int(self.configuracoes["margens"][2] * 0.3937 * 2540)
            
            # Desenhar imagem
            dib = ImageWin.Dib(img_impressao)
            dib.draw(hdc.GetHandleOutput(), (margem_esq, margem_topo, 
                                            margem_esq + largura_unidades, 
                                            margem_topo + altura_unidades))
            
            # Finalizar
            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
            
            messagebox.showinfo("Sucesso", "Imagem enviada para impressão!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro durante a impressão: {str(e)}")
    
    def configurar_pagina(self):
        """Configurar página para impressão"""
        if not IMPRESSAO_DISPONIVEL:
            messagebox.showinfo("Configurar Página", 
                "Funcionalidade disponível apenas com pywin32 instalado.")
            return
        
        # Diálogo de configuração
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurar Página")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Configurações de Página", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Tamanho do papel
        papel_frame = tk.Frame(frame)
        papel_frame.pack(fill=tk.X, pady=5)
        tk.Label(papel_frame, text="Tamanho do Papel:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        papel_combo = ttk.Combobox(papel_frame, 
                                   values=["A4", "A3", "A5", "Carta", "Ofício", "Legal"], 
                                   width=10)
        papel_combo.pack(side=tk.LEFT)
        papel_combo.set(self.configuracoes["formato_papel"])
        
        # Fechar
        tk.Button(frame, text="Fechar", command=dialog.destroy).pack(pady=(20, 0))
    
    def visualizar_impressao(self):
        """Visualizar como ficará a impressão"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhuma imagem para visualizar!")
            return
        
        # Criar janela de visualização
        preview = tk.Toplevel(self.root)
        preview.title("Visualizar Impressão")
        preview.geometry("600x800")
        preview.transient(self.root)
        
        frame = tk.Frame(preview, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Visualização de Impressão", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Informações
        info_text = (
            f"Imagem: {self.imagem_editada.width} x {self.imagem_editada.height} pixels\n"
            f"Qualidade: {self.configuracoes['qualidade_impressao']} DPI\n"
            f"Tamanho impresso: {self.imagem_editada.width/self.configuracoes['qualidade_impressao']:.1f}\" x "
            f"{self.imagem_editada.height/self.configuracoes['qualidade_impressao']:.1f}\"\n"
            f"Orientação: {self.configuracoes['orientacao']}\n"
            f"Margens: E:{self.configuracoes['margens'][0]}cm D:{self.configuracoes['margens'][1]}cm "
            f"T:{self.configuracoes['margens'][2]}cm B:{self.configuracoes['margens'][3]}cm"
        )
        
        tk.Label(frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        # Miniatura da imagem
        preview_width = 500
        preview_height = 500
        
        # Redimensionar para preview
        img_preview = self.imagem_editada.copy()
        img_preview.thumbnail((preview_width, preview_height), Image.Resampling.LANCZOS)
        
        # Adicionar bordas simulando margens
        preview_img = Image.new('RGB', (preview_width + 40, preview_height + 40), 'white')
        preview_img.paste(img_preview, (20, 20))
        
        preview_tk = ImageTk.PhotoImage(preview_img)
        preview_label = tk.Label(frame, image=preview_tk)
        preview_label.image = preview_tk
        preview_label.pack()
        
        tk.Button(frame, text="Fechar", command=preview.destroy).pack(pady=10)
    
    # ========== FUNÇÕES DE IMPORTAÇÃO/EXPORTAÇÃO (existentes) ==========
    
    def importar_imagem(self):
        """Importar imagem para o projeto atual"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Crie ou abra um projeto primeiro!")
            return
        
        file_path = filedialog.askopenfilename(
            filetypes=[("Arquivos de imagem", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff")]
        )
        
        if file_path:
            try:
                img_importada = Image.open(file_path)
                
                # Perguntar como importar
                resposta = messagebox.askyesno(
                    "Importar Imagem",
                    "Deseja importar como nova camada?\n"
                    "Sim = Nova camada\n"
                    "Não = Substituir imagem atual"
                )
                
                if resposta:  # Nova camada
                    # Combinar imagens
                    if img_importada.mode != self.imagem_editada.mode:
                        img_importada = img_importada.convert(self.imagem_editada.mode)
                    
                    # Criar nova imagem combinada
                    nova_largura = max(self.imagem_editada.width, img_importada.width)
                    nova_altura = max(self.imagem_editada.height, img_importada.height)
                    
                    nova_imagem = Image.new(self.imagem_editada.mode, (nova_largura, nova_altura), 
                                           (255, 255, 255) if self.imagem_editada.mode == 'RGB' else (0,0,0,0))
                    
                    nova_imagem.paste(self.imagem_editada, (0, 0))
                    
                    if img_importada.mode == 'RGBA':
                        nova_imagem.paste(img_importada, (0, 0), img_importada)
                    else:
                        nova_imagem.paste(img_importada, (0, 0))
                    
                    self.imagem_editada = nova_imagem
                    self.imagem_original = nova_imagem.copy()
                    
                else:  # Substituir
                    self.imagem_editada = img_importada
                    self.imagem_original = img_importada.copy()
                
                self.salvar_no_historico()
                self.marcar_alteracao()
                self.ajustar_tela()
                self.atualizar_visualizacao()
                self.status_label.config(text=f"Imagem importada: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível importar: {str(e)}")
    
    def exportar_imagem(self):
        """Exportar imagem em formato específico"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhuma imagem para exportar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("BMP", "*.bmp"),
                ("GIF", "*.gif"),
                ("TIFF", "*.tiff"),
                ("ICO", "*.ico")
            ]
        )
        
        if file_path:
            try:
                # Configurações de exportação
                if file_path.lower().endswith('.jpg'):
                    # Para JPG, perguntar qualidade
                    qualidade = simpledialog.askinteger("Qualidade", 
                                                        "Qualidade (1-100):",
                                                        minvalue=1, maxvalue=100,
                                                        initialvalue=95)
                    if qualidade:
                        img_export = self.imagem_editada
                        if img_export.mode == 'RGBA':
                            # Converter para RGB com fundo branco
                            bg = Image.new('RGB', img_export.size, (255, 255, 255))
                            bg.paste(img_export, mask=img_export.split()[3])
                            img_export = bg
                        img_export.save(file_path, quality=qualidade)
                
                elif file_path.lower().endswith('.png'):
                    self.imagem_editada.save(file_path, optimize=True)
                
                else:
                    self.imagem_editada.save(file_path)
                
                self.status_label.config(text=f"Imagem exportada: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exportar: {str(e)}")
    
    def exportar_configuracoes(self):
        """Exportar configurações do editor"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                config_export = {
                    "configuracoes": self.configuracoes,
                    "ultima_cor": self.cor_atual,
                    "tamanho_pincel": self.tamanho_pincel
                }
                
                with open(file_path, 'w') as f:
                    json.dump(config_export, f, indent=4)
                
                messagebox.showinfo("Sucesso", "Configurações exportadas!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar: {str(e)}")
    
    def importar_configuracoes(self):
        """Importar configurações do editor"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config_import = json.load(f)
                
                self.configuracoes.update(config_import.get("configuracoes", {}))
                self.cor_atual = config_import.get("ultima_cor", self.cor_atual)
                self.tamanho_pincel = config_import.get("tamanho_pincel", self.tamanho_pincel)
                
                # Atualizar interface
                self.btn_cor.config(bg=self.cor_atual)
                self.tamanho_scale.set(self.tamanho_pincel)
                
                messagebox.showinfo("Sucesso", "Configurações importadas!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao importar: {str(e)}")
    
    # ========== FUNÇÕES DE EDIÇÃO ADICIONAIS ==========
    
    def duplicar_selecao(self):
        """Duplicar área selecionada"""
        if self.area_selecionada:
            # Criar cópia da seleção
            copia = self.area_selecionada.copy()
            
            # Posicionar ao lado
            x = self.area_selecionada.width + 10
            y = 10
            
            if self.imagem_editada.mode == 'RGBA' and copia.mode == 'RGBA':
                self.imagem_editada.paste(copia, (x, y), copia)
            else:
                self.imagem_editada.paste(copia, (x, y))
            
            self.marcar_alteracao()
            self.atualizar_visualizacao()
            self.status_label.config(text="Seleção duplicada")
    
    def selecionar_tudo(self):
        """Selecionar toda a imagem"""
        if self.imagem_editada:
            self.selecao_inicio = (0, 0)
            self.selecao_fim = (self.imagem_editada.width - 1, self.imagem_editada.height - 1)
            self.selecao_ativa = False
            self.btn_limpar_selecao.config(state=tk.NORMAL)
            
            # Copiar área para área selecionada
            self.area_selecionada = self.imagem_editada.copy()
            
            # Mostrar retângulo de seleção
            if self.rect_selecao:
                self.canvas.delete(self.rect_selecao)
            
            canvas_coords1 = self.image_to_canvas_coords(0, 0)
            canvas_coords2 = self.image_to_canvas_coords(self.imagem_editada.width - 1, 
                                                         self.imagem_editada.height - 1)
            
            self.rect_selecao = self.canvas.create_rectangle(
                canvas_coords1[0], canvas_coords1[1],
                canvas_coords2[0], canvas_coords2[1],
                outline='red', width=2, dash=(5, 5)
            )
            
            self.status_label.config(text="Imagem toda selecionada")
    
    def toggle_fullscreen(self, event=None):
        """Alternar modo tela cheia"""
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))
    
    def toggle_grade(self):
        """Mostrar/ocultar grade (placeholder)"""
        messagebox.showinfo("Grade", "Funcionalidade em desenvolvimento")
    
    def toggle_regua(self):
        """Mostrar/ocultar régua (placeholder)"""
        messagebox.showinfo("Régua", "Funcionalidade em desenvolvimento")
    
    def configurar_ferramentas(self):
        """Configurar ferramentas do editor"""
        messagebox.showinfo("Configurar Ferramentas", "Funcionalidade em desenvolvimento")
    
    def gerenciar_cores(self):
        """Gerenciar paleta de cores"""
        messagebox.showinfo("Gerenciar Cores", "Funcionalidade em desenvolvimento")
    
    def mostrar_tutoriais(self):
        """Mostrar tutoriais"""
        tutorial_text = (
            "Tutoriais PaintWazzima:\n\n"
            "1. Primeiros Passos:\n"
            "   • Crie um novo projeto em Arquivo > Novo Projeto\n"
            "   • Escolha o tamanho e cor de fundo\n"
            "   • Use as ferramentas na toolbar\n\n"
            "2. Trabalhando com Efeitos:\n"
            "   • Acesse o menu Efeitos para aplicar filtros\n"
            "   • Cores: Inverter, Escala de Cinza, Sépia\n"
            "   • Filtros: Desfoque, Bordas, Realce\n"
            "   • Transformações: Rotacionar, Espelhar\n"
            "   • Especiais: Transparência, Pixelizar, Mosaico\n\n"
            "3. Trabalhando com Projetos:\n"
            "   • Salve seu trabalho como .paintwazzima\n"
            "   • Use o histórico de versões para acompanhar alterações\n"
            "   • Exporte como modelo para reutilizar configurações\n\n"
            "4. Impressão:\n"
            "   • Configure a página antes de imprimir\n"
            "   • Use a visualização para ver o resultado\n"
            "   • Ajuste DPI e margens conforme necessário\n\n"
            "5. Dicas:\n"
            "   • Use Ctrl+Z para desfazer efeitos\n"
            "   • Use Ctrl+ para zoom in/out\n"
            "   • Botão direito arrasta para navegar\n"
            "   • Projetos salvam todas as configurações"
        )
        messagebox.showinfo("Tutoriais", tutorial_text)
    
    # ========== FUNÇÕES DE VERIFICAÇÃO DE ALTERAÇÕES ==========
    
    def verificar_alteracoes_nao_salvas(self):
        """Verificar se há alterações não salvas e perguntar ao usuário"""
        if self.imagem_editada and self.houve_alteracao:
            resposta = messagebox.askyesnocancel(
                "Alterações não salvas",
                "Há alterações não salvas. Deseja salvá-las antes de continuar?"
            )
            if resposta is True:  # Sim
                if self.project_file:
                    self.salvar_projeto()
                else:
                    self.salvar_projeto_como()
                return True
            elif resposta is False:  # Não
                return True
            else:  # Cancelar
                return False
        return True
    
    def marcar_alteracao(self):
        """Marcar que houve alteração na imagem"""
        if self.imagem_editada:
            self.houve_alteracao = True
            self.modified_label.config(text="*Modificado*")
    
    def limpar_marcador_alteracao(self):
        """Limpar marcador de alteração (após salvar)"""
        self.houve_alteracao = False
        self.modified_label.config(text="")
    
    # ========== FUNÇÕES DE ARQUIVO (completas) ==========

    def nova_imagem(self):
        """Criar uma nova imagem em branco com tamanho personalizado"""
        if not self.verificar_alteracoes_nao_salvas():
            return
        
        self._nova_imagem_dialog()

    def _nova_imagem_dialog(self):
        """Diálogo para nova imagem"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nova Imagem")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar o diálogo
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (450 // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (400 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Frame principal
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        tk.Label(frame, text="Criar Nova Imagem", font=("Arial", 12, "bold")).pack(pady=(0, 15))
        
        # Informação de limites
        limites_text = f"Limites:\nLargura: até {self.MAX_LARGURA}px\nAltura: até {self.MAX_ALTURA}px\nMáx: {self.MAX_MEGAPIXELS} megapixels"
        tk.Label(frame, text=limites_text, justify=tk.LEFT, fg='gray').pack(anchor=tk.W, pady=(0, 15))
        
        # Largura
        largura_frame = tk.Frame(frame)
        largura_frame.pack(fill=tk.X, pady=5)
        tk.Label(largura_frame, text="Largura (px):", width=15, anchor=tk.W).pack(side=tk.LEFT)
        largura_entry = tk.Entry(largura_frame, width=15)
        largura_entry.pack(side=tk.LEFT)
        largura_entry.insert(0, "800")
        
        # Altura
        altura_frame = tk.Frame(frame)
        altura_frame.pack(fill=tk.X, pady=5)
        tk.Label(altura_frame, text="Altura (px):", width=15, anchor=tk.W).pack(side=tk.LEFT)
        altura_entry = tk.Entry(altura_frame, width=15)
        altura_entry.pack(side=tk.LEFT)
        altura_entry.insert(0, "600")
        
        # Cor de fundo
        cor_frame = tk.Frame(frame)
        cor_frame.pack(fill=tk.X, pady=5)
        tk.Label(cor_frame, text="Cor de fundo:", width=15, anchor=tk.W).pack(side=tk.LEFT)
        
        fundo_cor = "#FFFFFF"
        btn_cor_fundo = tk.Button(cor_frame, text="  ", bg=fundo_cor, 
                                  command=lambda: self._escolher_cor_nova_imagem(btn_cor_fundo))
        btn_cor_fundo.pack(side=tk.LEFT)
        
        # Opção de fundo transparente (para PNG)
        transparente_var = tk.BooleanVar()
        tk.Checkbutton(cor_frame, text="Transparente", variable=transparente_var).pack(side=tk.LEFT, padx=(10,0))
        
        # Botões
        botoes_frame = tk.Frame(frame)
        botoes_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Button(botoes_frame, text="Criar Imagem", 
                 command=lambda: self._criar_imagem_dialog(
                     largura_entry.get(), altura_entry.get(), 
                     btn_cor_fundo.cget('bg'), transparente_var.get(), dialog
                 )).pack(side=tk.LEFT, padx=5)
        
        tk.Button(botoes_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def _escolher_cor_nova_imagem(self, botao):
        """Escolher cor de fundo para nova imagem"""
        cor = colorchooser.askcolor(title="Cor de Fundo")
        if cor[1]:
            botao.config(bg=cor[1])

    def _criar_imagem_dialog(self, largura_str, altura_str, cor_fundo, transparente, dialog):
        """Criar imagem a partir do diálogo"""
        try:
            largura = int(largura_str)
            altura = int(altura_str)
            
            # Validações
            if largura <= 0 or altura <= 0:
                messagebox.showerror("Erro", "Largura e altura devem ser maiores que zero!")
                return
            
            if largura > self.MAX_LARGURA or altura > self.MAX_ALTURA:
                messagebox.showerror("Erro", f"Dimensões máximas: {self.MAX_LARGURA}x{self.MAX_ALTURA}")
                return
            
            # Verificar megapixels
            megapixels = (largura * altura) / 1_000_000
            if megapixels > self.MAX_MEGAPIXELS:
                resposta = messagebox.askyesno(
                    "Aviso de Memória",
                    f"Esta imagem terá {megapixels:.1f} megapixels, o que pode consumir muita memória.\n"
                    f"Limite recomendado: {self.MAX_MEGAPIXELS} megapixels.\n\n"
                    f"Deseja continuar mesmo assim?"
                )
                if not resposta:
                    return
            
            # Criar imagem
            if transparente:
                self.imagem_original = Image.new('RGBA', (largura, altura), (0, 0, 0, 0))
            else:
                cor_rgb = self.hex_para_rgb(cor_fundo)
                self.imagem_original = Image.new('RGB', (largura, altura), cor_rgb)
            
            self.imagem_editada = self.imagem_original.copy()
            self.current_file = None
            self.project_file = None
            self.project_metadata = {
                "nome": "Nova Imagem",
                "data_criacao": datetime.datetime.now().isoformat(),
                "autor": "Usuário",
                "descricao": "",
                "versoes": []
            }
            
            # Limpar histórico e salvar estado
            self.historico = []
            self.salvar_no_historico()
            
            self.limpar_selecao()
            self.limpar_marcador_alteracao()
            self.ajustar_tela()
            
            # Atualizar interface
            self.project_label.config(text="")
            modo = "transparente" if transparente else f"fundo {cor_fundo}"
            self.status_label.config(text=f"Nova imagem criada: {largura}x{altura} pixels, {modo}")
            
            dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira números válidos!")

    def abrir_imagem(self):
        """Abrir uma imagem do disco"""
        if not self.verificar_alteracoes_nao_salvas():
            return
        
        file_path = filedialog.askopenfilename(
            title="Abrir Imagem",
            filetypes=[
                ("Arquivos de imagem", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Verificar tamanho do arquivo
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                if file_size > 100:  # Mais de 100MB
                    resposta = messagebox.askyesno(
                        "Arquivo Grande",
                        f"Este arquivo tem {file_size:.1f}MB e pode consumir muita memória.\n"
                        f"Deseja continuar?"
                    )
                    if not resposta:
                        return
                
                self.imagem_original = Image.open(file_path)
                
                # Converter para RGB se necessário
                if self.imagem_original.mode not in ('RGB', 'RGBA'):
                    self.imagem_original = self.imagem_original.convert('RGB')
                
                # Verificar dimensões
                largura, altura = self.imagem_original.size
                megapixels = (largura * altura) / 1_000_000
                
                if megapixels > self.MAX_MEGAPIXELS:
                    resposta = messagebox.askyesno(
                        "Imagem Muito Grande",
                        f"Esta imagem tem {megapixels:.1f} megapixels ({largura}x{altura}).\n"
                        f"Isso pode consumir muita memória e causar lentidão.\n\n"
                        f"Deseja reduzir o tamanho automaticamente?"
                    )
                    if resposta:
                        # Redimensionar para um tamanho gerenciável
                        fator_redimensionamento = (self.MAX_MEGAPIXELS / megapixels) ** 0.5
                        nova_largura = int(largura * fator_redimensionamento)
                        nova_altura = int(altura * fator_redimensionamento)
                        self.imagem_original = self.imagem_original.resize(
                            (nova_largura, nova_altura), Image.Resampling.LANCZOS
                        )
                        messagebox.showinfo(
                            "Imagem Redimensionada",
                            f"Imagem redimensionada para {nova_largura}x{nova_altura}"
                        )
                
                self.imagem_editada = self.imagem_original.copy()
                self.current_file = file_path
                self.project_file = None
                self.project_metadata = {
                    "nome": os.path.basename(file_path),
                    "data_criacao": datetime.datetime.now().isoformat(),
                    "autor": "Usuário",
                    "descricao": "",
                    "versoes": []
                }
                
                # Limpar histórico e salvar estado
                self.historico = []
                self.salvar_no_historico()
                
                self.limpar_selecao()
                self.limpar_marcador_alteracao()
                self.ajustar_tela()
                
                self.project_label.config(text="")
                self.status_label.config(text=f"Imagem carregada: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir a imagem: {str(e)}")

    def salvar_imagem(self):
        """Salvar a imagem atual"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhuma imagem para salvar!")
            return
        
        if self.current_file:
            try:
                # Se for salvar como JPG e a imagem tiver transparência, converter para RGB
                if self.current_file.lower().endswith(('.jpg', '.jpeg')) and self.imagem_editada.mode == 'RGBA':
                    img_salvar = Image.new('RGB', self.imagem_editada.size, (255, 255, 255))
                    img_salvar.paste(self.imagem_editada, mask=self.imagem_editada.split()[3])
                else:
                    img_salvar = self.imagem_editada
                
                img_salvar.save(self.current_file)
                self.limpar_marcador_alteracao()
                self.status_label.config(text=f"Imagem salva: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar: {str(e)}")
        else:
            self.salvar_imagem_como()

    def salvar_imagem_como(self):
        """Salvar a imagem em um novo arquivo"""
        if not self.imagem_editada:
            messagebox.showwarning("Aviso", "Nenhuma imagem para salvar!")
            return
        
        # Determinar extensão padrão baseada no modo da imagem
        if self.imagem_editada.mode == 'RGBA':
            default_ext = ".png"
            filetypes = [("PNG", "*.png"), ("JPEG", "*.jpg"), ("BMP", "*.bmp")]
        else:
            default_ext = ".jpg"
            filetypes = [("JPEG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")]
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes
        )
        
        if file_path:
            try:
                # Se for salvar como JPG e a imagem tiver transparência, converter para RGB
                if file_path.lower().endswith(('.jpg', '.jpeg')) and self.imagem_editada.mode == 'RGBA':
                    img_salvar = Image.new('RGB', self.imagem_editada.size, (255, 255, 255))
                    img_salvar.paste(self.imagem_editada, mask=self.imagem_editada.split()[3])
                else:
                    img_salvar = self.imagem_editada
                
                img_salvar.save(file_path)
                self.current_file = file_path
                self.project_file = None
                self.limpar_marcador_alteracao()
                self.status_label.config(text=f"Imagem salva: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível salvar: {str(e)}")
    
    def reset_imagem(self):
        """Resetar para a imagem original"""
        if self.imagem_original:
            self.imagem_editada = self.imagem_original.copy()
            self.salvar_no_historico()
            self.limpar_selecao()
            self.marcar_alteracao()
            self.atualizar_visualizacao()
            self.status_label.config(text="Imagem resetada")
    
    def sair_aplicacao(self):
        """Sair da aplicação com verificação de alterações não salvas"""
        if self.verificar_alteracoes_nao_salvas():
            self.root.quit()
            self.root.destroy()
    
    # ========== FUNÇÕES DE ZOOM E PAN (existentes) ==========
    
    def zoom_in(self):
        """Aumentar zoom"""
        if self.imagem_editada:
            self.fator_zoom = min(self.fator_zoom * 1.2, self.zoom_maximo)
            self.atualizar_visualizacao()
    
    def zoom_out(self):
        """Diminuir zoom"""
        if self.imagem_editada:
            self.fator_zoom = max(self.fator_zoom * 0.8, self.zoom_minimo)
            self.atualizar_visualizacao()
    
    def zoom_100(self):
        """Zoom 100% (tamanho real)"""
        if self.imagem_editada:
            self.fator_zoom = 1.0
            self.offset_x = 0
            self.offset_y = 0
            self.atualizar_visualizacao()
    
    def ajustar_tela(self):
        """Ajustar imagem para caber na tela"""
        if self.imagem_editada:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_width, img_height = self.imagem_editada.size
                zoom_largura = canvas_width / img_width
                zoom_altura = canvas_height / img_height
                self.fator_zoom = min(zoom_largura, zoom_altura) * 0.9  # 90% para dar margem
                self.offset_x = 0
                self.offset_y = 0
                self.atualizar_visualizacao()
    
    def zoom_roda(self, event):
        """Zoom com a roda do mouse"""
        if self.imagem_editada:
            # Posição do mouse antes do zoom
            x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
            
            # Fator de zoom
            if event.num == 4 or event.delta > 0:  # Scroll up
                self.fator_zoom = min(self.fator_zoom * 1.1, self.zoom_maximo)
            elif event.num == 5 or event.delta < 0:  # Scroll down
                self.fator_zoom = max(self.fator_zoom * 0.9, self.zoom_minimo)
            
            self.atualizar_visualizacao()
    
    def iniciar_pan(self, event):
        """Iniciar movimento de pan (arrastar com botão direito)"""
        self.arrastando = True
        self.ultimo_pan_x = event.x
        self.ultimo_pan_y = event.y
        self.canvas.config(cursor="fleur")
    
    def fazer_pan(self, event):
        """Executar movimento de pan"""
        if self.arrastando and self.imagem_editada:
            dx = event.x - self.ultimo_pan_x
            dy = event.y - self.ultimo_pan_y
            
            self.offset_x += dx
            self.offset_y += dy
            
            self.ultimo_pan_x = event.x
            self.ultimo_pan_y = event.y
            
            self.atualizar_visualizacao()
    
    def parar_pan(self, event):
        """Parar movimento de pan"""
        self.arrastando = False
        self.canvas.config(cursor="cross")
    
    # ========== FUNÇÕES DE FERRAMENTAS ==========
    
    def selecionar_ferramenta(self, ferramenta):
        """Selecionar ferramenta ativa"""
        self.ferramenta_atual = ferramenta
        
        # Reset botões
        self.btn_selecao.config(bg='#f0f0f0')
        self.btn_caneta.config(bg='#f0f0f0')
        self.btn_borracha.config(bg='#f0f0f0')
        
        # Destacar ferramenta selecionada
        if ferramenta == "selecao":
            self.btn_selecao.config(bg='#c0c0c0')
            self.canvas.config(cursor="cross")
            self.status_label.config(text=f"Pronto | Ferramenta: Seleção")
        elif ferramenta == "caneta":
            self.btn_caneta.config(bg='#c0c0c0')
            self.canvas.config(cursor="pencil")
            self.status_label.config(text=f"Pronto | Ferramenta: Caneta")
        elif ferramenta == "borracha":
            self.btn_borracha.config(bg='#c0c0c0')
            self.canvas.config(cursor="dot")
            self.status_label.config(text=f"Pronto | Ferramenta: Borracha")
    
    def escolher_cor(self):
        """Abrir seletor de cor para a caneta"""
        cor = colorchooser.askcolor(title="Escolha uma cor", color=self.cor_atual)
        if cor[1]:
            self.cor_atual = cor[1]
            self.btn_cor.config(bg=self.cor_atual)
            # Ajustar cor do texto para contraste
            if self.cor_atual.lower() in ['#000000', '#000']:
                self.btn_cor.config(fg='white')
            else:
                self.btn_cor.config(fg='black')
    
    def ajustar_tamanho(self, value):
        """Ajustar tamanho do pincel/borracha"""
        self.tamanho_pincel = int(value)
    
    # ========== FUNÇÕES DE DESENHO ==========
    
    def on_mouse_down(self, event):
        """Evento de clique do mouse"""
        if not self.imagem_editada:
            return
        
        # Ajustar coordenadas considerando zoom e pan
        x, y = self.canvas_to_image_coords(event.x, event.y)
        
        # Verificar se está dentro da imagem
        if x < 0 or x >= self.imagem_editada.width or y < 0 or y >= self.imagem_editada.height:
            return
        
        if self.ferramenta_atual == "selecao":
            # Iniciar seleção
            self.selecao_ativa = True
            self.selecao_inicio = (x, y)
            
            # Remover retângulo de seleção anterior
            if self.rect_selecao:
                self.canvas.delete(self.rect_selecao)
                self.rect_selecao = None
        
        elif self.ferramenta_atual in ["caneta", "borracha"]:
            # Iniciar desenho
            self.desenho_ativo = True
            self.ultimo_x = x
            self.ultimo_y = y
            self.desenhar_ponto(x, y)
    
    def on_mouse_move(self, event):
        """Evento de movimento com mouse pressionado"""
        if not self.imagem_editada:
            return
        
        x, y = self.canvas_to_image_coords(event.x, event.y)
        
        # Verificar se está dentro da imagem
        if x < 0 or x >= self.imagem_editada.width or y < 0 or y >= self.imagem_editada.height:
            return
        
        if self.ferramenta_atual == "selecao" and self.selecao_ativa and self.selecao_inicio:
            # Atualizar retângulo de seleção
            if self.rect_selecao:
                self.canvas.delete(self.rect_selecao)
            
            # Desenhar retângulo temporário
            canvas_coords = self.image_to_canvas_coords(self.selecao_inicio[0], self.selecao_inicio[1])
            current_coords = self.image_to_canvas_coords(x, y)
            
            self.rect_selecao = self.canvas.create_rectangle(
                canvas_coords[0], canvas_coords[1],
                current_coords[0], current_coords[1],
                outline='red', width=2, dash=(5, 5)
            )
        
        elif self.ferramenta_atual in ["caneta", "borracha"] and self.desenho_ativo and self.ultimo_x is not None:
            # Desenhar linha entre último ponto e ponto atual
            self.desenhar_linha(self.ultimo_x, self.ultimo_y, x, y)
            self.ultimo_x = x
            self.ultimo_y = y
    
    def on_mouse_up(self, event):
        """Evento de soltar o mouse"""
        if not self.imagem_editada:
            return
        
        x, y = self.canvas_to_image_coords(event.x, event.y)
        
        if self.ferramenta_atual == "selecao" and self.selecao_ativa and self.selecao_inicio:
            # Finalizar seleção
            self.selecao_fim = (x, y)
            
            # Verificar se a seleção é válida (não é apenas um ponto)
            if (abs(self.selecao_fim[0] - self.selecao_inicio[0]) > 5 and
                abs(self.selecao_fim[1] - self.selecao_inicio[1]) > 5):
                self.selecao_ativa = False
                self.btn_limpar_selecao.config(state=tk.NORMAL)
                
                # Calcular área selecionada
                x1 = min(self.selecao_inicio[0], self.selecao_fim[0])
                y1 = min(self.selecao_inicio[1], self.selecao_fim[1])
                x2 = max(self.selecao_inicio[0], self.selecao_fim[0])
                y2 = max(self.selecao_inicio[1], self.selecao_fim[1])
                
                self.area_selecionada = self.imagem_editada.crop((x1, y1, x2, y2))
                
                self.status_label.config(text="Área selecionada. Use os botões de transformação.")
            else:
                self.limpar_selecao()
        
        elif self.ferramenta_atual in ["caneta", "borracha"]:
            if self.desenho_ativo:
                self.salvar_no_historico()
            self.desenho_ativo = False
            self.ultimo_x = None
            self.ultimo_y = None
    
    def on_mouse_over(self, event):
        """Evento de movimento do mouse (sem pressionar)"""
        if self.imagem_editada:
            x, y = self.canvas_to_image_coords(event.x, event.y)
            if 0 <= x < self.imagem_editada.width and 0 <= y < self.imagem_editada.height:
                self.coord_label.config(text=f" X:{x}, Y:{y}")
    
    def canvas_to_image_coords(self, canvas_x, canvas_y):
        """Converter coordenadas do canvas para coordenadas da imagem considerando zoom e pan"""
        if not self.imagem_editada:
            return (0, 0)
        
        # Ajustar para o centro e zoom
        canvas_center_x = self.canvas.winfo_width() / 2
        canvas_center_y = self.canvas.winfo_height() / 2
        
        # Calcular posição relativa ao centro com zoom
        rel_x = (canvas_x - canvas_center_x - self.offset_x) / self.fator_zoom
        rel_y = (canvas_y - canvas_center_y - self.offset_y) / self.fator_zoom
        
        # Converter para coordenadas da imagem
        img_x = int(rel_x + self.imagem_editada.width / 2)
        img_y = int(rel_y + self.imagem_editada.height / 2)
        
        return (img_x, img_y)
    
    def image_to_canvas_coords(self, img_x, img_y):
        """Converter coordenadas da imagem para coordenadas do canvas considerando zoom e pan"""
        if not self.imagem_editada:
            return (0, 0)
        
        canvas_center_x = self.canvas.winfo_width() / 2
        canvas_center_y = self.canvas.winfo_height() / 2
        
        # Calcular posição relativa ao centro da imagem
        rel_x = (img_x - self.imagem_editada.width / 2) * self.fator_zoom
        rel_y = (img_y - self.imagem_editada.height / 2) * self.fator_zoom
        
        # Adicionar offset e centro do canvas
        canvas_x = canvas_center_x + rel_x + self.offset_x
        canvas_y = canvas_center_y + rel_y + self.offset_y
        
        return (canvas_x, canvas_y)
    
    def desenhar_ponto(self, x, y):
        """Desenhar um ponto na imagem"""
        if not self.imagem_editada:
            return
        
        # Criar uma cópia para desenhar
        img_copy = self.imagem_editada.copy()
        draw = ImageDraw.Draw(img_copy)
        
        if self.ferramenta_atual == "caneta":
            cor = self.cor_atual
        else:  # borracha
            if self.imagem_editada.mode == 'RGBA':
                cor = (0, 0, 0, 0)  # transparente
            else:
                cor = (255, 255, 255)  # branco
        
        # Desenhar círculo
        raio = self.tamanho_pincel // 2
        draw.ellipse(
            [x - raio, y - raio, x + raio, y + raio],
            fill=cor, outline=cor
        )
        
        self.imagem_editada = img_copy
        self.marcar_alteracao()
        self.atualizar_visualizacao()
    
    def desenhar_linha(self, x1, y1, x2, y2):
        """Desenhar uma linha entre dois pontos"""
        if not self.imagem_editada:
            return
        
        img_copy = self.imagem_editada.copy()
        draw = ImageDraw.Draw(img_copy)
        
        if self.ferramenta_atual == "caneta":
            cor = self.cor_atual
        else:  # borracha
            if self.imagem_editada.mode == 'RGBA':
                cor = (0, 0, 0, 0)  # transparente
            else:
                cor = (255, 255, 255)  # branco
        
        # Desenhar linha
        draw.line([x1, y1, x2, y2], fill=cor, width=self.tamanho_pincel)
        
        self.imagem_editada = img_copy
        self.marcar_alteracao()
        self.atualizar_visualizacao()
    
    # ========== FUNÇÕES DE SELEÇÃO ==========
    
    def limpar_selecao(self):
        """Limpar a área de seleção atual"""
        self.selecao_ativa = False
        self.selecao_inicio = None
        self.selecao_fim = None
        self.area_selecionada = None
        if self.rect_selecao:
            self.canvas.delete(self.rect_selecao)
            self.rect_selecao = None
        self.btn_limpar_selecao.config(state=tk.DISABLED)
        self.status_label.config(text="Seleção limpa")
    
    def recortar_selecao(self):
        """Recortar a área selecionada"""
        if self.area_selecionada:
            self.salvar_no_historico()
            self.imagem_editada = self.area_selecionada.copy()
            self.imagem_original = self.imagem_editada.copy()
            self.limpar_selecao()
            self.marcar_alteracao()
            self.ajustar_tela()
            self.atualizar_visualizacao()
            self.status_label.config(text="Imagem recortada")
    
    def copiar_selecao(self):
        """Copiar a área selecionada"""
        if self.area_selecionada:
            # Já temos a área selecionada armazenada
            self.status_label.config(text="Área copiada")
        else:
            messagebox.showwarning("Aviso", "Nenhuma área selecionada!")
    
    def colar_selecao(self):
        """Colar a área copiada"""
        if self.area_selecionada and self.imagem_editada:
            self.salvar_no_historico()
            # Criar uma nova imagem com a área colada no centro
            nova_imagem = self.imagem_editada.copy()
            
            # Calcular posição central
            x = (nova_imagem.width - self.area_selecionada.width) // 2
            y = (nova_imagem.height - self.area_selecionada.height) // 2
            
            # Colar com suporte a transparência
            if nova_imagem.mode == 'RGBA' and self.area_selecionada.mode == 'RGBA':
                nova_imagem.paste(self.area_selecionada, (x, y), self.area_selecionada)
            else:
                nova_imagem.paste(self.area_selecionada, (x, y))
            
            self.imagem_editada = nova_imagem
            self.marcar_alteracao()
            self.atualizar_visualizacao()
            self.status_label.config(text="Área colada")
    
    # ========== FUNÇÕES DE VISUALIZAÇÃO ==========
    
    def atualizar_visualizacao(self):
        """Atualizar a imagem no canvas considerando zoom e pan"""
        if self.imagem_editada:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_width, img_height = self.imagem_editada.size
                
                # Calcular tamanho com zoom
                display_width = int(img_width * self.fator_zoom)
                display_height = int(img_height * self.fator_zoom)
                
                # Redimensionar imagem
                img_resized = self.imagem_editada.resize((display_width, display_height), Image.Resampling.LANCZOS)
                self.imagem_tk = ImageTk.PhotoImage(img_resized)
                
                # Limpar canvas
                self.canvas.delete("all")
                
                # Calcular posição centralizada com offset
                center_x = canvas_width // 2 + self.offset_x
                center_y = canvas_height // 2 + self.offset_y
                
                # Mostrar imagem
                self.canvas.create_image(
                    center_x, center_y,
                    image=self.imagem_tk,
                    anchor=tk.CENTER
                )
                
                # Redesenhar retângulo de seleção se existir
                if self.selecao_inicio and self.selecao_fim and not self.selecao_ativa:
                    canvas_coords1 = self.image_to_canvas_coords(self.selecao_inicio[0], self.selecao_inicio[1])
                    canvas_coords2 = self.image_to_canvas_coords(self.selecao_fim[0], self.selecao_fim[1])
                    
                    self.rect_selecao = self.canvas.create_rectangle(
                        canvas_coords1[0], canvas_coords1[1],
                        canvas_coords2[0], canvas_coords2[1],
                        outline='red', width=2, dash=(5, 5)
                    )
                
                # Atualizar label de zoom
                self.zoom_label.config(text=f"{int(self.fator_zoom * 100)}%")
                
                # Atualizar label de tamanho
                megapixels = (img_width * img_height) / 1_000_000
                modo = self.imagem_editada.mode
                self.size_label.config(
                    text=f" {img_width}x{img_height} | {modo} | {megapixels:.1f} MP"
                )
    
    # ========== FUNÇÕES DE INFORMAÇÃO ==========
    
    def mostrar_propriedades(self):
        """Mostrar propriedades da imagem atual"""
        if not self.imagem_editada:
            messagebox.showinfo("Propriedades", "Nenhuma imagem carregada.")
            return
        
        largura, altura = self.imagem_editada.size
        modo = self.imagem_editada.mode
        formato = self.current_file.split('.')[-1].upper() if self.current_file else "Não salvo"
        megapixels = (largura * altura) / 1_000_000
        memoria_kb = (largura * altura * len(self.imagem_editada.getbands())) / 1024
        
        propriedades = (
            f"Propriedades da Imagem:\n\n"
            f"Dimensões: {largura} x {altura} pixels\n"
            f"Megapixels: {megapixels:.2f} MP\n"
            f"Modo de cor: {modo}\n"
            f"Formato: {formato}\n"
            f"Tamanho aproximado em memória: {memoria_kb:.1f} KB\n"
            f"Arquivo: {self.current_file if self.current_file else 'Não salvo'}"
        )
        
        messagebox.showinfo("Propriedades da Imagem", propriedades)
    
    def hex_para_rgb(self, hex_cor):
        """Converter cor hexadecimal para tupla RGB"""
        hex_cor = hex_cor.lstrip('#')
        return tuple(int(hex_cor[i:i+2], 16) for i in (0, 2, 4))
    
    def mostrar_sobre(self):
        """Mostrar informações sobre o editor"""
        sobre_text = (
            "PaintWazzima Editor de Imagens\n\n"
            "Versão: 4.0 (com Efeitos)\n\n"
            "Funcionalidades:\n"
            "• Projetos .paintwazzima com metadados\n"
            "• Criar novas imagens com tamanho personalizado\n"
            "• Abrir e salvar imagens\n"
            "• Ferramentas de desenho (caneta, borracha)\n"
            "• Ferramenta de seleção\n"
            "• Recortar, copiar e colar\n"
            "• Zoom e pan (navegação)\n"
            "• Impressão com configurações\n"
            "• Histórico de versões\n"
            "• Exportar/Importar configurações\n"
            "• Proteção contra sobrecarga de memória\n"
            "• Alerta de alterações não salvas\n"
            "• MENU DE EFEITOS COMPLETO:\n"
            "  - Cores: Inverter, Escala de Cinza, Sépia, P&B\n"
            "  - Ajustes: Brilho, Contraste, Saturação\n"
            "  - Filtros: Desfoque, Bordas, Realce, Suavizar\n"
            "  - Transformações: Rotacionar, Espelhar, Redimensionar\n"
            "  - Especiais: Transparência, Pixelizar, Mosaico, Ruído\n\n"
            "Desenvolvido com Python, Tkinter e Pillow\n\n"
            "© 2024 PaintWazzima Studios"
            " Relatório: JAoI5mcT1wfHm8MSLOLl"
        )
        messagebox.showinfo("Sobre o PaintWazzima", sobre_text)
    
    def mostrar_limites(self):
        """Mostrar os limites do editor"""
        limites_text = (
            "Limites do Editor:\n\n"
            f"Largura máxima: {self.MAX_LARGURA} pixels\n"
            f"Altura máxima: {self.MAX_ALTURA} pixels\n"
            f"Máximo de megapixels: {self.MAX_MEGAPIXELS} MP\n"
            f"Zoom mínimo: {int(self.zoom_minimo * 100)}%\n"
            f"Zoom máximo: {int(self.zoom_maximo * 100)}%\n\n"
            "Recomendações:\n"
            "• Imagens muito grandes podem causar lentidão\n"
            "• Para trabalhos profissionais, use imagens até 4000x3000\n"
            "• Formatos suportados: JPG, PNG, BMP, GIF, TIFF\n\n"
            "Memória RAM necessária:\n"
            "• Uma imagem 800x600 usa ~1.4MB\n"
            "• Uma imagem 1920x1080 usa ~6MB\n"
            "• Uma imagem 4000x3000 usa ~36MB"
        )
        messagebox.showinfo("Limites do Editor", limites_text)
    
    def mostrar_atalhos(self):
        """Mostrar atalhos de teclado"""
        atalhos_text = (
            "Atalhos de Teclado:\n\n"
            "Arquivo:\n"
            "  Ctrl+N: Nova imagem\n"
            "  Ctrl+Shift+N: Novo projeto\n"
            "  Ctrl+O: Abrir imagem\n"
            "  Ctrl+Shift+O: Abrir projeto\n"
            "  Ctrl+S: Salvar\n"
            "  Ctrl+Shift+S: Salvar projeto\n"
            "  Ctrl+P: Imprimir\n"
            "  Ctrl+Q: Sair\n\n"
            "Edição:\n"
            "  Ctrl+Z: Desfazer\n"
            "  Ctrl+Y: Refazer\n"
            "  Ctrl+X: Recortar\n"
            "  Ctrl+C: Copiar\n"
            "  Ctrl+V: Colar\n"
            "  Ctrl+D: Duplicar\n"
            "  Ctrl+A: Selecionar tudo\n\n"
            "Visualização:\n"
            "  Ctrl++: Zoom in\n"
            "  Ctrl+-: Zoom out\n"
            "  Ctrl+0: Zoom 100%\n"
            "  Botão direito + arrastar: Pan\n"
            "  Roda do mouse: Zoom\n"
            "  F11: Tela cheia"
        )
        messagebox.showinfo("Atalhos do PaintWazzima", atalhos_text)

# ========== EXECUÇÃO PRINCIPAL ==========

if __name__ == "__main__":
    root = tk.Tk()
    
    # Tentar definir ícone se disponível
    try:
        root.iconbitmap(default='icon.ico')
    except:
        pass
    
    app = EditorImagem(root)
    root.mainloop()
