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
    print("Предупреждение: Библиотека 'cryptography' не установлена. Функция шифрования отключена.")

class SimpleTextEditor(QMainWindow):
    """
    Простой текстовый редактор, сохраняющий файлы в формате JSON с поддержкой шифрования
    Версия с шифрованием по паролю
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.setWindowTitle("Простой редактор - Блокнот JSON с шифрованием")
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
        """Инициализация пользовательского интерфейса"""
        
        # ========== BARRA DE MENUS ==========
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Файл")
        
        # Ações do menu Arquivo
        new_action = QAction("&Новый", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Создать новый файл")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Открыть...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Открыть существующий файл")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Сохранить", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Сохранить текущий файл")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Сохранить &как...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Сохранить файл с новым именем")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Ação para salvar com senha
        self.save_encrypted_action = QAction("Сохранить &с шифрованием...", self)
        self.save_encrypted_action.setShortcut("Ctrl+E")
        self.save_encrypted_action.setStatusTip("Сохранить файл с шифрованием по паролю")
        self.save_encrypted_action.triggered.connect(self.save_encrypted_file)
        if not CRYPTO_AVAILABLE:
            self.save_encrypted_action.setEnabled(False)
            self.save_encrypted_action.setToolTip("Функция недоступна — установите библиотеку 'cryptography'")
        file_menu.addAction(self.save_encrypted_action)
        
        file_menu.addSeparator()
        
        export_txt_action = QAction("Экспортировать как &TXT...", self)
        export_txt_action.setStatusTip("Экспортировать как обычный текстовый файл")
        export_txt_action.triggered.connect(self.export_as_txt)
        file_menu.addAction(export_txt_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Выйти из программы")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("&Правка")
        
        undo_action = QAction("&Отменить", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Повторить", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("&Вырезать", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Копировать", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Вставить", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Выделить &всё", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Menu Localizar
        search_menu = menubar.addMenu("&Поиск")
        
        find_action = QAction("&Найти...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_search)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("Найти &следующий", self)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)
        
        replace_action = QAction("&Заменить...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace)
        search_menu.addAction(replace_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("&Вид")
        
        word_wrap_action = QAction("&Перенос строк", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        toolbar_action = QAction("&Панель инструментов", self)
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)
        
        statusbar_action = QAction("&Строка состояния", self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Увеличить &масштаб", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Уменьшить &масштаб", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("&Сбросить масштаб", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("&Помощь")
        
        about_action = QAction("&О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # ========== BARRA DE FERRAMENTAS ==========
        self.toolbar = QToolBar("Панель инструментов")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Botões da barra de ferramentas
        btn_new = QAction(QIcon.fromTheme("document-new"), "Новый", self)
        btn_new.setStatusTip("Новый файл")
        btn_new.triggered.connect(self.new_file)
        self.toolbar.addAction(btn_new)
        
        btn_open = QAction(QIcon.fromTheme("document-open"), "Открыть", self)
        btn_open.setStatusTip("Открыть файл")
        btn_open.triggered.connect(self.open_file)
        self.toolbar.addAction(btn_open)
        
        btn_save = QAction(QIcon.fromTheme("document-save"), "Сохранить", self)
        btn_save.setStatusTip("Сохранить файл")
        btn_save.triggered.connect(self.save_file)
        self.toolbar.addAction(btn_save)
        
        self.toolbar.addSeparator()
        
        btn_cut = QAction(QIcon.fromTheme("edit-cut"), "Вырезать", self)
        btn_cut.setStatusTip("Вырезать")
        btn_cut.triggered.connect(self.cut)
        self.toolbar.addAction(btn_cut)
        
        btn_copy = QAction(QIcon.fromTheme("edit-copy"), "Копировать", self)
        btn_copy.setStatusTip("Копировать")
        btn_copy.triggered.connect(self.copy)
        self.toolbar.addAction(btn_copy)
        
        btn_paste = QAction(QIcon.fromTheme("edit-paste"), "Вставить", self)
        btn_paste.setStatusTip("Вставить")
        btn_paste.triggered.connect(self.paste)
        self.toolbar.addAction(btn_paste)
        
        self.toolbar.addSeparator()
        
        btn_undo = QAction(QIcon.fromTheme("edit-undo"), "Отменить", self)
        btn_undo.setStatusTip("Отменить")
        btn_undo.triggered.connect(self.undo)
        self.toolbar.addAction(btn_undo)
        
        btn_redo = QAction(QIcon.fromTheme("edit-redo"), "Повторить", self)
        btn_redo.setStatusTip("Повторить")
        btn_redo.triggered.connect(self.redo)
        self.toolbar.addAction(btn_redo)
        
        self.toolbar.addSeparator()
        
        btn_find = QAction(QIcon.fromTheme("edit-find"), "Найти", self)
        btn_find.setStatusTip("Найти текст")
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
        self.search_input.setPlaceholderText("Найти...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.find_next)
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Заменить на...")
        self.replace_input.returnPressed.connect(self.replace_current)
        self.replace_input.hide()
        
        btn_find_prev = QPushButton("⬆")
        btn_find_prev.setToolTip("Предыдущий")
        btn_find_prev.setMaximumWidth(30)
        btn_find_prev.clicked.connect(self.find_previous)
        
        btn_find_next = QPushButton("⬇")
        btn_find_next.setToolTip("Следующий")
        btn_find_next.setMaximumWidth(30)
        btn_find_next.clicked.connect(self.find_next)
        
        self.btn_replace = QPushButton("Заменить")
        self.btn_replace.setToolTip("Заменить текущее вхождение")
        self.btn_replace.hide()
        self.btn_replace.clicked.connect(self.replace_current)
        
        self.btn_replace_all = QPushButton("Заменить всё")
        self.btn_replace_all.setToolTip("Заменить все вхождения")
        self.btn_replace_all.hide()
        self.btn_replace_all.clicked.connect(self.replace_all)
        
        btn_close_search = QPushButton("✕")
        btn_close_search.setToolTip("Закрыть")
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
        self.position_label = QLabel("Стр 1, Стлб 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        # Label de modo de inserção
        self.mode_label = QLabel("ВСТ")
        self.status_bar.addPermanentWidget(self.mode_label)
        
        # Label de tamanho do arquivo
        self.size_label = QLabel("0 символов")
        self.status_bar.addPermanentWidget(self.size_label)
        
        # Label de status de criptografia
        self.encrypt_label = QLabel("🔓")
        self.encrypt_label.setToolTip("Файл не зашифрован")
        self.status_bar.addPermanentWidget(self.encrypt_label)
    
    def apply_style(self):
        """Применить визуальный стиль"""
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
        """Показать приветственное сообщение"""
        welcome_text = """# Простой редактор - Блокнот JSON с шифрованием

