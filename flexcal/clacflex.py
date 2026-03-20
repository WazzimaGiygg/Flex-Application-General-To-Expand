import sys
import json
import math
import random
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class HistoryEntry:
    """Classe para representar uma entrada no histórico"""
    def __init__(self, expression, result, mode, timestamp=None):
        self.expression = expression
        self.result = result
        self.mode = mode
        self.timestamp = timestamp or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def to_dict(self):
        return {
            'expression': self.expression,
            'result': self.result,
            'mode': self.mode,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['expression'], data['result'], data['mode'], data['timestamp'])

class Calculator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.setWindowTitle("Calculadora Multi-Modo")
        self.setGeometry(100, 100, 500, 600)
        self.setMinimumSize(400, 500)
        
        # Variáveis de estado
        self.current_mode = "Padrão"  # Padrão, Científica, Programador
        self.history = []
        self.current_expression = ""
        self.last_result = 0
        self.angle_unit = "DEG"  # DEG, RAD, GRAD
        self.word_size = 64  # Para modo programador (bits)
        self.number_base = 10  # 10=decimal, 16=hex, 8=oct, 2=bin
        
        # Configurar interface
        self.init_ui()
        
        # Aplicar estilo
        self.apply_style()
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(5)
        
        # ========== BARRA DE MENUS ==========
        menubar = self.menuBar()
        
        # Menu Arquivo
        file_menu = menubar.addMenu("&Arquivo")
        
        export_action = QAction("&Exportar Histórico...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_history)
        file_menu.addAction(export_action)
        
        import_action = QAction("&Importar Histórico...", self)
        import_action.setShortcut("Ctrl+I")
        import_action.triggered.connect(self.import_history)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        clear_history_action = QAction("&Limpar Histórico", self)
        clear_history_action.triggered.connect(self.clear_history)
        file_menu.addAction(clear_history_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("&Sair", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menu Modo
        mode_menu = menubar.addMenu("&Modo")
        
        self.mode_group = QActionGroup(self)
        
        mode_padrao = QAction("&Padrão", self, checkable=True)
        mode_padrao.setChecked(True)
        mode_padrao.triggered.connect(lambda: self.change_mode("Padrão"))
        mode_menu.addAction(mode_padrao)
        self.mode_group.addAction(mode_padrao)
        
        mode_cientifica = QAction("&Científica", self, checkable=True)
        mode_cientifica.triggered.connect(lambda: self.change_mode("Científica"))
        mode_menu.addAction(mode_cientifica)
        self.mode_group.addAction(mode_cientifica)
        
        mode_programador = QAction("&Programador", self, checkable=True)
        mode_programador.triggered.connect(lambda: self.change_mode("Programador"))
        mode_menu.addAction(mode_programador)
        self.mode_group.addAction(mode_programador)
        
        # Menu Configurações
        config_menu = menubar.addMenu("&Configurações")
        
        # Submenu para unidades angulares (modo científico)
        self.angle_menu = config_menu.addMenu("Unidade Angular")
        self.angle_group = QActionGroup(self)
        
        angle_deg = QAction("&Graus (DEG)", self, checkable=True)
        angle_deg.setChecked(True)
        angle_deg.triggered.connect(lambda: self.set_angle_unit("DEG"))
        self.angle_menu.addAction(angle_deg)
        self.angle_group.addAction(angle_deg)
        
        angle_rad = QAction("&Radianos (RAD)", self, checkable=True)
        angle_rad.triggered.connect(lambda: self.set_angle_unit("RAD"))
        self.angle_menu.addAction(angle_rad)
        self.angle_group.addAction(angle_rad)
        
        angle_grad = QAction("&Grados (GRAD)", self, checkable=True)
        angle_grad.triggered.connect(lambda: self.set_angle_unit("GRAD"))
        self.angle_menu.addAction(angle_grad)
        self.angle_group.addAction(angle_grad)
        
        # Submenu para base numérica (modo programador)
        self.base_menu = config_menu.addMenu("Base Numérica")
        self.base_group = QActionGroup(self)
        
        base_dec = QAction("&Decimal", self, checkable=True)
        base_dec.setChecked(True)
        base_dec.triggered.connect(lambda: self.set_number_base(10))
        self.base_menu.addAction(base_dec)
        self.base_group.addAction(base_dec)
        
        base_hex = QAction("&Hexadecimal", self, checkable=True)
        base_hex.triggered.connect(lambda: self.set_number_base(16))
        self.base_menu.addAction(base_hex)
        self.base_group.addAction(base_hex)
        
        base_oct = QAction("&Octal", self, checkable=True)
        base_oct.triggered.connect(lambda: self.set_number_base(8))
        self.base_menu.addAction(base_oct)
        self.base_group.addAction(base_oct)
        
        base_bin = QAction("&Binário", self, checkable=True)
        base_bin.triggered.connect(lambda: self.set_number_base(2))
        self.base_menu.addAction(base_bin)
        self.base_group.addAction(base_bin)
        
        config_menu.addSeparator()
        
        word_size_menu = config_menu.addMenu("Tamanho da Palavra")
        for bits in [8, 16, 32, 64]:
            action = QAction(f"{bits} bits", self)
            action.triggered.connect(lambda checked, b=bits: self.set_word_size(b))
            word_size_menu.addAction(action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("A&juda")
        
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # ========== BARRA DE FERRAMENTAS ==========
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Indicador de modo
        self.mode_label = QLabel("📱 Modo: Padrão")
        toolbar.addWidget(self.mode_label)
        
        toolbar.addSeparator()
        
        # Indicador de unidade angular (para modo científico)
        self.angle_label = QLabel("📐 DEG")
        toolbar.addWidget(self.angle_label)
        self.angle_label.hide()
        
        toolbar.addSeparator()
        
        # Indicador de base (para modo programador)
        self.base_label = QLabel("🔢 DEC")
        toolbar.addWidget(self.base_label)
        self.base_label.hide()
        
        toolbar.addSeparator()
        
        # Botão limpar tudo
        btn_clear_all = QAction("🗑️ Limpar Tudo", self)
        btn_clear_all.triggered.connect(self.clear_all)
        toolbar.addAction(btn_clear_all)
        
        # ========== ÁREA PRINCIPAL ==========
        main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Lado esquerdo: Calculadora
        calc_widget = QWidget()
        calc_layout = QVBoxLayout(calc_widget)
        calc_layout.setSpacing(10)
        
        # Display principal
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(80)
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 24px;
                font-weight: bold;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        calc_layout.addWidget(self.display)
        
        # Display de expressão
        self.expression_display = QLineEdit()
        self.expression_display.setReadOnly(True)
        self.expression_display.setAlignment(Qt.AlignRight)
        self.expression_display.setMinimumHeight(40)
        self.expression_display.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                color: #6c757d;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        calc_layout.addWidget(self.expression_display)
        
        # Área dos botões da calculadora
        self.buttons_widget = QStackedWidget()
        calc_layout.addWidget(self.buttons_widget)
        
        # Criar os diferentes modos de calculadora
        self.create_standard_mode()
        self.create_scientific_mode()
        self.create_programmer_mode()
        
        main_splitter.addWidget(calc_widget)
        
        # Lado direito: Histórico
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.setContentsMargins(5, 5, 5, 5)
        
        # Título do histórico
        history_title = QLabel("📋 Histórico")
        history_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
                background-color: #e9ecef;
                border-radius: 3px;
            }
        """)
        history_layout.addWidget(history_title)
        
        # Lista de histórico
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.history_item_clicked)
        history_layout.addWidget(self.history_list)
        
        # Botões do histórico
        history_buttons = QHBoxLayout()
        
        btn_copy = QPushButton("📋 Copiar")
        btn_copy.clicked.connect(self.copy_history_item)
        history_buttons.addWidget(btn_copy)
        
        btn_clear = QPushButton("🗑️ Limpar")
        btn_clear.clicked.connect(self.clear_history)
        history_buttons.addWidget(btn_clear)
        
        history_layout.addLayout(history_buttons)
        
        main_splitter.addWidget(history_widget)
        
        # Definir tamanhos iniciais do splitter
        main_splitter.setSizes([700, 300])
    
    def create_standard_mode(self):
        """Criar interface do modo padrão"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(2)
        
        # Definir botões do modo padrão
        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '=']
        ]
        
        # Criar e posicionar botões
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                btn = QPushButton(text)
                btn.setMinimumHeight(50)
                btn.setMinimumWidth(60)
                
                # Estilo especial para operadores
                if text in ['/', '*', '-', '+', '=']:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #ffc107;
                            color: black;
                            font-weight: bold;
                            font-size: 18px;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #e0a800;
                        }
                        QPushButton:pressed {
                            background-color: #d39e00;
                        }
                    """)
                elif text == 'C':
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #dc3545;
                            color: white;
                            font-weight: bold;
                            font-size: 14px;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #c82333;
                        }
                        QPushButton:pressed {
                            background-color: #bd2130;
                        }
                    """)
                elif text == '⌫':
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #6c757d;
                            color: white;
                            font-weight: bold;
                            font-size: 14px;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #5a6268;
                        }
                        QPushButton:pressed {
                            background-color: #545b62;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e9ecef;
                            color: black;
                            font-weight: bold;
                            font-size: 18px;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #dee2e6;
                        }
                        QPushButton:pressed {
                            background-color: #ced4da;
                        }
                    """)
                
                btn.clicked.connect(lambda checked, t=text: self.button_click(t))
                layout.addWidget(btn, i, j)
        
        self.buttons_widget.addWidget(widget)
    
    def create_scientific_mode(self):
        """Criar interface do modo científico"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(2)
        
        # Botões científicos
        scientific_buttons = [
            ['sin', 'cos', 'tan', 'π', 'e'],
            ['asin', 'acos', 'atan', 'log', 'ln'],
            ['sinh', 'cosh', 'tanh', '√', '∛'],
            ['x²', 'x³', 'x^y', '10^x', 'e^x'],
            ['(', ')', 'mod', '!', '1/x'],
            ['C', '⌫', '%', '/', '*'],
            ['7', '8', '9', '-', '+'],
            ['4', '5', '6', '×10^', '='],
            ['1', '2', '3', 'ANS', 'EXP'],
            ['±', '0', '.', '(', ')']
        ]
        
        for i, row in enumerate(scientific_buttons):
            for j, text in enumerate(row):
                if text:
                    btn = QPushButton(text)
                    btn.setMinimumHeight(40)
                    btn.setMinimumWidth(50)
                    
                    # Estilo baseado no tipo de botão
                    if text in ['sin', 'cos', 'tan', 'log', 'ln', '√', 'π', 'e']:
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: #17a2b8;
                                color: white;
                                font-weight: bold;
                                font-size: 12px;
                                border: none;
                                border-radius: 3px;
                            }
                            QPushButton:hover {
                                background-color: #138496;
                            }
                        """)
                    elif text in ['C', '⌫']:
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: #dc3545;
                                color: white;
                                font-weight: bold;
                                font-size: 12px;
                                border: none;
                                border-radius: 3px;
                            }
                            QPushButton:hover {
                                background-color: #c82333;
                            }
                        """)
                    elif text == '=':
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: #28a745;
                                color: white;
                                font-weight: bold;
                                font-size: 16px;
                                border: none;
                                border-radius: 3px;
                            }
                            QPushButton:hover {
                                background-color: #218838;
                            }
                        """)
                    else:
                        btn.setStyleSheet("""
                            QPushButton {
                                background-color: #e9ecef;
                                color: black;
                                font-weight: bold;
                                font-size: 14px;
                                border: none;
                                border-radius: 3px;
                            }
                            QPushButton:hover {
                                background-color: #dee2e6;
                            }
                        """)
                    
                    btn.clicked.connect(lambda checked, t=text: self.button_click(t))
                    layout.addWidget(btn, i, j)
        
        self.buttons_widget.addWidget(widget)
    
    def create_programmer_mode(self):
        """Criar interface do modo programador"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Display para representação binária
        self.binary_display = QLineEdit()
        self.binary_display.setReadOnly(True)
        self.binary_display.setAlignment(Qt.AlignLeft)
        self.binary_display.setPlaceholderText("Representação binária")
        self.binary_display.setStyleSheet("""
            QLineEdit {
                font-family: 'Courier New';
                font-size: 14px;
                background-color: #2d2d2d;
                color: #00ff00;
                border: 1px solid #555;
                padding: 8px;
            }
        """)
        layout.addWidget(self.binary_display)
        
        # Display para outras bases
        bases_widget = QWidget()
        bases_layout = QGridLayout(bases_widget)
        
        self.hex_display = QLineEdit()
        self.hex_display.setReadOnly(True)
        self.hex_display.setPlaceholderText("HEX")
        bases_layout.addWidget(QLabel("HEX:"), 0, 0)
        bases_layout.addWidget(self.hex_display, 0, 1)
        
        self.dec_display = QLineEdit()
        self.dec_display.setReadOnly(True)
        self.dec_display.setPlaceholderText("DEC")
        bases_layout.addWidget(QLabel("DEC:"), 1, 0)
        bases_layout.addWidget(self.dec_display, 1, 1)
        
        self.oct_display = QLineEdit()
        self.oct_display.setReadOnly(True)
        self.oct_display.setPlaceholderText("OCT")
        bases_layout.addWidget(QLabel("OCT:"), 2, 0)
        bases_layout.addWidget(self.oct_display, 2, 1)
        
        self.bin_display = QLineEdit()
        self.bin_display.setReadOnly(True)
        self.bin_display.setPlaceholderText("BIN")
        bases_layout.addWidget(QLabel("BIN:"), 3, 0)
        bases_layout.addWidget(self.bin_display, 3, 1)
        
        layout.addWidget(bases_widget)
        
        # Botões do modo programador
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setSpacing(2)
        
        # Operações lógicas
        logic_ops = ['AND', 'OR', 'XOR', 'NOT', '<<', '>>']
        for i, op in enumerate(logic_ops):
            btn = QPushButton(op)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #6f42c1;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #5e34a9;
                }
            """)
            btn.clicked.connect(lambda checked, t=op: self.button_click(t))
            buttons_layout.addWidget(btn, 0, i)
        
        # Botões numéricos
        num_buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['A', 'B', 'C', 'D'],
            ['E', 'F', '0', '=']
        ]
        
        for i, row in enumerate(num_buttons, start=1):
            for j, text in enumerate(row):
                btn = QPushButton(text)
                btn.setMinimumHeight(45)
                
                if text in ['A', 'B', 'C', 'D', 'E', 'F']:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #fd7e14;
                            color: white;
                            font-weight: bold;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #e46a0b;
                        }
                    """)
                elif text == '=':
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #28a745;
                            color: white;
                            font-weight: bold;
                            font-size: 16px;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #218838;
                        }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e9ecef;
                            color: black;
                            font-weight: bold;
                            font-size: 14px;
                            border: none;
                            border-radius: 3px;
                        }
                        QPushButton:hover {
                            background-color: #dee2e6;
                        }
                    """)
                
                btn.clicked.connect(lambda checked, t=text: self.button_click(t))
                buttons_layout.addWidget(btn, i, j)
        
        layout.addWidget(buttons_widget)
        self.buttons_widget.addWidget(widget)
    
    def apply_style(self):
        """Aplicar estilo visual"""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        QPushButton {
            font-size: 14px;
            border: none;
            border-radius: 3px;
            padding: 8px;
        }
        QPushButton:pressed {
            background-color: #adb5bd;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            font-family: 'Courier New';
            font-size: 12px;
        }
        QListWidget::item {
            padding: 5px;
            border-bottom: 1px solid #e9ecef;
        }
        QListWidget::item:selected {
            background-color: #007bff;
            color: white;
        }
        QSplitter::handle {
            background-color: #dee2e6;
            width: 2px;
        }
        QMenuBar {
            background-color: #343a40;
            color: white;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 5px 10px;
        }
        QMenuBar::item:selected {
            background-color: #007bff;
        }
        QMenu {
            background-color: white;
            border: 1px solid #dee2e6;
        }
        QMenu::item {
            padding: 5px 20px;
        }
        QMenu::item:selected {
            background-color: #007bff;
            color: white;
        }
        QToolBar {
            background-color: #343a40;
            color: white;
            spacing: 10px;
            padding: 5px;
        }
        QToolBar QLabel {
            color: white;
            font-weight: bold;
        }
        """
        self.setStyleSheet(style)
    
    def change_mode(self, mode):
        """Mudar o modo da calculadora"""
        self.current_mode = mode
        self.mode_label.setText(f"📱 Modo: {mode}")
        
        # Atualizar widgets visíveis
        if mode == "Padrão":
            self.buttons_widget.setCurrentIndex(0)
            self.angle_label.hide()
            self.base_label.hide()
        elif mode == "Científica":
            self.buttons_widget.setCurrentIndex(1)
            self.angle_label.show()
            self.base_label.hide()
        elif mode == "Programador":
            self.buttons_widget.setCurrentIndex(2)
            self.angle_label.hide()
            self.base_label.show()
    
    def set_angle_unit(self, unit):
        """Definir unidade angular"""
        self.angle_unit = unit
        self.angle_label.setText(f"📐 {unit}")
    
    def set_number_base(self, base):
        """Definir base numérica"""
        self.number_base = base
        base_names = {10: "DEC", 16: "HEX", 8: "OCT", 2: "BIN"}
        self.base_label.setText(f"🔢 {base_names[base]}")
        self.update_base_displays()
    
    def set_word_size(self, bits):
        """Definir tamanho da palavra (bits)"""
        self.word_size = bits
        self.statusBar().showMessage(f"Tamanho da palavra: {bits} bits", 2000)
    
    def button_click(self, value):
        """Processar clique em botão"""
        if value == 'C':
            self.clear_all()
        elif value == '⌫':
            self.backspace()
        elif value == '=':
            self.calculate()
        elif value == '±':
            self.negate()
        elif value == 'ANS':
            self.current_expression += str(self.last_result)
            self.update_displays()
        elif value in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 
                       'sinh', 'cosh', 'tanh', 'log', 'ln', '√', '∛',
                       'x²', 'x³', 'x^y', '10^x', 'e^x', '!', '1/x',
                       'π', 'e', 'mod', '×10^', 'EXP']:
            self.handle_scientific_function(value)
        elif value in ['AND', 'OR', 'XOR', 'NOT', '<<', '>>']:
            self.handle_logic_operation(value)
        elif value in ['A', 'B', 'C', 'D', 'E', 'F']:
            if self.current_mode == "Programador":
                self.current_expression += value
                self.update_displays()
        else:
            self.current_expression += str(value)
            self.update_displays()
    
    def handle_scientific_function(self, func):
        """Processar funções científicas"""
        if func == 'π':
            self.current_expression += str(math.pi)
        elif func == 'e':
            self.current_expression += str(math.e)
        elif func == '√':
            self.current_expression += 'sqrt('
        elif func == '∛':
            self.current_expression += 'cbrt('
        elif func == 'x²':
            self.current_expression += '^2'
        elif func == 'x³':
            self.current_expression += '^3'
        elif func == 'x^y':
            self.current_expression += '^'
        elif func == '10^x':
            self.current_expression += '10^'
        elif func == 'e^x':
            self.current_expression += 'exp('
        elif func == 'log':
            self.current_expression += 'log('
        elif func == 'ln':
            self.current_expression += 'ln('
        elif func == 'sin':
            self.current_expression += 'sin('
        elif func == 'cos':
            self.current_expression += 'cos('
        elif func == 'tan':
            self.current_expression += 'tan('
        elif func == 'asin':
            self.current_expression += 'asin('
        elif func == 'acos':
            self.current_expression += 'acos('
        elif func == 'atan':
            self.current_expression += 'atan('
        elif func == 'sinh':
            self.current_expression += 'sinh('
        elif func == 'cosh':
            self.current_expression += 'cosh('
        elif func == 'tanh':
            self.current_expression += 'tanh('
        elif func == '!':
            self.current_expression += '!'
        elif func == '1/x':
            self.current_expression = f"1/({self.current_expression})" if self.current_expression else "1/("
        elif func == 'mod':
            self.current_expression += '%'
        elif func == '×10^':
            self.current_expression += 'e'
        elif func == 'EXP':
            self.current_expression += 'e'
        
        self.update_displays()
    
    def handle_logic_operation(self, op):
        """Processar operações lógicas (modo programador)"""
        self.current_expression += f" {op} "
        self.update_displays()
    
    def calculate(self):
        """Calcular a expressão atual"""
        try:
            if not self.current_expression:
                return
            
            expression = self.current_expression
            
            # Substituir operadores
            expression = expression.replace('^', '**')
            expression = expression.replace('×', '*')
            expression = expression.replace('÷', '/')
            expression = expression.replace('√', 'sqrt')
            expression = expression.replace('∛', 'cbrt')
            
            # Processar funções trigonométricas com conversão de unidades
            if self.angle_unit != "RAD":
                # Converter graus/grados para radianos para funções trigonométricas
                import re
                
                def convert_angle(match):
                    func = match.group(1)
                    angle = float(match.group(2))
                    if self.angle_unit == "DEG":
                        angle = math.radians(angle)
                    elif self.angle_unit == "GRAD":
                        angle = angle * math.pi / 200
                    return f"{func}({angle})"
                
                # Aplicar conversão para funções trigonométricas
                for trig_func in ['sin', 'cos', 'tan']:
                    pattern = rf'{trig_func}\(([^)]+)\)'
                    expression = re.sub(pattern, convert_angle, expression)
            
            # Avaliar expressão com segurança
            # Usar um dicionário de funções matemáticas seguras
            safe_dict = {
                'sqrt': math.sqrt,
                'cbrt': lambda x: x**(1/3),
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'sinh': math.sinh,
                'cosh': math.cosh,
                'tanh': math.tanh,
                'log': math.log10,
                'ln': math.log,
                'exp': math.exp,
                'factorial': math.factorial,
                'pi': math.pi,
                'e': math.e,
                'abs': abs,
                'round': round,
                'int': int,
                'float': float
            }
            
            # Avaliar
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            # Arredondar para evitar problemas de precisão
            if isinstance(result, float):
                result = round(result, 10)
            
            # Adicionar ao histórico
            self.add_to_history(self.current_expression, result)
            
            # Atualizar displays
            self.display.setText(str(result))
            self.last_result = result
            self.current_expression = str(result)
            self.expression_display.setText("")
            
            # Atualizar displays do modo programador
            if self.current_mode == "Programador":
                self.update_programmer_displays(result)
            
        except Exception as e:
            self.display.setText("Erro")
            self.statusBar().showMessage(f"Erro: {str(e)}", 3000)
    
    def add_to_history(self, expression, result):
        """Adicionar entrada ao histórico"""
        entry = HistoryEntry(expression, result, self.current_mode)
        self.history.append(entry)
        
        # Adicionar à lista visual
        item_text = f"{entry.timestamp}\n{expression} = {result}\n"
        self.history_list.addItem(item_text)
        self.history_list.scrollToBottom()
    
    def history_item_clicked(self, item):
        """Clicar em item do histórico"""
        # Extrair resultado do item
        text = item.text()
        lines = text.split('\n')
        if len(lines) >= 2:
            result_part = lines[1].split('=')[-1].strip()
            try:
                result = float(result_part)
                self.display.setText(str(result))
                self.last_result = result
                self.current_expression = str(result)
            except:
                pass
    
    def copy_history_item(self):
        """Copiar item selecionado do histórico"""
        current_item = self.history_list.currentItem()
        if current_item:
            clipboard = QApplication.clipboard()
            clipboard.setText(current_item.text())
            self.statusBar().showMessage("Item copiado para área de transferência", 2000)
    
    def clear_history(self):
        """Limpar histórico"""
        reply = QMessageBox.question(self, "Limpar Histórico", 
                                     "Tem certeza que deseja limpar todo o histórico?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.history.clear()
            self.history_list.clear()
            self.statusBar().showMessage("Histórico limpo", 2000)
    
    def clear_all(self):
        """Limpar tudo"""
        self.current_expression = ""
        self.display.clear()
        self.expression_display.clear()
        if self.current_mode == "Programador":
            self.binary_display.clear()
            self.hex_display.clear()
            self.dec_display.clear()
            self.oct_display.clear()
            self.bin_display.clear()
    
    def backspace(self):
        """Apagar último caractere"""
        self.current_expression = self.current_expression[:-1]
        self.update_displays()
    
    def negate(self):
        """Inverter sinal"""
        if self.current_expression:
            try:
                value = float(self.current_expression)
                self.current_expression = str(-value)
                self.update_displays()
            except:
                pass
    
    def update_displays(self):
        """Atualizar displays"""
        self.expression_display.setText(self.current_expression)
        if self.current_expression:
            try:
                # Tentar avaliar para mostrar resultado parcial
                result = eval(self.current_expression.replace('^', '**'))
                if isinstance(result, (int, float)):
                    self.display.setText(str(result))
            except:
                pass
    
    def update_base_displays(self):
        """Atualizar displays de bases (modo programador)"""
        if self.current_mode == "Programador" and self.current_expression:
            try:
                # Tentar converter valor atual para diferentes bases
                value = int(float(self.current_expression))
                
                # Aplicar máscara de bits
                mask = (1 << self.word_size) - 1
                value = value & mask
                
                # Atualizar displays
                self.hex_display.setText(hex(value)[2:].upper())
                self.dec_display.setText(str(value))
                self.oct_display.setText(oct(value)[2:])
                self.bin_display.setText(bin(value)[2:])
                
                # Display binário formatado
                bin_str = bin(value)[2:].zfill(self.word_size)
                formatted_bin = ' '.join([bin_str[i:i+4] for i in range(0, len(bin_str), 4)])
                self.binary_display.setText(formatted_bin)
                
            except:
                pass
    
    def update_programmer_displays(self, value):
        """Atualizar displays do modo programador"""
        try:
            int_value = int(float(value))
            
            # Aplicar máscara de bits
            mask = (1 << self.word_size) - 1
            int_value = int_value & mask
            
            # Atualizar displays
            self.hex_display.setText(hex(int_value)[2:].upper())
            self.dec_display.setText(str(int_value))
            self.oct_display.setText(oct(int_value)[2:])
            self.bin_display.setText(bin(int_value)[2:])
            
            # Display binário formatado
            bin_str = bin(int_value)[2:].zfill(self.word_size)
            formatted_bin = ' '.join([bin_str[i:i+4] for i in range(0, len(bin_str), 4)])
            self.binary_display.setText(formatted_bin)
            
        except:
            pass
    
    def export_history(self):
        """Exportar histórico para JSON"""
        if not self.history:
            QMessageBox.warning(self, "Exportar", "Não há histórico para exportar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Histórico", "",
            "Arquivos JSON (*.json);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            try:
                data = {
                    'export_date': datetime.now().isoformat(),
                    'mode': self.current_mode,
                    'history': [entry.to_dict() for entry in self.history]
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                self.statusBar().showMessage(f"Histórico exportado para {file_path}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar: {str(e)}")
    
    def import_history(self):
        """Importar histórico de JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar Histórico", "",
            "Arquivos JSON (*.json);;Todos os Arquivos (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Limpar histórico atual
                self.history.clear()
                self.history_list.clear()
                
                # Importar novos dados
                for entry_data in data['history']:
                    entry = HistoryEntry.from_dict(entry_data)
                    self.history.append(entry)
                    
                    item_text = f"{entry.timestamp}\n{entry.expression} = {entry.result}\n"
                    self.history_list.addItem(item_text)
                
                self.statusBar().showMessage(f"Histórico importado de {file_path}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar: {str(e)}")
    
    def show_about(self):
        """Mostrar diálogo sobre"""
        about_text = """
        <h2>Calculadora Multi-Modo</h2>
        <p><b>Versão:</b> 1.0.0</p>
        
        <h3>Modos disponíveis:</h3>
        <ul>
            <li><b>Padrão:</b> Operações básicas</li>
            <li><b>Científica:</b> Funções trigonométricas, logaritmos, etc.</li>
            <li><b>Programador:</b> Operações lógicas, diferentes bases numéricas</li>
        </ul>
        
        <h3>Funcionalidades:</h3>
        <ul>
            <li>Histórico de cálculos</li>
            <li>Exportar/Importar histórico em JSON</li>
            <li>Conversão entre bases (modo programador)</li>
            <li>Unidades angulares (DEG, RAD, GRAD)</li>
        </ul>
        
        <h3>Desenvolvido com auxílio do DeepSeek</h3>
        <p>Όχι, ο Χρόνος δεν είναι ο άρχοντας της γνώσης</p>
        """
        
        QMessageBox.about(self, "Sobre a Calculadora", about_text)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Calculadora Multi-Modo")
    
    calculator = Calculator()
    calculator.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
