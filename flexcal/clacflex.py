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
    def __init__(self, expression, result, mode, timestamp=None, category="normal"):
        self.expression = expression
        self.result = result
        self.mode = mode
        self.category = category
        self.timestamp = timestamp or datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    def to_dict(self):
        return {
            'expression': self.expression,
            'result': self.result,
            'mode': self.mode,
            'category': self.category,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['expression'], data['result'], data['mode'], 
                   data['timestamp'], data.get('category', 'normal'))

class FunctionPlotter(QMainWindow):
    """Janela para plotar funções (versão simplificada sem matplotlib)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculadora de Funções")
        self.setGeometry(200, 200, 500, 400)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Instruções
        instructions = QLabel(
            "Esta calculadora avalia funções em pontos específicos.\n"
            "Use as funções: sin, cos, tan, log, exp, sqrt"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #e9ecef; padding: 10px; border-radius: 5px;")
        layout.addWidget(instructions)
        
        # Entrada da função
        func_layout = QHBoxLayout()
        func_layout.addWidget(QLabel("f(x) ="))
        self.function_input = QLineEdit()
        self.function_input.setPlaceholderText("Ex: sin(x) + cos(x)")
        func_layout.addWidget(self.function_input)
        layout.addLayout(func_layout)
        
        # Entrada do valor de x
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("x ="))
        self.x_value = QLineEdit()
        self.x_value.setPlaceholderText("Digite o valor de x")
        x_layout.addWidget(self.x_value)
        
        btn_calc = QPushButton("Calcular")
        btn_calc.clicked.connect(self.calculate_point)
        x_layout.addWidget(btn_calc)
        layout.addLayout(x_layout)
        
        # Resultado
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #28a745;
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                min-height: 50px;
            }
        """)
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
        # Tabela de valores
        table_group = QGroupBox("Tabela de Valores")
        table_layout = QVBoxLayout()
        
        # Controles para tabela
        table_controls = QHBoxLayout()
        table_controls.addWidget(QLabel("De:"))
        self.start_value = QLineEdit("-5")
        self.start_value.setMaximumWidth(60)
        table_controls.addWidget(self.start_value)
        
        table_controls.addWidget(QLabel("Até:"))
        self.end_value = QLineEdit("5")
        self.end_value.setMaximumWidth(60)
        table_controls.addWidget(self.end_value)
        
        table_controls.addWidget(QLabel("Passo:"))
        self.step_value = QLineEdit("1")
        self.step_value.setMaximumWidth(60)
        table_controls.addWidget(self.step_value)
        
        btn_table = QPushButton("Gerar Tabela")
        btn_table.clicked.connect(self.generate_table)
        table_controls.addWidget(btn_table)
        
        table_layout.addLayout(table_controls)
        
        # Tabela
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["x", "f(x)"])
        table_layout.addWidget(self.table_widget)
        
        table_group.setLayout(table_layout)
        layout.addWidget(table_group)
    
    def calculate_point(self):
        """Calcular função em um ponto"""
        try:
            func_str = self.function_input.text()
            x = float(self.x_value.text())
            
            if not func_str:
                QMessageBox.warning(self, "Aviso", "Digite uma função!")
                return
            
            # Avaliar função
            result = self.evaluate_function(func_str, x)
            self.result_label.setText(f"f({x}) = {result:.6f}")
            
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor válido para x!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao calcular: {str(e)}")
    
    def generate_table(self):
        """Gerar tabela de valores"""
        try:
            func_str = self.function_input.text()
            start = float(self.start_value.text())
            end = float(self.end_value.text())
            step = float(self.step_value.text())
            
            if not func_str:
                QMessageBox.warning(self, "Aviso", "Digite uma função!")
                return
            
            if step <= 0:
                QMessageBox.warning(self, "Aviso", "O passo deve ser positivo!")
                return
            
            # Gerar valores
            x_values = []
            y_values = []
            x = start
            while x <= end:
                try:
                    y = self.evaluate_function(func_str, x)
                    x_values.append(x)
                    y_values.append(y)
                except:
                    y_values.append("Erro")
                x += step
            
            # Atualizar tabela
            self.table_widget.setRowCount(len(x_values))
            for i, (x, y) in enumerate(zip(x_values, y_values)):
                self.table_widget.setItem(i, 0, QTableWidgetItem(f"{x:.3f}"))
                self.table_widget.setItem(i, 1, QTableWidgetItem(f"{y:.6f}" if isinstance(y, float) else y))
            
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite valores válidos para os intervalos!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar tabela: {str(e)}")
    
    def evaluate_function(self, func_str, x):
        """Avaliar função com segurança"""
        # Dicionário de funções seguras
        safe_dict = {
            'x': x,
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan,
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'exp': math.exp, 'log': math.log, 'log10': math.log10,
            'sqrt': math.sqrt, 'abs': abs,
            'pi': math.pi, 'e': math.e
        }
        
        # Substituir operadores
        expr = func_str.replace('^', '**')
        
        return eval(expr, {"__builtins__": {}}, safe_dict)

