import sys
import os
import json
import shutil
import tempfile
import uuid
from datetime import datetime
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from urllib.parse import quote

class VisualizadorCodigoFonte(QDialog):
    """Janela para visualizar código fonte HTML"""
    def __init__(self, parent=None, url="", html="", titulo=""):
        super().__init__(parent)
        self.parent = parent
        self.url = url
        self.html_original = html
        self.titulo = titulo
        
        self.setWindowTitle(f"Visualizador de Código Fonte - {titulo[:50]} - Python Navigator")
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
        search_layout.addWidget(QLabel("Buscar:"))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite texto para buscar...")
        self.search_input.textChanged.connect(self.buscar_texto)
        search_layout.addWidget(self.search_input)
        
        self.btn_search_next = QPushButton("Próximo")
        self.btn_search_next.clicked.connect(lambda: self.buscar_texto_direcao(1))
        search_layout.addWidget(self.btn_search_next)
        
        self.btn_search_prev = QPushButton("Anterior")
        self.btn_search_prev.clicked.connect(lambda: self.buscar_texto_direcao(-1))
        search_layout.addWidget(self.btn_search_prev)
        
        self.search_count_label = QLabel("0/0")
        search_layout.addWidget(self.search_count_label)
        
        search_frame.setLayout(search_layout)
        layout.addWidget(search_frame)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.btn_copy = QPushButton("📋 Copiar")
        self.btn_copy.clicked.connect(self.copiar_codigo)
        buttons_layout.addWidget(self.btn_copy)
        
        self.btn_save = QPushButton("💾 Salvar como...")
        self.btn_save.clicked.connect(self.salvar_codigo)
        buttons_layout.addWidget(self.btn_save)
        
        self.btn_refresh = QPushButton("⟳ Atualizar")
        self.btn_refresh.clicked.connect(self.atualizar_codigo)
        buttons_layout.addWidget(self.btn_refresh)
        
        self.btn_word_wrap = QPushButton("📝 Quebra de linha")
        self.btn_word_wrap.setCheckable(True)
        self.btn_word_wrap.toggled.connect(self.toggle_word_wrap)
        buttons_layout.addWidget(self.btn_word_wrap)
        
        buttons_layout.addStretch()
        
        self.btn_close = QPushButton("Fechar")
        self.btn_close.clicked.connect(self.accept)
        buttons_layout.addWidget(self.btn_close)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Variáveis para busca
        self.search_positions = []
        self.current_search_index = -1
        
        # Barra de status do visualizador
        self.status_label = QLabel("Pronto")
        layout.addWidget(self.status_label)
    
    def buscar_texto(self):
        """Buscar texto no código fonte"""
        texto_busca = self.search_input.text()
        if not texto_busca:
            self.search_positions = []
            self.current_search_index = -1
            self.search_count_label.setText("0/0")
            # Remover destaque
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
            QMessageBox.information(self, "Busca", f"Nenhum resultado encontrado para '{texto_busca}'")
    
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
        QMessageBox.information(self, "Copiar", "Código fonte copiado para a área de transferência!")
    
    def salvar_codigo(self):
        """Salvar código fonte em arquivo"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar código fonte",
            f"{self.titulo[:30].replace(' ', '_')}.html",
            "Arquivos HTML (*.html);;Arquivos de texto (*.txt);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.text_edit.toPlainText())
                QMessageBox.information(self, "Sucesso", f"Código fonte salvo em:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo: {e}")
    
    def atualizar_codigo(self):
        """Atualizar código fonte da página atual"""
        web_view = self.parent.get_current_web_view()
        if web_view:
            self.status_label.setText("Atualizando código fonte...")
            web_view.page().toHtml(self.on_html_loaded)
    
    def on_html_loaded(self, html):
        """Callback quando o HTML é carregado"""
        self.text_edit.setPlainText(html)
        self.html_original = html
        self.search_positions = []
        self.search_input.clear()
        self.status_label.setText("Código fonte atualizado com sucesso!")
        QMessageBox.information(self, "Atualizado", "Código fonte atualizado com sucesso!")
    
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

class ConsoleWindow(QDialog):
    """Janela do console JavaScript"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Console JavaScript - Python Navigator")
        self.setGeometry(300, 300, 800, 500)
        
        layout = QVBoxLayout()
        
        # Filtros
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar:"))
        
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Digite para filtrar mensagens...")
        self.filter_input.textChanged.connect(self.filtrar_mensagens)
        filter_layout.addWidget(self.filter_input)
        
        self.btn_clear = QPushButton("Limpar")
        self.btn_clear.clicked.connect(self.limpar_console)
        filter_layout.addWidget(self.btn_clear)
        
        self.btn_close = QPushButton("Fechar")
        self.btn_close.clicked.connect(self.accept)
        filter_layout.addWidget(self.btn_close)
        
        layout.addLayout(filter_layout)
        
        # Lista de mensagens
        self.messages_list = QListWidget()
        self.messages_list.setFont(QFont("Courier New", 9))
        layout.addWidget(self.messages_list)
        
        self.setLayout(layout)
        
        self.all_messages = []
    
    def adicionar_mensagem(self, mensagem, tipo="info"):
        """Adicionar mensagem ao console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Definir cor baseada no tipo
        cor = {
            "info": "blue",
            "warning": "orange",
            "error": "red",
            "deprecation": "purple"
        }.get(tipo, "black")
        
        item_text = f"[{timestamp}] [{tipo.upper()}] {mensagem}"
        self.all_messages.append((item_text, tipo))
        
        if self.filtrar_mensagens_por_texto(item_text):
            item = QListWidgetItem(item_text)
            item.setForeground(QColor(cor))
            self.messages_list.addItem(item)
            self.messages_list.scrollToBottom()
    
    def filtrar_mensagens(self):
        """Filtrar mensagens baseado no texto"""
        texto_filtro = self.filter_input.text().lower()
        self.messages_list.clear()
        
        for item_text, tipo in self.all_messages:
            if texto_filtro in item_text.lower():
                item = QListWidgetItem(item_text)
                cor = {
                    "info": "blue",
                    "warning": "orange",
                    "error": "red",
                    "deprecation": "purple"
                }.get(tipo, "black")
                item.setForeground(QColor(cor))
                self.messages_list.addItem(item)
    
    def filtrar_mensagens_por_texto(self, texto):
        """Verificar se a mensagem deve ser exibida baseado no filtro atual"""
        texto_filtro = self.filter_input.text().lower()
        if not texto_filtro:
            return True
        return texto_filtro in texto.lower()
    
    def limpar_console(self):
        """Limpar todas as mensagens do console"""
        self.all_messages.clear()
        self.messages_list.clear()

class HistoricoWindow(QDialog):
    """Janela de histórico"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Histórico - Python Navigator")
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

