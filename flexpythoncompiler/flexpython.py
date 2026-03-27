import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
import threading
import shutil

class PyToExeConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Python to EXE Converter")
        self.root.geometry("750x700")
        self.root.resizable(True, True)
        
        # Variáveis
        self.py_file = tk.StringVar()
        self.icon_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.app_name = tk.StringVar()
        self.console_mode = tk.BooleanVar(value=False)  # False = windowed, True = console
        self.one_file = tk.BooleanVar(value=True)
        self.additional_files = tk.StringVar()
        self.additional_dirs = tk.StringVar()
        self.use_upx = tk.BooleanVar(value=False)
        
        # Configurar interface
        self.setup_ui()
        
        # Verificar PyInstaller ao iniciar
        self.check_pyinstaller()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="Conversor Python para Executável", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Arquivo Python
        ttk.Label(main_frame, text="Arquivo Python (.py):*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.py_file, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_py).grid(row=1, column=2, padx=5, pady=5)
        
        # Arquivo Ícone
        ttk.Label(main_frame, text="Arquivo Ícone (.ico):").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.icon_file, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_icon).grid(row=2, column=2, padx=5, pady=5)
        
        # Diretório de saída
        ttk.Label(main_frame, text="Diretório de Saída:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(main_frame, text="Procurar", command=self.browse_output).grid(row=3, column=2, padx=5, pady=5)
        
        # Nome do aplicativo
        ttk.Label(main_frame, text="Nome do Executável:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.app_name, width=50).grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        
        # Opções
        options_frame = ttk.LabelFrame(main_frame, text="Opções", padding="10")
        options_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Checkbutton(options_frame, text="Modo Janela (sem console)", 
                       variable=self.console_mode).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Arquivo Único (--onefile)", 
                       variable=self.one_file).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Usar UPX (compactação)", 
                       variable=self.use_upx).grid(row=0, column=2, sticky=tk.W, pady=2)
        
        # Arquivos adicionais
        ttk.Label(main_frame, text="Arquivos Adicionais (separados por vírgula):").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.additional_files, width=50).grid(row=6, column=1, columnspan=2, padx=5, pady=5)
        
        ttk.Label(main_frame, text="Pastas Adicionais (separadas por vírgula):").grid(row=7, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.additional_dirs, width=50).grid(row=7, column=1, columnspan=2, padx=5, pady=5)
        
        # Status do PyInstaller
        self.pyinstaller_status = ttk.Label(main_frame, text="", foreground="red")
        self.pyinstaller_status.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=3, pady=20)
        
        self.convert_btn = ttk.Button(button_frame, text="Converter para EXE", 
                                      command=self.start_conversion, width=20)
        self.convert_btn.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="Limpar", command=self.clear_fields, 
                  width=15).grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame, text="Instalar PyInstaller", 
                  command=self.install_pyinstaller, width=20).grid(row=0, column=2, padx=5)
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Log de Conversão", padding="10")
        log_frame.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Adicionar barra de rolagem ao log
        log_container = ttk.Frame(log_frame)
        log_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.log_text = tk.Text(log_container, height=15, width=80, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_container, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_container.columnconfigure(0, weight=1)
        log_container.rowconfigure(0, weight=1)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=11, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(10, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
    def check_pyinstaller(self):
        """Verifica se o PyInstaller está instalado"""
        try:
            import PyInstaller
            self.pyinstaller_status.config(text="✓ PyInstaller instalado", foreground="green")
            return True
        except ImportError:
            self.pyinstaller_status.config(text="✗ PyInstaller não instalado. Clique em 'Instalar PyInstaller'", foreground="red")
            return False
    
    def install_pyinstaller(self):
        """Instala o PyInstaller usando pip"""
        try:
            self.log_message("Instalando PyInstaller...")
            self.log_message("-" * 50)
            
            process = subprocess.Popen(
                f'"{sys.executable}" -m pip install --upgrade pyinstaller',
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True
            )
            
            for line in process.stdout:
                if line.strip():
                    self.log_message(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_message("✓ PyInstaller instalado com sucesso!")
                self.check_pyinstaller()
                messagebox.showinfo("Sucesso", "PyInstaller instalado com sucesso!")
            else:
                self.log_message("✗ Erro ao instalar PyInstaller")
                messagebox.showerror("Erro", "Falha ao instalar PyInstaller")
                
        except Exception as e:
            self.log_message(f"Erro: {str(e)}")
            messagebox.showerror("Erro", f"Erro ao instalar: {str(e)}")
    
    def browse_py(self):
        filename = filedialog.askopenfilename(
            title="Selecione o arquivo Python",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if filename:
            self.py_file.set(filename)
            # Sugerir nome do aplicativo baseado no arquivo
            base_name = os.path.splitext(os.path.basename(filename))[0]
            self.app_name.set(base_name)
            # Sugerir diretório de saída
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(filename))
    
    def browse_icon(self):
        filename = filedialog.askopenfilename(
            title="Selecione o arquivo de ícone",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if filename:
            self.icon_file.set(filename)
    
    def browse_output(self):
        directory = filedialog.askdirectory(title="Selecione o diretório de saída")
        if directory:
            self.output_dir.set(directory)
    
    def clear_fields(self):
        self.py_file.set("")
        self.icon_file.set("")
        self.output_dir.set("")
        self.app_name.set("")
        self.additional_files.set("")
        self.additional_dirs.set("")
        self.console_mode.set(False)
        self.one_file.set(True)
        self.use_upx.set(False)
        self.log_text.delete(1.0, tk.END)
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_conversion(self):
        # Verificar PyInstaller
        if not self.check_pyinstaller():
            if messagebox.askyesno("PyInstaller não encontrado", 
                                   "PyInstaller não está instalado. Deseja instalar agora?"):
                self.install_pyinstaller()
                return
            else:
                return
        
        # Validar campos obrigatórios
        if not self.py_file.get():
            messagebox.showerror("Erro", "Selecione um arquivo Python!")
            return
        
        if not os.path.exists(self.py_file.get()):
            messagebox.showerror("Erro", "Arquivo Python não encontrado!")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Erro", "Selecione o diretório de saída!")
            return
        
        # Criar diretório de saída se não existir
        os.makedirs(self.output_dir.get(), exist_ok=True)
        
        # Iniciar conversão em thread separada
        self.convert_btn.config(state="disabled")
        self.progress.start()
        self.log_message("=" * 50)
        self.log_message("Iniciando conversão...")
        
        thread = threading.Thread(target=self.convert_to_exe)
        thread.daemon = True
        thread.start()
    
    def convert_to_exe(self):
        try:
            # Construir comando no formato que funcionou
            # Formato: python -m PyInstaller --onefile --windowed --icon=icon.ico --name="Nome" arquivo.py
            
            # Comando base
            cmd_parts = ["python", "-m", "PyInstaller"]
            
            # Opção onefile/onedir
            if self.one_file.get():
                cmd_parts.append("--onefile")
            else:
                cmd_parts.append("--onedir")
            
            # Opção windowed (sem console) ou console
            if not self.console_mode.get():
                cmd_parts.append("--windowed")
            # Se for modo console, não adiciona nada (padrão é console)
            
            # Ícone
            if self.icon_file.get() and os.path.exists(self.icon_file.get()):
                icon_path = os.path.abspath(self.icon_file.get())
                cmd_parts.append(f"--icon={icon_path}")
            
            # Nome do executável (com aspas para suportar espaços)
            name = self.app_name.get() if self.app_name.get() else os.path.splitext(os.path.basename(self.py_file.get()))[0]
            cmd_parts.append(f'--name="{name}"')
            
            # UPX (compactação)
            if self.use_upx.get():
                cmd_parts.append("--upx-dir=.")
            
            # Arquivos adicionais
            if self.additional_files.get():
                files = [f.strip() for f in self.additional_files.get().split(",") if f.strip()]
                for file in files:
                    if os.path.exists(file):
                        abs_file = os.path.abspath(file)
                        cmd_parts.append(f'--add-data="{abs_file}{os.pathsep}."')
                    else:
                        self.log_message(f"Aviso: Arquivo adicional não encontrado: {file}")
            
            # Pastas adicionais
            if self.additional_dirs.get():
                dirs = [d.strip() for d in self.additional_dirs.get().split(",") if d.strip()]
                for dir_path in dirs:
                    if os.path.exists(dir_path):
                        abs_dir = os.path.abspath(dir_path)
                        cmd_parts.append(f'--add-data="{abs_dir}{os.pathsep}{os.path.basename(dir_path)}"')
                    else:
                        self.log_message(f"Aviso: Pasta adicional não encontrada: {dir_path}")
            
            # Arquivo Python de entrada
            py_file = os.path.abspath(self.py_file.get())
            cmd_parts.append(f'"{py_file}"')
            
            # Juntar comando
            full_cmd = " ".join(cmd_parts)
            
            # Mostrar comando que será executado
            self.log_message("Comando gerado (igual ao que funcionou no PowerShell):")
            self.log_message(full_cmd)
            self.log_message("-" * 50)
            
            # Mudar para o diretório de saída antes de executar
            work_dir = os.path.abspath(self.output_dir.get())
            
            # Executar o comando
            process = subprocess.Popen(
                full_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                shell=True,
                cwd=work_dir
            )
            
            # Mostrar saída em tempo real
            for line in process.stdout:
                if line.strip():
                    self.log_message(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log_message("-" * 50)
                self.log_message("✅ CONVERSÃO CONCLUÍDA COM SUCESSO!")
                
                # Localizar o executável gerado
                exe_name = f"{name}.exe"
                
                if self.one_file.get():
                    # No modo onefile, o executável fica diretamente no distpath
                    exe_path = os.path.join(work_dir, exe_name)
                else:
                    # No modo onedir, o executável fica dentro de uma pasta com o nome do app
                    exe_path = os.path.join(work_dir, name, exe_name)
                
                # Também verificar na pasta dist (padrão do PyInstaller)
                dist_path = os.path.join(work_dir, "dist")
                if not os.path.exists(exe_path) and os.path.exists(dist_path):
                    if self.one_file.get():
                        alt_path = os.path.join(dist_path, exe_name)
                    else:
                        alt_path = os.path.join(dist_path, name, exe_name)
                    
                    if os.path.exists(alt_path):
                        exe_path = alt_path
                
                if os.path.exists(exe_path):
                    self.log_message(f"Executável gerado em: {exe_path}")
                    size_kb = os.path.getsize(exe_path) / 1024
                    size_mb = size_kb / 1024
                    if size_mb >= 1:
                        self.log_message(f"Tamanho: {size_mb:.2f} MB")
                    else:
                        self.log_message(f"Tamanho: {size_kb:.2f} KB")
                    
                    # Perguntar se quer abrir a pasta
                    self.root.after(0, lambda: self.ask_open_folder(work_dir))
                else:
                    self.log_message(f"⚠️ Executável não encontrado em: {exe_path}")
                    self.log_message("Procurando em pastas comuns...")
                    
                    # Procurar recursivamente pelo arquivo .exe
                    for root_dir, dirs, files in os.walk(work_dir):
                        for file in files:
                            if file.endswith(".exe") and name.lower() in file.lower():
                                self.log_message(f"Encontrado: {os.path.join(root_dir, file)}")
            else:
                self.log_message("-" * 50)
                self.log_message("❌ ERRO NA CONVERSÃO! Verifique os logs acima.")
                
        except Exception as e:
            self.log_message(f"❌ Erro: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
            
        finally:
            self.root.after(0, self.conversion_finished)
    
    def ask_open_folder(self, folder):
        if messagebox.askyesno("Conversão Concluída", 
                               "Conversão finalizada! Deseja abrir a pasta com o executável?"):
            try:
                if sys.platform == 'win32':
                    os.startfile(folder)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', folder])
                else:
                    subprocess.run(['xdg-open', folder])
            except Exception as e:
                self.log_message(f"Erro ao abrir pasta: {e}")
    
    def conversion_finished(self):
        self.convert_btn.config(state="normal")
        self.progress.stop()
        self.log_message("")
        self.log_message("Pronto para nova conversão!")

def main():
    root = tk.Tk()
    app = PyToExeConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