class UnitConverter(QDialog):
    """Conversor de unidades"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conversor de Unidades")
        self.setGeometry(300, 300, 500, 400)
        
        layout = QVBoxLayout()
        
        # Categorias de unidades
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Comprimento", "Massa", "Temperatura", "Área", 
            "Volume", "Velocidade", "Tempo", "Energia"
        ])
        self.category_combo.currentTextChanged.connect(self.update_units)
        layout.addWidget(self.category_combo)
        
        # Unidades de origem e destino
        units_layout = QHBoxLayout()
        
        self.from_combo = QComboBox()
        self.to_combo = QComboBox()
        
        units_layout.addWidget(QLabel("De:"))
        units_layout.addWidget(self.from_combo)
        units_layout.addWidget(QLabel("Para:"))
        units_layout.addWidget(self.to_combo)
        
        layout.addLayout(units_layout)
        
        # Valor de entrada
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Valor:"))
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Digite o valor...")
        input_layout.addWidget(self.value_input)
        layout.addLayout(input_layout)
        
        # Botão converter
        btn_convert = QPushButton("Converter")
        btn_convert.clicked.connect(self.convert)
        layout.addWidget(btn_convert)
        
        # Resultado
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #28a745;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                min-height: 50px;
            }
        """)
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)
        
        self.setLayout(layout)
        self.update_units("Comprimento")
    
    def update_units(self, category):
        """Atualizar lista de unidades baseado na categoria"""
        self.from_combo.clear()
        self.to_combo.clear()
        
        units = self.get_units_for_category(category)
        self.from_combo.addItems(units)
        self.to_combo.addItems(units)
    
    def get_units_for_category(self, category):
        """Obter unidades para uma categoria"""
        units_dict = {
            "Comprimento": ["Metro", "Quilômetro", "Centímetro", "Milímetro", 
                           "Polegada", "Pé", "Jarda", "Milha"],
            "Massa": ["Quilograma", "Grama", "Miligrama", "Tonelada", 
                     "Libra", "Onça"],
            "Temperatura": ["Celsius", "Fahrenheit", "Kelvin"],
            "Área": ["Metro²", "Quilômetro²", "Centímetro²", "Hectare", "Acre"],
            "Volume": ["Metro³", "Litro", "Mililitro", "Galão"],
            "Velocidade": ["m/s", "km/h", "mph", "nó"],
            "Tempo": ["Segundo", "Minuto", "Hora", "Dia"],
            "Energia": ["Joule", "Caloria", "Quilocaloria", "BTU", "kWh"]
        }
        return units_dict.get(category, [])
    
    def convert(self):
        """Realizar conversão"""
        try:
            value = float(self.value_input.text())
            from_unit = self.from_combo.currentText()
            to_unit = self.to_combo.currentText()
            category = self.category_combo.currentText()
            
            # Converter
            result = self.convert_unit(value, from_unit, to_unit, category)
            
            self.result_label.setText(f"{value} {from_unit} = {result:.6g} {to_unit}")
            
        except ValueError:
            QMessageBox.warning(self, "Erro", "Digite um valor válido!")
    
    def convert_unit(self, value, from_unit, to_unit, category):
        """Converter entre unidades"""
        # Fatores de conversão para unidade base (SI)
        base_factors = {
            "Comprimento": {
                "Metro": 1, "Quilômetro": 1000, "Centímetro": 0.01, "Milímetro": 0.001,
                "Polegada": 0.0254, "Pé": 0.3048, "Jarda": 0.9144, "Milha": 1609.344
            },
            "Massa": {
                "Quilograma": 1, "Grama": 0.001, "Miligrama": 0.000001, "Tonelada": 1000,
                "Libra": 0.453592, "Onça": 0.0283495
            },
            "Temperatura": {
                "Celsius": lambda v: v,
                "Fahrenheit": lambda v: (v - 32) * 5/9,
                "Kelvin": lambda v: v - 273.15
            },
            "Área": {
                "Metro²": 1, "Quilômetro²": 1e6, "Centímetro²": 0.0001,
                "Hectare": 10000, "Acre": 4046.86
            },
            "Volume": {
                "Metro³": 1, "Litro": 0.001, "Mililitro": 0.000001, "Galão": 0.00378541
            },
            "Velocidade": {
                "m/s": 1, "km/h": 0.277778, "mph": 0.44704, "nó": 0.514444
            },
            "Tempo": {
                "Segundo": 1, "Minuto": 60, "Hora": 3600, "Dia": 86400
            },
            "Energia": {
                "Joule": 1, "Caloria": 4.184, "Quilocaloria": 4184, "BTU": 1055.06, "kWh": 3.6e6
            }
        }
        
        # Fatores de conversão da unidade base para a unidade destino
        to_factors = {
            "Comprimento": {
                "Metro": 1, "Quilômetro": 0.001, "Centímetro": 100, "Milímetro": 1000,
                "Polegada": 39.3701, "Pé": 3.28084, "Jarda": 1.09361, "Milha": 0.000621371
            },
            "Massa": {
                "Quilograma": 1, "Grama": 1000, "Miligrama": 1e6, "Tonelada": 0.001,
                "Libra": 2.20462, "Onça": 35.274
            },
            "Temperatura": {
                "Celsius": lambda v: v,
                "Fahrenheit": lambda v: v * 9/5 + 32,
                "Kelvin": lambda v: v + 273.15
            },
            "Área": {
                "Metro²": 1, "Quilômetro²": 1e-6, "Centímetro²": 10000,
                "Hectare": 0.0001, "Acre": 0.000247105
            },
            "Volume": {
                "Metro³": 1, "Litro": 1000, "Mililitro": 1e6, "Galão": 264.172
            },
            "Velocidade": {
                "m/s": 1, "km/h": 3.6, "mph": 2.23694, "nó": 1.94384
            },
            "Tempo": {
                "Segundo": 1, "Minuto": 1/60, "Hora": 1/3600, "Dia": 1/86400
            },
            "Energia": {
                "Joule": 1, "Caloria": 1/4.184, "Quilocaloria": 1/4184,
                "BTU": 1/1055.06, "kWh": 1/3.6e6
            }
        }
        
        if category == "Temperatura":
            # Temperatura usa funções especiais
            base_value = base_factors[category][from_unit](value)
            return to_factors[category][to_unit](base_value)
        else:
            # Converter para unidade base e depois para destino
            base_value = value * base_factors[category][from_unit]
            return base_value * to_factors[category][to_unit]