## 📝 Добро пожаловать!

Это текстовый редактор, сохраняющий файлы в формате JSON с поддержкой шифрования.

### ✨ Возможности:
- ✅ Сохранение файлов в формате JSON
- ✅ Шифрование по паролю (AES-256)
- ✅ Открытие зашифрованных и незашифрованных файлов
- ✅ Поиск и замена текста
- ✅ Отмена/Повтор
- ✅ Перенос строк
- ✅ Регулируемый масштаб

### 🔒 Как использовать шифрование:
- Используйте **Ctrl+E** или меню Файл > "Сохранить с шифрованием..."
- Введите надежный пароль для защиты файла
- Файл будет сохранен с расширением .json (но будет зашифрован)
- При открытии зашифрованного файла будет запрошен пароль

### 🚀 Как пользоваться:
- Используйте **Ctrl+N** для нового файла
- Используйте **Ctrl+O** для открытия
- Используйте **Ctrl+S** для сохранения (без шифрования)
- Используйте **Ctrl+E** для сохранения с шифрованием
- Используйте **Ctrl+F** для поиска
- Используйте **Ctrl+H** для замены

### 📁 Формат JSON:
Файлы сохраняются с метаданными, включая:
- Дату создания и изменения
- Количество символов, слов и строк
- Индикатор шифрования

