import json
import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog, colorchooser
from tkinter.font import Font

class NotepadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Anotações Rápidas - Editor Rico (JSON)")
        self.root.geometry("1000x700")
        
        # Arquivo de sessão atual
        self.session_file = None
        
        # Configurar fonte padrão
        self.default_font = Font(family="Courier", size=11)
        self.current_font_family = "Courier"
        self.current_font_size = 11
        
        # Dicionário para armazenar dados de cada aba
        self.tabs_data = {}
        
        # Criar menu
        self.create_menu()
        
        # Criar barra de ferramentas
        self.create_toolbar()
        
        # Criar barra de formatação adicional
        self.create_formatting_toolbar()
        
        # Criar notebook (abas)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Criar primeira aba
        self.new_tab()
        
        # Atalhos de teclado
        self.setup_shortcuts()
        
        # Status bar
        self.status_bar = Label(root, text="Pronto", bd=1, relief=SUNKEN, anchor=W)
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        # Variáveis de formatação
        self.current_format = {"bold": False, "italic": False, "underline": False}
    
    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Nova Sessão", command=self.new_session, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir Sessão", command=self.open_session, accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar Sessão", command=self.save_session, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Sessão Como...", command=self.save_session_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exportar Aba Atual como TXT", command=self.export_current_tab_as_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Fechar Aba", command=self.close_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Sair", command=self.exit_app, accelerator="Ctrl+Q")
        
        # Menu Aba
        tab_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aba", menu=tab_menu)
        tab_menu.add_command(label="Nova Aba", command=self.new_tab, accelerator="Ctrl+T")
        tab_menu.add_command(label="Próxima Aba", command=self.next_tab, accelerator="Ctrl+Tab")
        tab_menu.add_command(label="Aba Anterior", command=self.prev_tab, accelerator="Ctrl+Shift+Tab")
        
        # Menu Formatação
        format_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Formatação", menu=format_menu)
        format_menu.add_command(label="Negrito", command=self.toggle_bold, accelerator="Ctrl+B")
        format_menu.add_command(label="Itálico", command=self.toggle_italic, accelerator="Ctrl+I")
        format_menu.add_command(label="Sublinhado", command=self.toggle_underline, accelerator="Ctrl+U")
        format_menu.add_separator()
        format_menu.add_command(label="Aumentar Fonte", command=self.increase_font, accelerator="Ctrl++")
        format_menu.add_command(label="Diminuir Fonte", command=self.decrease_font, accelerator="Ctrl+-")
        format_menu.add_command(label="Fonte Padrão", command=self.reset_font)
        format_menu.add_separator()
        format_menu.add_command(label="Cor do Texto", command=self.change_text_color)
        format_menu.add_command(label="Cor de Fundo", command=self.change_bg_color)
        
        # Menu Alinhamento (apenas esquerda, centro, direita)
        align_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Alinhamento", menu=align_menu)
        align_menu.add_command(label="Esquerda", command=lambda: self.set_alignment("left"))
        align_menu.add_command(label="Centro", command=lambda: self.set_alignment("center"))
        align_menu.add_command(label="Direita", command=lambda: self.set_alignment("right"))
        
        # Menu Ajuda
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
    
    def create_toolbar(self):
        toolbar = Frame(self.root)
        toolbar.pack(side=TOP, fill=X, padx=2, pady=2)
        
        # Botões de formatação básica
        self.btn_bold = Button(toolbar, text="N", font=("Arial", 10, "bold"), 
                              command=self.toggle_bold, width=3)
        self.btn_bold.pack(side=LEFT, padx=2)
        
        self.btn_italic = Button(toolbar, text="I", font=("Arial", 10, "italic"), 
                                command=self.toggle_italic, width=3)
        self.btn_italic.pack(side=LEFT, padx=2)
        
        self.btn_underline = Button(toolbar, text="U", font=("Arial", 10, "underline"), 
                                   command=self.toggle_underline, width=3)
        self.btn_underline.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botões de alinhamento
        self.btn_left = Button(toolbar, text="← Esq", command=lambda: self.set_alignment("left"), width=5)
        self.btn_left.pack(side=LEFT, padx=2)
        
        self.btn_center = Button(toolbar, text="↔ Cen", command=lambda: self.set_alignment("center"), width=5)
        self.btn_center.pack(side=LEFT, padx=2)
        
        self.btn_right = Button(toolbar, text="→ Dir", command=lambda: self.set_alignment("right"), width=5)
        self.btn_right.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botões de fonte
        self.btn_font_up = Button(toolbar, text="A+", command=self.increase_font, width=3)
        self.btn_font_up.pack(side=LEFT, padx=2)
        
        self.btn_font_down = Button(toolbar, text="A-", command=self.decrease_font, width=3)
        self.btn_font_down.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botões de cor
        self.btn_text_color = Button(toolbar, text="Cor", command=self.change_text_color, width=5)
        self.btn_text_color.pack(side=LEFT, padx=2)
        
        self.btn_bg_color = Button(toolbar, text="Fundo", command=self.change_bg_color, width=5)
        self.btn_bg_color.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botões de gerenciamento de abas
        btn_new_tab = Button(toolbar, text="+ Nova Aba", command=self.new_tab)
        btn_new_tab.pack(side=LEFT, padx=2)
        
        btn_close_tab = Button(toolbar, text="X Fechar Aba", command=self.close_tab)
        btn_close_tab.pack(side=LEFT, padx=2)
        
        btn_save = Button(toolbar, text="💾 Salvar Sessão", command=self.save_session)
        btn_save.pack(side=LEFT, padx=2)
    
    def create_formatting_toolbar(self):
        """Cria uma barra de ferramentas adicional com mais opções"""
        format_toolbar = Frame(self.root)
        format_toolbar.pack(side=TOP, fill=X, padx=2, pady=2)
        
        # Lista de famílias de fonte
        font_families = ["Courier", "Arial", "Times New Roman", "Verdana", "Tahoma", "Georgia"]
        self.font_family_var = StringVar()
        self.font_family_combo = ttk.Combobox(format_toolbar, textvariable=self.font_family_var, 
                                               values=font_families, width=15, state="readonly")
        self.font_family_combo.set(self.current_font_family)
        self.font_family_combo.bind('<<ComboboxSelected>>', self.change_font_family)
        self.font_family_combo.pack(side=LEFT, padx=2)
        
        # Lista de tamanhos de fonte
        font_sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 36, 48, 72]
        self.font_size_var = StringVar()
        self.font_size_combo = ttk.Combobox(format_toolbar, textvariable=self.font_size_var, 
                                            values=font_sizes, width=5, state="readonly")
        self.font_size_combo.set(self.current_font_size)
        self.font_size_combo.bind('<<ComboboxSelected>>', self.change_font_size)
        self.font_size_combo.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(format_toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botão de marcadores
        self.btn_bullet = Button(format_toolbar, text="• Lista", command=self.insert_bullet_point)
        self.btn_bullet.pack(side=LEFT, padx=2)
        
        # Botão de numeração
        self.btn_number = Button(format_toolbar, text="1. Lista", command=self.insert_numbered_list)
        self.btn_number.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(format_toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botões de indentação
        self.btn_indent = Button(format_toolbar, text="↹ Indentar", command=self.indent_text)
        self.btn_indent.pack(side=LEFT, padx=2)
        
        self.btn_dedent = Button(format_toolbar, text="↺ Desindentar", command=self.dedent_text)
        self.btn_dedent.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(format_toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Botão de limpar formatação
        self.btn_clear = Button(format_toolbar, text="Limpar Formatação", command=self.clear_formatting)
        self.btn_clear.pack(side=LEFT, padx=2)
        
        # Separador
        ttk.Separator(format_toolbar, orient=VERTICAL).pack(side=LEFT, fill=Y, padx=5, pady=2)
        
        # Label para informações
        self.info_label = Label(format_toolbar, text="Selecione o texto para formatar")
        self.info_label.pack(side=LEFT, padx=10)
    
    def setup_shortcuts(self):
        # Atalhos de teclado
        self.root.bind('<Control-n>', lambda e: self.new_session())
        self.root.bind('<Control-o>', lambda e: self.open_session())
        self.root.bind('<Control-s>', lambda e: self.save_session())
        self.root.bind('<Control-w>', lambda e: self.close_tab())
        self.root.bind('<Control-q>', lambda e: self.exit_app())
        self.root.bind('<Control-t>', lambda e: self.new_tab())
        self.root.bind('<Control-Tab>', lambda e: self.next_tab())
        self.root.bind('<Control-Shift-Tab>', lambda e: self.prev_tab())
        self.root.bind('<Control-b>', lambda e: self.toggle_bold())
        self.root.bind('<Control-i>', lambda e: self.toggle_italic())
        self.root.bind('<Control-u>', lambda e: self.toggle_underline())
        self.root.bind('<Control-plus>', lambda e: self.increase_font())
        self.root.bind('<Control-minus>', lambda e: self.decrease_font())
        self.root.bind('<Control-equal>', lambda e: self.increase_font())
    
    def get_text_with_formatting(self, text_widget):
        """Extrai o texto e suas formatações"""
        content = []
        
        # Verificar se o texto está vazio
        text_content = text_widget.get(1.0, END).strip()
        if not text_content:
            return []
        
        # Processar o texto caractere por caractere para capturar formatações
        current_pos = 1.0
        while True:
            try:
                # Obter o próximo caractere
                char_pos = text_widget.index(current_pos)
                char = text_widget.get(char_pos, f"{char_pos}+1c")
                
                if not char or char == '':
                    break
                
                # Se chegou ao final
                if char_pos == 'end-1c':
                    break
                
                # Verificar tags na posição atual
                tags = text_widget.tag_names(char_pos)
                
                # Capturar formatações
                is_bold = 'bold' in tags
                is_italic = 'italic' in tags
                is_underline = 'underline' in tags
                
                # Capturar cor do texto
                text_color = None
                for tag in tags:
                    if tag.startswith('color_'):
                        text_color = tag.replace('color_', '')
                        break
                
                # Capturar cor de fundo
                bg_color = None
                for tag in tags:
                    if tag.startswith('bg_'):
                        bg_color = tag.replace('bg_', '')
                        break
                
                # Capturar alinhamento (apenas left, center, right)
                alignment = 'left'
                for tag in tags:
                    if tag in ['left', 'center', 'right']:
                        alignment = tag
                        break
                
                content.append({
                    'char': char,
                    'bold': is_bold,
                    'italic': is_italic,
                    'underline': is_underline,
                    'text_color': text_color,
                    'bg_color': bg_color,
                    'alignment': alignment,
                    'font_family': self.current_font_family,
                    'font_size': self.current_font_size
                })
                
                # Avançar para o próximo caractere
                current_pos = text_widget.index(f"{char_pos}+1c")
                
                # Evitar loop infinito
                if current_pos == char_pos:
                    break
                    
            except Exception as e:
                print(f"Erro ao processar caractere: {e}")
                break
        
        return content
    
    def load_text_with_formatting(self, text_widget, formatted_content):
        """Carrega o texto com as formatações"""
        text_widget.delete(1.0, END)
        
        if not formatted_content:
            return
        
        # Acumular texto e aplicar formatação por blocos
        current_text = ""
        current_format = {}
        start_pos = 1.0
        
        for item in formatted_content:
            # Criar chave de formatação
            format_key = (
                item.get('bold', False),
                item.get('italic', False),
                item.get('underline', False),
                item.get('text_color', ''),
                item.get('bg_color', ''),
                item.get('alignment', 'left'),
                item.get('font_family', 'Courier'),
                item.get('font_size', 11)
            )
            
            # Se a formatação mudou, aplicar a formatação anterior
            if 'current_format' in locals() and format_key != current_format and current_text:
                end_pos = text_widget.index(f"{start_pos}+{len(current_text)}c")
                text_widget.insert(start_pos, current_text)
                
                # Aplicar formatações
                self.apply_formatting_to_range(text_widget, start_pos, end_pos, current_format)
                
                start_pos = end_pos
                current_text = ""
            
            current_format = format_key
            current_text += item['char']
        
        # Inserir o último bloco
        if current_text:
            end_pos = text_widget.index(f"{start_pos}+{len(current_text)}c")
            text_widget.insert(start_pos, current_text)
            self.apply_formatting_to_range(text_widget, start_pos, end_pos, current_format)
    
    def apply_formatting_to_range(self, text_widget, start, end, format_tuple):
        """Aplica formatação a um intervalo de texto"""
        bold, italic, underline, text_color, bg_color, alignment, font_family, font_size = format_tuple
        
        # Configurar fonte
        font_style = []
        if bold:
            font_style.append('bold')
        if italic:
            font_style.append('italic')
        if underline:
            font_style.append('underline')
        
        font_style_str = ' '.join(font_style) if font_style else 'normal'
        
        # Criar tag personalizada para a fonte
        font_tag = f"font_{font_family}_{font_size}_{font_style_str}"
        font = Font(family=font_family, size=font_size)
        if bold:
            font.configure(weight='bold')
        if italic:
            font.configure(slant='italic')
        if underline:
            font.configure(underline=True)
        
        text_widget.tag_configure(font_tag, font=font)
        text_widget.tag_add(font_tag, start, end)
        
        # Aplicar cor do texto
        if text_color:
            color_tag = f"color_{text_color}"
            text_widget.tag_configure(color_tag, foreground=text_color)
            text_widget.tag_add(color_tag, start, end)
        
        # Aplicar cor de fundo
        if bg_color:
            bg_tag = f"bg_{bg_color}"
            text_widget.tag_configure(bg_tag, background=bg_color)
            text_widget.tag_add(bg_tag, start, end)
        
        # Aplicar alinhamento (apenas left, center, right)
        if alignment and alignment in ['left', 'center', 'right']:
            text_widget.tag_configure(alignment, justify=alignment)
            text_widget.tag_add(alignment, start, end)
    
    def apply_formatting_to_selection(self, format_type, value=None):
        """Aplica formatação ao texto selecionado"""
        text_widget = self.get_current_text()
        if not text_widget:
            return
        
        try:
            if text_widget.tag_ranges("sel"):
                start = text_widget.index("sel.first")
                end = text_widget.index("sel.last")
                
                if format_type == "bold":
                    if "bold" in text_widget.tag_names(start):
                        text_widget.tag_remove("bold", start, end)
                    else:
                        text_widget.tag_add("bold", start, end)
                        text_widget.tag_configure("bold", font=("Courier", self.current_font_size, "bold"))
                
                elif format_type == "italic":
                    if "italic" in text_widget.tag_names(start):
                        text_widget.tag_remove("italic", start, end)
                    else:
                        text_widget.tag_add("italic", start, end)
                        text_widget.tag_configure("italic", font=("Courier", self.current_font_size, "italic"))
                
                elif format_type == "underline":
                    if "underline" in text_widget.tag_names(start):
                        text_widget.tag_remove("underline", start, end)
                    else:
                        text_widget.tag_add("underline", start, end)
                        text_widget.tag_configure("underline", underline=True)
                
                elif format_type == "text_color" and value:
                    # Remover cor anterior
                    for tag in text_widget.tag_names(start):
                        if tag.startswith('color_'):
                            text_widget.tag_remove(tag, start, end)
                    
                    color_tag = f"color_{value}"
                    text_widget.tag_configure(color_tag, foreground=value)
                    text_widget.tag_add(color_tag, start, end)
                
                elif format_type == "bg_color" and value:
                    # Remover cor de fundo anterior
                    for tag in text_widget.tag_names(start):
                        if tag.startswith('bg_'):
                            text_widget.tag_remove(tag, start, end)
                    
                    bg_tag = f"bg_{value}"
                    text_widget.tag_configure(bg_tag, background=value)
                    text_widget.tag_add(bg_tag, start, end)
                
                elif format_type == "alignment" and value in ['left', 'center', 'right']:
                    # Remover alinhamento anterior
                    for align in ['left', 'center', 'right']:
                        if align in text_widget.tag_names(start):
                            text_widget.tag_remove(align, start, end)
                    
                    text_widget.tag_configure(value, justify=value)
                    text_widget.tag_add(value, start, end)
                
                text_widget.focus_set()
        except Exception as e:
            print(f"Erro ao aplicar formatação: {e}")
    
    def new_tab(self, formatted_content=None, title="Nova Anotação"):
        """Cria uma nova aba com opção de conteúdo formatado"""
        # Frame para a aba
        tab_frame = Frame(self.notebook)
        
        # Criar Text widget com scrollbar
        text_widget = Text(tab_frame, wrap=WORD, undo=True)
        scrollbar = Scrollbar(tab_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Configurar tags para formatação (apenas left, center, right)
        text_widget.tag_configure("bold", font=("Courier", self.current_font_size, "bold"))
        text_widget.tag_configure("italic", font=("Courier", self.current_font_size, "italic"))
        text_widget.tag_configure("underline", underline=True)
        text_widget.tag_configure("left", justify="left")
        text_widget.tag_configure("center", justify="center")
        text_widget.tag_configure("right", justify="right")
        
        # Carregar conteúdo formatado se fornecido
        if formatted_content:
            self.load_text_with_formatting(text_widget, formatted_content)
        
        # Adicionar ao notebook
        self.notebook.add(tab_frame, text=title)
        tab_id = self.notebook.index("end") - 1
        
        # Armazenar dados da aba
        self.tabs_data[tab_id] = {
            'text_widget': text_widget,
            'title': title,
            'modified': False
        }
        
        # Configurar evento de modificação
        def on_modified(event, tid=tab_id):
            self.on_text_modified(tid)
        
        text_widget.bind('<<Modified>>', on_modified)
        
        # Selecionar a nova aba
        self.notebook.select(tab_id)
        
        return text_widget
    
    def get_current_text(self):
        """Obtém o text widget da aba atual"""
        try:
            current_tab = self.notebook.select()
            if current_tab:
                tab_id = self.notebook.index("current")
                return self.tabs_data.get(tab_id, {}).get('text_widget')
        except:
            pass
        return None
    
    def get_current_tab_id(self):
        """Obtém o ID da aba atual"""
        try:
            if self.notebook.select():
                return self.notebook.index("current")
        except:
            pass
        return None
    
    def on_text_modified(self, tab_id):
        """Marca a aba como modificada quando o texto é alterado"""
        if tab_id in self.tabs_data:
            if not self.tabs_data[tab_id]['modified']:
                self.tabs_data[tab_id]['modified'] = True
                try:
                    current_title = self.notebook.tab(tab_id, "text")
                    if not current_title.endswith("*"):
                        self.notebook.tab(tab_id, text=current_title + "*")
                except:
                    pass
    
    # ========== MÉTODOS DE FORMATAÇÃO ==========
    
    def toggle_bold(self):
        self.apply_formatting_to_selection("bold")
    
    def toggle_italic(self):
        self.apply_formatting_to_selection("italic")
    
    def toggle_underline(self):
        self.apply_formatting_to_selection("underline")
    
    def change_text_color(self):
        color = colorchooser.askcolor(title="Escolha a cor do texto")
        if color[1]:
            self.apply_formatting_to_selection("text_color", color[1])
    
    def change_bg_color(self):
        color = colorchooser.askcolor(title="Escolha a cor de fundo")
        if color[1]:
            self.apply_formatting_to_selection("bg_color", color[1])
    
    def set_alignment(self, alignment):
        if alignment in ['left', 'center', 'right']:
            self.apply_formatting_to_selection("alignment", alignment)
    
    def change_font_family(self, event=None):
        new_family = self.font_family_var.get()
        self.current_font_family = new_family
        self.update_font_for_selection()
    
    def change_font_size(self, event=None):
        new_size = int(self.font_size_var.get())
        self.current_font_size = new_size
        self.update_font_for_selection()
    
    def update_font_for_selection(self):
        """Atualiza a fonte do texto selecionado"""
        text_widget = self.get_current_text()
        if not text_widget:
            return
        
        try:
            if text_widget.tag_ranges("sel"):
                start = text_widget.index("sel.first")
                end = text_widget.index("sel.last")
                
                # Criar tag com a nova fonte
                font_tag = f"custom_font_{self.current_font_family}_{self.current_font_size}"
                new_font = Font(family=self.current_font_family, size=self.current_font_size)
                text_widget.tag_configure(font_tag, font=new_font)
                text_widget.tag_add(font_tag, start, end)
        except:
            pass
    
    def increase_font(self):
        self.current_font_size += 1
        self.font_size_combo.set(self.current_font_size)
        self.update_font_for_selection()
    
    def decrease_font(self):
        if self.current_font_size > 1:
            self.current_font_size -= 1
            self.font_size_combo.set(self.current_font_size)
            self.update_font_for_selection()
    
    def reset_font(self):
        self.current_font_family = "Courier"
        self.current_font_size = 11
        self.font_family_combo.set(self.current_font_family)
        self.font_size_combo.set(self.current_font_size)
        self.update_font_for_selection()
    
    def insert_bullet_point(self):
        """Insere um marcador no início da linha atual"""
        text_widget = self.get_current_text()
        if text_widget:
            try:
                current_pos = text_widget.index(INSERT)
                line_start = f"{current_pos} linestart"
                text_widget.insert(line_start, "• ")
            except:
                pass
    
    def insert_numbered_list(self):
        """Insere uma lista numerada"""
        text_widget = self.get_current_text()
        if text_widget:
            try:
                current_pos = text_widget.index(INSERT)
                line_start = f"{current_pos} linestart"
                line_num = int(current_pos.split('.')[0])
                text_widget.insert(line_start, f"{line_num}. ")
            except:
                pass
    
    def indent_text(self):
        """Adiciona indentação ao texto selecionado"""
        text_widget = self.get_current_text()
        if text_widget:
            try:
                if text_widget.tag_ranges("sel"):
                    start = text_widget.index("sel.first")
                    end = text_widget.index("sel.last")
                    
                    # Obter todas as linhas na seleção
                    start_line = int(start.split('.')[0])
                    end_line = int(end.split('.')[0])
                    
                    for line in range(start_line, end_line + 1):
                        text_widget.insert(f"{line}.0", "    ")
            except:
                pass
    
    def dedent_text(self):
        """Remove indentação do texto selecionado"""
        text_widget = self.get_current_text()
        if text_widget:
            try:
                if text_widget.tag_ranges("sel"):
                    start = text_widget.index("sel.first")
                    end = text_widget.index("sel.last")
                    
                    # Obter todas as linhas na seleção
                    start_line = int(start.split('.')[0])
                    end_line = int(end.split('.')[0])
                    
                    for line in range(start_line, end_line + 1):
                        line_text = text_widget.get(f"{line}.0", f"{line}.4")
                        if line_text == "    " or line_text.startswith("    "):
                            text_widget.delete(f"{line}.0", f"{line}.4")
                        elif line_text.startswith("\t"):
                            text_widget.delete(f"{line}.0", f"{line}.1")
            except:
                pass
    
    def clear_formatting(self):
        """Limpa toda a formatação do texto selecionado"""
        text_widget = self.get_current_text()
        if text_widget:
            try:
                if text_widget.tag_ranges("sel"):
                    start = text_widget.index("sel.first")
                    end = text_widget.index("sel.last")
                    
                    # Remover todas as tags
                    tags_to_remove = []
                    for tag in text_widget.tag_names():
                        if tag not in ['sel', 'sel.first', 'sel.last']:
                            tags_to_remove.append(tag)
                    
                    for tag in tags_to_remove:
                        text_widget.tag_remove(tag, start, end)
                    
                    self.update_status("Formatação removida")
            except:
                pass
    
    # ========== MÉTODOS DE GERENCIAMENTO DE SESSÃO ==========
    
    def new_session(self):
        """Cria uma nova sessão (limpa todas as abas)"""
        if self.confirm_save_session():
            # Limpar todas as abas
            while self.notebook.index("end") > 0:
                self.notebook.forget(0)
            self.tabs_data.clear()
            
            # Criar nova aba
            self.new_tab()
            self.session_file = None
            self.update_status("Nova sessão criada")
    
    def open_session(self):
        """Abre uma sessão completa de um arquivo JSON"""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # Verificar formato do arquivo
                if isinstance(data, dict) and 'tabs' in data:
                    # Limpar abas existentes
                    while self.notebook.index("end") > 0:
                        self.notebook.forget(0)
                    self.tabs_data.clear()
                    
                    # Recriar abas a partir do JSON
                    for tab_data in data['tabs']:
                        self.new_tab(
                            formatted_content=tab_data.get('content', []),
                            title=tab_data.get('title', 'Nova Anotação')
                        )
                    
                    self.session_file = file_path
                    self.update_status(f"Sessão aberta: {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Erro", "Formato de arquivo de sessão inválido")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir a sessão:\n{str(e)}")
    
    def save_session(self):
        """Salva todas as abas em um único arquivo JSON"""
        if self.session_file:
            self._save_to_file(self.session_file)
        else:
            self.save_session_as()
    
    def save_session_as(self):
        """Salva a sessão em um novo arquivo JSON"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            if not file_path.endswith('.json'):
                file_path += '.json'
            
            self.session_file = file_path
            self._save_to_file(file_path)
    
    def _save_to_file(self, file_path):
        """Salva todas as abas no arquivo especificado"""
        try:
            # Coletar dados de todas as abas
            tabs_data = []
            for tab_id in range(self.notebook.index("end")):
                tab_info = self.tabs_data.get(tab_id, {})
                text_widget = tab_info.get('text_widget')
                
                # Obter título sem o asterisco
                try:
                    title = self.notebook.tab(tab_id, "text")
                    if title.endswith("*"):
                        title = title[:-1]
                except:
                    title = "Nova Anotação"
                
                if text_widget:
                    formatted_content = self.get_text_with_formatting(text_widget)
                    tabs_data.append({
                        'title': title,
                        'content': formatted_content
                    })
            
            # Preparar dados para JSON
            data = {
                'version': '3.0',
                'tabs': tabs_data,
                'metadata': {
                    'created': os.path.getctime(file_path) if os.path.exists(file_path) else None,
                    'modified': os.path.getmtime(file_path) if os.path.exists(file_path) else None,
                    'tab_count': len(tabs_data),
                    'font_family': self.current_font_family,
                    'font_size': self.current_font_size
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            
            # Remover marcadores de modificação de todas as abas
            for tab_id in range(self.notebook.index("end")):
                if tab_id in self.tabs_data:
                    self.tabs_data[tab_id]['modified'] = False
                    try:
                        current_title = self.notebook.tab(tab_id, "text")
                        if current_title.endswith("*"):
                            self.notebook.tab(tab_id, text=current_title[:-1])
                    except:
                        pass
            
            self.update_status(f"Sessão salva: {os.path.basename(file_path)}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar a sessão:\n{str(e)}")
    
    def export_current_tab_as_txt(self):
        """Exporta a aba atual como arquivo TXT simples"""
        text_widget = self.get_current_text()
        if not text_widget:
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        
        if file_path:
            try:
                # Exportar apenas texto sem formatação
                content = text_widget.get(1.0, END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                
                self.update_status(f"Exportado como TXT: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível exportar:\n{str(e)}")
    
    def close_tab(self):
        """Fecha a aba atual"""
        try:
            if self.notebook.index("end") > 1:  # Se há mais de uma aba
                current_tab_id = self.get_current_tab_id()
                if current_tab_id is not None and current_tab_id in self.tabs_data:
                    # Verificar se a aba está modificada
                    if self.tabs_data[current_tab_id].get('modified', False):
                        response = messagebox.askyesnocancel(
                            "Salvar alterações",
                            f"A aba '{self.notebook.tab(current_tab_id, 'text')}' foi modificada.\nDeseja salvar a sessão?"
                        )
                        if response is True:  # Sim
                            self.save_session()
                        elif response is None:  # Cancelar
                            return
                    
                    # Fechar a aba
                    self.notebook.forget(current_tab_id)
                    del self.tabs_data[current_tab_id]
                    
                    # Reorganizar os IDs das abas
                    new_tabs_data = {}
                    for idx, (key, value) in enumerate(self.tabs_data.items()):
                        new_tabs_data[idx] = value
                    self.tabs_data = new_tabs_data
        except:
            pass
    
    def confirm_save_session(self):
        """Confirma se o usuário quer salvar a sessão antes de fechar"""
        # Verificar se alguma aba foi modificada
        any_modified = any(tab.get('modified', False) for tab in self.tabs_data.values())
        
        if any_modified:
            response = messagebox.askyesnocancel(
                "Salvar alterações",
                "A sessão foi modificada.\nDeseja salvar as alterações?"
            )
            if response is True:  # Sim
                self.save_session()
                return True
            elif response is False:  # Não
                return True
            else:  # Cancelar
                return False
        return True
    
    def next_tab(self):
        """Vai para a próxima aba"""
        try:
            current = self.notebook.index("current")
            if current < self.notebook.index("end") - 1:
                self.notebook.select(current + 1)
        except:
            pass
    
    def prev_tab(self):
        """Vai para a aba anterior"""
        try:
            current = self.notebook.index("current")
            if current > 0:
                self.notebook.select(current - 1)
        except:
            pass
    
    def update_status(self, message):
        """Atualiza a barra de status"""
        self.status_bar.config(text=message)
        self.root.after(3000, lambda: self.status_bar.config(text="Pronto"))
    
    def show_about(self):
        """Mostra informações sobre o aplicativo"""
        messagebox.showinfo(
            "Sobre",
            "Anotações Rápidas - Editor Rico\n\n"
            "Versão 4.0\n"
            "Editor de texto com múltiplas abas e formatação rica\n\n"
            "Recursos de Formatação:\n"
            "• Negrito, Itálico, Sublinhado\n"
            "• Cores de texto e fundo\n"
            "• Alinhamento (esquerda, centro, direita)\n"
            "• Famílias e tamanhos de fonte\n"
            "• Listas com marcadores e numeradas\n"
            "• Indentação\n\n"
            "Atalhos:\n"
            "Ctrl+N - Nova Sessão\n"
            "Ctrl+O - Abrir Sessão\n"
            "Ctrl+S - Salvar Sessão\n"
            "Ctrl+T - Nova Aba\n"
            "Ctrl+W - Fechar Aba\n"
            "Ctrl+B - Negrito\n"
            "Ctrl+I - Itálico\n"
            "Ctrl+U - Sublinhado\n"
            "Ctrl++ - Aumentar Fonte\n"
            "Ctrl+- - Diminuir Fonte\n\n"
            "Todas as abas e formatações são salvas em JSON!\n\n"
            "Nota: O alinhamento justificado não está disponível\n"
            "devido a limitações do Tkinter."
        )
    
    def exit_app(self):
        """Sai do aplicativo"""
        if self.confirm_save_session():
            self.root.quit()

def main():
    root = Tk()
    app = NotepadApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