class ConfiguracoesWindow(QDialog):
    """Janela de configurações"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Configurações - Python Navigator")
        self.setGeometry(200, 200, 450, 550)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Informações do navegador
        group_info = QGroupBox("Sobre o Python Navigator")
        info_layout = QVBoxLayout()
        info_label = QLabel("""<b>Python Navigator 1.0.1</b><br>
        Navegador web desenvolvido em Python com PyQt5<br>
        Identificador: PythonNavigator/1.0.1""")
        info_label.setWordWrap(True)
        info_layout.addWidget(info_label)
        group_info.setLayout(info_layout)
        layout.addWidget(group_info)
        
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
        
        # Configurações de JavaScript
        group_js = QGroupBox("JavaScript")
        js_layout = QVBoxLayout()
        
        self.js_enabled = QCheckBox("Habilitar JavaScript")
        self.js_enabled.setChecked(parent.javascript_enabled)
        self.js_enabled.toggled.connect(self.on_js_toggled)
        js_layout.addWidget(self.js_enabled)
        
        self.js_info = QLabel("O JavaScript é necessário para a maioria dos sites modernos.\nDesativar pode melhorar a segurança e velocidade,\nmas muitos sites podem não funcionar corretamente.")
        self.js_info.setWordWrap(True)
        self.js_info.setStyleSheet("color: #666; font-size: 10px;")
        js_layout.addWidget(self.js_info)
        
        group_js.setLayout(js_layout)
        layout.addWidget(group_js)
        
        # Configurações do Console
        group_console = QGroupBox("Console JavaScript")
        console_layout = QVBoxLayout()
        
        self.console_enabled = QCheckBox("Habilitar console JavaScript")
        self.console_enabled.setChecked(parent.console_enabled)
        console_layout.addWidget(self.console_enabled)
        
        self.console_info = QLabel("Mostra mensagens de erro, avisos e depuração do JavaScript.")
        self.console_info.setWordWrap(True)
        self.console_info.setStyleSheet("color: #666; font-size: 10px;")
        console_layout.addWidget(self.console_info)
        
        group_console.setLayout(console_layout)
        layout.addWidget(group_console)
        
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
    
    def on_js_toggled(self, enabled):
        """Quando o JavaScript é ativado/desativado"""
        if not enabled:
            reply = QMessageBox.question(self, "Confirmar", 
                                         "Desativar o JavaScript pode fazer com que muitos sites não funcionem corretamente.\nDeseja continuar?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                self.js_enabled.setChecked(True)
    
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
                    
                    # Carregar configuração de JavaScript
                    js_enabled = config.get("javascript_enabled", True)
                    self.js_enabled.setChecked(js_enabled)
                    
                    # Carregar configuração do console
                    console_enabled = config.get("console_enabled", True)
                    self.console_enabled.setChecked(console_enabled)
                    
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
                "javascript_enabled": self.js_enabled.isChecked(),
                "console_enabled": self.console_enabled.isChecked(),
                "skin": self.skin_combo.currentText()
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # Atualizar configurações no navegador
            self.parent.home_page = self.home_page_edit.text()
            self.parent.javascript_enabled = self.js_enabled.isChecked()
            self.parent.console_enabled = self.console_enabled.isChecked()
            self.parent.aplicar_configuracoes_javascript()
            self.parent.aplicar_skin(self.skin_combo.currentText())
            
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {e}")

class SobreWindow(QDialog):
    """Janela Sobre"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sobre - Python Navigator")
        self.setGeometry(400, 400, 500, 440)
        
        layout = QVBoxLayout()
        
        # Logo e informações
        label_title = QLabel("<h1>🐍 Python Navigator</h1>")
        label_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_title)
        
        label_version = QLabel("<b>Versão:</b> 1.0.1")
        label_version.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_version)
        
        label_id = QLabel("<b>Identificador:</b> PythonNavigator/1.0.1")
        label_id.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_id)
        
        layout.addWidget(QLabel(""))
        
        label_desc = QLabel("Navegador web desenvolvido em Python com PyQt5")
        label_desc.setAlignment(Qt.AlignCenter)
        label_desc.setWordWrap(True)
        layout.addWidget(label_desc)
        
        layout.addWidget(QLabel(""))
        
        label_features = QLabel("""<b>Funcionalidades:</b><br>
        • Múltiplas abas<br>
        • Modo anônimo (privado)<br>
        • Histórico de navegação<br>
        • Visualizador de código fonte<br>
        • Console JavaScript<br>
        • Configurações personalizáveis<br>
        • Sistema de skins/temas<br>
        • JavaScript configurável<br>
        • Atalhos de teclado<br>
        • Abrir arquivos HTML locais<br>
        • Motor de busca personalizável<br>
        • User Agent personalizado""")
        label_features.setAlignment(Qt.AlignLeft)
        label_features.setWordWrap(True)
        layout.addWidget(label_features)
        
        layout.addWidget(QLabel(""))
        
        label_credit = QLabel("<i>© 2024 - Python Navigator Team</i>")
        label_credit.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_credit)
        
        btn_close = QPushButton("Fechar")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        
        self.setLayout(layout)

