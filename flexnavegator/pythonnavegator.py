import sys
import os
import json
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from urllib.parse import quote

class ConfiguracoesWindow(QDialog):
    """Janela de configurações"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Configurações")
        self.setGeometry(200, 200, 450, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Página inicial
        group_home = QGroupBox("Página inicial")
        home_layout = QHBoxLayout()
        self.home_page_edit = QLineEdit()
        self.home_page_edit.setText(parent.home_page)
        home_layout.addWidget(QLabel("URL:"))
        home_layout.addWidget(self.home_page_edit)
        group_home.setLayout(home_layout)
        layout.addWidget(group_home)
        
        # Motor de busca
        group_search = QGroupBox("Motor de busca")
        search_layout = QVBoxLayout()
        self.search_engine = QComboBox()
        self.search_engine.addItems(["Google", "Bing", "DuckDuckGo"])
        search_layout.addWidget(QLabel("Motor de busca padrão:"))
        search_layout.addWidget(self.search_engine)
        group_search.setLayout(search_layout)
        layout.addWidget(group_search)
        
        # Skins/Temas
        group_skin = QGroupBox("Aparência (Skin)")
        skin_layout = QVBoxLayout()
        
        self.skin_combo = QComboBox()
        self.carregar_skins_disponiveis()
        skin_layout.addWidget(QLabel("Selecione um tema:"))
        skin_layout.addWidget(self.skin_combo)
        
        # Pré-visualização
        self.skin_preview = QLabel()
        self.skin_preview.setFixedHeight(50)
        self.skin_preview.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        skin_layout.addWidget(self.skin_preview)
        
        group_skin.setLayout(skin_layout)
        layout.addWidget(group_skin)
        
        # Conectar evento de mudança de skin
        self.skin_combo.currentTextChanged.connect(self.preview_skin)
        
        # Botões
        buttons_layout = QHBoxLayout()
        btn_save = QPushButton("Salvar")
        btn_cancel = QPushButton("Cancelar")
        btn_save.clicked.connect(self.save_config)
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_save)
        buttons_layout.addWidget(btn_cancel)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Carregar configurações salvas
        self.load_config()
    
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
        # Skin escura
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
        
        # Skin azul
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
        
        # Salvar skins
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
            # Carregar arquivo CSS da skin
            skin_file = f"skins/{skin_name.lower()}.css"
            try:
                with open(skin_file, "r", encoding="utf-8") as f:
                    css = f.read()
            except:
                css = ""
        
        # Atualizar pré-visualização
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
                    
                    # Carregar skin salva
                    skin = config.get("skin", "Padrão (Claro)")
                    index = self.skin_combo.findText(skin)
                    if index >= 0:
                        self.skin_combo.setCurrentIndex(index)
                        self.preview_skin(skin)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def save_config(self):
        """Salvar configurações"""
        try:
            config = {
                "home_page": self.home_page_edit.text(),
                "search_engine": self.search_engine.currentText(),
                "skin": self.skin_combo.currentText()
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Atualizar configurações no navegador
            self.parent.home_page = self.home_page_edit.text()
            self.parent.aplicar_skin(self.skin_combo.currentText())
            
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {e}")

class HistoricoWindow(QDialog):
    """Janela de histórico"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Histórico")
        self.setGeometry(300, 300, 600, 400)
        
        layout = QVBoxLayout()
        
        # Lista de histórico
        self.historico_list = QListWidget()
        self.historico_list.itemDoubleClicked.connect(self.abrir_historico)
        layout.addWidget(QLabel("Histórico de navegação:"))
        layout.addWidget(self.historico_list)
        
        # Botões
        buttons_layout = QHBoxLayout()
        btn_clear = QPushButton("Limpar histórico")
        btn_close = QPushButton("Fechar")
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
            print(f"Erro ao carregar histórico: {e}")
    
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
        reply = QMessageBox.question(self, "Confirmar", 
                                     "Tem certeza que deseja limpar todo o histórico?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists("historico.json"):
                    os.remove("historico.json")
                self.historico_list.clear()
                QMessageBox.information(self, "Sucesso", "Histórico limpo com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao limpar histórico: {e}")

class SobreWindow(QDialog):
    """Janela Sobre"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre")
        self.setGeometry(400, 400, 400, 300)
        
        layout = QVBoxLayout()
        
        # Logo e informações
        label_title = QLabel("<h1>Navegador Web</h1>")
        label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_title)
        
        label_version = QLabel("<b>Versão:</b> 1.0.0")
        label_version.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_version)
        
        label_desc = QLabel("Navegador web desenvolvido em Python com PyQt5")
        label_desc.setAlignment(Qt.AlignCenter)
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)
        
        label_features = QLabel("""<b>Funcionalidades:</b><br>
        • Múltiplas abas<br>
        • Histórico de navegação<br>
        • Configurações personalizáveis<br>
        • Sistema de skins/temas<br>
        • Atalhos de teclado<br>
        • Abrir arquivos HTML locais<br>
        • Motor de busca personalizável""")
        label_features.setAlignment(Qt.AlignLeft)
        label_features.setWordWrap(True)
        layout.addWidget(label_features)
        
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

class NavegadorWeb(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Navegador Web")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurar página inicial padrão
        self.home_page = "https://www.google.com"
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        }
        
        # Skin atual
        self.current_skin = "Padrão (Claro)"
        
        # Dicionário para mapear abas para seus web views
        self.web_views = {}
        
        # Carregar configurações salvas
        self.carregar_configuracoes()
        
        self.init_ui()
        
        # Aplicar skin inicial
        self.aplicar_skin(self.current_skin)
        
        # Criar primeira aba
        self.nova_aba()
    
    def carregar_configuracoes(self):
        """Carregar configurações salvas"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.home_page = config.get("home_page", self.home_page)
                    self.current_skin = config.get("skin", "Padrão (Claro)")
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def aplicar_skin(self, skin_name):
        """Aplicar a skin selecionada"""
        self.current_skin = skin_name
        
        if skin_name == "Padrão (Claro)":
            # Skin padrão (sem CSS adicional)
            self.setStyleSheet("""
                QTabBar::tab {
                    background: #f0f0f0;
                    padding: 8px 15px;
                    margin: 2px;
                }
                QTabBar::tab:selected {
                    background: white;
                    border-top: 2px solid #0078d7;
                }
                QTabBar::tab:hover {
                    background: #e0e0e0;
                }
                QLineEdit {
                    padding: 5px;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QPushButton {
                    background: #f0f0f0;
                    border: 1px solid #ccc;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background: #e0e0e0;
                }
                QMenuBar {
                    background-color: #f8f8f8;
                }
                QMenuBar::item {
                    padding: 5px 10px;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
            """)
        else:
            # Carregar skin do arquivo CSS
            skin_file = f"skins/{skin_name.lower()}.css"
            try:
                with open(skin_file, "r", encoding="utf-8") as f:
                    css = f.read()
                    self.setStyleSheet(css)
            except Exception as e:
                print(f"Erro ao carregar skin {skin_name}: {e}")
                # Fallback para skin padrão
                self.setStyleSheet("")
    
    def salvar_historico(self, url, titulo):
        """Salvar URL no histórico"""
        try:
            historico = []
            if os.path.exists("historico.json"):
                with open("historico.json", "r", encoding="utf-8") as f:
                    historico = json.load(f)
            
            # Adicionar novo item
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            historico.append({
                "url": url,
                "titulo": titulo,
                "data": data_atual
            })
            
            # Manter apenas os últimos 100 itens
            if len(historico) > 100:
                historico = historico[-100:]
            
            with open("historico.json", "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        # Criar menus
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        abrir_arquivo_action = QAction("Abrir arquivo HTML...", self)
        abrir_arquivo_action.setShortcut("Ctrl+O")
        abrir_arquivo_action.triggered.connect(self.abrir_arquivo_html)
        file_menu.addAction(abrir_arquivo_action)
        
        file_menu.addSeparator()
        
        sair_action = QAction("Sair", self)
        sair_action.setShortcut("Ctrl+Q")
        sair_action.triggered.connect(self.close)
        file_menu.addAction(sair_action)
        
        # Menu Histórico
        historico_menu = menubar.addMenu("Histórico")
        
        ver_historico_action = QAction("Ver histórico", self)
        ver_historico_action.setShortcut("Ctrl+H")
        ver_historico_action.triggered.connect(self.mostrar_historico)
        historico_menu.addAction(ver_historico_action)
        
        limpar_historico_action = QAction("Limpar histórico", self)
        limpar_historico_action.triggered.connect(self.limpar_historico)
        historico_menu.addAction(limpar_historico_action)
        
        # Menu Configurações
        config_menu = menubar.addMenu("Configurações")
        
        config_action = QAction("Preferências", self)
        config_action.setShortcut("Ctrl+P")
        config_action.triggered.connect(self.mostrar_configuracoes)
        config_menu.addAction(config_action)
        
        # Menu Ajuda
        ajuda_menu = menubar.addMenu("Ajuda")
        
        sobre_action = QAction("Sobre", self)
        sobre_action.triggered.connect(self.mostrar_sobre)
        ajuda_menu.addAction(sobre_action)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Barra de navegação
        nav_bar = QHBoxLayout()
        
        # Botões de navegação
        self.btn_back = QPushButton("◀")
        self.btn_forward = QPushButton("▶")
        self.btn_refresh = QPushButton("⟳")
        self.btn_home = QPushButton("🏠")
        self.btn_new_tab = QPushButton("+ Nova Aba")
        
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_refresh.clicked.connect(self.refresh_page)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_new_tab.clicked.connect(lambda: self.nova_aba())
        
        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Adicionar widgets à barra de navegação
        nav_bar.addWidget(self.btn_back)
        nav_bar.addWidget(self.btn_forward)
        nav_bar.addWidget(self.btn_refresh)
        nav_bar.addWidget(self.btn_home)
        nav_bar.addWidget(self.btn_new_tab)
        nav_bar.addWidget(self.url_bar)
        
        # Sistema de abas
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        
        # Adicionar layouts
        main_layout.addLayout(nav_bar)
        main_layout.addWidget(self.tabs)
        
        # Atalhos de teclado
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcut_new.activated.connect(lambda: self.nova_aba())
        
        self.shortcut_close = QShortcut(QKeySequence("Ctrl+W"), self)
        self.shortcut_close.activated.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        
        self.shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        self.shortcut_refresh.activated.connect(self.refresh_page)
    
    def abrir_arquivo_html(self):
        """Abrir arquivo HTML local"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Abrir arquivo HTML", 
            "", 
            "Arquivos HTML (*.html *.htm);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            # Converter caminho para URL
            file_url = QUrl.fromLocalFile(file_path)
            self.nova_aba(file_url.toString())
    
    def mostrar_historico(self):
        """Mostrar janela de histórico"""
        historico_window = HistoricoWindow(self)
        historico_window.exec_()
    
    def limpar_historico(self):
        """Limpar histórico"""
        reply = QMessageBox.question(self, "Confirmar", 
                                     "Tem certeza que deseja limpar todo o histórico?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.exists("historico.json"):
                    os.remove("historico.json")
                QMessageBox.information(self, "Sucesso", "Histórico limpo com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao limpar histórico: {e}")
    
    def mostrar_configuracoes(self):
        """Mostrar janela de configurações"""
        config_window = ConfiguracoesWindow(self)
        config_window.exec_()
    
    def mostrar_sobre(self):
        """Mostrar janela sobre"""
        sobre_window = SobreWindow(self)
        sobre_window.exec_()
    
    def nova_aba(self, url=None):
        """Criar uma nova aba com uma página web"""
        # Verificar se url é booleano ou None
        if url is None or isinstance(url, bool):
            url = self.home_page
        elif not isinstance(url, str):
            url = str(url)
        
        # Garantir que é uma string
        url_str = str(url)
        
        # Criar widget da aba
        tab_widget = QWidget()
        layout = QVBoxLayout()
        tab_widget.setLayout(layout)
        
        # Criar web view
        web_view = QWebEngineView()
        
        # Carregar URL
        try:
            web_view.setUrl(QUrl(url_str))
        except Exception as e:
            print(f"Erro ao carregar URL: {e}")
            web_view.setUrl(QUrl(self.home_page))
        
        # Conectar sinais
        web_view.urlChanged.connect(self.on_url_changed)
        web_view.titleChanged.connect(self.on_title_changed)
        web_view.loadFinished.connect(self.on_load_finished)
        
        layout.addWidget(web_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Adicionar aba
        index = self.tabs.addTab(tab_widget, "Carregando...")
        self.tabs.setCurrentIndex(index)
        
        # Armazenar o web view
        self.web_views[tab_widget] = web_view
        
        return web_view
    
    def get_current_web_view(self):
        """Obter o web view da aba atual"""
        current_widget = self.tabs.currentWidget()
        if current_widget and current_widget in self.web_views:
            return self.web_views[current_widget]
        return None
    
    def get_tab_widget_from_web_view(self, web_view):
        """Obter o widget da aba a partir do web view"""
        for tab_widget, wv in self.web_views.items():
            if wv == web_view:
                return tab_widget
        return None
    
    def navigate_to_url(self):
        """Navegar para a URL digitada na barra de endereço"""
        url = self.url_bar.text().strip()
        if not url:
            return
            
        if not url.startswith("http://") and not url.startswith("https://"):
            # Verificar se é uma pesquisa ou URL
            if '.' in url and ' ' not in url and not url.startswith("file://"):
                url = "https://" + url
            else:
                # Se não parecer uma URL, fazer pesquisa no motor de busca
                url = self.search_engines.get("Google", "https://www.google.com/search?q={}").format(quote(url))
        
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(url))
    
    def on_url_changed(self, url):
        """Quando a URL muda em qualquer aba"""
        web_view = self.sender()
        current_view = self.get_current_web_view()
        
        # Atualizar barra de URL apenas se for a aba atual
        if current_view == web_view:
            self.url_bar.setText(url.toString())
            self.url_bar.setCursorPosition(0)
    
    def on_title_changed(self, title):
        """Quando o título muda em qualquer aba"""
        web_view = self.sender()
        tab_widget = self.get_tab_widget_from_web_view(web_view)
        
        if tab_widget:
            index = self.tabs.indexOf(tab_widget)
            if index >= 0:
                if len(title) > 30:
                    title = title[:27] + "..."
                self.tabs.setTabText(index, title if title else "Nova aba")
                
                # Salvar no histórico quando o título for carregado
                current_url = web_view.url().toString()
                if current_url and current_url not in ["about:blank", ""]:
                    self.salvar_historico(current_url, title)
    
    def on_load_finished(self, ok):
        """Quando o carregamento da página termina"""
        self.update_navigation_buttons()
    
    def update_navigation_buttons(self):
        """Atualizar o estado dos botões de navegação"""
        web_view = self.get_current_web_view()
        if web_view:
            self.btn_back.setEnabled(web_view.history().canGoBack())
            self.btn_forward.setEnabled(web_view.history().canGoForward())
    
    def go_back(self):
        """Voltar uma página"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.back()
    
    def go_forward(self):
        """Avançar uma página"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.forward()
    
    def refresh_page(self):
        """Recarregar a página atual"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.reload()
    
    def go_home(self):
        """Ir para a página inicial"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setUrl(QUrl(self.home_page))
    
    def close_tab(self, index):
        """Fechar uma aba específica"""
        if self.tabs.count() > 1:
            tab_widget = self.tabs.widget(index)
            if tab_widget:
                # Remover do dicionário
                if tab_widget in self.web_views:
                    del self.web_views[tab_widget]
                # Fechar a aba
                self.tabs.removeTab(index)
                tab_widget.deleteLater()
        else:
            # Se for a última aba, fechar o navegador
            self.close()
    
    def current_tab_changed(self, index):
        """Quando a aba atual muda, atualizar a interface"""
        if index >= 0:
            web_view = self.get_current_web_view()
            if web_view:
                self.url_bar.setText(web_view.url().toString())
                self.update_navigation_buttons()

def main():
    app = QApplication(sys.argv)
    
    # Configurar aplicação
    app.setApplicationName("Navegador Web")
    app.setOrganizationName("MeuNavegador")
    
    # Criar e mostrar navegador
    navegador = NavegadorWeb()
    navegador.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