class StatisticsCalculator(QDialog):
    """Calculadora estatística simples"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculadora Estatística")
        self.setGeometry(200, 200, 500, 500)
        
        layout = QVBoxLayout()
        
        # Entrada de dados
        input_group = QGroupBox("Dados")
        input_layout = QVBoxLayout()
        
        input_layout.addWidget(QLabel("Digite os números (separados por vírgula):"))
        self.data_input = QTextEdit()
        self.data_input.setPlaceholderText("Ex: 10, 20, 30, 40, 50")
        self.data_input.setMaximumHeight(80)
        input_layout.addWidget(self.data_input)
        
        btn_calc = QPushButton("Calcular Estatísticas")
        btn_calc.clicked.connect(self.calculate_stats)
        input_layout.addWidget(btn_calc)
        
        input_group.setLayout(input_layout)
        layout.addWidget(input_group)
        
        # Resultados
        results_group = QGroupBox("Resultados")
        results_layout = QGridLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(200)
        results_layout.addWidget(self.results_text, 0, 0, 1, 2)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Gráfico simples com texto
        viz_group = QGroupBox("Visualização (Distribuição)")
        viz_layout = QVBoxLayout()
        
        self.viz_text = QTextEdit()
        self.viz_text.setReadOnly(True)
        self.viz_text.setMaximumHeight(150)
        self.viz_text.setFont(QFont("Courier New", 10))
        viz_layout.addWidget(self.viz_text)
        
        viz_group.setLayout(viz_layout)
        layout.addWidget(viz_group)
        
        self.setLayout(layout)
    
    def calculate_stats(self):
        """Calcular estatísticas"""
        try:
            # Processar dados
            text = self.data_input.toPlainText()
            numbers = [float(x.strip()) for x in text.split(',') if x.strip()]
            
            if len(numbers) == 0:
                QMessageBox.warning(self, "Aviso", "Digite alguns números!")
                return
            
            n = len(numbers)
            soma = sum(numbers)
            media = soma / n
            variancia = sum((x - media) ** 2 for x in numbers) / n
            desvio = math.sqrt(variancia)
            
            # Ordenar para mediana e quartis
            sorted_numbers = sorted(numbers)
            mediana = sorted_numbers[n // 2] if n % 2 else (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2
            
            # Moda
            from collections import Counter
            freq = Counter(numbers)
            max_freq = max(freq.values())
            moda = [k for k, v in freq.items() if v == max_freq]
            
            # Resultado
            result_text = f"""
            📊 Estatísticas Descritivas:
            
            Número de elementos: {n}
            Soma: {soma:.4f}
            Média: {media:.4f}
            Mediana: {mediana:.4f}
            Moda: {', '.join(f'{x:.4f}' for x in moda)}
            Variância: {variancia:.4f}
            Desvio Padrão: {desvio:.4f}
            Mínimo: {min(numbers):.4f}
            Máximo: {max(numbers):.4f}
            Amplitude: {max(numbers) - min(numbers):.4f}
            
            Quartis:
            Q1 (25%): {sorted_numbers[n // 4]:.4f}
            Q2 (50%): {mediana:.4f}
            Q3 (75%): {sorted_numbers[3 * n // 4]:.4f}
            """
            
            self.results_text.setText(result_text)
            
            # Gerar visualização simples
            self.generate_simple_viz(numbers)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro nos cálculos: {str(e)}")
    
    def generate_simple_viz(self, numbers):
        """Gerar visualização simples com caracteres"""
        # Criar histograma simples
        min_val = min(numbers)
        max_val = max(numbers)
        range_val = max_val - min_val
        
        if range_val == 0:
            self.viz_text.setText("Todos os valores são iguais")
            return
        
        # Criar 10 bins
        bins = 10
        bin_size = range_val / bins
        
        # Contar frequências
        freq = [0] * bins
        for x in numbers:
            bin_index = min(int((x - min_val) / bin_size), bins - 1)
            freq[bin_index] += 1
        
        # Escalar para máximo 20 caracteres
        max_freq = max(freq)
        scale = 20 / max_freq if max_freq > 0 else 1
        
        # Gerar visualização
        viz = "Distribuição dos dados:\n\n"
        for i in range(bins):
            start = min_val + i * bin_size
            end = min_val + (i + 1) * bin_size
            bar_length = int(freq[i] * scale)
            bar = "█" * bar_length
            viz += f"[{start:6.2f} - {end:6.2f}] |{bar:<20} {freq[i]}\n"
        
        self.viz_text.setText(viz)

class MatrixCalculator(QDialog):
    """Calculadora de matrizes simples"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculadora de Matrizes")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        # Tabs para diferentes operações
        tabs = QTabWidget()
        
        # Tab Soma
        sum_tab = self.create_sum_tab()
        tabs.addTab(sum_tab, "Soma/Subtração")
        
        # Tab Multiplicação
        mult_tab = self.create_mult_tab()
        tabs.addTab(mult_tab, "Multiplicação")
        
        # Tab Determinante
        det_tab = self.create_det_tab()
        tabs.addTab(det_tab, "Determinante")
        
        layout.addWidget(tabs)
        self.setLayout(layout)
    
    def create_sum_tab(self):
        """Criar tab de soma/subtração"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tamanho da matriz
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Tamanho:"))
        self.sum_size = QSpinBox()
        self.sum_size.setRange(1, 4)
        self.sum_size.setValue(2)
        self.sum_size.valueChanged.connect(lambda: self.update_matrix_size(self.sum_a, self.sum_size.value()))
        size_layout.addWidget(self.sum_size)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Matrizes A e B
        matrices_layout = QHBoxLayout()
        
        # Matriz A
        a_group = QGroupBox("Matriz A")
        a_layout = QVBoxLayout()
        self.sum_a = QTableWidget(2, 2)
        a_layout.addWidget(self.sum_a)
        a_group.setLayout(a_layout)
        matrices_layout.addWidget(a_group)
        
        # Matriz B
        b_group = QGroupBox("Matriz B")
        b_layout = QVBoxLayout()
        self.sum_b = QTableWidget(2, 2)
        b_layout.addWidget(self.sum_b)
        b_group.setLayout(b_layout)
        matrices_layout.addWidget(b_group)
        
        layout.addLayout(matrices_layout)
        
        # Operação
        op_layout = QHBoxLayout()
        self.sum_op = QComboBox()
        self.sum_op.addItems(["A + B", "A - B", "B - A"])
        op_layout.addWidget(self.sum_op)
        
        btn_calc = QPushButton("Calcular")
        btn_calc.clicked.connect(self.calculate_sum)
        op_layout.addWidget(btn_calc)
        layout.addLayout(op_layout)
        
        # Resultado
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        self.sum_result = QTableWidget()
        result_layout.addWidget(self.sum_result)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_mult_tab(self):
        """Criar tab de multiplicação"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tamanhos
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Linhas A:"))
        self.mult_rows_a = QSpinBox()
        self.mult_rows_a.setRange(1, 4)
        self.mult_rows_a.setValue(2)
        self.mult_rows_a.valueChanged.connect(self.update_mult_matrices)
        size_layout.addWidget(self.mult_rows_a)
        
        size_layout.addWidget(QLabel("Colunas A:"))
        self.mult_cols_a = QSpinBox()
        self.mult_cols_a.setRange(1, 4)
        self.mult_cols_a.setValue(3)
        self.mult_cols_a.valueChanged.connect(self.update_mult_matrices)
        size_layout.addWidget(self.mult_cols_a)
        
        size_layout.addWidget(QLabel("Linhas B:"))
        self.mult_rows_b = QSpinBox()
        self.mult_rows_b.setRange(1, 4)
        self.mult_rows_b.setValue(3)
        self.mult_rows_b.valueChanged.connect(self.update_mult_matrices)
        size_layout.addWidget(self.mult_rows_b)
        
        size_layout.addWidget(QLabel("Colunas B:"))
        self.mult_cols_b = QSpinBox()
        self.mult_cols_b.setRange(1, 4)
        self.mult_cols_b.setValue(2)
        self.mult_cols_b.valueChanged.connect(self.update_mult_matrices)
        size_layout.addWidget(self.mult_cols_b)
        
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Matrizes A e B
        matrices_layout = QHBoxLayout()
        
        # Matriz A
        a_group = QGroupBox("Matriz A")
        a_layout = QVBoxLayout()
        self.mult_a = QTableWidget(2, 3)
        a_layout.addWidget(self.mult_a)
        a_group.setLayout(a_layout)
        matrices_layout.addWidget(a_group)
        
        # Matriz B
        b_group = QGroupBox("Matriz B")
        b_layout = QVBoxLayout()
        self.mult_b = QTableWidget(3, 2)
        b_layout.addWidget(self.mult_b)
        b_group.setLayout(b_layout)
        matrices_layout.addWidget(b_group)
        
        layout.addLayout(matrices_layout)
        
        # Botão calcular
        btn_calc = QPushButton("Calcular A × B")
        btn_calc.clicked.connect(self.calculate_mult)
        layout.addWidget(btn_calc)
        
        # Resultado
        result_group = QGroupBox("Resultado")
        result_layout = QVBoxLayout()
        self.mult_result = QTableWidget()
        result_layout.addWidget(self.mult_result)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        
        widget.setLayout(layout)
        return widget
    
    def create_det_tab(self):
        """Criar tab de determinante"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tamanho da matriz
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Ordem:"))
        self.det_size = QSpinBox()
        self.det_size.setRange(1, 4)
        self.det_size.setValue(2)
        self.det_size.valueChanged.connect(lambda: self.update_matrix_size(self.det_matrix, self.det_size.value()))
        size_layout.addWidget(self.det_size)
        size_layout.addStretch()
        layout.addLayout(size_layout)
        
        # Matriz
        self.det_matrix = QTableWidget(2, 2)
        layout.addWidget(self.det_matrix)
        
        # Botão calcular
        btn_calc = QPushButton("Calcular Determinante")
        btn_calc.clicked.connect(self.calculate_det)
        layout.addWidget(btn_calc)
        
        # Resultado
        self.det_result = QLabel("")
        self.det_result.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #007bff;
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
            }
        """)
        self.det_result.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.det_result)
        
        widget.setLayout(layout)
        return widget
    
    def update_matrix_size(self, table, size):
        """Atualizar tamanho da matriz"""
        table.setRowCount(size)
        table.setColumnCount(size)
    
    def update_mult_matrices(self):
        """Atualizar tamanhos das matrizes de multiplicação"""
        self.mult_a.setRowCount(self.mult_rows_a.value())
        self.mult_a.setColumnCount(self.mult_cols_a.value())
        self.mult_b.setRowCount(self.mult_rows_b.value())
        self.mult_b.setColumnCount(self.mult_cols_b.value())
    
    def calculate_sum(self):
        """Calcular soma/subtração de matrizes"""
        try:
            size = self.sum_size.value()
            
            # Ler matrizes
            A = []
            B = []
            
            for i in range(size):
                row_a = []
                row_b = []
                for j in range(size):
                    item_a = self.sum_a.item(i, j)
                    item_b = self.sum_b.item(i, j)
                    val_a = float(item_a.text()) if item_a else 0
                    val_b = float(item_b.text()) if item_b else 0
                    row_a.append(val_a)
                    row_b.append(val_b)
                A.append(row_a)
                B.append(row_b)
            
            # Calcular
            op = self.sum_op.currentText()
            if op == "A + B":
                result = [[A[i][j] + B[i][j] for j in range(size)] for i in range(size)]
            elif op == "A - B":
                result = [[A[i][j] - B[i][j] for j in range(size)] for i in range(size)]
            else:  # B - A
                result = [[B[i][j] - A[i][j] for j in range(size)] for i in range(size)]
            
            # Mostrar resultado
            self.sum_result.setRowCount(size)
            self.sum_result.setColumnCount(size)
            for i in range(size):
                for j in range(size):
                    self.sum_result.setItem(i, j, QTableWidgetItem(f"{result[i][j]:.2f}"))
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no cálculo: {str(e)}")
    
    def calculate_mult(self):
        """Calcular multiplicação de matrizes"""
        try:
            rows_a = self.mult_rows_a.value()
            cols_a = self.mult_cols_a.value()
            rows_b = self.mult_rows_b.value()
            cols_b = self.mult_cols_b.value()
            
            if cols_a != rows_b:
                QMessageBox.warning(self, "Erro", 
                    "Número de colunas de A deve ser igual ao número de linhas de B")
                return
            
            # Ler matrizes
            A = []
            B = []
            
            for i in range(rows_a):
                row = []
                for j in range(cols_a):
                    item = self.mult_a.item(i, j)
                    row.append(float(item.text()) if item else 0)
                A.append(row)
            
            for i in range(rows_b):
                row = []
                for j in range(cols_b):
                    item = self.mult_b.item(i, j)
                    row.append(float(item.text()) if item else 0)
                B.append(row)
            
            # Multiplicar
            result = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
            for i in range(rows_a):
                for j in range(cols_b):
                    for k in range(cols_a):
                        result[i][j] += A[i][k] * B[k][j]
            
            # Mostrar resultado
            self.mult_result.setRowCount(rows_a)
            self.mult_result.setColumnCount(cols_b)
            for i in range(rows_a):
                for j in range(cols_b):
                    self.mult_result.setItem(i, j, QTableWidgetItem(f"{result[i][j]:.2f}"))
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no cálculo: {str(e)}")
    
    def calculate_det(self):
        """Calcular determinante"""
        try:
            size = self.det_size.value()
            
            # Ler matriz
            matrix = []
            for i in range(size):
                row = []
                for j in range(size):
                    item = self.det_matrix.item(i, j)
                    row.append(float(item.text()) if item else 0)
                matrix.append(row)
            
            # Calcular determinante (implementação simples para matrizes até 4x4)
            if size == 1:
                det = matrix[0][0]
            elif size == 2:
                det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
            elif size == 3:
                det = (matrix[0][0] * matrix[1][1] * matrix[2][2] +
                       matrix[0][1] * matrix[1][2] * matrix[2][0] +
                       matrix[0][2] * matrix[1][0] * matrix[2][1] -
                       matrix[0][2] * matrix[1][1] * matrix[2][0] -
                       matrix[0][1] * matrix[1][0] * matrix[2][2] -
                       matrix[0][0] * matrix[1][2] * matrix[2][1])
            else:  # size == 4
                # Método simplificado para 4x4
                det = 0
                for i in range(4):
                    # Calcular menor complementar
                    submatrix = []
                    for j in range(1, 4):
                        row = []
                        for k in range(4):
                            if k != i:
                                row.append(matrix[j][k])
                        submatrix.append(row)
                    
                    # Calcular determinante da submatriz 3x3
                    subdet = (submatrix[0][0] * submatrix[1][1] * submatrix[2][2] +
                              submatrix[0][1] * submatrix[1][2] * submatrix[2][0] +
                              submatrix[0][2] * submatrix[1][0] * submatrix[2][1] -
                              submatrix[0][2] * submatrix[1][1] * submatrix[2][0] -
                              submatrix[0][1] * submatrix[1][0] * submatrix[2][2] -
                              submatrix[0][0] * submatrix[1][2] * submatrix[2][1])
                    
                    det += matrix[0][i] * (-1) ** i * subdet
            
            self.det_result.setText(f"det = {det:.6f}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro no cálculo: {str(e)}")

class EnhancedCalculator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.setWindowTitle("Calculadora Avançada")
        self.setGeometry(100, 100, 1000, 700)
        
        # Variáveis de estado
        self.current_mode = "Padrão"
        self.history = []
        self.current_expression = ""
        self.last_result = 0
        self.angle_unit = "DEG"
        self.word_size = 64
        self.number_base = 10
        self.memory = {}
        self.variables = {'ans': 0}
        
        # Configurar interface
        self.init_ui()
        self.apply_style()
    
    def init_ui(self):
        """Inicializar interface do usuário"""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(5)
        
        # ========== PAINEL ESQUERDO (Calculadora) ==========
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(5)
        
        # Barra de ferramentas superior
        self.create_top_toolbar(left_layout)
        
        # Displays
        self.create_displays(left_layout)
        
        # Área dos botões
        self.buttons_widget = QStackedWidget()
        left_layout.addWidget(self.buttons_widget)
        
        # Criar os diferentes modos
        self.create_standard_mode()
        self.create_scientific_mode()
        self.create_programmer_mode()
        
        main_layout.addWidget(left_panel, 2)
        
        # ========== PAINEL DIREITO (Ferramentas) ==========
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(5)
        
        # Abas para diferentes ferramentas
        self.tools_tabs = QTabWidget()
        
        # Aba de Histórico
        self.create_history_tab()
        
        # Aba de Memória
        self.create_memory_tab()
        
        # Aba de Funções Especiais
        self.create_functions_tab()
        
        # Aba de Conversões
        self.create_conversions_tab()
        
        # Aba de Estatísticas
        self.create_statistics_tab()
        
        right_layout.addWidget(self.tools_tabs)
        
        main_layout.addWidget(right_panel, 1)
        
        # Barra de menus
        self.create_menu_bar()
    
    def create_menu_bar(self):
        """Criar barra de menus"""
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
        
        # Menu Ferramentas
        tools_menu = menubar.addMenu("&Ferramentas")
        
        function_action = QAction("📈 Calculadora de Funções", self)
        function_action.triggered.connect(self.show_function_calc)
        tools_menu.addAction(function_action)
        
        matrix_action = QAction("🔢 Calculadora de Matrizes", self)
        matrix_action.triggered.connect(self.show_matrix_calc)
        tools_menu.addAction(matrix_action)
        
        stats_action = QAction("📊 Calculadora Estatística", self)
        stats_action.triggered.connect(self.show_stats_calc)
        tools_menu.addAction(stats_action)
        
        tools_menu.addSeparator()
        
        unit_action = QAction("📏 Conversor de Unidades", self)
        unit_action.triggered.connect(self.show_unit_converter)
        tools_menu.addAction(unit_action)
        
        # Menu Ajuda
        help_menu = menubar.addMenu("A&juda")
        
        about_action = QAction("&Sobre", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_top_toolbar(self, layout):
        """Criar barra de ferramentas superior"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        
        # Indicador de modo
        self.mode_label = QLabel("📱 Modo: Padrão")
        toolbar.addWidget(self.mode_label)
        
        toolbar.addSeparator()
        
        # Indicador de unidade angular
        self.angle_label = QLabel("📐 DEG")
        toolbar.addWidget(self.angle_label)
        
        toolbar.addSeparator()
        
        # Indicador de base
        self.base_label = QLabel("🔢 DEC")
        toolbar.addWidget(self.base_label)
        
        toolbar.addSeparator()
        
        # Botões de memória
        btn_memory_store = QAction("M+", self)
        btn_memory_store.triggered.connect(self.memory_store)
        toolbar.addAction(btn_memory_store)
        
        btn_memory_recall = QAction("MR", self)
        btn_memory_recall.triggered.connect(self.memory_recall)
        toolbar.addAction(btn_memory_recall)
        
        btn_memory_clear = QAction("MC", self)
        btn_memory_clear.triggered.connect(self.memory_clear)
        toolbar.addAction(btn_memory_clear)
        
        toolbar.addSeparator()
        
        # Botão limpar tudo
        btn_clear_all = QAction("🗑️ Limpar Tudo", self)
        btn_clear_all.triggered.connect(self.clear_all)
        toolbar.addAction(btn_clear_all)
        
        layout.addWidget(toolbar)
    
    def create_displays(self, layout):
        """Criar displays"""
        # Display principal
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setAlignment(Qt.AlignRight)
        self.display.setMinimumHeight(80)
        self.display.setStyleSheet("""
            QLineEdit {
                font-size: 28px;
                font-weight: bold;
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(self.display)
        
        # Display de expressão
        self.expression_display = QLineEdit()
        self.expression_display.setReadOnly(True)
        self.expression_display.setAlignment(Qt.AlignRight)
        self.expression_display.setMinimumHeight(40)
        self.expression_display.setStyleSheet("""
            QLineEdit {
                font-size: 16px;
                color: #6c757d;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                padding: 5px;
                font-family: 'Courier New';
            }
        """)
        layout.addWidget(self.expression_display)
    
    def create_standard_mode(self):
        """Criar interface do modo padrão"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(2)
        
        buttons = [
            ['C', '⌫', '%', '/'],
            ['7', '8', '9', '*'],
            ['4', '5', '6', '-'],
            ['1', '2', '3', '+'],
            ['±', '0', '.', '=']
        ]
        
        for i, row in enumerate(buttons):
            for j, text in enumerate(row):
                btn = QPushButton(text)
                btn.setMinimumHeight(60)
                btn.setMinimumWidth(70)
                btn.clicked.connect(lambda checked, t=text: self.button_click(t))
                layout.addWidget(btn, i, j)
        
        self.buttons_widget.addWidget(widget)
    
    def create_scientific_mode(self):
        """Criar interface do modo científico"""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setSpacing(2)
        
        scientific_buttons = [
            ['sin', 'cos', 'tan', 'π', 'e', '!'],
            ['asin', 'acos', 'atan', 'log', 'ln', '√'],
            ['sinh', 'cosh', 'tanh', 'x²', 'x³', '∛'],
            ['(', ')', 'mod', '^', '10^', 'e^'],
            ['7', '8', '9', '/', '*', '1/x'],
            ['4', '5', '6', '-', '+', 'ANS'],
            ['1', '2', '3', '×10^', 'EXP', '='],
            ['C', '⌫', '0', '.', '±', 'RCL']
        ]
        
        for i, row in enumerate(scientific_buttons):
            for j, text in enumerate(row):
                if text:
                    btn = QPushButton(text)
                    btn.setMinimumHeight(50)
                    btn.setMinimumWidth(60)
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
                font-size: 16px;
                background-color: #2d2d2d;
                color: #00ff00;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 3px;
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
            btn.setMinimumHeight(45)
            btn.clicked.connect(lambda checked, t=op: self.button_click(t))
            buttons_layout.addWidget(btn, 0, i)
        
        # Botões numéricos
        num_buttons = [
            ['C', '⌫', '%', '/', '*'],
            ['7', '8', '9', '-', '+'],
            ['4', '5', '6', '(', ')'],
            ['1', '2', '3', 'A', 'B'],
            ['0', '.', '±', 'C', 'D'],
            ['E', 'F', '<<', '>>', '=']
        ]
        
        for i, row in enumerate(num_buttons, start=1):
            for j, text in enumerate(row):
                btn = QPushButton(text)
                btn.setMinimumHeight(45)
                btn.clicked.connect(lambda checked, t=text: self.button_click(t))
                buttons_layout.addWidget(btn, i, j)
        
        layout.addWidget(buttons_widget)
        self.buttons_widget.addWidget(widget)
    
    def create_history_tab(self):
        """Criar aba de histórico"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Filtros
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filtrar:"))
        self.history_filter = QLineEdit()
        self.history_filter.setPlaceholderText("Digite para filtrar...")
        self.history_filter.textChanged.connect(self.filter_history)
        filter_layout.addWidget(self.history_filter)
        layout.addLayout(filter_layout)
        
        # Lista de histórico
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.history_item_clicked)
        layout.addWidget(self.history_list)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        btn_copy = QPushButton("📋 Copiar")
        btn_copy.clicked.connect(self.copy_history_item)
        buttons_layout.addWidget(btn_copy)
        
        btn_clear = QPushButton("🗑️ Limpar")
        btn_clear.clicked.connect(self.clear_history)
        buttons_layout.addWidget(btn_clear)
        
        btn_export = QPushButton("💾 Exportar")
        btn_export.clicked.connect(self.export_history)
        buttons_layout.addWidget(btn_export)
        
        layout.addLayout(buttons_layout)
        
        self.tools_tabs.addTab(widget, "📋 Histórico")
    
    def create_memory_tab(self):
        """Criar aba de memória"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Lista de memória
        self.memory_list = QTableWidget()
        self.memory_list.setColumnCount(3)
        self.memory_list.setHorizontalHeaderLabels(["Chave", "Valor", "Ações"])
        layout.addWidget(self.memory_list)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        btn_store = QPushButton("M+ (Guardar)")
        btn_store.clicked.connect(self.memory_store_dialog)
        buttons_layout.addWidget(btn_store)
        
        btn_recall = QPushButton("MR (Recuperar)")
        btn_recall.clicked.connect(self.memory_recall_dialog)
        buttons_layout.addWidget(btn_recall)
        
        btn_clear = QPushButton("MC (Limpar Tudo)")
        btn_clear.clicked.connect(self.memory_clear_all)
        buttons_layout.addWidget(btn_clear)
        
        layout.addLayout(buttons_layout)
        
        self.tools_tabs.addTab(widget, "💾 Memória")
    
    def create_functions_tab(self):
        """Criar aba de funções especiais"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Funções matemáticas
        math_group = QGroupBox("Funções Matemáticas")
        math_layout = QGridLayout()
        
        functions = [
            ("Fatorial", "!"),
            ("Parte Inteira", "floor"),
            ("Arredondar", "round"),
            ("Aleatório", "rand"),
            ("Absoluto", "abs"),
            ("Primo?", "isprime")
        ]
        
        for i, (label, func) in enumerate(functions):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, f=func: self.special_function(f))
            math_layout.addWidget(btn, i // 2, i % 2)
        
        math_group.setLayout(math_layout)
        layout.addWidget(math_group)
        
        # Constantes
        const_group = QGroupBox("Constantes")
        const_layout = QGridLayout()
        
        constants = [
            ("π (pi)", "pi"),
            ("e", "e"),
            ("φ (ouro)", "phi"),
            ("γ (Euler)", "gamma")
        ]
        
        for i, (label, const) in enumerate(constants):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=const: self.insert_constant(c))
            const_layout.addWidget(btn, i // 2, i % 2)
        
        const_group.setLayout(const_layout)
        layout.addWidget(const_group)
        
        self.tools_tabs.addTab(widget, "⚡ Funções")
    
    def create_conversions_tab(self):
        """Criar aba de conversões"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Botão para abrir conversor de unidades
        btn_unit = QPushButton("📏 Conversor de Unidades")
        btn_unit.setMinimumHeight(50)
        btn_unit.clicked.connect(self.show_unit_converter)
        layout.addWidget(btn_unit)
        
        # Conversões rápidas
        quick_group = QGroupBox("Conversões Rápidas")
        quick_layout = QGridLayout()
        
        conversions = [
            ("°C → °F", "c_to_f"),
            ("°F → °C", "f_to_c"),
            ("km → mi", "km_to_mi"),
            ("mi → km", "mi_to_km"),
            ("kg → lb", "kg_to_lb"),
            ("lb → kg", "lb_to_kg")
        ]
        
        for i, (label, conv) in enumerate(conversions):
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=conv: self.quick_convert(c))
            quick_layout.addWidget(btn, i // 2, i % 2)
        
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        self.tools_tabs.addTab(widget, "🔄 Conversões")
    
    def create_statistics_tab(self):
        """Criar aba de estatísticas"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        btn_stats = QPushButton("📊 Calculadora Estatística")
        btn_stats.setMinimumHeight(50)
        btn_stats.clicked.connect(self.show_stats_calc)
        layout.addWidget(btn_stats)
        
        self.tools_tabs.addTab(widget, "📊 Estatísticas")
    
    def apply_style(self):
        """Aplicar estilo visual"""
        style = """
        QMainWindow {
            background-color: #f8f9fa;
        }
        QPushButton {
            font-size: 14px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 8px;
            background-color: white;
        }
        QPushButton:hover {
            background-color: #e9ecef;
        }
        QPushButton:pressed {
            background-color: #dee2e6;
        }
        QListWidget, QTableWidget {
            background-color: white;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            font-family: 'Courier New';
            font-size: 12px;
        }
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #e9ecef;
            padding: 8px 15px;
            margin-right: 2px;
            border: 1px solid #dee2e6;
            border-bottom: none;
            border-top-left-radius: 3px;
            border-top-right-radius: 3px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #007bff;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        """
        self.setStyleSheet(style)
    
    def change_mode(self, mode):
        """Mudar o modo da calculadora"""
        self.current_mode = mode
        self.mode_label.setText(f"📱 Modo: {mode}")
        
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
        elif value == 'RCL':
            self.memory_recall_dialog()
        elif value in ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 
                       'sinh', 'cosh', 'tanh', 'log', 'ln', '√', '∛',
                       'x²', 'x³', '^', '10^', 'e^', '!', '1/x',
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
        elif func == '^':
            self.current_expression += '^'
        elif func == '10^':
            self.current_expression += '10^'
        elif func == 'e^':
            self.current_expression += 'exp('
        elif func == 'log':
            self.current_expression += 'log10('
        elif func == 'ln':
            self.current_expression += 'log('
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
            self.current_expression += '*10**'
        elif func == 'EXP':
            self.current_expression += '*10**'
        
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
            expression = expression.replace('mod', '%')
            expression = expression.replace('×10^', '*10**')
            expression = expression.replace('EXP', '*10**')
            
            # Processar funções especiais
            expression = expression.replace('log10', 'math.log10')
            expression = expression.replace('log', 'math.log')
            expression = expression.replace('exp', 'math.exp')
            expression = expression.replace('sqrt', 'math.sqrt')
            expression = expression.replace('cbrt', 'lambda x: x**(1/3)')
            expression = expression.replace('sin', 'math.sin')
            expression = expression.replace('cos', 'math.cos')
            expression = expression.replace('tan', 'math.tan')
            expression = expression.replace('asin', 'math.asin')
            expression = expression.replace('acos', 'math.acos')
            expression = expression.replace('atan', 'math.atan')
            expression = expression.replace('sinh', 'math.sinh')
            expression = expression.replace('cosh', 'math.cosh')
            expression = expression.replace('tanh', 'math.tanh')
            
            # Converter unidades angulares
            if self.angle_unit != "RAD":
                import re
                
                def convert_angle(match):
                    func = match.group(1)
                    angle = float(match.group(2))
                    if self.angle_unit == "DEG":
                        angle = math.radians(angle)
                    elif self.angle_unit == "GRAD":
                        angle = angle * math.pi / 200
                    return f"math.{func}({angle})"
                
                for trig_func in ['sin', 'cos', 'tan']:
                    pattern = rf'{trig_func}\(([^)]+)\)'
                    expression = re.sub(pattern, convert_angle, expression)
            
            # Avaliar expressão
            safe_dict = {
                'math': math,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'asin': math.asin,
                'acos': math.acos,
                'atan': math.atan,
                'sinh': math.sinh,
                'cosh': math.cosh,
                'tanh': math.tanh,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e,
                'abs': abs,
                'round': round,
                'int': int,
                'float': float,
                'ans': self.last_result
            }
            
            safe_dict['cbrt'] = lambda x: x**(1/3)
            
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            
            if isinstance(result, float):
                result = round(result, 10)
            
            self.add_to_history(self.current_expression, result)
            
            self.display.setText(str(result))
            self.last_result = result
            self.variables['ans'] = result
            self.current_expression = str(result)
            self.expression_display.setText("")
            
            if self.current_mode == "Programador":
                self.update_programmer_displays(result)
            
        except Exception as e:
            self.display.setText("Erro")
            self.statusBar().showMessage(f"Erro: {str(e)}", 3000)
    
    def add_to_history(self, expression, result):
        """Adicionar entrada ao histórico"""
        entry = HistoryEntry(expression, result, self.current_mode)
        self.history.append(entry)
        
        item_text = f"[{entry.timestamp}] {entry.mode}\n{expression} = {result}\n"
        self.history_list.addItem(item_text)
        self.history_list.scrollToBottom()
        
        self.update_memory_display()
    
    def update_memory_display(self):
        """Atualizar display de memória"""
        self.memory_list.setRowCount(len(self.memory))
        
        for i, (key, value) in enumerate(self.memory.items()):
            self.memory_list.setItem(i, 0, QTableWidgetItem(key))
            self.memory_list.setItem(i, 1, QTableWidgetItem(str(value)))
            
            btn_recall = QPushButton("MR")
            btn_recall.clicked.connect(lambda checked, k=key: self.memory_recall_key(k))
            self.memory_list.setCellWidget(i, 2, btn_recall)
    
    def filter_history(self, text):
        """Filtrar histórico"""
        for i in range(self.history_list.count()):
            item = self.history_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    
    def history_item_clicked(self, item):
        """Clicar em item do histórico"""
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
                    'version': '2.0',
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
                
                self.history.clear()
                self.history_list.clear()
                
                for entry_data in data['history']:
                    entry = HistoryEntry.from_dict(entry_data)
                    self.history.append(entry)
                    
                    item_text = f"[{entry.timestamp}] {entry.mode}\n{entry.expression} = {entry.result}\n"
                    self.history_list.addItem(item_text)
                
                self.statusBar().showMessage(f"Histórico importado de {file_path}", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar: {str(e)}")
    
    def memory_store(self):
        """Guardar valor na memória"""
        if self.display.text():
            key, ok = QInputDialog.getText(self, "Guardar na Memória", 
                                           "Nome da variável:")
            if ok and key:
                try:
                    value = float(self.display.text())
                    self.memory[key] = value
                    self.update_memory_display()
                    self.statusBar().showMessage(f"Valor {value} guardado em '{key}'", 2000)
                except:
                    pass
    
    def memory_recall(self):
        """Recuperar valor da memória"""
        if self.memory:
            key, ok = QInputDialog.getItem(self, "Recuperar da Memória",
                                          "Selecione a variável:",
                                          list(self.memory.keys()), 0, False)
            if ok and key:
                self.current_expression += str(self.memory[key])
                self.update_displays()
    
    def memory_clear(self):
        """Limpar memória"""
        self.memory.clear()
        self.memory_list.setRowCount(0)
        self.statusBar().showMessage("Memória limpa", 2000)
    
    def memory_store_dialog(self):
        """Diálogo para guardar na memória"""
        if self.display.text():
            key, ok = QInputDialog.getText(self, "Guardar na Memória", 
                                           "Nome da variável:")
            if ok and key:
                try:
                    value = float(self.display.text())
                    self.memory[key] = value
                    self.update_memory_display()
                    self.statusBar().showMessage(f"Valor {value} guardado em '{key}'", 2000)
                except:
                    pass
    
    def memory_recall_dialog(self):
        """Diálogo para recuperar da memória"""
        if self.memory:
            key, ok = QInputDialog.getItem(self, "Recuperar da Memória",
                                          "Selecione a variável:",
                                          list(self.memory.keys()), 0, False)
            if ok and key:
                self.current_expression += str(self.memory[key])
                self.update_displays()
    
    def memory_recall_key(self, key):
        """Recuperar valor específico da memória"""
        if key in self.memory:
            self.current_expression += str(self.memory[key])
            self.update_displays()
    
    def memory_clear_all(self):
        """Limpar toda a memória"""
        self.memory.clear()
        self.memory_list.setRowCount(0)
        self.statusBar().showMessage("Toda memória limpa", 2000)
    
    def special_function(self, func):
        """Processar funções especiais"""
        try:
            value = float(self.display.text()) if self.display.text() else 0
            
            if func == "!":
                result = math.factorial(int(value))
            elif func == "floor":
                result = math.floor(value)
            elif func == "round":
                result = round(value)
            elif func == "rand":
                result = random.random()
            elif func == "abs":
                result = abs(value)
            elif func == "isprime":
                result = self.is_prime(int(value))
            else:
                return
            
            self.display.setText(str(result))
            self.last_result = result
            self.current_expression = str(result)
            
        except Exception as e:
            self.statusBar().showMessage(f"Erro: {str(e)}", 2000)
    
    def is_prime(self, n):
        """Verificar se número é primo"""
        if n < 2:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True
    
    def insert_constant(self, const):
        """Inserir constante"""
        constants = {
            'pi': math.pi,
            'e': math.e,
            'phi': (1 + math.sqrt(5)) / 2,
            'gamma': 0.5772156649015329
        }
        
        self.current_expression += str(constants.get(const, 0))
        self.update_displays()
    
    def quick_convert(self, conv):
        """Conversões rápidas"""
        try:
            value = float(self.display.text()) if self.display.text() else 0
            
            conversions = {
                'c_to_f': value * 9/5 + 32,
                'f_to_c': (value - 32) * 5/9,
                'km_to_mi': value * 0.621371,
                'mi_to_km': value * 1.60934,
                'kg_to_lb': value * 2.20462,
                'lb_to_kg': value * 0.453592
            }
            
            result = conversions.get(conv, value)
            self.display.setText(str(result))
            self.last_result = result
            self.current_expression = str(result)
            
        except Exception as e:
            self.statusBar().showMessage(f"Erro: {str(e)}", 2000)
    
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
                result = eval(self.current_expression.replace('^', '**'))
                if isinstance(result, (int, float)):
                    self.display.setText(str(result))
            except:
                pass
    
    def update_programmer_displays(self, value):
        """Atualizar displays do modo programador"""
        try:
            int_value = int(float(value))
            
            mask = (1 << self.word_size) - 1
            int_value = int_value & mask
            
            self.hex_display.setText(hex(int_value)[2:].upper())
            self.dec_display.setText(str(int_value))
            self.oct_display.setText(oct(int_value)[2:])
            self.bin_display.setText(bin(int_value)[2:])
            
            bin_str = bin(int_value)[2:].zfill(self.word_size)
            formatted_bin = ' '.join([bin_str[i:i+4] for i in range(0, len(bin_str), 4)])
            self.binary_display.setText(formatted_bin)
            
        except:
            pass
    
    def show_function_calc(self):
        """Mostrar calculadora de funções"""
        self.function_calc = FunctionPlotter(self)
        self.function_calc.show()
    
    def show_matrix_calc(self):
        """Mostrar calculadora de matrizes"""
        self.matrix_calc = MatrixCalculator(self)
        self.matrix_calc.show()
    
    def show_stats_calc(self):
        """Mostrar calculadora estatística"""
        self.stats_calc = StatisticsCalculator(self)
        self.stats_calc.show()
    
    def show_unit_converter(self):
        """Mostrar conversor de unidades"""
        self.unit_converter = UnitConverter(self)
        self.unit_converter.show()
    
    def show_about(self):
        """Mostrar diálogo sobre"""
        about_text = """
        <h2>Calculadora Avançada</h2>
        <p><b>Versão:</b> 2.0.0</p>
        
        <h3>Modos disponíveis:</h3>
        <ul>
            <li><b>Padrão:</b> Operações básicas</li>
            <li><b>Científica:</b> Funções trigonométricas, logaritmos, etc.</li>
            <li><b>Programador:</b> Operações lógicas, diferentes bases numéricas</li>
        </ul>
        
        <h3>Ferramentas incluídas:</h3>
        <ul>
            <li>📈 Calculadora de Funções</li>
            <li>🔢 Calculadora de Matrizes</li>
            <li>📊 Calculadora Estatística</li>
            <li>📏 Conversor de Unidades</li>
            <li>💾 Memória de variáveis</li>
            <li>📋 Histórico com exportação JSON</li>
        </ul>
        
        <h3>Desenvolvido com:</h3>
        <p>Python 3 + PyQt5</p>
        """
        
        QMessageBox.about(self, "Sobre a Calculadora", about_text)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Calculadora Avançada")
    
    calculator = EnhancedCalculator()
    calculator.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
