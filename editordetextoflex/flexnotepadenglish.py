import sys
import json
import os
import base64
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import encryption libraries
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("Warning: 'cryptography' library not installed. Encryption functionality disabled.")

class SimpleTextEditor(QMainWindow):
    """
    Simple text editor that saves files in JSON format with encryption support
    Password encryption version
    """
    
    def __init__(self):
        super().__init__()
        
        # Window settings
        self.setWindowTitle("Simple Editor - JSON Notebook with Encryption")
        self.setGeometry(100, 100, 900, 600)
        
        # State variables
        self.current_file = None
        self.is_modified = False
        self.search_text = ""
        self.replace_text = ""
        self.is_encrypted = False  # Indicates if current file is encrypted
        
        # Setup UI
        self.init_ui()
        
        # Apply style
        self.apply_style()
        
        # Show welcome message
        self.show_welcome()
    
    def init_ui(self):
        """Initialize user interface"""
        
        # ========== MENU BAR ==========
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        # File menu actions
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Create a new file")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Open an existing file")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Save the current file")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Save the file with a new name")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Action to save with password
        self.save_encrypted_action = QAction("Save &Encrypted...", self)
        self.save_encrypted_action.setShortcut("Ctrl+E")
        self.save_encrypted_action.setStatusTip("Save file with password encryption")
        self.save_encrypted_action.triggered.connect(self.save_encrypted_file)
        if not CRYPTO_AVAILABLE:
            self.save_encrypted_action.setEnabled(False)
            self.save_encrypted_action.setToolTip("Feature unavailable - install 'cryptography' library")
        file_menu.addAction(self.save_encrypted_action)
        
        file_menu.addSeparator()
        
        export_txt_action = QAction("Export as &TXT...", self)
        export_txt_action.setStatusTip("Export as plain text file")
        export_txt_action.triggered.connect(self.export_as_txt)
        file_menu.addAction(export_txt_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the program")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Search Menu
        search_menu = menubar.addMenu("&Search")
        
        find_action = QAction("&Find...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_search)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("Find &Next", self)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)
        
        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace)
        search_menu.addAction(replace_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        word_wrap_action = QAction("&Word Wrap", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        toolbar_action = QAction("&Toolbar", self)
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)
        
        statusbar_action = QAction("&Status Bar", self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("&Reset Zoom", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # ========== TOOLBAR ==========
        self.toolbar = QToolBar("Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Toolbar buttons
        btn_new = QAction(QIcon.fromTheme("document-new"), "New", self)
        btn_new.setStatusTip("New file")
        btn_new.triggered.connect(self.new_file)
        self.toolbar.addAction(btn_new)
        
        btn_open = QAction(QIcon.fromTheme("document-open"), "Open", self)
        btn_open.setStatusTip("Open file")
        btn_open.triggered.connect(self.open_file)
        self.toolbar.addAction(btn_open)
        
        btn_save = QAction(QIcon.fromTheme("document-save"), "Save", self)
        btn_save.setStatusTip("Save file")
        btn_save.triggered.connect(self.save_file)
        self.toolbar.addAction(btn_save)
        
        self.toolbar.addSeparator()
        
        btn_cut = QAction(QIcon.fromTheme("edit-cut"), "Cut", self)
        btn_cut.setStatusTip("Cut")
        btn_cut.triggered.connect(self.cut)
        self.toolbar.addAction(btn_cut)
        
        btn_copy = QAction(QIcon.fromTheme("edit-copy"), "Copy", self)
        btn_copy.setStatusTip("Copy")
        btn_copy.triggered.connect(self.copy)
        self.toolbar.addAction(btn_copy)
        
        btn_paste = QAction(QIcon.fromTheme("edit-paste"), "Paste", self)
        btn_paste.setStatusTip("Paste")
        btn_paste.triggered.connect(self.paste)
        self.toolbar.addAction(btn_paste)
        
        self.toolbar.addSeparator()
        
        btn_undo = QAction(QIcon.fromTheme("edit-undo"), "Undo", self)
        btn_undo.setStatusTip("Undo")
        btn_undo.triggered.connect(self.undo)
        self.toolbar.addAction(btn_undo)
        
        btn_redo = QAction(QIcon.fromTheme("edit-redo"), "Redo", self)
        btn_redo.setStatusTip("Redo")
        btn_redo.triggered.connect(self.redo)
        self.toolbar.addAction(btn_redo)
        
        self.toolbar.addSeparator()
        
        btn_find = QAction(QIcon.fromTheme("edit-find"), "Find", self)
        btn_find.setStatusTip("Find text")
        btn_find.triggered.connect(self.show_search)
        self.toolbar.addAction(btn_find)
        
        # ========== CENTRAL AREA ==========
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Text area
        self.text_area = QPlainTextEdit()
        self.text_area.setFont(QFont("Consolas", 11))
        self.text_area.textChanged.connect(self.on_text_changed)
        self.text_area.cursorPositionChanged.connect(self.on_cursor_position_changed)
        layout.addWidget(self.text_area)
        
        # Search bar (initially hidden)
        self.search_bar = QWidget()
        self.search_bar.setObjectName("search-bar")
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.find_next)
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Replace with...")
        self.replace_input.returnPressed.connect(self.replace_current)
        self.replace_input.hide()
        
        btn_find_prev = QPushButton("⬆")
        btn_find_prev.setToolTip("Previous")
        btn_find_prev.setMaximumWidth(30)
        btn_find_prev.clicked.connect(self.find_previous)
        
        btn_find_next = QPushButton("⬇")
        btn_find_next.setToolTip("Next")
        btn_find_next.setMaximumWidth(30)
        btn_find_next.clicked.connect(self.find_next)
        
        self.btn_replace = QPushButton("Replace")
        self.btn_replace.setToolTip("Replace current occurrence")
        self.btn_replace.hide()
        self.btn_replace.clicked.connect(self.replace_current)
        
        self.btn_replace_all = QPushButton("Replace All")
        self.btn_replace_all.setToolTip("Replace all occurrences")
        self.btn_replace_all.hide()
        self.btn_replace_all.clicked.connect(self.replace_all)
        
        btn_close_search = QPushButton("✕")
        btn_close_search.setToolTip("Close")
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
        
        # ========== STATUS BAR ==========
        self.status_bar = self.statusBar()
        
        # Cursor position label
        self.position_label = QLabel("Ln 1, Col 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        # Insert mode label
        self.mode_label = QLabel("INS")
        self.status_bar.addPermanentWidget(self.mode_label)
        
        # File size label
        self.size_label = QLabel("0 characters")
        self.status_bar.addPermanentWidget(self.size_label)
        
        # Encryption status label
        self.encrypt_label = QLabel("🔓")
        self.encrypt_label.setToolTip("File not encrypted")
        self.status_bar.addPermanentWidget(self.encrypt_label)
    
    def apply_style(self):
        """Apply visual style"""
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
        """Show welcome message"""
        welcome_text = """# Simple Editor - JSON Notebook with Encryption

## 📝 Welcome!

This is a text editor that saves files in JSON format with encryption support.

### ✨ Features:
- ✅ Save files in JSON format
- ✅ Password encryption (AES-256)
- ✅ Open encrypted and unencrypted files
- ✅ Find and replace text
- ✅ Undo/Redo
- ✅ Word wrap
- ✅ Adjustable zoom

### 🔒 How to use encryption:
- Use **Ctrl+E** or File menu > "Save Encrypted..."
- Enter a strong password to protect your file
- The file will be saved with .json extension (but will be encrypted)
- When opening an encrypted file, the password will be requested

### 🚀 How to use:
- Use **Ctrl+N** for new file
- Use **Ctrl+O** to open
- Use **Ctrl+S** to save (without encryption)
- Use **Ctrl+E** to save with encryption
- Use **Ctrl+F** to find
- Use **Ctrl+H** to replace

### 📁 JSON Format:
Files are saved with metadata including:
- Creation and modification date
- Character, word and line count
- Encryption indicator

Enjoy! 🎉
"""
        self.text_area.setPlainText(welcome_text)
        self.current_file = None
        self.is_modified = False
        self.is_encrypted = False
        self.update_window_title()
        self.update_encrypt_label()
    
    def on_text_changed(self):
        """When text changes"""
        self.is_modified = True
        self.update_window_title()
        self.update_size_label()
    
    def on_cursor_position_changed(self):
        """When cursor position changes"""
        cursor = self.text_area.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.position_label.setText(f"Ln {line}, Col {col}")
    
    def update_window_title(self):
        """Update window title"""
        title = "Simple Editor"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_encrypted:
            title += " [Encrypted]"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def update_size_label(self):
        """Update size label"""
        text = self.text_area.toPlainText()
        chars = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        
        self.size_label.setText(f"{chars} characters | {words} words | {lines} lines")
    
    def update_encrypt_label(self):
        """Update encryption label on status bar"""
        if self.is_encrypted:
            self.encrypt_label.setText("🔒")
            self.encrypt_label.setToolTip("File encrypted")
        else:
            self.encrypt_label.setText("🔓")
            self.encrypt_label.setToolTip("File not encrypted")
    
    # ========== ENCRYPTION FUNCTIONS ==========
    
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """Derive key from password using PBKDF2"""
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
        """Encrypt content with password"""
        if not CRYPTO_AVAILABLE:
            raise Exception("'cryptography' library is not installed")
        
        # Generate random salt
        salt = os.urandom(16)
        
        # Derive key
        key, _ = self.derive_key(password, salt)
        
        # Create cipher
        f = Fernet(key)
        
        # Encrypt content
        encrypted_data = f.encrypt(content.encode('utf-8'))
        
        # Return encrypted data with salt
        return {
            'encrypted': True,
            'salt': base64.b64encode(salt).decode(),
            'data': base64.b64encode(encrypted_data).decode(),
            'algorithm': 'AES-256-CBC',
            'key_derivation': 'PBKDF2-HMAC-SHA256'
        }
    
    def decrypt_content(self, encrypted_data: dict, password: str) -> str:
        """Decrypt content with password"""
        if not CRYPTO_AVAILABLE:
            raise Exception("'cryptography' library is not installed")
        
        # Check if it's an encrypted file
        if not encrypted_data.get('encrypted', False):
            return None
        
        try:
            # Retrieve salt
            salt = base64.b64decode(encrypted_data['salt'])
            
            # Derive key
            key, _ = self.derive_key(password, salt)
            
            # Create cipher
            f = Fernet(key)
            
            # Decrypt
            encrypted_content = base64.b64decode(encrypted_data['data'])
            decrypted_content = f.decrypt(encrypted_content)
            
            return decrypted_content.decode('utf-8')
        except Exception as e:
            raise Exception("Incorrect password or corrupted file")
    
    def get_password(self, title="Password", message="Enter password:", is_new=False):
        """Dialog to get password from user"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setModal(True)
        layout = QVBoxLayout()
        
        # Message
        label = QLabel(message)
        layout.addWidget(label)
        
        # Password field
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(password_input)
        
        if is_new:
            # Confirm password
            label_confirm = QLabel("Confirm password:")
            layout.addWidget(label_confirm)
            
            confirm_input = QLineEdit()
            confirm_input.setEchoMode(QLineEdit.Password)
            layout.addWidget(confirm_input)
        
        # Buttons
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
                    QMessageBox.warning(self, "Error", "Passwords do not match!")
                    return None
                if not password:
                    QMessageBox.warning(self, "Error", "Password cannot be empty!")
                    return None
            return password
        
        return None
    
    def save_encrypted_file(self):
        """Save file with encryption"""
        if not CRYPTO_AVAILABLE:
            QMessageBox.critical(self, "Error", 
                               "'cryptography' library is not installed.\n"
                               "Install with: pip install cryptography")
            return
        
        # Check if need to save first
        if self.is_modified and self.current_file and not self.is_encrypted:
            reply = QMessageBox.question(
                self, "Save?",
                "Current file is not saved. Would you like to save it first?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_file()
        
        # Choose location to save
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Encrypted File", "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        # Get password
        password = self.get_password("Encrypt File", 
                                     "Enter a password to protect the file:", 
                                     is_new=True)
        if not password:
            return
        
        try:
            content = self.text_area.toPlainText()
            
            # Create metadata
            metadata = {
                'created': datetime.now().isoformat() if not self.current_file else None,
                'modified': datetime.now().isoformat(),
                'characters': len(content),
                'words': len(content.split()),
                'lines': content.count('\n') + 1
            }
            
            # Encrypt content
            encrypted_data = self.encrypt_content(content, password)
            
            # Save encrypted data with metadata
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
            self.status_bar.showMessage(f"Encrypted file saved: {file_path}", 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving encrypted file:\n{str(e)}")
    
    def save_to_file(self, file_path):
        """Save content to file (without encryption)"""
        try:
            content = self.text_area.toPlainText()
            
            if file_path.endswith('.json'):
                # Save with metadata
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
                # Save as plain text
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self.current_file = file_path
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"File saved: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving file:\n{str(e)}")
    
    def open_file(self):
        """Open file"""
        if not self.check_save():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Check if encrypted file
                    if isinstance(data, dict) and data.get('encrypted', False):
                        # Request password
                        password = self.get_password("Encrypted File", 
                                                    "This file is encrypted.\nEnter password to open:")
                        if not password:
                            return
                        
                        # Decrypt
                        content = self.decrypt_content(data['crypto_info'], password)
                        if content is None:
                            QMessageBox.critical(self, "Error", "Failed to decrypt file.")
                            return
                        
                        self.text_area.setPlainText(content)
                        self.is_encrypted = True
                    else:
                        # Normal file
                        if isinstance(data, dict) and 'content' in data:
                            content = data['content']
                        else:
                            content = str(data)
                        self.text_area.setPlainText(content)
                        self.is_encrypted = False
            else:
                # Plain text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
                self.is_encrypted = False
            
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage(f"File loaded: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error opening file:\n{str(e)}")
    
    def new_file(self):
        """Create new file"""
        if self.check_save():
            self.text_area.clear()
            self.current_file = None
            self.is_modified = False
            self.is_encrypted = False
            self.update_window_title()
            self.update_size_label()
            self.update_encrypt_label()
            self.status_bar.showMessage("New file created", 3000)
    
    def export_as_txt(self):
        """Export as TXT"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export as TXT", "",
            "Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            try:
                content = self.text_area.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.showMessage(f"File exported: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exporting:\n{str(e)}")
    
    def check_save(self):
        """Check if need to save before closing/opening new"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Save?",
                "The file has been modified. Do you want to save the changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def save_file(self):
        """Save file (normal or encrypted depending on state)"""
        if self.current_file:
            if self.is_encrypted:
                # If current file is encrypted, save as encrypted
                self.save_encrypted_file()
            else:
                self.save_to_file(self.current_file)
        else:
            # Ask if want to save encrypted or not
            reply = QMessageBox.question(
                self, "Save Type",
                "Do you want to save with encryption?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                self.save_encrypted_file()
            else:
                self.save_file_as()
    
    def save_file_as(self):
        """Save file as (without encryption)"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "",
            "JSON Files (*.json);;Text Files (*.txt);;All Files (*.*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def closeEvent(self, event):
        """Window close event"""
        if self.check_save():
            event.accept()
        else:
            event.ignore()
    
    # ========== EDITING FUNCTIONS ==========
    
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
    
    # ========== SEARCH FUNCTIONS ==========
    
    def show_search(self):
        """Show search bar"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.hide()
        self.btn_replace.hide()
        self.btn_replace_all.hide()
    
    def show_replace(self):
        """Show replace bar"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.show()
        self.btn_replace.show()
        self.btn_replace_all.show()
    
    def hide_search(self):
        """Hide search bar"""
        self.search_bar.hide()
        self.search_input.clear()
        self.replace_input.clear()
        self.text_area.setExtraSelections([])
    
    def on_search_text_changed(self, text):
        """When search text changes"""
        self.search_text = text
        self.highlight_all()
    
    def highlight_all(self):
        """Highlight all occurrences"""
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
        """Find next occurrence"""
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
                self.status_bar.showMessage("Reached beginning of document", 3000)
            else:
                self.status_bar.showMessage(f"Text '{self.search_text}' not found", 3000)
                return False
        
        return True
    
    def find_previous(self):
        """Find previous occurrence"""
        if not self.search_text:
            return
        
        found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
        
        if not found:
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.End)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
            
            if found:
                self.status_bar.showMessage("Reached end of document", 3000)
            else:
                self.status_bar.showMessage(f"Text '{self.search_text}' not found", 3000)
                return False
        
        return True
    
    def replace_current(self):
        """Replace current occurrence"""
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
        """Replace all occurrences"""
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
            QMessageBox.information(self, "Replace", f"Replaced {count} occurrences.")
        else:
            QMessageBox.information(self, "Replace", f"Text '{self.search_text}' not found.")
    
    # ========== VIEW FUNCTIONS ==========
    
    def toggle_word_wrap(self, checked):
        """Toggle word wrap"""
        if checked:
            self.text_area.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
    
    def toggle_toolbar(self, checked):
        """Toggle toolbar"""
        if checked:
            self.toolbar.show()
        else:
            self.toolbar.hide()
    
    def toggle_statusbar(self, checked):
        """Toggle status bar"""
        if checked:
            self.status_bar.show()
        else:
            self.status_bar.hide()
    
    def zoom_in(self):
        """Zoom in"""
        font = self.text_area.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_area.setFont(font)
    
    def zoom_out(self):
        """Zoom out"""
        font = self.text_area.font()
        size = font.pointSize()
        if size > 8:
            font.setPointSize(size - 1)
            self.text_area.setFont(font)
    
    def zoom_reset(self):
        """Reset zoom"""
        font = QFont("Consolas", 11)
        self.text_area.setFont(font)
    
    # ========== HELP FUNCTIONS ==========
    
    def show_about(self):
        """Show about dialog"""
        crypto_status = "✅ Available" if CRYPTO_AVAILABLE else "❌ Not available (install cryptography)"
        
        about_text = f"""
        <h2>Simple Editor</h2>
        <p><b>Version:</b> 2.0.0</p>
        <p>A text editor that saves in JSON format with encryption support.</p>
        
        <h3>🔒 Encryption:</h3>
        <p><b>Status:</b> {crypto_status}</p>
        <p><b>Algorithm:</b> AES-256 (Fernet)</p>
        <p><b>Key Derivation:</b> PBKDF2-HMAC-SHA256</p>
        
        <h3>Features:</h3>
        <ul>
            <li>Save files in JSON with metadata</li>
            <li>Password encryption (AES-256)</li>
            <li>Open encrypted and unencrypted files</li>
            <li>Find and replace text</li>
            <li>Character, word and line counter</li>
            <li>Adjustable zoom</li>
            <li>Word wrap</li>
        </ul>
        
        <h3>Shortcuts:</h3>
        <ul>
            <li>Ctrl+N: New file</li>
            <li>Ctrl+O: Open</li>
            <li>Ctrl+S: Save</li>
            <li>Ctrl+E: Save Encrypted</li>
            <li>Ctrl+F: Find</li>
            <li>Ctrl+H: Replace</li>
            <li>Ctrl+Z: Undo</li>
            <li>Ctrl+Y: Redo</li>
            <li>Ctrl++: Zoom in</li>
            <li>Ctrl+-: Zoom out</li>
        </ul>
        
        <p><i>Developed with assistance from DeepSeek</i></p>
        <p><i>Όχι, ο Χρόνος δεν είναι ο άρχοντας της γνώσης</i></p>
        """
        
        QMessageBox.about(self, "About Simple Editor", about_text)


class StartupDialog(QDialog):
    """Initial dialog with options"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Editor")
        self.setModal(True)
        self.setGeometry(400, 300, 500, 300)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📝 SIMPLE EDITOR\nwith Encryption 🔒")
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
        
        # Options
        options = QWidget()
        options_layout = QVBoxLayout(options)
        
        btn_new = QPushButton("📄 New File")
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
        
        btn_open = QPushButton("📂 Open File")
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
            warning = QLabel("⚠️ Encryption feature not available.\nInstall: pip install cryptography")
            warning.setStyleSheet("color: orange; padding: 10px;")
            warning.setAlignment(Qt.AlignCenter)
            options_layout.addWidget(warning)
        
        layout.addWidget(options)
        
        # Exit button
        btn_exit = QPushButton("❌ Exit")
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
        """Open file directly"""
        self.open_file_requested = True
        self.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Editor")
    
    if not CRYPTO_AVAILABLE:
        QMessageBox.warning(None, "Warning", 
                          "'cryptography' library is not installed.\n"
                          "Encryption functionality will be disabled.\n\n"
                          "To install: pip install cryptography")
    
    # Initial dialog
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
