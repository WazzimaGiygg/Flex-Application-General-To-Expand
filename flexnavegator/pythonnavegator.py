import sys
import os
import json
import shutil
import tempfile
import uuid
import importlib.util
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from urllib.parse import quote

# ==================== SISTEMA DE IDIOMAS ====================
class LanguageManager:
    """Gerenciador de idiomas para o navegador"""
    
    def __init__(self):
        self.current_language = "pt_BR"
        self.strings = {}
        self.languages_dir = "languages"
        self.load_language(self.current_language)
    
    def load_language(self, lang_code):
        """Carregar um arquivo de idioma"""
        self.current_language = lang_code
        lang_file = os.path.join(self.languages_dir, f"{lang_code}.txt")
        
        # Criar diretório de idiomas se não existir
        if not os.path.exists(self.languages_dir):
            os.makedirs(self.languages_dir)
            self.create_default_languages()
        
        # Carregar arquivo de idioma
        try:
            if os.path.exists(lang_file):
                with open(lang_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            if "=" in line:
                                key, value = line.split("=", 1)
                                self.strings[key.strip()] = value.strip()
            else:
                self.create_default_languages()
                self.load_language(lang_code)
        except Exception as e:
            print(f"Erro ao carregar idioma {lang_code}: {e}")
            self.load_default_strings()
    
    def create_default_languages(self):
        """Criar arquivos de idioma padrão"""
        # Português (Brasil)
        pt_br_content = """# Python Navigator - Arquivo de idioma Português (Brasil)
# Formato: chave=valor

# Menu Arquivo
menu_file=Arquivo
menu_new_window=Nova janela
menu_new_anonymous=Nova janela anônima
menu_open_file=Abrir arquivo HTML...
menu_exit=Sair

# Menu Exibir
menu_view=Exibir
view_source=Código fonte da página
view_zoom_in=Aumentar zoom
view_zoom_out=Diminuir zoom
view_zoom_reset=Zoom padrão

# Menu Histórico
menu_history=Histórico
view_history=Ver histórico
clear_history=Limpar histórico

# Menu Configurações
menu_settings=Configurações
preferences=Preferências

# Menu Ajuda
menu_help=Ajuda
about=Sobre

# Botões
btn_back=◀
btn_forward=▶
btn_refresh=⟳
btn_home=🏠
btn_source=</> Código
btn_anonymous=🕶️ Anônimo
btn_new_tab=+ Nova Aba
btn_extensions=🔌 Extensões

# Mensagens
loading=Carregando...
new_tab=Nova aba
ready=Pronto
js_enabled=JavaScript: Ativado
js_disabled=JavaScript: Desativado
page_loaded=Página carregada
zoom_percent=Zoom: {}%
zoom_100=Zoom: 100%
anonymous_mode_activated=Modo anônimo ativado - Seu histórico não será salvo
anonymous_info=Você está navegando em modo anônimo.\\n\\n✓ Histórico não será salvo\\n✓ Cookies não serão mantidos\\n✓ Dados temporários serão apagados ao fechar\\n\\nObservação: Isso não torna sua navegação completamente anônima na internet.

# Configurações
settings_title=Configurações - Python Navigator
about_title=Sobre o Python Navigator
home_page=Página inicial
search_engine=Motor de busca padrão:
javascript_settings=JavaScript
enable_js=Habilitar JavaScript
js_info=O JavaScript é necessário para a maioria dos sites modernos.\\nDesativar pode melhorar a segurança e velocidade,\\nmas muitos sites podem não funcionar corretamente.
extensions_settings=Extensões
language_settings=Idioma
select_language=Selecione o idioma:
appearance_settings=Aparência (Skin)
select_skin=Selecione um tema:
save_config=Salvar
cancel_config=Cancelar
config_saved=Configurações salvas com sucesso!

# Extensões
extensions_title=Gerenciador de Extensões
no_extensions=Nenhuma extensão instalada.
install_extension=Instalar extensão
remove_extension=Remover
extension_loaded=Extensão carregada: {}
extension_error=Erro ao carregar extensão: {}
extension_removed=Extensão removida: {}

# Visualizador de código
source_viewer_title=Visualizador de Código Fonte - {}
copy_code=Copiar
save_code=Salvar como...
refresh_code=Atualizar
word_wrap=Quebra de linha
close=Fechar
search=Buscar:
search_placeholder=Digite texto para buscar...
next=Próximo
prev=Anterior
code_loaded=Código fonte carregado
code_updated=Código fonte atualizado com sucesso!
code_copied=Código fonte copiado para a área de transferência!
no_results=Nenhum resultado encontrado para '{}'

# Histórico
history_title=Histórico - Python Navigator
clear_history_confirm=Tem certeza que deseja limpar todo o histórico?
history_cleared=Histórico limpo com sucesso!

# Sobre
about_version=Versão:
about_identifier=Identificador:
about_desc=Navegador web desenvolvido em Python com PyQt5
about_features=Funcionalidades:
about_features_list=• Múltiplas abas\\n• Modo anônimo (privado)\\n• Histórico de navegação\\n• Visualizador de código fonte\\n• Sistema de extensões\\n• Configurações personalizáveis\\n• Sistema de skins/temas\\n• JavaScript configurável\\n• Suporte a múltiplos idiomas\\n• Atalhos de teclado\\n• Abrir arquivos HTML locais\\n• Motor de busca personalizável\\n• User Agent personalizado
about_credit=© 2024 - Python Navigator Team

# Erros
error_title=Erro
error_save_file=Erro ao salvar arquivo: {}
error_load_history=Erro ao carregar histórico: {}
error_clear_history=Erro ao limpar histórico: {}
error_load_config=Erro ao carregar configurações: {}
error_save_config=Erro ao salvar configurações: {}
"""
        
        # Inglês
        en_us_content = """# Python Navigator - English Language File
# Format: key=value

# File Menu
menu_file=File
menu_new_window=New window
menu_new_anonymous=New anonymous window
menu_open_file=Open HTML file...
menu_exit=Exit

# View Menu
menu_view=View
view_source=Page source code
view_zoom_in=Zoom in
view_zoom_out=Zoom out
view_zoom_reset=Reset zoom

# History Menu
menu_history=History
view_history=View history
clear_history=Clear history

# Settings Menu
menu_settings=Settings
preferences=Preferences

# Help Menu
menu_help=Help
about=About

# Buttons
btn_back=◀
btn_forward=▶
btn_refresh=⟳
btn_home=🏠
btn_source=</> Source
btn_anonymous=🕶️ Anonymous
btn_new_tab=+ New Tab
btn_extensions=🔌 Extensions

# Messages
loading=Loading...
new_tab=New tab
ready=Ready
js_enabled=JavaScript: Enabled
js_disabled=JavaScript: Disabled
page_loaded=Page loaded
zoom_percent=Zoom: {}%
zoom_100=Zoom: 100%
anonymous_mode_activated=Anonymous mode activated - Your history will not be saved
anonymous_info=You are browsing in anonymous mode.\\n\\n✓ History will not be saved\\n✓ Cookies will not be kept\\n✓ Temporary data will be deleted when closing\\n\\nNote: This does not make your browsing completely anonymous on the internet.

# Settings
settings_title=Settings - Python Navigator
about_title=About Python Navigator
home_page=Home page
search_engine=Default search engine:
javascript_settings=JavaScript
enable_js=Enable JavaScript
js_info=JavaScript is required for most modern websites.\\nDisabling may improve security and speed,\\nbut many sites may not work properly.
extensions_settings=Extensions
language_settings=Language
select_language=Select language:
appearance_settings=Appearance (Skin)
select_skin=Select a theme:
save_config=Save
cancel_config=Cancel
config_saved=Settings saved successfully!

# Extensions
extensions_title=Extensions Manager
no_extensions=No extensions installed.
install_extension=Install extension
remove_extension=Remove
extension_loaded=Extension loaded: {}
extension_error=Error loading extension: {}
extension_removed=Extension removed: {}

# Source Viewer
source_viewer_title=Source Code Viewer - {}
copy_code=Copy
save_code=Save as...
refresh_code=Refresh
word_wrap=Word wrap
close=Close
search=Search:
search_placeholder=Type text to search...
next=Next
prev=Previous
code_loaded=Source code loaded
code_updated=Source code updated successfully!
code_copied=Source code copied to clipboard!
no_results=No results found for '{}'

# History
history_title=History - Python Navigator
clear_history_confirm=Are you sure you want to clear all history?
history_cleared=History cleared successfully!

# About
about_version=Version:
about_identifier=Identifier:
about_desc=Web browser developed in Python with PyQt5
about_features=Features:
about_features_list=• Multiple tabs\\n• Anonymous (private) mode\\n• Browsing history\\n• Source code viewer\\n• Extension system\\n• Customizable settings\\n• Skins/themes system\\n• Configurable JavaScript\\n• Multi-language support\\n• Keyboard shortcuts\\n• Open local HTML files\\n• Customizable search engine\\n• Custom User Agent
about_credit=© 2024 - Python Navigator Team

# Errors
error_title=Error
error_save_file=Error saving file: {}
error_load_history=Error loading history: {}
error_clear_history=Error clearing history: {}
error_load_config=Error loading settings: {}
error_save_config=Error saving settings: {}
"""
        
        # Salvar arquivos de idioma
        try:
            with open(os.path.join(self.languages_dir, "pt_BR.txt"), "w", encoding="utf-8") as f:
                f.write(pt_br_content)
            with open(os.path.join(self.languages_dir, "en_US.txt"), "w", encoding="utf-8") as f:
                f.write(en_us_content)
        except Exception as e:
            print(f"Erro ao criar arquivos de idioma: {e}")
    
    def load_default_strings(self):
        """Carregar strings padrão em caso de erro"""
        self.strings = {
            "menu_file": "Arquivo",
            "menu_exit": "Sair",
            "btn_back": "◀",
            "btn_forward": "▶",
            "btn_refresh": "⟳",
            "btn_home": "🏠",
            "btn_source": "</> Código",
            "btn_anonymous": "🕶️ Anônimo",
            "btn_new_tab": "+ Nova Aba",
            "btn_extensions": "🔌 Extensões",
            "loading": "Carregando...",
            "new_tab": "Nova aba",
            "ready": "Pronto"
        }
    
    def get(self, key, default=None):
        """Obter string pelo código"""
        return self.strings.get(key, default or key)
    
    def get_available_languages(self):
        """Obter lista de idiomas disponíveis"""
        languages = []
        if os.path.exists(self.languages_dir):
            for file in os.listdir(self.languages_dir):
                if file.endswith(".txt"):
                    lang_code = file.replace(".txt", "")
                    languages.append(lang_code)
        return languages


# ==================== SISTEMA DE EXTENSÕES ====================
class Extension:
    """Classe base para extensões"""
    
    def __init__(self, name, version, author, description):
        self.name = name
        self.version = version
        self.author = author
        self.description = description
        self.enabled = True
    
    def on_load(self, browser):
        """Chamado quando a extensão é carregada"""
        pass
    
    def on_unload(self):
        """Chamado quando a extensão é descarregada"""
        pass
    
    def on_page_load(self, web_view, url):
        """Chamado quando uma página é carregada"""
        pass
    
    def on_url_changed(self, web_view, url):
        """Chamado quando a URL muda"""
        pass
    
    def get_menu_items(self):
        """Retornar itens de menu adicionais"""
        return []
    
    def get_toolbar_buttons(self):
        """Retornar botões de barra de ferramentas adicionais"""
        return []


class ExtensionManager:
    """Gerenciador de extensões"""
    
    def __init__(self, browser):
        self.browser = browser
        self.extensions = {}
        self.extensions_dir = "extensions"
        
        # Criar diretório de extensões se não existir
        if not os.path.exists(self.extensions_dir):
            os.makedirs(self.extensions_dir)
            self.create_sample_extension()
        
        self.load_all_extensions()
    
    def create_sample_extension(self):
        """Criar uma extensão de exemplo"""
        sample_extension = """# Exemplo de extensão para Python Navigator
# Este é um arquivo de configuração para uma extensão simples

[Info]
name=Hello World Extension
version=1.0.0
author=Python Navigator Team
description=Uma extensão de exemplo que mostra uma mensagem ao carregar páginas

[Script]
# Código Python da extensão
def on_load(browser):
    print("Hello World Extension carregada!")

def on_page_load(web_view, url):
    print(f"Página carregada: {url}")

def on_url_changed(web_view, url):
    print(f"URL alterada: {url}")
"""
        
        try:
            ext_dir = os.path.join(self.extensions_dir, "hello_world")
            os.makedirs(ext_dir, exist_ok=True)
            with open(os.path.join(ext_dir, "extension.ini"), "w", encoding="utf-8") as f:
                f.write(sample_extension)
        except Exception as e:
            print(f"Erro ao criar extensão de exemplo: {e}")
    
    def load_all_extensions(self):
        """Carregar todas as extensões disponíveis"""
        if not os.path.exists(self.extensions_dir):
            return
        
        for ext_name in os.listdir(self.extensions_dir):
            ext_path = os.path.join(self.extensions_dir, ext_name)
            if os.path.isdir(ext_path):
                self.load_extension(ext_name)
    
    def load_extension(self, ext_name):
        """Carregar uma extensão específica"""
        ext_path = os.path.join(self.extensions_dir, ext_name)
        config_file = os.path.join(ext_path, "extension.ini")
        
        if not os.path.exists(config_file):
            return False
        
        try:
            # Ler configuração da extensão
            config = {}
            with open(config_file, "r", encoding="utf-8") as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if line.startswith("[") and line.endswith("]"):
                        current_section = line[1:-1]
                        config[current_section] = {}
                    elif "=" in line and current_section:
                        key, value = line.split("=", 1)
                        config[current_section][key.strip()] = value.strip()
            
            if "Info" not in config:
                return False
            
            info = config["Info"]
            extension = Extension(
                name=info.get("name", ext_name),
                version=info.get("version", "1.0"),
                author=info.get("author", "Unknown"),
                description=info.get("description", "")
            )
            
            # Tentar carregar script Python se existir
            script_file = os.path.join(ext_path, "extension.py")
            if os.path.exists(script_file):
                spec = importlib.util.spec_from_file_location(f"extension_{ext_name}", script_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Vincular métodos da extensão
                if hasattr(module, "on_load"):
                    extension.on_load = lambda b: module.on_load(b)
                if hasattr(module, "on_unload"):
                    extension.on_unload = lambda: module.on_unload()
                if hasattr(module, "on_page_load"):
                    extension.on_page_load = lambda wv, u: module.on_page_load(wv, u)
                if hasattr(module, "on_url_changed"):
                    extension.on_url_changed = lambda wv, u: module.on_url_changed(wv, u)
            
            self.extensions[ext_name] = extension
            extension.on_load(self.browser)
            return True
            
        except Exception as e:
            print(f"Erro ao carregar extensão {ext_name}: {e}")
            return False
    
    def unload_extension(self, ext_name):
        """Descarregar uma extensão"""
        if ext_name in self.extensions:
            self.extensions[ext_name].on_unload()
            del self.extensions[ext_name]
            return True
        return False
    
    def on_page_load(self, web_view, url):
        """Notificar todas as extensões sobre carregamento de página"""
        for ext in self.extensions.values():
            try:
                ext.on_page_load(web_view, url)
            except Exception as e:
                print(f"Erro na extensão {ext.name}: {e}")
    
    def on_url_changed(self, web_view, url):
        """Notificar todas as extensões sobre mudança de URL"""
        for ext in self.extensions.values():
            try:
                ext.on_url_changed(web_view, url)
            except Exception as e:
                print(f"Erro na extensão {ext.name}: {e}")
    
    def get_extensions_list(self):
        """Obter lista de extensões carregadas"""
        return [(name, ext) for name, ext in self.extensions.items()]


class ExtensionsWindow(QDialog):
    """Janela de gerenciamento de extensões"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.lang = parent.lang if parent else LanguageManager()
        self.setWindowTitle(self.lang.get("extensions_title"))
        self.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        # Lista de extensões
        self.extensions_list = QListWidget()
        layout.addWidget(QLabel(self.lang.get("extensions_settings")))
        layout.addWidget(self.extensions_list)
        
        # Botões
        btn_layout = QHBoxLayout()
        
        btn_install = QPushButton(self.lang.get("install_extension"))
        btn_install.clicked.connect(self.install_extension)
        btn_layout.addWidget(btn_install)
        
        btn_remove = QPushButton(self.lang.get("remove_extension"))
        btn_remove.clicked.connect(self.remove_extension)
        btn_layout.addWidget(btn_remove)
        
        btn_close = QPushButton(self.lang.get("close"))
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.refresh_list()
    
    def refresh_list(self):
        """Atualizar lista de extensões"""
        self.extensions_list.clear()
        extensions = self.parent.extension_manager.get_extensions_list()
        
        if not extensions:
            self.extensions_list.addItem(self.lang.get("no_extensions"))
        else:
            for name, ext in extensions:
                item_text = f"{ext.name} v{ext.version} - {ext.author}\n  {ext.description}"
                self.extensions_list.addItem(item_text)
    
    def install_extension(self):
        """Instalar nova extensão"""
        folder = QFileDialog.getExistingDirectory(
            self,
            self.lang.get("install_extension"),
            "extensions"
        )
        
        if folder:
            ext_name = os.path.basename(folder)
            target_path = os.path.join("extensions", ext_name)
            
            try:
                if os.path.exists(target_path):
                    shutil.rmtree(target_path)
                shutil.copytree(folder, target_path)
                
                if self.parent.extension_manager.load_extension(ext_name):
                    QMessageBox.information(
                        self,
                        self.lang.get("extensions_title"),
                        self.lang.get("extension_loaded").format(ext_name)
                    )
                    self.refresh_list()
                else:
                    QMessageBox.warning(
                        self,
                        self.lang.get("error_title"),
                        self.lang.get("extension_error").format(ext_name)
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.lang.get("error_title"),
                    f"Erro ao instalar extensão: {e}"
                )
    
    def remove_extension(self):
        """Remover extensão selecionada"""
        current_item = self.extensions_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self,
            self.lang.get("extensions_title"),
            f"Remover extensão '{current_item.text().split(' v')[0]}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            ext_name = current_item.text().split(' v')[0].lower().replace(' ', '_')
            
            if self.parent.extension_manager.unload_extension(ext_name):
                ext_path = os.path.join("extensions", ext_name)
                if os.path.exists(ext_path):
                    shutil.rmtree(ext_path)
                QMessageBox.information(
                    self,
                    self.lang.get("extensions_title"),
                    self.lang.get("extension_removed").format(ext_name)
                )
                self.refresh_list()


# ==================== CLASSES EXISTENTES (MODIFICADAS) ====================
class VisualizadorCodigoFonte(QDialog):
    """Janela para visualizar código fonte HTML"""
    def __init__(self, parent=None, url="", html="", titulo=""):
        super().__init__(parent)
        self.parent = parent
        self.lang = parent.lang if parent else LanguageManager()
        self.url = url
        self.html_original = html
        self.titulo = titulo
        
        self.setWindowTitle(self.lang.get("source_viewer_title").format(titulo[:50]))
        self.setGeometry(200, 200, 900, 700)
        
        layout = QVBoxLayout()
        
        # Barra de informações
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        info_layout = QHBoxLayout()
        
        self.url_label = QLabel(f"<b>URL:</b> {url}")
        self.url_label.setWordWrap(True)
        info_layout.addWidget(self.url_label, 1)
        
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)
        
        # Editor de código fonte
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(html)
        self.text_edit.setFont(QFont("Courier New", 10))
        
        # Configurar syntax highlighting básico
        self.highlighter = SyntaxHighlighter(self.text_edit.document())
        
        layout.addWidget(self.text_edit, 1)
        
        # Barra de busca
        search_frame = QFrame()
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel(self.lang.get("search")))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.lang.get("search_placeholder"))
        self.search_input.textChanged.connect(self.buscar_texto)
        search_layout.addWidget(self.search_input)
        
        self.btn_search_next = QPushButton(self.lang.get("next"))
        self.btn_search_next.clicked.connect(lambda: self.buscar_texto_direcao(1))
        search_layout.addWidget(self.btn_search_next)
        
        self.btn_search_prev = QPushButton(self.lang.get("prev"))
        self.btn_search_prev.clicked.connect(lambda: self.buscar_texto_direcao(-1))
        search_layout.addWidget(self.btn_search_prev)
        
        self.search_count_label = QLabel("0/0")
        search_layout.addWidget(self.search_count_label)
        
        search_frame.setLayout(search_layout)
        layout.addWidget(search_frame)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.btn_copy = QPushButton(f"📋 {self.lang.get('copy_code')}")
        self.btn_copy.clicked.connect(self.copiar_codigo)
        buttons_layout.addWidget(self.btn_copy)
        
        self.btn_save = QPushButton(f"💾 {self.lang.get('save_code')}")
        self.btn_save.clicked.connect(self.salvar_codigo)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_refresh = QPushButton(f"⟳ {self.lang.get('refresh_code')}")
        self.btn_refresh.clicked.connect(self.atualizar_codigo)
        buttons_layout.addWidget(self.btn_refresh)
        
        self.btn_word_wrap = QPushButton(f"📝 {self.lang.get('word_wrap')}")
        self.btn_word_wrap.setCheckable(True)
        self.btn_word_wrap.toggled.connect(self.toggle_word_wrap)
        buttons_layout.addWidget(self.btn_word_wrap)
        
        buttons_layout.addStretch()
        
        self.btn_close = QPushButton(self.lang.get("close"))
        self.btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Variáveis para busca
        self.search_positions = []
        self.current_search_index = -1
        
        # Barra de status do visualizador
        self.status_label = QLabel(self.lang.get("ready"))
        layout.addWidget(self.status_label)
    
    def buscar_texto(self):
        """Buscar texto no código fonte"""
        texto_busca = self.search_input.text()
        if not texto_busca:
            self.search_positions = []
            self.current_search_index = -1
            self.search_count_label.setText("0/0")
            cursor = self.text_edit.textCursor()
            cursor.clearSelection()
            self.text_edit.setTextCursor(cursor)
            return
        
        # Encontrar todas as ocorrências
        self.search_positions = []
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        while True:
            cursor = self.text_edit.document().find(texto_busca, cursor)
            if cursor.isNull():
                break
            self.search_positions.append(cursor.position())
            cursor.movePosition(QTextCursor.NextCharacter)
        
        if self.search_positions:
            self.current_search_index = 0
            self.search_count_label.setText(f"1/{len(self.search_positions)}")
            self.destacar_busca(0)
        else:
            self.current_search_index = -1
            self.search_count_label.setText("0/0")
            QMessageBox.information(self, self.lang.get("search"), self.lang.get("no_results").format(texto_busca))
    
    def buscar_texto_direcao(self, direcao):
        """Buscar texto na direção especificada"""
        if not self.search_positions:
            return
        
        self.current_search_index += direcao
        if self.current_search_index >= len(self.search_positions):
            self.current_search_index = 0
        elif self.current_search_index < 0:
            self.current_search_index = len(self.search_positions) - 1
        
        self.destacar_busca(self.current_search_index)
        self.search_count_label.setText(f"{self.current_search_index + 1}/{len(self.search_positions)}")
    
    def destacar_busca(self, index):
        """Destacar a ocorrência da busca"""
        if index < 0 or index >= len(self.search_positions):
            return
        
        cursor = self.text_edit.textCursor()
        cursor.setPosition(self.search_positions[index])
        cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, len(self.search_input.text()))
        self.text_edit.setTextCursor(cursor)
        self.text_edit.ensureCursorVisible()
    
    def copiar_codigo(self):
        """Copiar código fonte para área de transferência"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text_edit.toPlainText())
        QMessageBox.information(self, self.lang.get("copy_code"), self.lang.get("code_copied"))
    
    def salvar_codigo(self):
        """Salvar código fonte em arquivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            self.lang.get("save_code"),
            f"{self.titulo[:30].replace(' ', '_')}.html",
            "Arquivos HTML (*.html);;Arquivos de texto (*.txt);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, self.lang.get("save_code"), f"Código fonte salvo em:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, self.lang.get("error_title"), self.lang.get("error_save_file").format(e))
    
    def atualizar_codigo(self):
        """Atualizar código fonte da página atual"""
        web_view = self.parent.get_current_web_view()
        if web_view:
            self.status_label.setText(self.lang.get("refresh_code") + "...")
            web_view.page().toHtml(self.on_html_loaded)
    
    def on_html_loaded(self, html):
        """Callback quando o HTML é carregado"""
        self.text_edit.setPlainText(html)
        self.html_original = html
        self.search_positions = []
        self.search_input.clear()
        self.status_label.setText(self.lang.get("code_updated"))
        QMessageBox.information(self, self.lang.get("refresh_code"), self.lang.get("code_updated"))
    
    def toggle_word_wrap(self, checked):
        """Alternar quebra de linha"""
        if checked:
            self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        else:
            self.text_edit.setLineWrapMode(QTextEdit.NoWrap)


class SyntaxHighlighter(QSyntaxHighlighter):
    """Realce de sintaxe para HTML/CSS/JS"""
    def __init__(self, document):
        super().__init__(document)
        
        # Regras para HTML tags
        self.rules = []
        
        # Tags HTML
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor(0, 0, 255))
        tag_format.setFontWeight(QFont.Bold)
        self.rules.append((QRegExp("<[^>]+>"), tag_format))
        
        # Atributos HTML
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor(128, 0, 128))
        self.rules.append((QRegExp("\\b\\w+=\\s*[\"'][^\"']*[\"']"), attr_format))
        
        # Comentários HTML
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(0, 128, 0))
        comment_format.setFontItalic(True)
        self.rules.append((QRegExp("<!--[^>]*-->"), comment_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(255, 0, 0))
        self.rules.append((QRegExp("[\"'][^\"']*[\"']"), string_format))
        
        # CSS dentro de style
        css_format = QTextCharFormat()
        css_format.setForeground(QColor(0, 128, 128))
        self.rules.append((QRegExp("style\\s*=\\s*[\"'][^\"']*[\"']"), css_format))
        
        # JavaScript dentro de script
        js_format = QTextCharFormat()
        js_format.setForeground(QColor(255, 128, 0))
        self.rules.append((QRegExp("script\\s*=\\s*[\"'][^\"']*[\"']"), js_format))
    
    def highlightBlock(self, text):
        """Aplicar realce de sintaxe ao bloco de texto"""
        for pattern, format in self.rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class HistoricoWindow(QDialog):
    """Janela de histórico"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.lang = parent.lang if parent else LanguageManager()
        self.setWindowTitle(self.lang.get("history_title"))
        self.setGeometry(300, 300, 600, 400)
        
        layout = QVBoxLayout()
        
        # Lista de histórico
        self.historico_list = QListWidget()
        self.historico_list.itemDoubleClicked.connect(self.abrir_historico)
        layout.addWidget(QLabel("Histórico de navegação:"))
        layout.addWidget(self.historico_list)
        
        # Botões
        buttons_layout = QHBoxLayout()
        btn_clear = QPushButton(self.lang.get("clear_history"))
        btn_close = QPushButton(self.lang.get("close"))
        btn_clear.clicked.connect(self.limpar_historico)
        btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_clear)
        buttons_layout.addWidget(btn_close)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Carregar histórico
        self.carregar_historico()
    
    def carregar_historico(self):
        """Carregar histórico do arquivo"""
        try:
            if os.path.exists("historico.json"):
                with open("historico.json", "r", encoding="utf-8") as f:
                    historico = json.load(f)
                    for item in reversed(historico):  # Mostrar do mais recente
                        titulo = item.get("titulo", "Sem título")
                        url = item.get("url", "")
                        data = item.get("data", "")
                        self.historico_list.addItem(f"{data} - {titulo}\n{url}")
        except Exception as e:
            print(self.lang.get("error_load_history").format(e))
    
    def abrir_historico(self, item):
        """Abrir URL do histórico"""
        texto = item.text()
        linhas = texto.split("\n")
        if len(linhas) >= 2:
            url = linhas[1]
            self.parent.nova_aba(url)
            self.accept()
    
    def limpar_historico(self):
        """Limpar histórico"""
        reply = QMessageBox.question(self, self.lang.get("clear_history"), 
                                     self.lang.get("clear_history_confirm"),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists("historico.json"):
                    os.remove("historico.json")
                self.historico_list.clear()
                QMessageBox.information(self, self.lang.get("clear_history"), self.lang.get("history_cleared"))
            except Exception as e:
                QMessageBox.critical(self, self.lang.get("error_title"), self.lang.get("error_clear_history").format(e))


class ConfiguracoesWindow(QDialog):
    """Janela de configurações"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.lang = parent.lang
        self.setWindowTitle(self.lang.get("settings_title"))
        self.setGeometry(200, 200, 450, 600)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Informações do navegador
        group_info = QGroupBox(self.lang.get("about_title"))
        info_layout = QVBoxLayout()
        info_label = QLabel(f"""<b>Python Navigator 1.0.2</b><br>
        {self.lang.get("about_desc")}<br>
        Identificador: PythonNavigator/1.0.2""")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        group_info.setLayout(info_layout)
        layout.addWidget(group_info)
        
        # Página inicial
        group_home = QGroupBox(self.lang.get("home_page"))
        home_layout = QHBoxLayout()
        self.home_page_edit = QLineEdit()
        self.home_page_edit.setText(parent.home_page)
        home_layout.addWidget(QLabel("URL:"))
        home_layout.addWidget(self.home_page_edit)
        group_home.setLayout(home_layout)
        layout.addWidget(group_home)
        
        # Motor de busca
        group_search = QGroupBox(self.lang.get("search_engine").replace(":", ""))
        search_layout = QVBoxLayout()
        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "Bing", "DuckDuckGo"])
        search_layout.addWidget(QLabel(self.lang.get("search_engine")))
        search_layout.addWidget(self.search_engine)
        group_search.setLayout(search_layout)
        layout.addWidget(group_search)
        
        # Configurações de JavaScript
        group_js = QGroupBox(self.lang.get("javascript_settings"))
        js_layout = QVBoxLayout()
        
        self.js_enabled = QCheckBox(self.lang.get("enable_js"))
        self.js_enabled.setChecked(parent.javascript_enabled)
        self.js_enabled.toggled.connect(self.on_js_toggled)
        js_layout.addWidget(self.js_enabled)
        
        self.js_info = QLabel(self.lang.get("js_info"))
        self.js_info.setWordWrap(True)
        self.js_info.setStyleSheet("color: #666; font-size: 10px;")
        js_layout.addWidget(self.js_info)
        
        group_js.setLayout(js_layout)
        layout.addWidget(group_js)
        
        # Configurações de Idioma
        group_lang = QGroupBox(self.lang.get("language_settings"))
        lang_layout = QVBoxLayout()
        
        self.lang_combo = QComboBox()
        self.carregar_idiomas_disponiveis()
        lang_layout.addWidget(QLabel(self.lang.get("select_language")))
        lang_layout.addWidget(self.lang_combo)
        
        group_lang.setLayout(lang_layout)
        layout.addWidget(group_lang)
        
        # Skins/Temas
        group_skin = QGroupBox(self.lang.get("appearance_settings"))
        skin_layout = QVBoxLayout()
        
        self.skin_combo = QComboBox()
        self.carregar_skins_disponiveis()
        skin_layout.addWidget(QLabel(self.lang.get("select_skin")))
        skin_layout.addWidget(self.skin_combo)
        
        # Pré-visualização
        self.skin_preview = QLabel()
        self.skin_preview.setFixedHeight(50)
        self.skin_preview.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        skin_layout.addWidget(self.skin_preview)
        
        group_skin.setLayout(skin_layout)
        layout.addWidget(group_skin)
        
        # Conectar eventos
        self.skin_combo.currentTextChanged.connect(self.preview_skin)
        
        # Botões
        buttons_layout = QHBoxLayout()
        btn_save = QPushButton(self.lang.get("save_config"))
        btn_cancel = QPushButton(self.lang.get("cancel_config"))
        btn_save.clicked.connect(self.save_config)
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Carregar configurações salvas
        self.load_config()
    
    def on_js_toggled(self, enabled):
        """Quando o JavaScript é ativado/desativado"""
        if not enabled:
            reply = QMessageBox.question(self, self.lang.get("javascript_settings"), 
                                         self.lang.get("js_info") + "\n\nDeseja continuar?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                self.js_enabled.setChecked(True)
    
    def carregar_idiomas_disponiveis(self):
        """Carregar lista de idiomas disponíveis"""
        languages = self.lang.get_available_languages()
        for lang in languages:
            nome = "Português (Brasil)" if lang == "pt_BR" else "English (US)" if lang == "en_US" else lang
            self.lang_combo.addItem(nome, lang)
        
        # Selecionar idioma atual
        current_lang = self.lang.current_language
        for i in range(self.lang_combo.count()):
            if self.lang_combo.itemData(i) == current_lang:
                self.lang_combo.setCurrentIndex(i)
                break
    
    def carregar_skins_disponiveis(self):
        """Carregar lista de skins disponíveis"""
        self.skin_combo.addItem("Padrão (Claro)")
        
        # Criar pasta de skins se não existir
        if not os.path.exists("skins"):
            os.makedirs("skins")
            self.criar_skins_padrao()
        
        # Procurar arquivos CSS na pasta skins
        try:
            for file in os.listdir("skins"):
                if file.endswith(".css"):
                    nome_skin = file.replace(".css", "").capitalize()
                    self.skin_combo.addItem(nome_skin)
        except Exception as e:
            print(f"Erro ao carregar skins: {e}")
    
    def criar_skins_padrao(self):
        """Criar skins de exemplo"""
        dark_skin = """
QMainWindow, QDialog {
    background-color: #2b2b2b;
}

QTabBar::tab {
    background: #3c3c3c;
    color: #ffffff;
    padding: 8px 15px;
    margin: 2px;
}

QTabBar::tab:selected {
    background: #4a4a4a;
    border-top: 2px solid #0078d7;
}

QTabBar::tab:hover {
    background: #505050;
}

QLineEdit {
    padding: 5px;
    border: 1px solid #555;
    border-radius: 3px;
    background-color: #3c3c3c;
    color: #ffffff;
}

QPushButton {
    background: #3c3c3c;
    border: 1px solid #555;
    color: #ffffff;
    padding: 5px 10px;
    border-radius: 3px;
}

QPushButton:hover {
    background: #505050;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMenuBar::item {
    padding: 5px 10px;
}

QMenuBar::item:selected {
    background-color: #3c3c3c;
}

QMenu {
    background-color: #2b2b2b;
    color: #ffffff;
    border: 1px solid #555;
}

QMenu::item:selected {
    background-color: #3c3c3c;
}

QGroupBox {
    color: #ffffff;
    border: 1px solid #555;
    margin-top: 10px;
}

QLabel {
    color: #ffffff;
}
"""
        
        blue_skin = """
QMainWindow, QDialog {
    background-color: #e3f2fd;
}

QTabBar::tab {
    background: #bbdef5;
    color: #0d47a1;
    padding: 8px 15px;
    margin: 2px;
    border-radius: 5px;
}

QTabBar::tab:selected {
    background: #1976d2;
    color: white;
    border-top: 2px solid #ffd700;
}

QTabBar::tab:hover {
    background: #64b5f6;
    color: white;
}

QLineEdit {
    padding: 5px;
    border: 2px solid #1976d2;
    border-radius: 5px;
    background-color: white;
    color: #0d47a1;
}

QPushButton {
    background: #1976d2;
    border: none;
    color: white;
    padding: 5px 10px;
    border-radius: 5px;
}

QPushButton:hover {
    background: #0d47a1;
}

QMenuBar {
    background-color: #bbdef5;
    color: #0d47a1;
}

QMenuBar::item:selected {
    background-color: #1976d2;
    color: white;
}

QMenu {
    background-color: white;
    color: #0d47a1;
    border: 1px solid #1976d2;
}

QMenu::item:selected {
    background-color: #bbdef5;
}

QGroupBox {
    color: #0d47a1;
    border: 2px solid #1976d2;
    border-radius: 5px;
    margin-top: 10px;
}

QLabel {
    color: #0d47a1;
}
"""
        
        try:
            with open("skins/escura.css", "w", encoding="utf-8") as f:
                f.write(dark_skin)
            with open("skins/azul.css", "w", encoding="utf-8") as f:
                f.write(blue_skin)
        except Exception as e:
            print(f"Erro ao criar skins: {e}")
    
    def preview_skin(self, skin_name):
        """Pré-visualizar a skin selecionada"""
        if skin_name == "Padrão (Claro)":
            css = ""
        else:
            skin_file = f"skins/{skin_name.lower()}.css"
            try:
                with open(skin_file, "r", encoding="utf-8") as f:
                    css = f.read()
            except:
                css = ""
        
        preview_css = """
        QLabel {
            font-size: 12px;
        }
        """
        self.skin_preview.setStyleSheet(css + preview_css)
        self.skin_preview.setText(f"Pré-visualização do tema: {skin_name}")
    
    def load_config(self):
        """Carregar configurações salvas"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.home_page_edit.setText(config.get("home_page", "https://www.google.com"))
                    search = config.get("search_engine", "Google")
                    index = self.search_engine.findText(search)
                    if index >= 0:
                        self.search_engine.setCurrentIndex(index)
                    
                    js_enabled = config.get("javascript_enabled", True)
                    self.js_enabled.setChecked(js_enabled)
                    
                    skin = config.get("skin", "Padrão (Claro)")
                    index = self.skin_combo.findText(skin)
                    if index >= 0:
                        self.skin_combo.setCurrentIndex(index)
                        self.preview_skin(skin)
                    
                    # Idioma
                    lang = config.get("language", "pt_BR")
                    for i in range(self.lang_combo.count()):
                        if self.lang_combo.itemData(i) == lang:
                            self.lang_combo.setCurrentIndex(i)
                            break
        except Exception as e:
            print(self.lang.get("error_load_config").format(e))
    
    def save_config(self):
        """Salvar configurações"""
        try:
            config = {
                "home_page": self.home_page_edit.text(),
                "search_engine": self.search_engine.currentText(),
                "javascript_enabled": self.js_enabled.isChecked(),
                "skin": self.skin_combo.currentText(),
                "language": self.lang_combo.currentData()
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Atualizar configurações no navegador
            self.parent.home_page = self.home_page_edit.text()
            self.parent.javascript_enabled = self.js_enabled.isChecked()
            self.parent.aplicar_configuracoes_javascript()
            self.parent.aplicar_skin(self.skin_combo.currentText())
            
            # Mudar idioma se necessário
            new_lang = self.lang_combo.currentData()
            if new_lang != self.parent.lang.current_language:
                self.parent.lang.load_language(new_lang)
                QMessageBox.information(
                    self,
                    self.lang.get("settings_title"),
                    "Idioma alterado. Reinicie o navegador para aplicar completamente."
                )
            
            QMessageBox.information(self, self.lang.get("settings_title"), self.lang.get("config_saved"))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, self.lang.get("error_title"), self.lang.get("error_save_config").format(e))


class SobreWindow(QDialog):
    """Janela Sobre"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.lang = parent.lang if parent else LanguageManager()
        self.setWindowTitle(self.lang.get("about"))
        self.setGeometry(400, 400, 500, 440)
        
        layout = QVBoxLayout()
        
        # Logo e informações
        label_title = QLabel("<h1>🐍 Python Navigator</h1>")
        label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_title)
        
        label_version = QLabel(f"<b>{self.lang.get('about_version')}</b> 1.0.2")
        label_version.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_version)
        
        label_id = QLabel(f"<b>{self.lang.get('about_identifier')}</b> PythonNavigator/1.0.2")
        label_id.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_id)
        
        layout.addWidget(QLabel(""))
        
        label_desc = QLabel(self.lang.get("about_desc"))
        label_desc.setAlignment(Qt.AlignCenter)
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)
        
        layout.addWidget(QLabel(""))
        
        label_features = QLabel(f"""<b>{self.lang.get('about_features')}</b><br>
        {self.lang.get('about_features_list')}""")
        label_features.setAlignment(Qt.AlignLeft)
        label_features.setWordWrap(True)
        layout.addWidget(label_features)
        
        layout.addWidget(QLabel(""))
        
        label_credit = QLabel(self.lang.get("about_credit"))
        label_credit.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_credit)
        
        btn_close = QPushButton(self.lang.get("close"))
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)


class NavegadorAnonimo(QMainWindow):
    """Janela de navegação anônima (modo privado)"""
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.lang = parent.lang if parent else LanguageManager()
        self.setWindowTitle(f"🐍 Python Navigator - {self.lang.get('menu_new_anonymous')}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurar página inicial padrão
        self.home_page = "https://www.google.com"
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        }
        
        self.browser_name = "PythonNavigator"
        self.browser_version = "1.0.2"
        self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.browser_name}/{self.browser_version} Chrome/120.0.0.0 Safari/537.36"
        self.javascript_enabled = True
        self.web_views = {}
        
        self.create_anonymous_profile()
        self.init_ui()
        self.nova_aba()
        
        self.statusBar().showMessage(self.lang.get("anonymous_mode_activated"), 5000)
        
        QMessageBox.information(self, self.lang.get("menu_new_anonymous"), 
                                self.lang.get("anonymous_info"),
                                QMessageBox.Ok)
    
    def create_anonymous_profile(self):
        """Criar perfil anônimo temporário"""
        self.temp_profile_dir = os.path.join(tempfile.gettempdir(), f"python_navigator_anon_{uuid.uuid4().hex}")
        self.profile = QWebEngineProfile("Anonymous", self)
        self.profile.setPersistentStoragePath(self.temp_profile_dir)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        self.profile.setHttpUserAgent(self.user_agent)
        
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu(self.lang.get("menu_file"))
        
        nova_aba_anonima_action = QAction(self.lang.get("menu_new_anonymous"), self)
        nova_aba_anonima_action.setShortcut("Ctrl+Shift+N")
        nova_aba_anonima_action.triggered.connect(self.nova_aba)
        file_menu.addAction(nova_aba_anonima_action)
        
        file_menu.addSeparator()
        
        abrir_arquivo_action = QAction(self.lang.get("menu_open_file"), self)
        abrir_arquivo_action.setShortcut("Ctrl+O")
        abrir_arquivo_action.triggered.connect(self.abrir_arquivo_html)
        file_menu.addAction(abrir_arquivo_action)
        
        file_menu.addSeparator()
        
        sair_action = QAction(self.lang.get("menu_exit"), self)
        sair_action.setShortcut("Ctrl+Q")
        sair_action.triggered.connect(self.close)
        file_menu.addAction(sair_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu(self.lang.get("menu_view"))
        
        ver_codigo_action = QAction(self.lang.get("view_source"), self)
        ver_codigo_action.setShortcut("Ctrl+U")
        ver_codigo_action.triggered.connect(self.visualizar_codigo_fonte)
        view_menu.addAction(ver_codigo_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction(self.lang.get("view_zoom_in"), self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction(self.lang.get("view_zoom_out"), self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction(self.lang.get("view_zoom_reset"), self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Barra de navegação
        nav_bar = QHBoxLayout()
        
        self.btn_back = QPushButton(self.lang.get("btn_back"))
        self.btn_forward = QPushButton(self.lang.get("btn_forward"))
        self.btn_refresh = QPushButton(self.lang.get("btn_refresh"))
        self.btn_home = QPushButton(self.lang.get("btn_home"))
        self.btn_source = QPushButton(self.lang.get("btn_source"))
        self.btn_new_tab = QPushButton(self.lang.get("btn_new_tab"))
        
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_refresh.clicked.connect(self.refresh_page)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_source.clicked.connect(self.visualizar_codigo_fonte)
        self.btn_new_tab.clicked.connect(lambda: self.nova_aba())
        
        self.btn_source.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        nav_bar.addWidget(self.btn_back)
        nav_bar.addWidget(self.btn_forward)
        nav_bar.addWidget(self.btn_refresh)
        nav_bar.addWidget(self.btn_home)
        nav_bar.addWidget(self.btn_source)
        nav_bar.addWidget(self.btn_new_tab)
        nav_bar.addWidget(self.url_bar)
        
        # Sistema de abas
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        
        main_layout.addLayout(nav_bar)
        main_layout.addWidget(self.tabs)
        
        # Atalhos de teclado
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_new.activated.connect(lambda: self.nova_aba())
        
        self.shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_close.activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        
        self.shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        self.shortcut_refresh.activated.connect(self.refresh_page)
        
        self.shortcut_code = QShortcut(QKeySequence("Ctrl+U"), self)
        self.shortcut_code.activated.connect(self.visualizar_codigo_fonte)
        
        self.shortcut_zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_zoom_in.activated.connect(self.zoom_in)
        
        self.shortcut_zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_out.activated.connect(self.zoom_out)
        
        self.shortcut_zoom_reset = QShortcut(QKeySequence("Ctrl+0"), self)
        self.shortcut_zoom_reset.activated.connect(self.zoom_reset)
        
        self.statusBar().showMessage(f"Python Navigator - {self.lang.get('menu_new_anonymous')}")
    
    def zoom_in(self):
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(factor + 0.1)
            self.statusBar().showMessage(self.lang.get("zoom_percent").format(int((factor + 0.1) * 100)), 2000)
    
    def zoom_out(self):
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(max(0.3, factor - 0.1))
            self.statusBar().showMessage(self.lang.get("zoom_percent").format(int((factor - 0.1) * 100)), 2000)
    
    def zoom_reset(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(1.0)
            self.statusBar().showMessage(self.lang.get("zoom_100"), 2000)
    
    def abrir_arquivo_html(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            self.lang.get("menu_open_file"), 
            "", 
            "Arquivos HTML (*.html *.htm);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            file_url = QUrl.fromLocalFile(file_path)
            self.nova_aba(file_url.toString())
    
    def visualizar_codigo_fonte(self):
        web_view = self.get_current_web_view()
        if web_view:
            url = web_view.url().toString()
            titulo = web_view.title()
            self.statusBar().showMessage(self.lang.get("refresh_code") + "...")
            web_view.page().toHtml(lambda html: self.mostrar_visualizador_codigo(url, html, titulo))
    
    def mostrar_visualizador_codigo(self, url, html, titulo):
        visualizador = VisualizadorCodigoFonte(self, url, html, titulo)
        visualizador.exec_()
        self.statusBar().showMessage(self.lang.get("code_loaded"), 3000)
    
    def nova_aba(self, url=None):
        if url is None or isinstance(url, bool):
            url = self.home_page
        elif not isinstance(url, str):
            url = str(url)
        
        url_str = str(url)
        
        tab_widget = QWidget()
        layout = QVBoxLayout()
        tab_widget.setLayout(layout)
        
        web_view = QWebEngineView()
        web_view.setPage(QWebEnginePage(self.profile, web_view))
        web_view.page().profile().setHttpUserAgent(self.user_agent)
        
        settings = web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        
        try:
            web_view.setUrl(QUrl(url_str))
        except Exception as e:
            print(f"Erro ao carregar URL: {e}")
            web_view.setUrl(QUrl(self.home_page))
        
        web_view.urlChanged.connect(self.on_url_changed)
        web_view.titleChanged.connect(self.on_title_changed)
        web_view.loadFinished.connect(self.on_load_finished)
        
        layout.addWidget(web_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        index = self.tabs.addTab(tab_widget, f"🕶️ {self.lang.get('loading')}...")
        self.tabs.setCurrentIndex(index)
        
        self.web_views[tab_widget] = web_view
        
        return web_view
    
    def get_current_web_view(self):
        current_widget = self.tabs.currentWidget()
        if current_widget and current_widget in self.web_views:
            return self.web_views[current_widget]
        return None
    
    def get_tab_widget_from_web_view(self, web_view):
        for tab_widget, wv in self.web_views.items():
            if wv == web_view:
                return tab_widget
        return None
    
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
            
        if not url.startswith("http://") and not url.startswith("https://"):
            if '.' in url and ' ' not in url and not url.startswith("file://"):
                url = "https://" + url
            else:
                url = self.search_engines.get("Google", "https://www.google.com/search?q={}").format(quote(url))
        
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(url))
    
    def on_url_changed(self, url):
        web_view = self.sender()
        current_view = self.get_current_web_view()
        
        if current_view == web_view:
            self.url_bar.setText(url.toString())
            self.url_bar.setCursorPosition(0)
    
    def on_title_changed(self, title):
        web_view = self.sender()
        tab_widget = self.get_tab_widget_from_web_view(web_view)
        
        if tab_widget:
            index = self.tabs.indexOf(tab_widget)
            if index >= 0:
                if len(title) > 30:
                    title = title[:27] + "..."
                self.tabs.setTabText(index, f"🕶️ {title}" if title else f"🕶️ {self.lang.get('new_tab')}")
    
    def on_load_finished(self, ok):
        self.update_navigation_buttons()
        self.statusBar().showMessage(f"Python Navigator - {self.lang.get('page_loaded')}", 3000)
    
    def update_navigation_buttons(self):
        web_view = self.get_current_web_view()
        if web_view:
            self.btn_back.setEnabled(web_view.history().canGoBack())
            self.btn_forward.setEnabled(web_view.history().canGoForward())
    
    def go_back(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.back()
    
    def go_forward(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.forward()
    
    def refresh_page(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.reload()
    
    def go_home(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(self.home_page))
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            tab_widget = self.tabs.widget(index)
            if tab_widget:
                if tab_widget in self.web_views:
                    del self.web_views[tab_widget]
                self.tabs.removeTab(index)
                tab_widget.deleteLater()
        else:
            self.close()
    
    def current_tab_changed(self, index):
        if index >= 0:
            web_view = self.get_current_web_view()
            if web_view:
                self.url_bar.setText(web_view.url().toString())
                self.update_navigation_buttons()
    
    def closeEvent(self, event):
        try:
            if hasattr(self, 'temp_profile_dir') and os.path.exists(self.temp_profile_dir):
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
        except Exception as e:
            print(f"Erro ao limpar dados temporários: {e}")
        event.accept()


class NavegadorWeb(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Gerenciador de idiomas
        self.lang = LanguageManager()
        
        self.setWindowTitle(f"Python Navigator 1.0.2")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurar página inicial padrão
        self.home_page = "https://www.google.com"
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        }
        
        self.browser_name = "PythonNavigator"
        self.browser_version = "1.0.2"
        self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.browser_name}/{self.browser_version} Chrome/120.0.0.0 Safari/537.36"
        
        self.javascript_enabled = True
        self.current_skin = "Padrão (Claro)"
        self.web_views = {}
        
        # Gerenciador de extensões
        self.extension_manager = ExtensionManager(self)
        
        self.carregar_configuracoes()
        self.init_ui()
        self.aplicar_skin(self.current_skin)
        self.configurar_user_agent()
        self.aplicar_configuracoes_javascript()
        self.nova_aba()
    
    def configurar_user_agent(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(self.user_agent)
    
    def aplicar_configuracoes_javascript(self):
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()
        
        if self.javascript_enabled:
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
            self.statusBar().showMessage(f"Python Navigator {self.browser_version} - {self.lang.get('js_enabled')}", 3000)
        else:
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, False)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
            settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
            self.statusBar().showMessage(f"Python Navigator {self.browser_version} - {self.lang.get('js_disabled')}", 3000)
        
        for tab_widget, web_view in self.web_views.items():
            page_settings = web_view.page().settings()
            page_settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
            page_settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, self.javascript_enabled)
            page_settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, self.javascript_enabled)
    
    def carregar_configuracoes(self):
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.home_page = config.get("home_page", self.home_page)
                    self.current_skin = config.get("skin", "Padrão (Claro)")
                    self.javascript_enabled = config.get("javascript_enabled", True)
                    
                    lang = config.get("language", "pt_BR")
                    self.lang.load_language(lang)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def aplicar_skin(self, skin_name):
        self.current_skin = skin_name
        
        if skin_name == "Padrão (Claro)":
            self.setStyleSheet(f"""
                QMainWindow::title {{
                    font-weight: bold;
                }}
                QTabBar::tab {{
                    background: #f0f0f0;
                    padding: 8px 15px;
                    margin: 2px;
                }}
                QTabBar::tab:selected {{
                    background: white;
                    border-top: 2px solid #0078d7;
                }}
                QTabBar::tab:hover {{
                    background: #e0e0e0;
                }}
                QLineEdit {{
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }}
                QPushButton {{
                    background: #f0f0f0;
                    border: 1px solid #ccc;
                    padding: 5px 10px;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    background: #e0e0e0;
                }}
                QMenuBar {{
                    background-color: #f8f8f8;
                }}
                QMenuBar::item {{
                    padding: 5px 10px;
                }}
                QMenuBar::item:selected {{
                    background-color: #e0e0e0;
                }}
            """)
        else:
            skin_file = f"skins/{skin_name.lower()}.css"
            try:
                with open(skin_file, "r", encoding="utf-8") as f:
                    css = f.read()
                    self.setStyleSheet(css)
            except Exception as e:
                print(f"Erro ao carregar skin {skin_name}: {e}")
                self.setStyleSheet("")
    
    def salvar_historico(self, url, titulo):
        try:
            historico = []
            if os.path.exists("historico.json"):
                with open("historico.json", "r", encoding="utf-8") as f:
                    historico = json.load(f)
            
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            historico.append({
                "url": url,
                "titulo": titulo,
                "data": data_atual,
                "navegador": f"{self.browser_name} {self.browser_version}"
            })
            
            if len(historico) > 100:
                historico = historico[-100:]
            
            with open("historico.json", "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def abrir_janela_anonima(self):
        self.janela_anonima = NavegadorAnonimo(self)
        self.janela_anonima.show()
    
    def abrir_gerenciador_extensoes(self):
        ext_window = ExtensionsWindow(self)
        ext_window.exec_()
    
    def visualizar_codigo_fonte(self):
        web_view = self.get_current_web_view()
        if web_view:
            url = web_view.url().toString()
            titulo = web_view.title()
            self.statusBar().showMessage(self.lang.get("refresh_code") + "...")
            web_view.page().toHtml(lambda html: self.mostrar_visualizador_codigo(url, html, titulo))
    
    def mostrar_visualizador_codigo(self, url, html, titulo):
        visualizador = VisualizadorCodigoFonte(self, url, html, titulo)
        visualizador.exec_()
        self.statusBar().showMessage(self.lang.get("code_loaded"), 3000)
    
    def init_ui(self):
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu(self.lang.get("menu_file"))
        
        nova_janela_action = QAction(self.lang.get("menu_new_window"), self)
        nova_janela_action.setShortcut("Ctrl+N")
        nova_janela_action.triggered.connect(self.nova_janela)
        file_menu.addAction(nova_janela_action)
        
        nova_janela_anonima_action = QAction(self.lang.get("menu_new_anonymous"), self)
        nova_janela_anonima_action.setShortcut("Ctrl+Shift+N")
        nova_janela_anonima_action.triggered.connect(self.abrir_janela_anonima)
        file_menu.addAction(nova_janela_anonima_action)
        
        file_menu.addSeparator()
        
        abrir_arquivo_action = QAction(self.lang.get("menu_open_file"), self)
        abrir_arquivo_action.setShortcut("Ctrl+O")
        abrir_arquivo_action.triggered.connect(self.abrir_arquivo_html)
        file_menu.addAction(abrir_arquivo_action)
        
        file_menu.addSeparator()
        
        sair_action = QAction(self.lang.get("menu_exit"), self)
        sair_action.setShortcut("Ctrl+Q")
        sair_action.triggered.connect(self.close)
        file_menu.addAction(sair_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu(self.lang.get("menu_view"))
        
        ver_codigo_action = QAction(self.lang.get("view_source"), self)
        ver_codigo_action.setShortcut("Ctrl+U")
        ver_codigo_action.triggered.connect(self.visualizar_codigo_fonte)
        view_menu.addAction(ver_codigo_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction(self.lang.get("view_zoom_in"), self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction(self.lang.get("view_zoom_out"), self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction(self.lang.get("view_zoom_reset"), self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Menu Extensões
        extensions_menu = menubar.addMenu(self.lang.get("extensions_settings"))
        
        gerenciar_extensoes_action = QAction(self.lang.get("extensions_title"), self)
        gerenciar_extensoes_action.triggered.connect(self.abrir_gerenciador_extensoes)
        extensions_menu.addAction(gerenciar_extensoes_action)
        
        # Menu Histórico
        historico_menu = menubar.addMenu(self.lang.get("menu_history"))
        
        ver_historico_action = QAction(self.lang.get("view_history"), self)
        ver_historico_action.setShortcut("Ctrl+H")
        ver_historico_action.triggered.connect(self.mostrar_historico)
        historico_menu.addAction(ver_historico_action)
        
        limpar_historico_action = QAction(self.lang.get("clear_history"), self)
        limpar_historico_action.triggered.connect(self.limpar_historico)
        historico_menu.addAction(limpar_historico_action)
        
        # Menu Configurações
        config_menu = menubar.addMenu(self.lang.get("menu_settings"))
        
        config_action = QAction(self.lang.get("preferences"), self)
        config_action.setShortcut("Ctrl+P")
        config_action.triggered.connect(self.mostrar_configuracoes)
        config_menu.addAction(config_action)
        
        # Menu Ajuda
        ajuda_menu = menubar.addMenu(self.lang.get("menu_help"))
        
        sobre_action = QAction(self.lang.get("about"), self)
        sobre_action.triggered.connect(self.mostrar_sobre)
        ajuda_menu.addAction(sobre_action)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Barra de navegação
        nav_bar = QHBoxLayout()
        
        self.btn_back = QPushButton(self.lang.get("btn_back"))
        self.btn_forward = QPushButton(self.lang.get("btn_forward"))
        self.btn_refresh = QPushButton(self.lang.get("btn_refresh"))
        self.btn_home = QPushButton(self.lang.get("btn_home"))
        self.btn_source = QPushButton(self.lang.get("btn_source"))
        self.btn_anonymous = QPushButton(self.lang.get("btn_anonymous"))
        self.btn_extensions = QPushButton(self.lang.get("btn_extensions"))
        self.btn_new_tab = QPushButton(self.lang.get("btn_new_tab"))
        
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_refresh.clicked.connect(self.refresh_page)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_source.clicked.connect(self.visualizar_codigo_fonte)
        self.btn_anonymous.clicked.connect(self.abrir_janela_anonima)
        self.btn_extensions.clicked.connect(self.abrir_gerenciador_extensoes)
        self.btn_new_tab.clicked.connect(lambda: self.nova_aba())
        
        self.btn_source.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        self.btn_anonymous.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        
        self.btn_extensions.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        nav_bar.addWidget(self.btn_back)
        nav_bar.addWidget(self.btn_forward)
        nav_bar.addWidget(self.btn_refresh)
        nav_bar.addWidget(self.btn_home)
        nav_bar.addWidget(self.btn_source)
        nav_bar.addWidget(self.btn_anonymous)
        nav_bar.addWidget(self.btn_extensions)
        nav_bar.addWidget(self.btn_new_tab)
        nav_bar.addWidget(self.url_bar)
        
        # Sistema de abas
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        
        main_layout.addLayout(nav_bar)
        main_layout.addWidget(self.tabs)
        
        # Atalhos de teclado
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_new.activated.connect(lambda: self.nova_aba())
        
        self.shortcut_new_window = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new_window.activated.connect(self.nova_janela)
        
        self.shortcut_new_anon = QShortcut(QKeySequence("Ctrl+Shift+N"), self)
        self.shortcut_new_anon.activated.connect(self.abrir_janela_anonima)
        
        self.shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_close.activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        
        self.shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        self.shortcut_refresh.activated.connect(self.refresh_page)
        
        self.shortcut_code = QShortcut(QKeySequence("Ctrl+U"), self)
        self.shortcut_code.activated.connect(self.visualizar_codigo_fonte)
        
        self.shortcut_zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_zoom_in.activated.connect(self.zoom_in)
        
        self.shortcut_zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_out.activated.connect(self.zoom_out)
        
        self.shortcut_zoom_reset = QShortcut(QKeySequence("Ctrl+0"), self)
        self.shortcut_zoom_reset.activated.connect(self.zoom_reset)
        
        js_status = self.lang.get("js_enabled") if self.javascript_enabled else self.lang.get("js_disabled")
        self.statusBar().showMessage(f"Python Navigator {self.browser_version} - {js_status} - {self.lang.get('ready')}")
    
    def nova_janela(self):
        nova_janela = NavegadorWeb()
        nova_janela.show()
    
    def zoom_in(self):
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(factor + 0.1)
            self.statusBar().showMessage(self.lang.get("zoom_percent").format(int((factor + 0.1) * 100)), 2000)
    
    def zoom_out(self):
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(max(0.3, factor - 0.1))
            self.statusBar().showMessage(self.lang.get("zoom_percent").format(int((factor - 0.1) * 100)), 2000)
    
    def zoom_reset(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(1.0)
            self.statusBar().showMessage(self.lang.get("zoom_100"), 2000)
    
    def abrir_arquivo_html(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            self.lang.get("menu_open_file"), 
            "", 
            "Arquivos HTML (*.html *.htm);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            file_url = QUrl.fromLocalFile(file_path)
            self.nova_aba(file_url.toString())
    
    def mostrar_historico(self):
        historico_window = HistoricoWindow(self)
        historico_window.exec_()
    
    def limpar_historico(self):
        reply = QMessageBox.question(self, self.lang.get("clear_history"), 
                                     self.lang.get("clear_history_confirm"),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists("historico.json"):
                    os.remove("historico.json")
                QMessageBox.information(self, self.lang.get("clear_history"), self.lang.get("history_cleared"))
            except Exception as e:
                QMessageBox.critical(self, self.lang.get("error_title"), self.lang.get("error_clear_history").format(e))
    
    def mostrar_configuracoes(self):
        config_window = ConfiguracoesWindow(self)
        config_window.exec_()
    
    def mostrar_sobre(self):
        sobre_window = SobreWindow(self)
        sobre_window.exec_()
    
    def nova_aba(self, url=None):
        if url is None or isinstance(url, bool):
            url = self.home_page
        elif not isinstance(url, str):
            url = str(url)
        
        url_str = str(url)
        
        tab_widget = QWidget()
        layout = QVBoxLayout()
        tab_widget.setLayout(layout)
        
        web_view = QWebEngineView()
        web_view.page().profile().setHttpUserAgent(self.user_agent)
        
        settings = web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        
        try:
            web_view.setUrl(QUrl(url_str))
        except Exception as e:
            print(f"Erro ao carregar URL: {e}")
            web_view.setUrl(QUrl(self.home_page))
        
        web_view.urlChanged.connect(self.on_url_changed)
        web_view.titleChanged.connect(self.on_title_changed)
        web_view.loadFinished.connect(self.on_load_finished)
        
        layout.addWidget(web_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        index = self.tabs.addTab(tab_widget, f"{self.lang.get('loading')}...")
        self.tabs.setCurrentIndex(index)
        
        self.web_views[tab_widget] = web_view
        
        return web_view
    
    def get_current_web_view(self):
        current_widget = self.tabs.currentWidget()
        if current_widget and current_widget in self.web_views:
            return self.web_views[current_widget]
        return None
    
    def get_tab_widget_from_web_view(self, web_view):
        for tab_widget, wv in self.web_views.items():
            if wv == web_view:
                return tab_widget
        return None
    
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url:
            return
            
        if not url.startswith("http://") and not url.startswith("https://"):
            if '.' in url and ' ' not in url and not url.startswith("file://"):
                url = "https://" + url
            else:
                url = self.search_engines.get("Google", "https://www.google.com/search?q={}").format(quote(url))
        
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(url))
    
    def on_url_changed(self, url):
        web_view = self.sender()
        current_view = self.get_current_web_view()
        
        if current_view == web_view:
            self.url_bar.setText(url.toString())
            self.url_bar.setCursorPosition(0)
        
        # Notificar extensões
        self.extension_manager.on_url_changed(web_view, url.toString())
    
    def on_title_changed(self, title):
        web_view = self.sender()
        tab_widget = self.get_tab_widget_from_web_view(web_view)
        
        if tab_widget:
            index = self.tabs.indexOf(tab_widget)
            if index >= 0:
                if len(title) > 30:
                    title = title[:27] + "..."
                self.tabs.setTabText(index, title if title else self.lang.get("new_tab"))
                
                current_url = web_view.url().toString()
                if current_url and current_url not in ["about:blank", ""]:
                    self.salvar_historico(current_url, title)
    
    def on_load_finished(self, ok):
        self.update_navigation_buttons()
        web_view = self.sender()
        current_url = web_view.url().toString()
        
        # Notificar extensões
        self.extension_manager.on_page_load(web_view, current_url)
        
        js_status = self.lang.get("js_enabled") if self.javascript_enabled else self.lang.get("js_disabled")
        self.statusBar().showMessage(f"Python Navigator {self.browser_version} - {js_status} - {self.lang.get('page_loaded')}", 3000)
    
    def update_navigation_buttons(self):
        web_view = self.get_current_web_view()
        if web_view:
            self.btn_back.setEnabled(web_view.history().canGoBack())
            self.btn_forward.setEnabled(web_view.history().canGoForward())
    
    def go_back(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.back()
    
    def go_forward(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.forward()
    
    def refresh_page(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.reload()
    
    def go_home(self):
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(self.home_page))
    
    def close_tab(self, index):
        if self.tabs.count() > 1:
            tab_widget = self.tabs.widget(index)
            if tab_widget:
                if tab_widget in self.web_views:
                    del self.web_views[tab_widget]
                self.tabs.removeTab(index)
                tab_widget.deleteLater()
        else:
            self.close()
    
    def current_tab_changed(self, index):
        if index >= 0:
            web_view = self.get_current_web_view()
            if web_view:
                self.url_bar.setText(web_view.url().toString())
                self.update_navigation_buttons()


def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("Python Navigator")
    app.setApplicationDisplayName("Python Navigator 1.0.2")
    app.setOrganizationName("PythonNavigator")
    
    navegador = NavegadorWeb()
    navegador.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
