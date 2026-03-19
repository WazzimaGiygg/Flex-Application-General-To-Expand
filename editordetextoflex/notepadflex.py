import sys
import json
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class SimpleTextEditor(QMainWindow):
    """
    Editor de texto simples que salva arquivos em formato JSON
    Versão base para futuros aprimoramentos
    """
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.setWindowTitle("Editor Simples de Texto - WazzimaGiygg - Bloco de Notas JSON")
        self.setGeometry(100, 100, 900, 600)
        
        # Variáveis de estado
        self.current_file = None
        self.is_modified = False
        self.search_text = ""
        self.replace_text = ""
        
        # Configurar interface
        self.init_ui()
        
        # Aplicar estilo
        self.apply_style()
        
        # Mostrar boas-vindas
        self.show_welcome()
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        
        # ========== BARRA DE MENUS ==========
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        # Ações do menu Arquivo
        new_action = QAction("&Novo", self)
        new_action.setShortcut("Ctrl+N")
        new_action.setStatusTip("Criar novo arquivo")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Abrir...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Abrir arquivo existente")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Salvar", self)
        save_action.setShortcut("Ctrl+S")
        save_action.setStatusTip("Salvar arquivo atual")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Salvar &Como...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.setStatusTip("Salvar arquivo com novo nome")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_txt_action = QAction("Exportar como &TXT...", self)
        export_txt_action.setStatusTip("Exportar como arquivo de texto simples")
        export_txt_action.triggered.connect(self.export_as_txt)
        file_menu.addAction(export_txt_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Sair do programa")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Editar
        edit_menu = menubar.addMenu("&Editar")
        
        undo_action = QAction("&Desfazer", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Refazer", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("&Recortar", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copiar", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Colar", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Selecionar &Tudo", self)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Menu Localizar
        search_menu = menubar.addMenu("&Localizar")
        
        find_action = QAction("&Localizar...", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.show_search)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("Localizar &Próximo", self)
        find_next_action.setShortcut("F3")
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)
        
        replace_action = QAction("&Substituir...", self)
        replace_action.setShortcut("Ctrl+H")
        replace_action.triggered.connect(self.show_replace)
        search_menu.addAction(replace_action)
        
        # Menu Exibir
        view_menu = menubar.addMenu("&Exibir")
        
        word_wrap_action = QAction("&Quebra de Linha", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(True)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        view_menu.addAction(word_wrap_action)
        
        toolbar_action = QAction("&Barra de Ferramentas", self)
        toolbar_action.setCheckable(True)
        toolbar_action.setChecked(True)
        toolbar_action.triggered.connect(self.toggle_toolbar)
        view_menu.addAction(toolbar_action)
        
        statusbar_action = QAction("&Barra de Status", self)
        statusbar_action.setCheckable(True)
        statusbar_action.setChecked(True)
        statusbar_action.triggered.connect(self.toggle_statusbar)
        view_menu.addAction(statusbar_action)
        
        view_menu.addSeparator()
        
        zoom_in_action = QAction("Aumentar &Zoom", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Diminuir &Zoom", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_reset_action = QAction("&Resetar Zoom", self)
        zoom_reset_action.setShortcut("Ctrl+0")
        zoom_reset_action.triggered.connect(self.zoom_reset)
        view_menu.addAction(zoom_reset_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("A&juda")
        
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # ========== BARRA DE FERRAMENTAS ==========
        self.toolbar = QToolBar("Barra de Ferramentas")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # Botões da barra de ferramentas
        btn_new = QAction(QIcon.fromTheme("document-new"), "Novo", self)
        btn_new.setStatusTip("Novo arquivo")
        btn_new.triggered.connect(self.new_file)
        self.toolbar.addAction(btn_new)
        
        btn_open = QAction(QIcon.fromTheme("document-open"), "Abrir", self)
        btn_open.setStatusTip("Abrir arquivo")
        btn_open.triggered.connect(self.open_file)
        self.toolbar.addAction(btn_open)
        
        btn_save = QAction(QIcon.fromTheme("document-save"), "Salvar", self)
        btn_save.setStatusTip("Salvar arquivo")
        btn_save.triggered.connect(self.save_file)
        self.toolbar.addAction(btn_save)
        
        self.toolbar.addSeparator()
        
        btn_cut = QAction(QIcon.fromTheme("edit-cut"), "Recortar", self)
        btn_cut.setStatusTip("Recortar")
        btn_cut.triggered.connect(self.cut)
        self.toolbar.addAction(btn_cut)
        
        btn_copy = QAction(QIcon.fromTheme("edit-copy"), "Copiar", self)
        btn_copy.setStatusTip("Copiar")
        btn_copy.triggered.connect(self.copy)
        self.toolbar.addAction(btn_copy)
        
        btn_paste = QAction(QIcon.fromTheme("edit-paste"), "Colar", self)
        btn_paste.setStatusTip("Colar")
        btn_paste.triggered.connect(self.paste)
        self.toolbar.addAction(btn_paste)
        
        self.toolbar.addSeparator()
        
        btn_undo = QAction(QIcon.fromTheme("edit-undo"), "Desfazer", self)
        btn_undo.setStatusTip("Desfazer")
        btn_undo.triggered.connect(self.undo)
        self.toolbar.addAction(btn_undo)
        
        btn_redo = QAction(QIcon.fromTheme("edit-redo"), "Refazer", self)
        btn_redo.setStatusTip("Refazer")
        btn_redo.triggered.connect(self.redo)
        self.toolbar.addAction(btn_redo)
        
        self.toolbar.addSeparator()
        
        btn_find = QAction(QIcon.fromTheme("edit-find"), "Localizar", self)
        btn_find.setStatusTip("Localizar texto")
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
        search_layout = QHBoxLayout(self.search_bar)
        search_layout.setContentsMargins(5, 5, 5, 5)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Localizar...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.find_next)
        
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Substituir por...")
        self.replace_input.hide()  # Inicialmente oculto
        
        btn_find_prev = QPushButton("⬆")
        btn_find_prev.setToolTip("Anterior")
        btn_find_prev.setMaximumWidth(30)
        btn_find_prev.clicked.connect(self.find_previous)
        
        btn_find_next = QPushButton("⬇")
        btn_find_next.setToolTip("Próximo")
        btn_find_next.setMaximumWidth(30)
        btn_find_next.clicked.connect(self.find_next)
        
        btn_replace = QPushButton("Substituir")
        btn_replace.hide()
        btn_replace.clicked.connect(self.replace_current)
        
        btn_replace_all = QPushButton("Substituir Tudo")
        btn_replace_all.hide()
        btn_replace_all.clicked.connect(self.replace_all)
        
        btn_close_search = QPushButton("✕")
        btn_close_search.setToolTip("Fechar")
        btn_close_search.setMaximumWidth(30)
        btn_close_search.clicked.connect(self.hide_search)
        
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_find_prev)
        search_layout.addWidget(btn_find_next)
        search_layout.addWidget(self.replace_input)
        search_layout.addWidget(btn_replace)
        search_layout.addWidget(btn_replace_all)
        search_layout.addStretch()
        search_layout.addWidget(btn_close_search)
        
        layout.addWidget(self.search_bar)
        self.search_bar.hide()  # Inicialmente oculto
        
        # ========== BARRA DE STATUS ==========
        self.status_bar = self.statusBar()
        
        # Label de posição do cursor
        self.position_label = QLabel("Lin 1, Col 1")
        self.status_bar.addPermanentWidget(self.position_label)
        
        # Label de modo de inserção
        self.mode_label = QLabel("INS")
        self.status_bar.addPermanentWidget(self.mode_label)
        
        # Label de tamanho do arquivo
        self.size_label = QLabel("0 caracteres")
        self.status_bar.addPermanentWidget(self.size_label)
    
    def apply_style(self):
        """Aplicar estilo visual"""
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
        .search-bar {
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
        """Mostrar mensagem de boas-vindas"""
        welcome_text = """# Editor Simples - Bloco de Notas JSON

## 📝 Bem-vindo!

Este é um editor de texto simples que salva arquivos em formato JSON.

### ✨ Funcionalidades:
- ✅ Salvar arquivos em formato JSON
- ✅ Abrir arquivos existentes
- ✅ Localizar e substituir texto
- ✅ Desfazer/Refazer
- ✅ Quebra de linha
- ✅ Zoom ajustável

### 🚀 Como usar:
- Use **Ctrl+N** para novo arquivo
- Use **Ctrl+O** para abrir
- Use **Ctrl+S** para salvar
- Use **Ctrl+F** para localizar
- Use **Ctrl+H** para substituir

### 📁 Formato JSON:
Os arquivos são salvos com metadados incluindo:
- Data de criação
- Última modificação
- Contagem de caracteres

Divirta-se! 🎉
"""
        self.text_area.setPlainText(welcome_text)
        self.current_file = None
        self.is_modified = False
        self.update_window_title()
    
    def on_text_changed(self):
        """Quando o texto muda"""
        self.is_modified = True
        self.update_window_title()
        self.update_size_label()
    
    def on_cursor_position_changed(self):
        """Quando o cursor muda de posição"""
        cursor = self.text_area.textCursor()
        line = cursor.blockNumber() + 1
        col = cursor.columnNumber() + 1
        self.position_label.setText(f"Lin {line}, Col {col}")
    
    def update_window_title(self):
        """Atualizar título da janela"""
        title = "Editor Simples"
        if self.current_file:
            title += f" - {os.path.basename(self.current_file)}"
        if self.is_modified:
            title += " *"
        self.setWindowTitle(title)
    
    def update_size_label(self):
        """Atualizar label de tamanho"""
        text = self.text_area.toPlainText()
        chars = len(text)
        words = len(text.split())
        lines = text.count('\n') + 1
        
        self.size_label.setText(f"{chars} caracteres | {words} palavras | {lines} linhas")
    
    def new_file(self):
        """Criar novo arquivo"""
        if self.check_save():
            self.text_area.clear()
            self.current_file = None
            self.is_modified = False
            self.update_window_title()
            self.update_size_label()
            self.status_bar.showMessage("Novo arquivo criado", 3000)
    
    def open_file(self):
        """Abrir arquivo"""
        if not self.check_save():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Arquivo", "",
            "Arquivos JSON (*.json);;Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'content' in data:
                        content = data['content']
                        self.text_area.setPlainText(content)
                    else:
                        self.text_area.setPlainText(str(data))
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_area.setPlainText(content)
            
            self.current_file = file_path
            self.is_modified = False
            self.update_window_title()
            self.update_size_label()
            self.status_bar.showMessage(f"Arquivo carregado: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao abrir arquivo:\n{str(e)}")
    
    def save_file(self):
        """Salvar arquivo"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Salvar arquivo como"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo Como", "",
            "Arquivos JSON (*.json);;Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            self.save_to_file(file_path)
    
    def save_to_file(self, file_path):
        """Salvar conteúdo no arquivo"""
        try:
            content = self.text_area.toPlainText()
            
            if file_path.endswith('.json'):
                # Salvar com metadados
                data = {
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
            self.update_window_title()
            self.status_bar.showMessage(f"Arquivo salvo: {file_path}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar arquivo:\n{str(e)}")
    
    def export_as_txt(self):
        """Exportar como TXT"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar como TXT", "",
            "Arquivos de Texto (*.txt);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            try:
                content = self.text_area.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_bar.showMessage(f"Arquivo exportado: {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar:\n{str(e)}")
    
    def check_save(self):
        """Verificar se precisa salvar antes de fechar/abrir novo"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Salvar?",
                "O arquivo foi modificado. Deseja salvar as alterações?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return True
            elif reply == QMessageBox.Cancel:
                return False
        
        return True
    
    def closeEvent(self, event):
        """Evento de fechar a janela"""
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
        """Mostrar barra de localização"""
        self.search_bar.show()
        self.search_input.setFocus()
        self.replace_input.hide()
        self.find_buttons_show()
    
    def show_replace(self):
        """Mostrar barra de substituição"""
        self.search_bar.show()
        self.replace_input.show()
        self.find_buttons_show()
        self.find_buttons_show(True)
    
    def hide_search(self):
        """Ocultar barra de localização"""
        self.search_bar.hide()
        self.search_input.clear()
        self.replace_input.clear()
        self.replace_input.hide()
    
    def find_buttons_show(self, replace=False):
        """Mostrar botões apropriados"""
        # Implementar se necessário
        pass
    
    def on_search_text_changed(self, text):
        """Quando o texto de busca muda"""
        self.search_text = text
        self.highlight_all()
    
    def highlight_all(self):
        """Destacar todas as ocorrências"""
        # Limpar seleções existentes
        cursor = self.text_area.textCursor()
        cursor.clearSelection()
        self.text_area.setTextCursor(cursor)
        
        # Criar formato de destaque
        extra_selections = []
        
        if self.search_text:
            # Procurar todas as ocorrências
            document = self.text_area.document()
            cursor = QTextCursor(document)
            
            while not cursor.isNull() and not cursor.atEnd():
                cursor = document.find(self.search_text, cursor)
                if not cursor.isNull():
                    selection = QTextEdit.ExtraSelection()
                    selection.cursor = cursor
                    selection.format.setBackground(QColor(255, 255, 0, 100))
                    extra_selections.append(selection)
        
        self.text_area.setExtraSelections(extra_selections)
    
    def find_next(self):
        """Encontrar próxima ocorrência"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        found = self.text_area.find(self.search_text)
        
        if not found:
            # Voltar ao início
            cursor.movePosition(QTextCursor.Start)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text)
            
            if found:
                self.status_bar.showMessage("Início do documento alcançado", 3000)
            else:
                self.status_bar.showMessage(f"Texto '{self.search_text}' não encontrado", 3000)
    
    def find_previous(self):
        """Encontrar ocorrência anterior"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
        
        if not found:
            # Ir ao final
            cursor.movePosition(QTextCursor.End)
            self.text_area.setTextCursor(cursor)
            found = self.text_area.find(self.search_text, QTextDocument.FindBackward)
            
            if found:
                self.status_bar.showMessage("Final do documento alcançado", 3000)
            else:
                self.status_bar.showMessage(f"Texto '{self.search_text}' não encontrado", 3000)
    
    def replace_current(self):
        """Substituir ocorrência atual"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == self.search_text:
            cursor.insertText(self.replace_input.text())
            self.find_next()
    
    def replace_all(self):
        """Substituir todas as ocorrências"""
        if not self.search_text:
            return
        
        cursor = self.text_area.textCursor()
        cursor.beginEditBlock()
        
        count = 0
        cursor.movePosition(QTextCursor.Start)
        self.text_area.setTextCursor(cursor)
        
        while self.text_area.find(self.search_text):
            cursor = self.text_area.textCursor()
            cursor.insertText(self.replace_input.text())
            count += 1
        
        cursor.endEditBlock()
        
        QMessageBox.information(self, "Substituir", f"Foram substituídas {count} ocorrências.")
    
    # ========== FUNÇÕES DE EXIBIÇÃO ==========
    
    def toggle_word_wrap(self, checked):
        """Alternar quebra de linha"""
        if checked:
            self.text_area.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        else:
            self.text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
    
    def toggle_toolbar(self, checked):
        """Alternar barra de ferramentas"""
        if checked:
            self.toolbar.show()
        else:
            self.toolbar.hide()
    
    def toggle_statusbar(self, checked):
        """Alternar barra de status"""
        if checked:
            self.status_bar.show()
        else:
            self.status_bar.hide()
    
    def zoom_in(self):
        """Aumentar zoom"""
        font = self.text_area.font()
        font.setPointSize(font.pointSize() + 1)
        self.text_area.setFont(font)
    
    def zoom_out(self):
        """Diminuir zoom"""
        font = self.text_area.font()
        size = font.pointSize()
        if size > 8:
            font.setPointSize(size - 1)
            self.text_area.setFont(font)
    
    def zoom_reset(self):
        """Resetar zoom"""
        font = QFont("Consolas", 11)
        self.text_area.setFont(font)
    
    # ========== FUNÇÕES DE AJUDA ==========
    
    def show_about(self):
        """Mostrar diálogo sobre"""
        about_text = """
        <h2>Editor Simples</h2>
        <p><b>Versão:</b> 1.0.0</p>
        <p>Um editor de texto simples que salva em formato JSON.</p>
        
        <h3>Funcionalidades:</h3>
        <ul>
            <li>Salvar arquivos em JSON com metadados</li>
            <li>Abrir arquivos existentes</li>
            <li>Localizar e substituir texto</li>
            <li>Contador de caracteres, palavras e linhas</li>
            <li>Zoom ajustável</li>
            <li>Quebra de linha</li>
        </ul>
        
        <h3>Atalhos:</h3>
        <ul>
            <li>Ctrl+N: Novo arquivo</li>
            <li>Ctrl+O: Abrir</li>
            <li>Ctrl+S: Salvar</li>
            <li>Ctrl+F: Localizar</li>
            <li>Ctrl+H: Substituir</li>
            <li>Ctrl+Z: Desfazer</li>
            <li>Ctrl+Y: Refazer</li>
            <li>Ctrl++: Aumentar zoom</li>
            <li>Ctrl+-: Diminuir zoom</li>
        </ul>
        
        <p><i>Desenvolvido com auxílio do DeepSeek</i></p>
        <p><i>Όχι, ο Χρόνος δεν είναι ο άρχοντας της γνώσης</i></p>
        """
        
        QMessageBox.about(self, "Sobre o Editor Simples", about_text)

class StartupDialog(QDialog):
    """Diálogo inicial com opções"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editor Simples")
        self.setModal(True)
        self.setGeometry(400, 300, 500, 300)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📝 EDITOR SIMPLES")
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
        
        btn_new = QPushButton("📄 Novo Arquivo")
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
        
        btn_open = QPushButton("📂 Abrir Arquivo")
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
        
        layout.addWidget(options)
        
        # Botão sair
        btn_exit = QPushButton("❌ Sair")
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
    
    def open_file(self):
        """Abrir arquivo diretamente"""
        self.accept()
        self.open_file_requested = True

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Editor Simples")
    
    # Diálogo inicial
    dialog = StartupDialog()
    if dialog.exec_() == QDialog.Accepted:
        editor = SimpleTextEditor()
        editor.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