class NavegadorAnonimo(QMainWindow):
    """Janela de navegação anônima (modo privado)"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🐍 Python Navigator - Modo Anônimo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurar página inicial padrão
        self.home_page = "https://www.google.com"
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        }
        
        # Identificador do navegador
        self.browser_name = "PythonNavigator"
        self.browser_version = "1.0.1"
        self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.browser_name}/{self.browser_version} Chrome/120.0.0.0 Safari/537.36"
        
        # Configurações de JavaScript (sempre ativado no modo anônimo)
        self.javascript_enabled = True
        
        # Dicionário para mapear abas para seus web views
        self.web_views = {}
        
        # Criar perfil anônimo
        self.create_anonymous_profile()
        
        self.init_ui()
        
        # Criar primeira aba
        self.nova_aba()
        
        # Mostrar aviso de modo anônimo
        self.statusBar().showMessage("Modo anônimo ativado - Seu histórico não será salvo", 5000)
        
        # Mensagem informativa
        QMessageBox.information(self, "Modo Anônimo", 
                                "Você está navegando em modo anônimo.\n\n"
                                "✓ Histórico não será salvo\n"
                                "✓ Cookies não serão mantidos\n"
                                "✓ Dados temporários serão apagados ao fechar\n\n"
                                "Observação: Isso não torna sua navegação completamente anônima na internet.",
                                QMessageBox.Ok)
    
    def create_anonymous_profile(self):
        """Criar perfil anônimo temporário"""
        # Criar pasta temporária para o perfil anônimo
        self.temp_profile_dir = os.path.join(tempfile.gettempdir(), f"python_navigator_anon_{uuid.uuid4().hex}")
        
        # Criar perfil
        self.profile = QWebEngineProfile("Anonymous", self)
        self.profile.setPersistentStoragePath(self.temp_profile_dir)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        self.profile.setHttpUserAgent(self.user_agent)
        
        # Configurar para não salvar dados
        settings = self.profile.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        # Criar menus
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        nova_aba_anonima_action = QAction("Nova aba anônima", self)
        nova_aba_anonima_action.setShortcut("Ctrl+Shift+N")
        nova_aba_anonima_action.triggered.connect(self.nova_aba)
        file_menu.addAction(nova_aba_anonima_action)
        
        file_menu.addSeparator()
        
        abrir_arquivo_action = QAction("Abrir arquivo HTML...", self)
        abrir_arquivo_action.setShortcut("Ctrl+O")
        abrir_arquivo_action.triggered.connect(self.abrir_arquivo_html)
        file_menu.addAction(abrir_arquivo_action)
        
        file_menu.addSeparator()
        
        sair_action = QAction("Sair", self)
        sair_action.setShortcut("Ctrl+Q")
        sair_action.triggered.connect(self.close)
        file_menu.addAction(sair_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("Exibir")
        
        ver_codigo_action = QAction("Código fonte da página", self)
        ver_codigo_action.setShortcut("Ctrl+U")
        ver_codigo_action.triggered.connect(self.visualizar_codigo_fonte)
        view_menu.addAction(ver_codigo_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Aumentar zoom", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Diminuir zoom", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("Zoom padrão", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
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
        self.btn_code = QPushButton("</> Código")
        self.btn_new_tab = QPushButton("+ Nova Aba")
        
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_refresh.clicked.connect(self.refresh_page)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_code.clicked.connect(self.visualizar_codigo_fonte)
        self.btn_new_tab.clicked.connect(lambda: self.nova_aba())
        
        # Configurar estilo do botão código
        self.btn_code.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Adicionar widgets à barra de navegação
        nav_bar.addWidget(self.btn_back)
        nav_bar.addWidget(self.btn_forward)
        nav_bar.addWidget(self.btn_refresh)
        nav_bar.addWidget(self.btn_home)
        nav_bar.addWidget(self.btn_code)
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
        
        self.shortcut_new_anon = QShortcut(QKeySequence("Ctrl+Shift+N"), self)
        self.shortcut_new_anon.activated.connect(lambda: self.nova_aba())
        
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
        
        # Adicionar identificador na barra de título
        self.statusBar().showMessage("Python Navigator - Modo Anônimo - Navegação privada ativada")
    
    def zoom_in(self):
        """Aumentar zoom da página"""
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(factor + 0.1)
            self.statusBar().showMessage(f"Zoom: {int((factor + 0.1) * 100)}%", 2000)
    
    def zoom_out(self):
        """Diminuir zoom da página"""
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(max(0.3, factor - 0.1))
            self.statusBar().showMessage(f"Zoom: {int((factor - 0.1) * 100)}%", 2000)
    
    def zoom_reset(self):
        """Resetar zoom para padrão"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(1.0)
            self.statusBar().showMessage("Zoom: 100%", 2000)
    
    def abrir_arquivo_html(self):
        """Abrir arquivo HTML local"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Abrir arquivo HTML - Python Navigator (Modo Anônimo)", 
            "", 
            "Arquivos HTML (*.html *.htm);;Todos os arquivos (*.*)"
        )
        
        if file_path:
            # Converter caminho para URL
            file_url = QUrl.fromLocalFile(file_path)
            self.nova_aba(file_url.toString())
    
    def visualizar_codigo_fonte(self):
        """Visualizar código fonte da página atual"""
        web_view = self.get_current_web_view()
        if web_view:
            url = web_view.url().toString()
            titulo = web_view.title()
            
            # Mostrar mensagem de carregamento
            self.statusBar().showMessage("Carregando código fonte...")
            
            # Obter HTML da página
            web_view.page().toHtml(lambda html: self.mostrar_visualizador_codigo(url, html, titulo))
    
    def mostrar_visualizador_codigo(self, url, html, titulo):
        """Mostrar janela do visualizador de código fonte"""
        visualizador = VisualizadorCodigoFonte(self, url, html, titulo)
        visualizador.exec_()
        self.statusBar().showMessage("Código fonte carregado", 3000)
    
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
        
        # Criar web view com perfil anônimo
        web_view = QWebEngineView()
        web_view.setPage(QWebEnginePage(self.profile, web_view))
        
        # Configurar user agent
        web_view.page().profile().setHttpUserAgent(self.user_agent)
        
        # Configurar JavaScript
        settings = web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, self.javascript_enabled)
        
        # Outras configurações
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)  # Desativar localStorage no modo anônimo
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        
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
        
        # Adicionar aba com ícone de máscara
        index = self.tabs.addTab(tab_widget, "🕶️ Carregando...")
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
                # Adicionar ícone de máscara nas abas anônimas
                self.tabs.setTabText(index, f"🕶️ {title}" if title else "🕶️ Nova aba")
    
    def on_load_finished(self, ok):
        """Quando o carregamento da página termina"""
        self.update_navigation_buttons()
        self.statusBar().showMessage("Python Navigator - Modo Anônimo - Página carregada", 3000)
    
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
    
    def closeEvent(self, event):
        """Quando fechar a janela, limpar dados temporários"""
        try:
            # Limpar pasta temporária
            if hasattr(self, 'temp_profile_dir') and os.path.exists(self.temp_profile_dir):
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
        except Exception as e:
            print(f"Erro ao limpar dados temporários: {e}")
        event.accept()

class NavegadorWeb(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Python Navigator 1.0.1")
        self.setGeometry(100, 100, 1200, 800)
        
        # Configurar página inicial padrão
        self.home_page = "https://www.google.com"
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}"
        }
        
        # Identificador do navegador
        self.browser_name = "PythonNavigator"
        self.browser_version = "1.0.1"
        self.user_agent = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) {self.browser_name}/{self.browser_version} Chrome/120.0.0.0 Safari/537.36"
        
        # Configurações
        self.javascript_enabled = True
        self.console_enabled = True
        
        # Skin atual
        self.current_skin = "Padrão (Claro)"
        
        # Dicionário para mapear abas para seus web views
        self.web_views = {}
        
        # Console JavaScript
        self.console_window = None
        
        # Carregar configurações salvas
        self.carregar_configuracoes()
        
        self.init_ui()
        
        # Aplicar skin inicial
        self.aplicar_skin(self.current_skin)
        
        # Configurar user agent e JavaScript
        self.configurar_user_agent()
        self.aplicar_configuracoes_javascript()
        
        # Criar primeira aba
        self.nova_aba()
    
    def configurar_user_agent(self):
        """Configurar user agent personalizado para todas as páginas"""
        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent(self.user_agent)
    
    def aplicar_configuracoes_javascript(self):
        """Aplicar configurações de JavaScript em todas as abas"""
        # Configurar o perfil padrão
        profile = QWebEngineProfile.defaultProfile()
        settings = profile.settings()
        
        if self.javascript_enabled:
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
            settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
            self.statusBar().showMessage(f"Python Navigator {self.browser_version} - JavaScript: Ativado", 3000)
        else:
            settings.setAttribute(QWebEngineSettings.JavascriptEnabled, False)
            settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
            settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
            self.statusBar().showMessage(f"Python Navigator {self.browser_version} - JavaScript: Desativado", 3000)
        
        # Atualizar configurações em todas as abas existentes
        for tab_widget, web_view in self.web_views.items():
            page_settings = web_view.page().settings()
            page_settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
            page_settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, self.javascript_enabled)
            page_settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, self.javascript_enabled)
    
    def carregar_configuracoes(self):
        """Carregar configurações salvas"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.home_page = config.get("home_page", self.home_page)
                    self.current_skin = config.get("skin", "Padrão (Claro)")
                    self.javascript_enabled = config.get("javascript_enabled", True)
                    self.console_enabled = config.get("console_enabled", True)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")
    
    def aplicar_skin(self, skin_name):
        """Aplicar a skin selecionada"""
        self.current_skin = skin_name
        
        if skin_name == "Padrão (Claro)":
            # Skin padrão com identificador
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
                "data": data_atual,
                "navegador": f"{self.browser_name} {self.browser_version}"
            })
            
            # Manter apenas os últimos 100 itens
            if len(historico) > 100:
                historico = historico[-100:]
            
            with open("historico.json", "w", encoding="utf-8") as f:
                json.dump(historico, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")
    
    def abrir_janela_anonima(self):
        """Abrir nova janela em modo anônimo"""
        self.janela_anonima = NavegadorAnonimo()
        self.janela_anonima.show()
    
    def visualizar_codigo_fonte(self):
        """Visualizar código fonte da página atual"""
        web_view = self.get_current_web_view()
        if web_view:
            url = web_view.url().toString()
            titulo = web_view.title()
            
            # Mostrar mensagem de carregamento
            self.statusBar().showMessage("Carregando código fonte...")
            
            # Obter HTML da página
            web_view.page().toHtml(lambda html: self.mostrar_visualizador_codigo(url, html, titulo))
    
    def mostrar_visualizador_codigo(self, url, html, titulo):
        """Mostrar janela do visualizador de código fonte"""
        visualizador = VisualizadorCodigoFonte(self, url, html, titulo)
        visualizador.exec_()
        self.statusBar().showMessage("Código fonte carregado", 3000)
    
    def mostrar_console(self):
        """Mostrar console JavaScript"""
        if not self.console_window:
            self.console_window = ConsoleWindow(self)
        self.console_window.show()
        self.console_window.raise_()
    
    def on_java_script_message(self, level, message, line, source):
        """Receber mensagens do JavaScript"""
        if self.console_enabled:
            if not self.console_window:
                self.console_window = ConsoleWindow(self)
            
            # Identificar tipo da mensagem
            tipo = "info"
            if "deprecated" in message.lower():
                tipo = "deprecation"
            elif "error" in message.lower() or "exception" in message.lower():
                tipo = "error"
            elif "warning" in message.lower() or "cors" in message.lower():
                tipo = "warning"
            
            self.console_window.adicionar_mensagem(message, tipo)
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        # Criar menus
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("Arquivo")
        
        nova_janela_action = QAction("Nova janela", self)
        nova_janela_action.setShortcut("Ctrl+N")
        nova_janela_action.triggered.connect(self.nova_janela)
        file_menu.addAction(nova_janela_action)
        
        nova_janela_anonima_action = QAction("Nova janela anônima", self)
        nova_janela_anonima_action.setShortcut("Ctrl+Shift+N")
        nova_janela_anonima_action.triggered.connect(self.abrir_janela_anonima)
        file_menu.addAction(nova_janela_anonima_action)
        
        file_menu.addSeparator()
        
        abrir_arquivo_action = QAction("Abrir arquivo HTML...", self)
        abrir_arquivo_action.setShortcut("Ctrl+O")
        abrir_arquivo_action.triggered.connect(self.abrir_arquivo_html)
        file_menu.addAction(abrir_arquivo_action)
        
        file_menu.addSeparator()
        
        sair_action = QAction("Sair", self)
        sair_action.setShortcut("Ctrl+Q")
        sair_action.triggered.connect(self.close)
        file_menu.addAction(sair_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("Exibir")
        
        ver_codigo_action = QAction("Código fonte da página", self)
        ver_codigo_action.setShortcut("Ctrl+U")
        ver_codigo_action.triggered.connect(self.visualizar_codigo_fonte)
        view_menu.addAction(ver_codigo_action)
        
        ver_console_action = QAction("Console JavaScript", self)
        ver_console_action.setShortcut("Ctrl+Shift+J")
        ver_console_action.triggered.connect(self.mostrar_console)
        view_menu.addAction(ver_console_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Aumentar zoom", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Diminuir zoom", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("Zoom padrão", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
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
        self.btn_code = QPushButton("</> Código")
        self.btn_console = QPushButton("📋 Console")
        self.btn_anonimo = QPushButton("🕶️ Anônimo")
        self.btn_new_tab = QPushButton("+ Nova Aba")
        
        self.btn_back.clicked.connect(self.go_back)
        self.btn_forward.clicked.connect(self.go_forward)
        self.btn_refresh.clicked.connect(self.refresh_page)
        self.btn_home.clicked.connect(self.go_home)
        self.btn_code.clicked.connect(self.visualizar_codigo_fonte)
        self.btn_console.clicked.connect(self.mostrar_console)
        self.btn_anonimo.clicked.connect(self.abrir_janela_anonima)
        self.btn_new_tab.clicked.connect(lambda: self.nova_aba())
        
        # Configurar estilo dos botões
        self.btn_code.setStyleSheet("""
            QPushButton {
                background: #6c757d;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        self.btn_console.setStyleSheet("""
            QPushButton {
                background: #17a2b8;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #138496;
            }
        """)
        
        self.btn_anonimo.setStyleSheet("""
            QPushButton {
                background: #28a745;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        
        # Barra de URL
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        # Adicionar widgets à barra de navegação
        nav_bar.addWidget(self.btn_back)
        nav_bar.addWidget(self.btn_forward)
        nav_bar.addWidget(self.btn_refresh)
        nav_bar.addWidget(self.btn_home)
        nav_bar.addWidget(self.btn_code)
        nav_bar.addWidget(self.btn_console)
        nav_bar.addWidget(self.btn_anonimo)
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
        
        self.shortcut_console = QShortcut(QKeySequence("Ctrl+Shift+J"), self)
        self.shortcut_console.activated.connect(self.mostrar_console)
        
        self.shortcut_zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        self.shortcut_zoom_in.activated.connect(self.zoom_in)
        
        self.shortcut_zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        self.shortcut_zoom_out.activated.connect(self.zoom_out)
        
        self.shortcut_zoom_reset = QShortcut(QKeySequence("Ctrl+0"), self)
        self.shortcut_zoom_reset.activated.connect(self.zoom_reset)
        
        # Adicionar identificador na barra de título
        js_status = "JS: ON" if self.javascript_enabled else "JS: OFF"
        self.statusBar().showMessage(f"Python Navigator {self.browser_version} - {js_status} - Pronto")
    
    def nova_janela(self):
        """Abrir nova janela normal"""
        nova_janela = NavegadorWeb()
        nova_janela.show()
    
    def zoom_in(self):
        """Aumentar zoom da página"""
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(factor + 0.1)
            self.statusBar().showMessage(f"Zoom: {int((factor + 0.1) * 100)}%", 2000)
    
    def zoom_out(self):
        """Diminuir zoom da página"""
        web_view = self.get_current_web_view()
        if web_view:
            factor = web_view.zoomFactor()
            web_view.setZoomFactor(max(0.3, factor - 0.1))
            self.statusBar().showMessage(f"Zoom: {int((factor - 0.1) * 100)}%", 2000)
    
    def zoom_reset(self):
        """Resetar zoom para padrão"""
        web_view = self.get_current_web_view()
        if web_view:
            web_view.setZoomFactor(1.0)
            self.statusBar().showMessage("Zoom: 100%", 2000)
    
    def abrir_arquivo_html(self):
        """Abrir arquivo HTML local"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Abrir arquivo HTML - Python Navigator", 
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
        
        # Configurar user agent e JavaScript individual para cada web view
        web_view.page().profile().setHttpUserAgent(self.user_agent)
        
        # Configurar JavaScript
        settings = web_view.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, self.javascript_enabled)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, self.javascript_enabled)
        
        # Outras configurações úteis
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        
        # Conectar sinal para mensagens JavaScript
        if self.console_enabled:
            web_view.page().javaScriptConsoleMessage = self.on_java_script_message
        
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
        js_status = "Ativado" if self.javascript_enabled else "Desativado"
        self.statusBar().showMessage(f"Python Navigator {self.browser_version} - JavaScript: {js_status} - Página carregada", 3000)
    
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
    app.setApplicationName("Python Navigator")
    app.setApplicationDisplayName("Python Navigator 1.0.1")
    app.setOrganizationName("PythonNavigator")
    
    # Criar e mostrar navegador
    navegador = NavegadorWeb()
    navegador.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