Приятного использования! 🎉
"""
        self.text_area.setPlainText(welcome_text)
        self.current_file = None
        self.is_modified = False
        self.is_encrypted = False
        self.update_window_title()
        self.update_encrypt_label()
    
    def on_text_changed(self):
        """Когда текст меняется"""
        self.is_modified = True
        self.update_window_title()
        self.update_size_label()
    
    def on_cursor_position_changed(self):
        """Когда курсор меняет положение"""
        cursor = self.text_area.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.position_label.setText(f"Стр {line}, Стлб {col}")
    
    def update_window_title(self):
        """Обновить заголовок окна"""
        title = "Простой редактор"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_encrypted:
            title += " [Зашифровано]"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def update_size_label(self):
        """Обновить метку размера"""
        text = self.text_area.toPlainText()
        chars = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        
        self.size_label.setText(f"{chars} символов | {words} слов | {lines} строк")
    
    def update_encrypt_label(self):
        """Обновить метку шифрования в строке состояния"""
        if self.is_encrypted:
            self.encrypt_label.setText("🔒")
            self.encrypt_label.setToolTip("Файл зашифрован")
        else:
            self.encrypt_label.setText("🔓")
            self.encrypt_label.setToolTip("Файл не зашифрован")
    
    # ========== FUNÇÕES DE CRIPTOGRAFIA ==========
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """Вывести ключ из пароля с использованием PBKDF2"""
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
        """Зашифровать содержимое паролем"""
        if not CRYPTO_AVAILABLE:
            raise Exception("Библиотека 'cryptography' не установлена")
        
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
        """Расшифровать содержимое паролем"""
        if not CRYPTO_AVAILABLE:
            raise Exception("Библиотека 'cryptography' не установлена")
        
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
            raise Exception("Неверный пароль или поврежденный файл")
    
    def get_password(self, title="Пароль", message="Введите пароль:", is_new=False):
        """Диалог для получения пароля от пользователя"""
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
            label_confirm = QLabel("Подтвердите пароль:")
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
                    QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
                    return None
                if not password:
                    QMessageBox.warning(self, "Ошибка", "Пароль не может быть пустым!")
                    return None
            return password
        
        return None
    
    def save_encrypted_file(self):
        """Сохранить файл с шифрованием"""
        if not CRYPTO_AVAILABLE:
            QMessageBox.critical(self, "Ошибка", 
                               "Библиотека 'cryptography' не установлена.\n"
                               "Установите: pip install cryptography")
            return
        
        # Verificar se precisa salvar antes
        if self.is_modified and self.current_file and not self.is_encrypted:
            reply = QMessageBox.question(
                self, "Сохранить?",
                "Текущий файл не сохранен. Сохранить его сначала?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_file()
        
        # Escolher local para salvar
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить зашифрованный файл", "",
            "Файлы JSON (*.json);;Все файлы (*.*)"
        )
        
        if not file_path:
            return
        
        # Obter senha
        password = self.get_password("Шифрование файла", 
                                     "Введите пароль для защиты файла:", 
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
            self.status_bar.showMessage(f"Зашифрованный файл сохранен: {file_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении зашифрованного файла:\n{str(e)}")
    
    def save_to_file(self, file_path):
        """Сохранить содержимое в файл (без шифрования)"""
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
            self.status_bar.showMessage(f"Файл сохранен: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла:\n{str(e)}")
    
    def open_file(self):
        """Открыть файл"""
        if not self.check_save():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Открыть файл", "",
            "Файлы JSON (*.json);;Текстовые файлы (*.txt);;Все файлы (*.*)"
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
                        password = self.get_password("Зашифрованный файл", 
                                                    "Этот файл зашифрован.\nВведите пароль для открытия:")
                        if not password:
                            return
                        
                        # Descriptografar
                        content = self.decrypt_content(data['crypto_info'], password)
                        if content is None:
                            QMessageBox.critical(self, "Ошибка", "Не удалось расшифровать файл.")
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
            self.status_bar.showMessage(f"Файл загружен: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии файла:\n{str(e)}")
    
    def new_file(self):
        """Создать новый файл"""
        if self.check_save():
            self.text_area.clear()
            self.current_file = None
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage("Создан новый файл", 3000)
    
    def export_as_txt(self):
        """Экспортировать как TXT"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспортировать как TXT", "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        
        if file_path:
            try:
                content = self.text_area.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.showMessage(f"Файл экспортирован: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка при экспорте:\n{str(e)}")
    
    def check_save(self):
        """Проверить, нужно ли сохранить перед закрытием/открытием нового"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Сохранить?",
                "Файл был изменен. Сохранить изменения?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def save_file(self):
        """Сохранить файл (обычный или зашифрованный в зависимости от состояния)"""
        if self.current_file:
            if self.is_encrypted:
                # Se o arquivo atual é criptografado, salvar como criptografado
                self.save_encrypted_file()
            else:
                self.save_to_file(self.current_file)
        else:
            # Perguntar se quer salvar criptografado ou não
            reply = QMessageBox.question(
                self, "Тип сохранения",
                "Сохранить с шифрованием?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_encrypted_file()
            else:
                self.save_file_as()
    
    def save_file_as(self):
        """Сохранить файл как (без шифрования)"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить как", "",
            "Файлы JSON (*.json);;Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def closeEvent(self, event):
        """Событие закрытия окна"""
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
        """Показать панель поиска"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.hide()
        self.btn_replace.hide()
        self.btn_replace_all.hide()
    
    def show_replace(self):
        """Показать панель замены"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.show()
        self.btn_replace.show()
        self.btn_replace_all.show()
    
    def hide_search(self):
        """Скрыть панель поиска"""
        self.search_bar.hide()
        self.search_input.clear()
        self.replace_input.clear()
        self.text_area.setExtraSelections([])
    
    def on_search_text_changed(self, text):
        """Когда текст поиска меняется"""
        self.search_text = text
        self.highlight_all()
    
    def highlight_all(self):
        """Подсветить все вхождения"""
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
        """Найти следующее вхождение"""
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
                self.status_bar.showMessage("Достигнуто начало документа", 3000)
            else:
                self.status_bar.showMessage(f"Текст '{self.search_text}' не найден", 3000)
                return False
        
        return True
    
    def find_previous(self):
        """Найти предыдущее вхождение"""
        if not self.search_text:
            return
        
        found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
        
        if not found:
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
            
            if found:
                self.status_bar.showMessage("Достигнут конец документа", 3000)
            else:
                self.status_bar.showMessage(f"Текст '{self.search_text}' не найден", 3000)
                return False
        
        return True
    
    def replace_current(self):
        """Заменить текущее вхождение"""
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
        """Заменить все вхождения"""
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
            QMessageBox.information(self, "Замена", f"Заменено {count} вхождений.")
        else:
            QMessageBox.information(self, "Замена", f"Текст '{self.search_text}' не найден.")
    
    # ========== FUNÇÕES DE EXIBIÇÃO ==========
    
    def toggle_word_wrap(self, checked):
        """Переключить перенос строк"""
        if checked:
            self.text_area.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
    
    def toggle_toolbar(self, checked):
        """Переключить панель инструментов"""
        if checked:
            self.toolbar.show()
        else:
            self.toolbar.hide()
    
    def toggle_statusbar(self, checked):
        """Переключить строку состояния"""
        if checked:
            self.status_bar.show()
        else:
            self.status_bar.hide()
    
    def zoom_in(self):
        """Увеличить масштаб"""
        font = self.text_area.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_area.setFont(font)
    
    def zoom_out(self):
        """Уменьшить масштаб"""
        font = self.text_area.font()
        size = font.pointSize()
        if size > 8:
            font.setPointSize(size - 1)
            self.text_area.setFont(font)
    
    def zoom_reset(self):
        """Сбросить масштаб"""
        font = QFont("Consolas", 11)
        self.text_area.setFont(font)
    
    # ========== FUNÇÕES DE AJUDA ==========
    
    def show_about(self):
        """Показать диалог о программе"""
        crypto_status = "✅ Доступно" if CRYPTO_AVAILABLE else "❌ Недоступно (установите cryptography)"
        
        about_text = f"""
        <h2>Простой редактор</h2>
        <p><b>Версия:</b> 2.0.0</p>
        <p>Текстовый редактор с сохранением в формате JSON и поддержкой шифрования.</p>
        
        <h3>🔒 Шифрование:</h3>
        <p><b>Статус:</b> {crypto_status}</p>
        <p><b>Алгоритм:</b> AES-256 (Fernet)</p>
        <p><b>Вывод ключа:</b> PBKDF2-HMAC-SHA256</p>
        
        <h3>Возможности:</h3>
        <ul>
            <li>Сохранение файлов в JSON с метаданными</li>
            <li>Шифрование по паролю (AES-256)</li>
            <li>Открытие зашифрованных и незашифрованных файлов</li>
            <li>Поиск и замена текста</li>
            <li>Счетчик символов, слов и строк</li>
            <li>Регулируемый масштаб</li>
            <li>Перенос строк</li>
        </ul>
        
        <h3>Горячие клавиши:</h3>
        <ul>
            <li>Ctrl+N: Новый файл</li>
            <li>Ctrl+O: Открыть</li>
            <li>Ctrl+S: Сохранить</li>
            <li>Ctrl+E: Сохранить с шифрованием</li>
            <li>Ctrl+F: Найти</li>
            <li>Ctrl+H: Заменить</li>
            <li>Ctrl+Z: Отменить</li>
            <li>Ctrl+Y: Повторить</li>
            <li>Ctrl++: Увеличить масштаб</li>
            <li>Ctrl+-: Уменьшить масштаб</li>
        </ul>
        
        <p><i>Разработано с помощью DeepSeek</i></p>
        <p><i>Όχι, ο Χρόνος δεν είναι ο άρχοντας της γνώσης</i></p>
        """
        
        QMessageBox.about(self, "О программе", about_text)


class StartupDialog(QDialog):
    """Начальный диалог с опциями"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой редактор")
        self.setModal(True)
        self.setGeometry(400, 300, 500, 300)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📝 ПРОСТОЙ РЕДАКТОР\nс шифрованием 🔒")
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
        
        btn_new = QPushButton("📄 Новый файл")
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
        
        btn_open = QPushButton("📂 Открыть файл")
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
            warning = QLabel("⚠️ Функция шифрования недоступна.\nУстановите: pip install cryptography")
            warning.setStyleSheet("color: orange; padding: 10px;")
            warning.setAlignment(Qt.AlignCenter)
            options_layout.addWidget(warning)
        
        layout.addWidget(options)
        
        # Botão sair
        btn_exit = QPushButton("❌ Выход")
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
        """Открыть файл напрямую"""
        self.open_file_requested = True
        self.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Простой редактор")
    
    if not CRYPTO_AVAILABLE:
        QMessageBox.warning(None, "Предупреждение", 
                          "Библиотека 'cryptography' не установлена.\n"
                          "Функция шифрования будет отключена.\n\n"
                          "Для установки: pip install cryptography")
    
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
