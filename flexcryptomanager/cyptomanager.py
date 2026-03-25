import json
import os
import base64
from pathlib import Path
from typing import List, Dict, Any
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import threading

class FileCryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Crypto Manager - Criptografia de Arquivos")
        self.root.geometry("800x600")
        
        # Arquivos selecionados
        self.selected_files = []
        
        # Configurar interface
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="File Crypto Manager", 
                                font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=10)
        
        # Frame de senha
        password_frame = ttk.LabelFrame(main_frame, text="Senha", padding="10")
        password_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        password_frame.columnconfigure(1, weight=1)
        
        ttk.Label(password_frame, text="Senha:").grid(row=0, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(password_frame, show="*", width=40)
        self.password_entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        ttk.Label(password_frame, text="Confirmar:").grid(row=1, column=0, sticky=tk.W)
        self.confirm_entry = ttk.Entry(password_frame, show="*", width=40)
        self.confirm_entry.grid(row=1, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # Frame de arquivos
        files_frame = ttk.LabelFrame(main_frame, text="Arquivos", padding="10")
        files_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(1, weight=1)
        
        # Botões de seleção de arquivos
        button_frame = ttk.Frame(files_frame)
        button_frame.grid(row=0, column=0, pady=5)
        
        ttk.Button(button_frame, text="Adicionar Arquivos", 
                  command=self.add_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Adicionar Pasta", 
                  command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remover Selecionados", 
                  command=self.remove_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Limpar Lista", 
                  command=self.clear_list).pack(side=tk.LEFT, padx=5)
        
        # Lista de arquivos
        columns = ('arquivo', 'status')
        self.files_tree = ttk.Treeview(files_frame, columns=columns, show='headings', height=10)
        self.files_tree.heading('arquivo', text='Arquivo')
        self.files_tree.heading('status', text='Status')
        self.files_tree.column('arquivo', width=400)
        self.files_tree.column('status', width=150)
        self.files_tree.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para a lista
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.files_tree.configure(yscrollcommand=scrollbar.set)
        
        # Frame de ações
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=3, column=0, pady=10)
        
        ttk.Button(actions_frame, text="Criptografar para JSON", 
                  command=self.encrypt_files, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="Descriptografar de JSON", 
                  command=self.decrypt_files).pack(side=tk.LEFT, padx=5)
        
        # Área de log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="10")
        log_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar estilo
        style = ttk.Style()
        style.configure("Accent.TButton", foreground="green")
        
    def add_files(self):
        files = filedialog.askopenfilenames(title="Selecionar arquivos")
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.files_tree.insert('', tk.END, values=(file, "Aguardando"))
                
    def add_folder(self):
        folder = filedialog.askdirectory(title="Selecionar pasta")
        if folder:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path not in self.selected_files:
                        self.selected_files.append(file_path)
                        self.files_tree.insert('', tk.END, values=(file_path, "Aguardando"))
                        
    def remove_selected(self):
        selected_items = self.files_tree.selection()
        for item in selected_items:
            values = self.files_tree.item(item, 'values')
            if values:
                file_path = values[0]
                if file_path in self.selected_files:
                    self.selected_files.remove(file_path)
            self.files_tree.delete(item)
            
    def clear_list(self):
        self.selected_files.clear()
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
            
    def log(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def update_file_status(self, file_path, status):
        for item in self.files_tree.get_children():
            values = self.files_tree.item(item, 'values')
            if values and values[0] == file_path:
                self.files_tree.item(item, values=(file_path, status))
                break
                
    def derive_key(self, password: str, salt: bytes = None) -> tuple:
        """Deriva uma chave a partir da senha"""
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
        
    def encrypt_file(self, file_path: str, password: str) -> bool:
        """Criptografa um arquivo e salva como JSON"""
        try:
            # Ler arquivo original
            with open(file_path, 'rb') as f:
                file_data = f.read()
                
            # Gerar chave e IV
            key, salt = self.derive_key(password)
            iv = os.urandom(16)
            
            # Criptografar dados
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted_data = encryptor.update(file_data) + encryptor.finalize()
            
            # Preparar estrutura JSON
            output_data = {
                'encrypted': True,
                'salt': base64.b64encode(salt).decode('utf-8'),
                'iv': base64.b64encode(iv).decode('utf-8'),
                'data': base64.b64encode(encrypted_data).decode('utf-8'),
                'original_filename': os.path.basename(file_path),
                'original_size': len(file_data)
            }
            
            # Salvar arquivo JSON
            output_path = file_path + '.encrypted.json'
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2)
                
            self.log(f"✓ Criptografado: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.log(f"✗ Erro ao criptografar {file_path}: {str(e)}")
            return False
            
    def decrypt_file(self, file_path: str, password: str) -> bool:
        """Descriptografa um arquivo JSON e restaura o original"""
        try:
            # Ler arquivo JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                
            # Verificar se é um arquivo criptografado válido
            if not json_data.get('encrypted', False):
                self.log(f"✗ Arquivo não é um arquivo criptografado válido: {file_path}")
                return False
                
            # Extrair dados
            salt = base64.b64decode(json_data['salt'])
            iv = base64.b64decode(json_data['iv'])
            encrypted_data = base64.b64decode(json_data['data'])
            original_filename = json_data['original_filename']
            
            # Derivar chave
            key, _ = self.derive_key(password, salt)
            
            # Descriptografar
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
            
            # Verificar integridade (opcional: comparar tamanho)
            if len(decrypted_data) != json_data['original_size']:
                self.log(f"⚠ Aviso: Tamanho do arquivo descriptografado difere do original")
                
            # Restaurar arquivo
            output_dir = os.path.dirname(file_path)
            output_path = os.path.join(output_dir, original_filename)
            
            # Se o arquivo já existe, adicionar sufixo
            counter = 1
            while os.path.exists(output_path):
                name, ext = os.path.splitext(original_filename)
                output_path = os.path.join(output_dir, f"{name}_restored_{counter}{ext}")
                counter += 1
                
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
                
            self.log(f"✓ Descriptografado: {file_path} -> {output_path}")
            return True
            
        except json.JSONDecodeError:
            self.log(f"✗ Arquivo JSON inválido: {file_path}")
            return False
        except Exception as e:
            self.log(f"✗ Erro ao descriptografar {file_path}: {str(e)}")
            return False
            
    def validate_password(self):
        """Valida a senha"""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        if not password:
            messagebox.showerror("Erro", "Por favor, insira uma senha")
            return None
            
        if confirm and password != confirm:
            messagebox.showerror("Erro", "As senhas não coincidem")
            return None
            
        return password
        
    def encrypt_files(self):
        """Criptografa todos os arquivos selecionados"""
        password = self.validate_password()
        if not password:
            return
            
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado")
            return
            
        self.log("\n=== Iniciando criptografia ===")
        
        def process():
            success_count = 0
            for file_path in self.selected_files:
                self.update_file_status(file_path, "Processando...")
                if self.encrypt_file(file_path, password):
                    success_count += 1
                    self.update_file_status(file_path, "Criptografado")
                else:
                    self.update_file_status(file_path, "Falhou")
                    
            self.log(f"\n=== Criptografia concluída: {success_count}/{len(self.selected_files)} arquivos processados ===")
            if success_count == len(self.selected_files):
                messagebox.showinfo("Sucesso", f"Todos os {success_count} arquivos foram criptografados com sucesso!")
            else:
                messagebox.showwarning("Concluído", f"{success_count} de {len(self.selected_files)} arquivos foram criptografados.")
                
        # Executar em thread separada para não travar a interface
        threading.Thread(target=process, daemon=True).start()
        
    def decrypt_files(self):
        """Descriptografa todos os arquivos selecionados"""
        password = self.validate_password()
        if not password:
            return
            
        if not self.selected_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo selecionado")
            return
            
        # Filtrar apenas arquivos .encrypted.json
        json_files = [f for f in self.selected_files if f.endswith('.encrypted.json')]
        if not json_files:
            messagebox.showwarning("Aviso", "Nenhum arquivo .encrypted.json selecionado")
            return
            
        self.log("\n=== Iniciando descriptografia ===")
        
        def process():
            success_count = 0
            for file_path in json_files:
                self.update_file_status(file_path, "Processando...")
                if self.decrypt_file(file_path, password):
                    success_count += 1
                    self.update_file_status(file_path, "Descriptografado")
                else:
                    self.update_file_status(file_path, "Falhou")
                    
            self.log(f"\n=== Descriptografia concluída: {success_count}/{len(json_files)} arquivos processados ===")
            if success_count == len(json_files):
                messagebox.showinfo("Sucesso", f"Todos os {success_count} arquivos foram descriptografados com sucesso!")
            else:
                messagebox.showwarning("Concluído", f"{success_count} de {len(json_files)} arquivos foram descriptografados.")
                
        # Executar em thread separada para não travar a interface
        threading.Thread(target=process, daemon=True).start()

def main():
    root = tk.Tk()
    app = FileCryptoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
