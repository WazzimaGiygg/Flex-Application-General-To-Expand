import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class TabEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Texto com Abas")
        self.root.geometry("800x600")
        
        self.tabs = {}
        self.active_tab = None
        self.next_tab_number = 1
        
        # Criar interface
        self.setup_ui()
        
        # Inicializar com uma aba
        self.add_tab()
    
    def setup_ui(self):
        # Frame para abas
        self.tabs_frame = ttk.Frame(self.root)
        self.tabs_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botão para adicionar aba
        self.add_tab_btn = ttk.Button(self.tabs_frame, text="Adicionar Aba", command=self.add_tab)
        self.add_tab_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para botões de abas
        self.tabs_buttons_frame = ttk.Frame(self.tabs_frame)
        self.tabs_buttons_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Frame principal do editor
        self.editor_frame = ttk.Frame(self.root)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Frame para novo item
        self.new_item_frame = ttk.Frame(self.editor_frame)
        self.new_item_frame.pack(fill=tk.X, pady=5)
        
        self.new_item_entry = ttk.Entry(self.new_item_frame)
        self.new_item_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.add_item_btn = ttk.Button(self.new_item_frame, text="Adicionar Item", command=self.add_new_item)
        self.add_item_btn.pack(side=tk.RIGHT)
        
        # Frame para lista de itens (com scrollbar)
        self.list_frame = ttk.Frame(self.editor_frame)
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar para scroll
        self.canvas = tk.Canvas(self.list_frame)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Frame para botões de salvar/carregar
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.save_btn = ttk.Button(self.buttons_frame, text="Salvar", command=self.save)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_encrypted_btn = ttk.Button(self.buttons_frame, text="Salvar com Criptografia", command=self.save_encrypted)
        self.save_encrypted_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(self.buttons_frame, text="Carregar", command=self.load)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_encrypted_btn = ttk.Button(self.buttons_frame, text="Carregar com Criptografia", command=self.load_encrypted)
        self.load_encrypted_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para senha
        self.password_frame = ttk.Frame(self.root)
        self.password_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(self.password_frame, text="Senha:").pack(side=tk.LEFT, padx=5)
        self.password_entry = ttk.Entry(self.password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Dicionário para armazenar os widgets dos itens
        self.item_widgets = {}
    
    def render_tabs(self):
        # Limpar frame de abas
        for widget in self.tabs_buttons_frame.winfo_children():
            widget.destroy()
        
        # Criar botões para cada aba
        for tab_number in sorted(self.tabs.keys(), key=int):
            tab_btn = ttk.Button(
                self.tabs_buttons_frame,
                text=f"Aba {tab_number}",
                command=lambda tn=tab_number: self.switch_tab(tn)
            )
            tab_btn.pack(side=tk.LEFT, padx=2)
            
            # Destacar aba ativa
            if str(tab_number) == str(self.active_tab):
                tab_btn.state(['pressed'])
    
    def switch_tab(self, tab_number):
        self.active_tab = tab_number
        self.render_tabs()
        self.render_list()
    
    def render_list(self):
        # Limpar frame rolável
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.item_widgets.clear()
        
        if self.active_tab in self.tabs:
            for index, item in enumerate(self.tabs[self.active_tab]):
                # Frame para cada item
                item_frame = ttk.Frame(self.scrollable_frame)
                item_frame.pack(fill=tk.X, pady=2)
                
                # Textarea (usando Text widget para múltiplas linhas)
                text_widget = tk.Text(item_frame, height=3, width=50, wrap=tk.WORD)
                text_widget.insert("1.0", item)
                text_widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
                
                # Botão remover
                remove_btn = ttk.Button(
                    item_frame,
                    text="Remover",
                    command=lambda idx=index: self.remove_item(idx)
                )
                remove_btn.pack(side=tk.RIGHT)
                
                # Armazenar referência para atualização
                self.item_widgets[index] = text_widget
    
    def remove_item(self, index):
        if self.active_tab in self.tabs:
            del self.tabs[self.active_tab][index]
            self.render_list()
    
    def add_tab(self):
        self.tabs[self.next_tab_number] = []
        self.active_tab = self.next_tab_number
        self.next_tab_number += 1
        self.render_tabs()
        self.render_list()
    
    def add_new_item(self):
        new_item_text = self.new_item_entry.get().strip()
        if new_item_text:
            if self.active_tab in self.tabs:
                self.tabs[self.active_tab].append(new_item_text)
                self.new_item_entry.delete(0, tk.END)
                self.render_list()
    
    def update_item_text(self, index):
        """Atualiza o texto do item quando o Text widget é modificado"""
        if self.active_tab in self.tabs and index in self.item_widgets:
            text_widget = self.item_widgets[index]
            new_text = text_widget.get("1.0", "end-1c")
            self.tabs[self.active_tab][index] = new_text
    
    def save(self):
        """Salvar em arquivo JSON não criptografado"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Atualizar todos os textos antes de salvar
                self.update_all_items()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.tabs, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def save_encrypted(self):
        """Salvar em arquivo criptografado"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".enc",
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")]
        )
        
        if file_path:
            password = self.password_entry.get()
            if not password:
                messagebox.showwarning("Aviso", "Digite uma senha para criptografar!")
                return
            
            try:
                # Atualizar todos os textos antes de salvar
                self.update_all_items()
                
                # Converter dados para JSON
                data = json.dumps(self.tabs, ensure_ascii=False).encode('utf-8')
                
                # Criptografar dados
                encrypted_data = self.encrypt_data(data, password)
                
                # Salvar arquivo
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
                
                messagebox.showinfo("Sucesso", "Arquivo salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def load(self):
        """Carregar arquivo JSON não criptografado"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.tabs = json.load(f)
                
                # Converter chaves para int se necessário
                self.tabs = {int(k): v for k, v in self.tabs.items()}
                
                # Atualizar next_tab_number
                if self.tabs:
                    self.next_tab_number = max(self.tabs.keys()) + 1
                    self.active_tab = min(self.tabs.keys())
                else:
                    self.next_tab_number = 1
                    self.active_tab = None
                
                self.render_tabs()
                self.render_list()
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
    
    def load_encrypted(self):
        """Carregar arquivo criptografado"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")]
        )
        
        if file_path:
            password = self.password_entry.get()
            if not password:
                messagebox.showwarning("Aviso", "Digite a senha para descriptografar!")
                return
            
            try:
                # Ler arquivo criptografado
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # Descriptografar dados
                decrypted_data = self.decrypt_data(encrypted_data, password)
                
                # Converter para JSON
                self.tabs = json.loads(decrypted_data.decode('utf-8'))
                
                # Converter chaves para int se necessário
                self.tabs = {int(k): v for k, v in self.tabs.items()}
                
                # Atualizar next_tab_number
                if self.tabs:
                    self.next_tab_number = max(self.tabs.keys()) + 1
                    self.active_tab = min(self.tabs.keys())
                else:
                    self.next_tab_number = 1
                    self.active_tab = None
                
                self.render_tabs()
                self.render_list()
                messagebox.showinfo("Sucesso", "Arquivo carregado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo: Senha incorreta ou arquivo corrompido.")
    
    def update_all_items(self):
        """Atualiza todos os itens nos dados antes de salvar"""
        for tab_number in self.tabs:
            if tab_number == self.active_tab:
                # Atualizar itens da aba ativa
                for index, text_widget in self.item_widgets.items():
                    if index < len(self.tabs[tab_number]):
                        self.tabs[tab_number][index] = text_widget.get("1.0", "end-1c")
    
    def encrypt_data(self, data, password):
        """Criptografa dados usando PBKDF2 e Fernet"""
        # Gerar salt
        salt = os.urandom(16)
        
        # Derivar chave a partir da senha
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Criptografar dados
        f = Fernet(key)
        encrypted = f.encrypt(data)
        
        # Retornar salt + dados criptografados
        return salt + encrypted
    
    def decrypt_data(self, encrypted_data, password):
        """Descriptografa dados usando PBKDF2 e Fernet"""
        # Extrair salt e dados criptografados
        salt = encrypted_data[:16]
        encrypted = encrypted_data[16:]
        
        # Derivar chave a partir da senha
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Descriptografar dados
        f = Fernet(key)
        decrypted = f.decrypt(encrypted)
        
        return decrypted

def main():
    root = tk.Tk()
    app = TabEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
