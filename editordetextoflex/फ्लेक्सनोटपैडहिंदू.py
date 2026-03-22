import sys
import json
import os
import base64
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Importar bibliotecas de criptografia
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("चेतावनी: 'cryptography' लाइब्रेरी स्थापित नहीं है। एन्क्रिप्शन सुविधा अक्षम है।")

class SimpleTextEditor(QMainWindow):
    """
    सरल टेक्स्ट संपादक जो JSON प्रारूप में फ़ाइलें सहेजता है, एन्क्रिप्शन समर्थन के साथ
    पासवर्ड एन्क्रिप्शन वाला संस्करण
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.setWindowTitle("सरल संपादक - एन्क्रिप्शन के साथ JSON नोटपैड")
        self.setGeometry(100, 100, 900, 600)
        
        # Variáveis de estado
        self.current_file = None
        self.is_modified = False
        self.search_text = ""
        self.replace_text = ""
        self.is_encrypted = False  # Indica se o arquivo atual está criptografado
        
        # Configurar interface
        self.init_ui()
        
        # Aplicar estilo
        self.apply_style()
        
        # Mostrar boas-vindas
        self.show_welcome()
    
    def init_ui(self):
        """उपयोगकर्ता इंटरफ़ेस आरंभ करें"""
        
        # ========== BARRA DE MENUS ==========
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("फ़ाइल (&F)")
        
        # Ações do menu Arquivo
        new_action = QAction("नया (&N)", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("नई फ़ाइल बनाएँ")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("खोलें (&O)...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("मौजूदा फ़ाइल खोलें")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("सहेजें (&S)", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("वर्तमान फ़ाइल सहेजें")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("इस रूप में सहेजें (&A)...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("फ़ाइल को नए नाम से सहेजें")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Ação para salvar com senha
        self.save_encrypted_action = QAction("एन्क्रिप्ट करके सहेजें (&E)...", self)
        self.save_encrypted_action.setShortcut("Ctrl+E")
        self.save_encrypted_action.setStatusTip("पासवर्ड एन्क्रिप्शन के साथ फ़ाइल सहेजें")
        self.save_encrypted_action.triggered.connect(self.save_encrypted_file)
        if not CRYPTO_AVAILABLE:
            self.save_encrypted_action.setEnabled(False)
            self.save_encrypted_action.setToolTip("सुविधा उपलब्ध नहीं - 'cryptography' लाइब्रेरी स्थापित करें")
        file_menu.addAction(self.save_encrypted_action)
        
        file_menu.addSeparator()
        
        export_txt_action = QAction("TXT के रूप में निर्यात करें (&T)...", self)
        export_txt_action.setStatusTip("साधारण टेक्स्ट फ़ाइल के रूप में निर्यात करें")
        export_txt_action.triggered.connect(self.export_as_txt)
        file_menu.addAction(export_txt_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("बाहर जाएँ (&X)", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("प्रोग्राम से बाहर जाएँ")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("संपादन (&E)")
        
        undo_action = QAction("पूर्ववत करें (&U)", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("फिर से करें (&R)", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("काटें (&T)", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("कॉपी करें (&C)", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("चिपकाएँ (&P)", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("सभी चुनें (&A)", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Menu Localizar
        search_menu = menubar.addMenu("खोजें (&F)")
        
        find_action = QAction("खोजें (&F)...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_search)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("अगला खोजें (&N)", self)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)
        
        replace_action = QAction("बदलें (&R)...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace)
        search_menu.addAction(replace_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("दृश्य (&V)")
        
        word_wrap_action = QAction("लाइन तोड़ें (&W)", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        toolbar_action = QAction("उपकरण पट्टी (&T)", self)
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)
        
        statusbar_action = QAction("स्थिति पट्टी (&S)", self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("ज़ूम बढ़ाएँ (&Z)", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("ज़ूम घटाएँ (&O)", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("ज़ूम रीसेट करें (&R)", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("सहायता (&H)")
        
        about_action = QAction("परिचय (&A)", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # ========== BARRA DE FERRAMENTAS ==========
        self.toolbar = QToolBar("उपकरण पट्टी")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Botões da barra de ferramentas
        btn_new = QAction(QIcon.fromTheme("document-new"), "नया", self)
        btn_new.setStatusTip("नई फ़ाइल")
        btn_new.triggered.connect(self.new_file)
        self.toolbar.addAction(btn_new)
        
        btn_open = QAction(QIcon.fromTheme("document-open"), "खोलें", self)
        btn_open.setStatusTip("फ़ाइल खोलें")
        btn_open.triggered.connect(self.open_file)
        self.toolbar.addAction(btn_open)
        
        btn_save = QAction(QIcon.fromTheme("document-save"), "सहेजें", self)
        btn_save.setStatusTip("फ़ाइल सहेजें")
        btn_save.triggered.connect(self.save_file)
        self.toolbar.addAction(btn_save)
        
        self.toolbar.addSeparator()
        
        btn_cut = QAction(QIcon.fromTheme("edit-cut"), "काटें", self)
        btn_cut.setStatusTip("काटें")
        btn_cut.triggered.connect(self.cut)
        self.toolbar.addAction(btn_cut)
        
        btn_copy = QAction(QIcon.fromTheme("edit-copy"), "कॉपी करें", self)
        btn_copy.setStatusTip("कॉपी करें")
        btn_copy.triggered.connect(self.copy)
        self.toolbar.addAction(btn_copy)
        
        btn_paste = QAction(QIcon.fromTheme("edit-paste"), "चिपकाएँ", self)
        btn_paste.setStatusTip("चिपकाएँ")
        btn_paste.triggered.connect(self.paste)
        self.toolbar.addAction(btn_paste)
        
        self.toolbar.addSeparator()
        
        btn_undo = QAction(QIcon.fromTheme("edit-undo"), "पूर्ववत करें", self)
        btn_undo.setStatusTip("पूर्ववत करें")
        btn_undo.triggered.connect(self.undo)
        self.toolbar.addAction(btn_undo)
        
        btn_redo = QAction(QIcon.fromTheme("edit-redo"), "फिर से करें", self)
        btn_redo.setStatusTip("फिर से करें")
        btn_redo.triggered.connect(self.redo)
        self.toolbar.addAction(btn_redo)
        
        self.toolbar.addSeparator()
        
        btn_find = QAction(QIcon.fromTheme("edit-find"), "खोजें", self)
        btn_find.setStatusTip("टेक्स्ट खोजें")
        btn_find.triggered.connect(self.show_search)
        self.toolbar.addAction(btn_find)
        
        # ========== ÁREA CENTRAL ==========
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de texto
        self.text_area = QPlainTextEdit()
        self.text_area.setFont(QFont("Consolas", 11))
        self.text_area.textChanged.connect(self.on_text_changed)
        self.text_area.cursorPositionChanged.connect(self.on_cursor_position_changed)
        layout.addWidget(self.text_area)
        
        # Barra de localização (inicialmente oculta)
        self.search_bar = QWidget()
        self.search_bar.setObjectName("search-bar")
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("खोजें...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.find_next)
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("इससे बदलें...")
        self.replace_input.returnPressed.connect(self.replace_current)
        self.replace_input.hide()
        
        btn_find_prev = QPushButton("⬆")
        btn_find_prev.setToolTip("पिछला")
        btn_find_prev.setMaximumWidth(30)
        btn_find_prev.clicked.connect(self.find_previous)
        
        btn_find_next = QPushButton("⬇")
        btn_find_next.setToolTip("अगला")
        btn_find_next.setMaximumWidth(30)
        btn_find_next.clicked.connect(self.find_next)
        
        self.btn_replace = QPushButton("बदलें")
        self.btn_replace.setToolTip("वर्तमान मिलान बदलें")
        self.btn_replace.hide()
        self.btn_replace.clicked.connect(self.replace_current)
        
        self.btn_replace_all = QPushButton("सभी बदलें")
        self.btn_replace_all.setToolTip("सभी मिलान बदलें")
        self.btn_replace_all.hide()
        self.btn_replace_all.clicked.connect(self.replace_all)
        
        btn_close_search = QPushButton("✕")
        btn_close_search.setToolTip("बंद करें")
        btn_close_search.setMaximumWidth(30)
        btn_close_search.clicked.connect(self.hide_search)
        
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_find_prev)
        search_layout.addWidget(btn_find_next)
        search_layout.addWidget(self.replace_input)
        search_layout.addWidget(self.btn_replace)
        search_layout.addWidget(self.btn_replace_all)
        search_layout.addStretch()
        search_layout.addWidget(btn_close_search)
        
        layout.addWidget(self.search_bar)
        self.search_bar.hide()
        
        # ========== BARRA DE STATUS ==========
        self.status_bar = self.statusBar()
        
        # Label de posição do cursor
        self.position_label = QLabel("पंक्ति 1, स्तंभ 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        # Label de modo de inserção
        self.mode_label = QLabel("सम्मिलन")
        self.status_bar.addPermanentWidget(self.mode_label)
        
        # Label de tamanho do arquivo
        self.size_label = QLabel("0 अक्षर")
        self.status_bar.addPermanentWidget(self.size_label)
        
        # Label de status de criptografia
        self.encrypt_label = QLabel("🔓")
        self.encrypt_label.setToolTip("फ़ाइल एन्क्रिप्ट नहीं है")
        self.status_bar.addPermanentWidget(self.encrypt_label)
    
    def apply_style(self):
        """दृश्य शैली लागू करें"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QPlainTextEdit {
            background-color: white;
            color: #2c3e50;
            border: none;
            selection-background-color: #3498db;
            selection-color: white;
        }
        QToolBar {
            background-color: #ecf0f1;
            border: none;
            spacing: 5px;
            padding: 5px;
        }
        QToolBar QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 3px;
            padding: 5px;
        }
        QToolBar QToolButton:hover {
            background-color: #bdc3c7;
        }
        QToolBar QToolButton:pressed {
            background-color: #95a5a6;
        }
        QMenuBar {
            background-color: #34495e;
            color: white;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 10px;
        }
        QMenuBar::item:selected {
            background-color: #2c3e50;
        }
        QMenu {
            background-color: white;
            border: 1px solid #bdc3c7;
        }
        QMenu::item {
            padding: 5px 30px 5px 20px;
        }
        QMenu::item:selected {
            background-color: #3498db;
            color: white;
        }
        QStatusBar {
            background-color: #34495e;
            color: white;
        }
        #search-bar {
            background-color: #ecf0f1;
            border-top: 1px solid #bdc3c7;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #bdc3c7;
            border-radius: 3px;
            background-color: white;
        }
        QLineEdit:focus {
            border-color: #3498db;
        }
        QPushButton {
            padding: 5px 10px;
            background-color: #3498db;
            color: white;
            border: none;
            border-radius: 3px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QPushButton:pressed {
            background-color: #1c6ea4;
        }
        """
        self.setStyleSheet(style)
    
    def show_welcome(self):
        """स्वागत संदेश दिखाएँ"""
        welcome_text = """# सरल संपादक - एन्क्रिप्शन के साथ JSON नोटपैड

## 📝 स्वागत है!

यह एक टेक्स्ट संपादक है जो JSON प्रारूप में फ़ाइलें सहेजता है और एन्क्रिप्शन का समर्थन करता है।

### ✨ विशेषताएँ:
- ✅ JSON प्रारूप में फ़ाइलें सहेजें
- ✅ पासवर्ड एन्क्रिप्शन (AES-256)
- ✅ एन्क्रिप्टेड और अनएन्क्रिप्टेड फ़ाइलें खोलें
- ✅ टेक्स्ट खोजें और बदलें
- ✅ पूर्ववत/पुनः करें
- ✅ लाइन तोड़ें
- ✅ समायोज्य ज़ूम

### 🔒 एन्क्रिप्शन का उपयोग कैसे करें:
- **Ctrl+E** या फ़ाइल मेनू > "एन्क्रिप्ट करके सहेजें..." का उपयोग करें
- अपनी फ़ाइल सुरक्षित रखने के लिए एक मजबूत पासवर्ड डालें
- फ़ाइल .json एक्सटेंशन के साथ सहेजी जाएगी (लेकिन एन्क्रिप्टेड होगी)
- एन्क्रिप्टेड फ़ाइल खोलते समय पासवर्ड मांगा जाएगा

### 🚀 उपयोग कैसे करें:
- **Ctrl+N** नई फ़ाइल के लिए
- **Ctrl+O** खोलने के लिए
- **Ctrl+S** सहेजने के लिए (बिना एन्क्रिप्शन)
- **Ctrl+E** एन्क्रिप्ट करके सहेजने के लिए
- **Ctrl+F** खोजने के लिए
- **Ctrl+H** बदलने के लिए

### 📁 JSON प्रारूप:
फ़ाइलें मेटाडेटा के साथ सहेजी जाती हैं जिनमें शामिल हैं:
- निर्माण और संशोधन तिथि
- अक्षर, शब्द और पंक्तियों की संख्या
- एन्क्रिप्शन संकेतक

आनंद लें! 🎉
"""
        self.text_area.setPlainText(welcome_text)
        self.current_file = None
        self.is_modified = False
        self.is_encrypted = False
        self.update_window_title()
        self.update_encrypt_label()
    
    def on_text_changed(self):
        """जब टेक्स्ट बदलता है"""
        self.is_modified = True
        self.update_window_title()
        self.update_size_label()
    
    def on_cursor_position_changed(self):
        """जब कर्सर की स्थिति बदलती है"""
        cursor = self.text_area.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.position_label.setText(f"पंक्ति {line}, स्तंभ {col}")
    
    def update_window_title(self):
        """विंडो शीर्षक अद्यतन करें"""
        title = "सरल संपादक"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_encrypted:
            title += " [एन्क्रिप्टेड]"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def update_size_label(self):
        """आकार लेबल अद्यतन करें"""
        text = self.text_area.toPlainText()
        chars = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        
        self.size_label.setText(f"{chars} अक्षर | {words} शब्द | {lines} पंक्तियाँ")
    
    def update_encrypt_label(self):
        """स्थिति पट्टी में एन्क्रिप्शन लेबल अद्यतन करें"""
        if self.is_encrypted:
            self.encrypt_label.setText("🔒")
            self.encrypt_label.setToolTip("फ़ाइल एन्क्रिप्टेड है")
        else:
            self.encrypt_label.setText("🔓")
            self.encrypt_label.setToolTip("फ़ाइल एन्क्रिप्ट नहीं है")
    
    # ========== FUNÇÕES DE CRIPTOGRAFIA ==========
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """PBKDF2 का उपयोग करके पासवर्ड से कुंजी व्युत्पन्न करें"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt_content(self, content: str, password: str) -> dict:
        """पासवर्ड के साथ सामग्री एन्क्रिप्ट करें"""
        if not CRYPTO_AVAILABLE:
            raise Exception("'cryptography' लाइब्रेरी स्थापित नहीं है")
        
        # Gerar salt aleatório
        salt = os.urandom(16)
        
        # Derivar chave
        key, _ = self.derive_key(password, salt)
        
        # Criar cipher
        f = Fernet(key)
        
        # Criptografar o conteúdo
        encrypted_data = f.encrypt(content.encode('utf-8'))
        
        # Retornar dados criptografados com salt
        return {
            'encrypted': True,
            'salt': base64.b64encode(salt).decode(),
            'data': base64.b64encode(encrypted_data).decode(),
            'algorithm': 'AES-256-CBC',
            'key_derivation': 'PBKDF2-HMAC-SHA256'
        }
    
    def decrypt_content(self, encrypted_data: dict, password: str) -> str:
        """पासवर्ड के साथ सामग्री डिक्रिप्ट करें"""
        if not CRYPTO_AVAILABLE:
            raise Exception("'cryptography' लाइब्रेरी स्थापित नहीं है")
        
        # Verificar se é um arquivo criptografado
        if not encrypted_data.get('encrypted', False):
            return None
        
        try:
            # Recuperar salt
            salt = base64.b64decode(encrypted_data['salt'])
            
            # Derivar chave
            key, _ = self.derive_key(password, salt)
            
            # Criar cipher
            f = Fernet(key)
            
            # Descriptografar
            encrypted_content = base64.b64decode(encrypted_data['data'])
            decrypted_content = f.decrypt(encrypted_content)
            
            return decrypted_content.decode('utf-8')
        except Exception as e:
            raise Exception("गलत पासवर्ड या फ़ाइल दूषित है")
    
    def get_password(self, title="पासवर्ड", message="पासवर्ड डालें:", is_new=False):
        """उपयोगकर्ता से पासवर्ड प्राप्त करने के लिए डायलॉग"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # Mensagem
        label = QLabel(message)
        layout.addWidget(label)
        
        # Campo de senha
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)
        
        if is_new:
            # Confirmar senha
            label_confirm = QLabel("पासवर्ड की पुष्टि करें:")
            layout.addWidget(label_confirm)
            
            confirm_input = QLineEdit()
            confirm_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(confirm_input)
        
        # Botões
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            password = password_input.text()
            if is_new:
                confirm = confirm_input.text()
                if password != confirm:
                    QMessageBox.warning(self, "त्रुटि", "पासवर्ड मेल नहीं खाते!")
                    return None
                if not password:
                    QMessageBox.warning(self, "त्रुटि", "पासवर्ड खाली नहीं हो सकता!")
                    return None
            return password
        
        return None
    
    def save_encrypted_file(self):
        """एन्क्रिप्शन के साथ फ़ाइल सहेजें"""
        if not CRYPTO_AVAILABLE:
            QMessageBox.critical(self, "त्रुटि", 
                               "'cryptography' लाइब्रेरी स्थापित नहीं है।\n"
                               "स्थापित करें: pip install cryptography")
            return
        
        # Verificar se precisa salvar antes
        if self.is_modified and self.current_file and not self.is_encrypted:
            reply = QMessageBox.question(
                self, "सहेजें?",
                "वर्तमान फ़ाइल सहेजी नहीं गई है। क्या आप पहले इसे सहेजना चाहेंगे?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_file()
        
        # Escolher local para salvar
        file_path, _ = QFileDialog.getSaveFileName(
            self, "एन्क्रिप्टेड फ़ाइल सहेजें", "",
            "JSON फ़ाइलें (*.json);;सभी फ़ाइलें (*.*)"
        )
        
        if not file_path:
            return
        
        # Obter senha
        password = self.get_password("फ़ाइल एन्क्रिप्ट करें", 
                                     "फ़ाइल सुरक्षित रखने के लिए पासवर्ड डालें:", 
                                     is_new=True)
        if not password:
            return
        
        try:
            content = self.text_area.toPlainText()
            
            # Criar metadados
            metadata = {
                'created': datetime.now().isoformat() if not self.current_file else None,
                'modified': datetime.now().isoformat(),
                'characters': len(content),
                'words': len(content.split()),
                'lines': content.count('\n') + 1
            }
            
            # Criptografar o conteúdo
            encrypted_data = self.encrypt_content(content, password)
            
            # Salvar dados criptografados com metadados
            save_data = {
                'encrypted': True,
                'metadata': metadata,
                'crypto_info': encrypted_data
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.current_file = file_path
            self.is_modified = False
            self.is_encrypted = True
            self.update_window_title()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"एन्क्रिप्टेड फ़ाइल सहेजी गई: {file_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"एन्क्रिप्टेड फ़ाइल सहेजते समय त्रुटि:\n{str(e)}")
    
    def save_to_file(self, file_path):
        """सामग्री को फ़ाइल में सहेजें (बिना एन्क्रिप्शन)"""
        try:
            content = self.text_area.toPlainText()
            
            if file_path.endswith('.json'):
                # Salvar com metadados
                data = {
                    'encrypted': False,
                    'content': content,
                    'metadata': {
                        'created': datetime.now().isoformat() if not self.current_file else None,
                        'modified': datetime.now().isoformat(),
                        'characters': len(content),
                        'words': len(content.split()),
                        'lines': content.count('\n') + 1
                    }
                }
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                # Salvar como texto simples
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.current_file = file_path
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"फ़ाइल सहेजी गई: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"फ़ाइल सहेजते समय त्रुटि:\n{str(e)}")
    
    def open_file(self):
        """फ़ाइल खोलें"""
        if not self.check_save():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "फ़ाइल खोलें", "",
            "JSON फ़ाइलें (*.json);;टेक्स्ट फ़ाइलें (*.txt);;सभी फ़ाइलें (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Verificar se é arquivo criptografado
                    if isinstance(data, dict) and data.get('encrypted', False):
                        # Solicitar senha
                        password = self.get_password("एन्क्रिप्टेड फ़ाइल", 
                                                    "यह फ़ाइल एन्क्रिप्टेड है।\nखोलने के लिए पासवर्ड डालें:")
                        if not password:
                            return
                        
                        # Descriptografar
                        content = self.decrypt_content(data['crypto_info'], password)
                        if content is None:
                            QMessageBox.critical(self, "त्रुटि", "फ़ाइल डिक्रिप्ट करने में विफल।")
                            return
                        
                        self.text_area.setPlainText(content)
                        self.is_encrypted = True
                    else:
                        # Arquivo normal
                        if isinstance(data, dict) and 'content' in data:
                            content = data['content']
                        else:
                            content = str(data)
                        self.text_area.setPlainText(content)
                        self.is_encrypted = False
            else:
                # Arquivo de texto simples
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
                self.is_encrypted = False
            
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"फ़ाइल लोड की गई: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "त्रुटि", f"फ़ाइल खोलते समय त्रुटि:\n{str(e)}")
    
    def new_file(self):
        """नई फ़ाइल बनाएँ"""
        if self.check_save():
            self.text_area.clear()
            self.current_file = None
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage("नई फ़ाइल बनाई गई", 3000)
    
    def export_as_txt(self):
        """TXT के रूप में निर्यात करें"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "TXT के रूप में निर्यात करें", "",
            "टेक्स्ट फ़ाइलें (*.txt);;सभी फ़ाइलें (*.*)"
        )
        
        if file_path:
            try:
                content = self.text_area.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.showMessage(f"फ़ाइल निर्यात की गई: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "त्रुटि", f"निर्यात करते समय त्रुटि:\n{str(e)}")
    
    def check_save(self):
        """बंद करने/नया खोलने से पहले सहेजने की आवश्यकता की जाँच करें"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "सहेजें?",
                "फ़ाइल बदली गई है। क्या आप परिवर्तन सहेजना चाहते हैं?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def save_file(self):
        """फ़ाइल सहेजें (स्थिति के अनुसार सामान्य या एन्क्रिप्टेड)"""
        if self.current_file:
            if self.is_encrypted:
                # Se o arquivo atual é criptografado, salvar como criptografado
                self.save_encrypted_file()
            else:
                self.save_to_file(self.current_file)
        else:
            # Perguntar se quer salvar criptografado ou não
            reply = QMessageBox.question(
                self, "सहेजने का प्रकार",
                "क्या आप एन्क्रिप्शन के साथ सहेजना चाहते हैं?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_encrypted_file()
            else:
                self.save_file_as()
    
    def save_file_as(self):
        """फ़ाइल को इस रूप में सहेजें (बिना एन्क्रिप्शन)"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "इस रूप में सहेजें", "",
            "JSON फ़ाइलें (*.json);;टेक्स्ट फ़ाइलें (*.txt);;सभी फ़ाइलें (*.*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def closeEvent(self, event):
        """विंडो बंद करने की घटना"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()
    
    # ========== FUNÇÕES DE EDIÇÃO ==========
    
    def undo(self):
        self.text_area.undo()
    
    def redo(self):
        self.text_area.redo()
    
    def cut(self):
        self.text_area.cut()
    
    def copy(self):
        self.text_area.copy()
    
    def paste(self):
        self.text_area.paste()
    
    def select_all(self):
        self.text_area.selectAll()
    
    # ========== FUNÇÕES DE LOCALIZAÇÃO ==========
    
    def show_search(self):
        """खोज पट्टी दिखाएँ"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.hide()
        self.btn_replace.hide()
        self.btn_replace_all.hide()
    
    def show_replace(self):
        """बदलें पट्टी दिखाएँ"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.show()
        self.btn_replace.show()
        self.btn_replace_all.show()
    
    def hide_search(self):
        """खोज पट्टी छिपाएँ"""
        self.search_bar.hide()
        self.search_input.clear()
        self.replace_input.clear()
        self.text_area.setExtraSelections([])
    
    def on_search_text_changed(self, text):
        """जब खोज टेक्स्ट बदलता है"""
        self.search_text = text
        self.highlight_all()
    
    def highlight_all(self):
        """सभी मिलान हाइलाइट करें"""
        extra_selections = []
        
        if self.search_text:
            highlight_format = QTextCharFormat()
            highlight_format.setBackground(QColor(255, 255, 0, 100))
            
            document = self.text_area.document()
            cursor = QTextCursor(document)
            
            while True:
                cursor = document.find(self.search_text, cursor)
                if cursor.isNull():
                    break
                
                selection = QTextEdit.ExtraSelection()
                selection.cursor = cursor
                selection.format = highlight_format
                extra_selections.append(selection)
        
        self.text_area.setExtraSelections(extra_selections)
    
    def find_next(self):
        """अगला मिलान खोजें"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        
        if cursor.hasSelection() and cursor.selectedText() == self.search_text:
            cursor.movePosition(QTextCursor.NextCharacter)
            self.text_area.setTextCursor(cursor)
        
        found = self.text_area.find(self.search_text)
        
        if not found:
            cursor.movePosition(QTextCursor.Start)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text)
            
            if found:
                self.status_bar.showMessage("दस्तावेज़ की शुरुआत पहुँच गया", 3000)
            else:
                self.status_bar.showMessage(f"टेक्स्ट '{self.search_text}' नहीं मिला", 3000)
                return False
        
        return True
    
    def find_previous(self):
        """पिछला मिलान खोजें"""
        if not self.search_text:
            return
        
        found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
        
        if not found:
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
            
            if found:
                self.status_bar.showMessage("दस्तावेज़ का अंत पहुँच गया", 3000)
            else:
                self.status_bar.showMessage(f"टेक्स्ट '{self.search_text}' नहीं मिला", 3000)
                return False
        
        return True
    
    def replace_current(self):
        """वर्तमान मिलान बदलें"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        
        if cursor.hasSelection() and cursor.selectedText() == self.search_text:
            cursor.insertText(self.replace_input.text())
            self.is_modified = True
            self.update_window_title()
            self.find_next()
        else:
            if self.find_next():
                self.replace_current()
    
    def replace_all(self):
        """सभी मिलान बदलें"""
        if not self.search_text:
            return
        
        original_cursor = self.text_area.textCursor()
        cursor = self.text_area.textCursor()
        cursor.beginEditBlock()
        
        cursor.movePosition(QTextCursor.Start)
        self.text_area.setTextCursor(cursor)
        
        count = 0
        replace_text = self.replace_input.text()
        
        while self.text_area.find(self.search_text):
            cursor = self.text_area.textCursor()
            cursor.insertText(replace_text)
            count += 1
        
        cursor.endEditBlock()
        self.text_area.setTextCursor(original_cursor)
        
        if count > 0:
            self.is_modified = True
            self.update_window_title()
            QMessageBox.information(self, "बदलें", f"{count} मिलान बदले गए।")
        else:
            QMessageBox.information(self, "बदलें", f"टेक्स्ट '{self.search_text}' नहीं मिला।")
    
    # ========== FUNÇÕES DE EXIBIÇÃO ==========
    
    def toggle_word_wrap(self, checked):
        """लाइन तोड़ें टॉगल करें"""
        if checked:
            self.text_area.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
    
    def toggle_toolbar(self, checked):
        """उपकरण पट्टी टॉगल करें"""
        if checked:
            self.toolbar.show()
        else:
            self.toolbar.hide()
    
    def toggle_statusbar(self, checked):
        """स्थिति पट्टी टॉगल करें"""
        if checked:
            self.status_bar.show()
        else:
            self.status_bar.hide()
    
    def zoom_in(self):
        """ज़ूम बढ़ाएँ"""
        font = self.text_area.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_area.setFont(font)
    
    def zoom_out(self):
        """ज़ूम घटाएँ"""
        font = self.text_area.font()
        size = font.pointSize()
        if size > 8:
            font.setPointSize(size - 1)
            self.text_area.setFont(font)
    
    def zoom_reset(self):
        """ज़ूम रीसेट करें"""
        font = QFont("Consolas", 11)
        self.text_area.setFont(font)
    
    # ========== FUNÇÕES DE AJUDA ==========
    
    def show_about(self):
        """परिचय डायलॉग दिखाएँ"""
        crypto_status = "✅ उपलब्ध" if CRYPTO_AVAILABLE else "❌ उपलब्ध नहीं (cryptography स्थापित करें)"
        
        about_text = f"""
        <h2>सरल संपादक</h2>
        <p><b>संस्करण:</b> 2.0.0</p>
        <p>JSON प्रारूप में सहेजने वाला टेक्स्ट संपादक जो एन्क्रिप्शन का समर्थन करता है।</p>
        
        <h3>🔒 एन्क्रिप्शन:</h3>
        <p><b>स्थिति:</b> {crypto_status}</p>
        <p><b>एल्गोरिदम:</b> AES-256 (Fernet)</p>
        <p><b>कुंजी व्युत्पत्ति:</b> PBKDF2-HMAC-SHA256</p>
        
        <h3>विशेषताएँ:</h3>
        <ul>
            <li>JSON में मेटाडेटा के साथ फ़ाइलें सहेजें</li>
            <li>पासवर्ड एन्क्रिप्शन (AES-256)</li>
            <li>एन्क्रिप्टेड और अनएन्क्रिप्टेड फ़ाइलें खोलें</li>
            <li>टेक्स्ट खोजें और बदलें</li>
            <li>अक्षर, शब्द और पंक्ति काउंटर</li>
            <li>समायोज्य ज़ूम</li>
            <li>लाइन तोड़ें</li>
        </ul>
        
        <h3>शॉर्टकट:</h3>
        <ul>
            <li>Ctrl+N: नई फ़ाइल</li>
            <li>Ctrl+O: खोलें</li>
            <li>Ctrl+S: सहेजें</li>
            <li>Ctrl+E: एन्क्रिप्ट करके सहेजें</li>
            <li>Ctrl+F: खोजें</li>
            <li>Ctrl+H: बदलें</li>
            <li>Ctrl+Z: पूर्ववत करें</li>
            <li>Ctrl+Y: फिर से करें</li>
            <li>Ctrl++: ज़ूम बढ़ाएँ</li>
            <li>Ctrl+-: ज़ूम घटाएँ</li>
        </ul>
        
        <p><i>DeepSeek की सहायता से विकसित</i></p>
        <p><i>Όχι, ο Χρόνος δεν είναι ο άρχοντας της γνώσης</i></p>
        """
        
        QMessageBox.about(self, "सरल संपादक के बारे में", about_text)


class StartupDialog(QDialog):
    """विकल्पों के साथ प्रारंभिक डायलॉग"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("सरल संपादक")
        self.setModal(True)
        self.setGeometry(400, 300, 500, 300)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📝 सरल संपादक\nएन्क्रिप्शन के साथ 🔒")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #3498db;
            padding: 20px;
            background-color: #ecf0f1;
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Opções
        options = QWidget()
        options_layout = QVBoxLayout(options)
        
        btn_new = QPushButton("📄 नई फ़ाइल")
        btn_new.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 15px;
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        btn_new.clicked.connect(self.accept)
        options_layout.addWidget(btn_new)
        
        btn_open = QPushButton("📂 फ़ाइल खोलें")
        btn_open.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 15px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_open.clicked.connect(self.open_file)
        options_layout.addWidget(btn_open)
        
        if not CRYPTO_AVAILABLE:
            warning = QLabel("⚠️ एन्क्रिप्शन सुविधा उपलब्ध नहीं है।\nस्थापित करें: pip install cryptography")
            warning.setStyleSheet("color: orange; padding: 10px;")
            warning.setAlignment(Qt.AlignCenter)
            options_layout.addWidget(warning)
        
        layout.addWidget(options)
        
        # Botão sair
        btn_exit = QPushButton("❌ बाहर जाएँ")
        btn_exit.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_exit.clicked.connect(self.reject)
        layout.addWidget(btn_exit)
        
        self.setLayout(layout)
        self.open_file_requested = False
    
    def open_file(self):
        """सीधे फ़ाइल खोलें"""
        self.open_file_requested = True
        self.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("सरल संपादक")
    
    if not CRYPTO_AVAILABLE:
        QMessageBox.warning(None, "चेतावनी", 
                          "'cryptography' लाइब्रेरी स्थापित नहीं है।\n"
                          "एन्क्रिप्शन सुविधा अक्षम रहेगी।\n\n"
                          "स्थापित करने के लिए: pip install cryptography")
    
    # Diálogo inicial
    dialog = StartupDialog()
    if dialog.exec_() == QDialog.Accepted:
        editor = SimpleTextEditor()
        if dialog.open_file_requested:
            editor.open_file()
        editor.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
