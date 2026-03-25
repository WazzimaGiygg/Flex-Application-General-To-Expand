import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import base64
import json
import os
import webbrowser
import tempfile
from Crypto.Cipher import AES
import hashlib

class JSONViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de JSON em Múltiplas Abas")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f4f4f4')
        
        # Armazenar os arquivos temporários
        self.temp_files = []
        
        self.setup_ui()
        self.setup_keyboard_protection()
        
    def setup_ui(self):
        # Container principal
        main_container = tk.Frame(self.root, bg='white')
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Frame para controles
        controls_frame = tk.Frame(main_container, bg='white')
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botão para selecionar arquivo
        self.file_path = tk.StringVar()
        self.file_button = tk.Button(
            controls_frame,
            text="Selecionar Arquivo JSON",
            command=self.select_file,
            bg='#4285F4',
            fg='white',
            font=('Arial', 12),
            cursor='hand2'
        )
        self.file_button.pack(fill=tk.X, pady=(0, 10))
        
        # Label para mostrar arquivo selecionado
        self.file_label = tk.Label(
            controls_frame,
            text="Nenhum arquivo selecionado",
            bg='white',
            font=('Arial', 10)
        )
        self.file_label.pack(fill=tk.X, pady=(0, 10))
        
        # Campo de senha
        self.password_label = tk.Label(
            controls_frame,
            text="Senha para descriptografia:",
            bg='white',
            font=('Arial', 10)
        )
        self.password_label.pack(fill=tk.X)
        
        self.password_entry = tk.Entry(
            controls_frame,
            show='•',
            font=('Arial', 12)
        )
        self.password_entry.pack(fill=tk.X, pady=(5, 10))
        self.password_entry.insert(0, "12.237.514")  # Pré-preencher com a senha
        
        # Botão de importar
        self.import_button = tk.Button(
            controls_frame,
            text="Importar JSON",
            command=self.import_json,
            bg='#4285F4',
            fg='white',
            font=('Arial', 12),
            cursor='hand2'
        )
        self.import_button.pack(fill=tk.X)
        
        # Notebook (sistema de abas)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Configurar estilo das abas
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', padding=[20, 5], font=('Arial', 10))
        
    def setup_keyboard_protection(self):
        """Desabilita atalhos de teclado comuns"""
        def key_handler(event):
            # Bloqueia Ctrl+S, Ctrl+U, Ctrl+P
            if event.state & 0x4 and event.keysym in ['s', 'u', 'p']:
                return "break"
            
            # Bloqueia Ctrl+Shift+I, F12
            if (event.state & 0x4 and event.state & 0x1 and event.keysym == 'i') or \
               event.keysym == 'F12':
                return "break"
            
            # Bloqueia F5 (recarregar)
            if event.keysym == 'F5':
                return "break"
        
        self.root.bind_all('<Key>', key_handler)
        
        # Desabilitar menu de contexto
        def context_menu_handler(event):
            return "break"
        
        self.root.bind_all('<Button-3>', context_menu_handler)
        self.root.bind_all('<Control-Button-1>', context_menu_handler)
        
    def select_file(self):
        """Seleciona o arquivo JSON"""
        file_path = filedialog.askopenfilename(
            title="Selecionar arquivo JSON",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            self.file_path.set(file_path)
            self.file_label.config(text=f"Arquivo: {os.path.basename(file_path)}")
    
    def decrypt_aes_cryptojs(self, encrypted_data, password):
        """
        Descriptografa dados no formato CryptoJS
        Formato: "U2FsdGVkX1..." + salt nos primeiros bytes
        """
        try:
            # Decodificar base64
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Verificar se tem o prefixo "Salted__" (CryptoJS adiciona isso)
            if encrypted_bytes[:8] == b'Salted__':
                salt = encrypted_bytes[8:16]
                cipher_text = encrypted_bytes[16:]
            else:
                # Se não tiver salt, usar os primeiros bytes como parte do cipher
                salt = b''
                cipher_text = encrypted_bytes
            
            # Derivar chave e IV usando EVP_BytesToKey (método do CryptoJS)
            def evp_bytes_to_key(password, salt, key_len=32, iv_len=16):
                """
                Implementação do EVP_BytesToKey do OpenSSL (usado pelo CryptoJS)
                """
                dtot = b''
                d = b''
                password_bytes = password.encode('utf-8')
                while len(dtot) < key_len + iv_len:
                    d = hashlib.md5(d + password_bytes + salt).digest()
                    dtot += d
                key = dtot[:key_len]
                iv = dtot[key_len:key_len + iv_len]
                return key, iv
            
            key, iv = evp_bytes_to_key(password, salt)
            
            # Descriptografar
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(cipher_text)
            
            # Remover padding PKCS7
            padding_length = decrypted[-1]
            if padding_length <= 16:
                decrypted = decrypted[:-padding_length]
            
            return decrypted.decode('utf-8')
            
        except Exception as e:
            raise Exception(f"Erro na descriptografia: {str(e)}")
    
    def import_json(self):
        """Importa e processa o arquivo JSON"""
        if not self.file_path.get():
            messagebox.showerror("Erro", "Por favor, selecione um arquivo JSON.")
            return
        
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Erro", "Por favor, digite a senha para descriptografia.")
            return
        
        try:
            # Mostrar mensagem de processamento
            self.root.config(cursor="watch")
            self.root.update()
            
            # Ler arquivo
            with open(self.file_path.get(), 'r', encoding='utf-8') as f:
                encrypted_data = f.read().strip()
            
            # Descriptografar
            json_string = self.decrypt_aes_cryptojs(encrypted_data, password)
            
            # Parse do JSON
            parsed_data = json.loads(json_string)
            
            # Limpar abas existentes
            for tab_id in self.notebook.tabs():
                self.notebook.forget(tab_id)
            
            # Limpar arquivos temporários antigos
            for temp_file in self.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except:
                    pass
            self.temp_files.clear()
            
            # Esconder elementos de entrada
            self.file_button.pack_forget()
            self.file_label.pack_forget()
            self.password_label.pack_forget()
            self.password_entry.pack_forget()
            self.import_button.pack_forget()
            
            # Criar abas
            for key, html_content in parsed_data.items():
                self.add_tab(html_content, key)
            
            # Restaurar cursor
            self.root.config(cursor="")
            
            if len(self.notebook.tabs()) == 0:
                messagebox.showwarning("Aviso", "Nenhum dado encontrado no arquivo JSON.")
            else:
                messagebox.showinfo("Sucesso", f"Importado {len(self.notebook.tabs())} aba(s) com sucesso!")
                
        except json.JSONDecodeError as e:
            self.root.config(cursor="")
            messagebox.showerror("Erro", f"Erro ao processar o arquivo JSON: {str(e)}")
        except UnicodeDecodeError as e:
            self.root.config(cursor="")
            messagebox.showerror("Erro", f"Erro de decodificação. Verifique a senha: {str(e)}")
        except Exception as e:
            self.root.config(cursor="")
            messagebox.showerror("Erro", f"Erro ao decriptografar o arquivo: {str(e)}")
    
    def add_tab(self, html_content, tab_name):
        """Adiciona uma nova aba com conteúdo HTML"""
        # Criar arquivo HTML temporário
        temp_dir = tempfile.gettempdir()
        # Sanitizar nome da aba para uso como nome de arquivo
        safe_tab_name = "".join(c for c in tab_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        if not safe_tab_name:
            safe_tab_name = f"tab_{len(self.temp_files)}"
        
        temp_file = os.path.join(temp_dir, f"json_viewer_{safe_tab_name}_{len(self.temp_files)}.html")
        
        # Escrever conteúdo HTML no arquivo temporário
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.temp_files.append(temp_file)
        
        # Criar frame para a aba
        frame = ttk.Frame(self.notebook)
        
        # Criar um frame para o conteúdo
        content_frame = tk.Frame(frame, bg='white')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar widget de texto para exibir HTML (como texto)
        text_widget = tk.Text(content_frame, wrap=tk.NONE, bg='white', font=('Courier', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Adicionar scrollbars
        v_scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=text_widget.yview)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar = ttk.Scrollbar(content_frame, orient=tk.HORIZONTAL, command=text_widget.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        text_widget.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Carregar o HTML como texto
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Mostrar apenas as primeiras 5000 linhas para performance
                lines = content.split('\n')
                if len(lines) > 5000:
                    content = '\n'.join(lines[:5000]) + '\n\n... (conteúdo truncado) ...'
                text_widget.insert('1.0', content)
                text_widget.configure(state='disabled')  # Tornar somente leitura
        except Exception as e:
            text_widget.insert('1.0', f"Erro ao carregar conteúdo: {str(e)}")
            text_widget.configure(state='disabled')
        
        # Adicionar opção para abrir no navegador
        def open_in_browser():
            webbrowser.open(f"file:///{temp_file}")
        
        # Botão para abrir no navegador
        button_frame = tk.Frame(frame, bg='#f0f0f0')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        browser_button = tk.Button(
            button_frame,
            text="🌐 Abrir no Navegador",
            command=open_in_browser,
            bg='#4285F4',
            fg='white',
            font=('Arial', 9),
            cursor='hand2'
        )
        browser_button.pack(pady=5)
        
        # Configurar menu de contexto para abrir no navegador
        def show_context_menu(event, temp_file_path):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Abrir no navegador", 
                           command=lambda: webbrowser.open(f"file:///{temp_file_path}"))
            menu.post(event.x_root, event.y_root)
        
        text_widget.bind('<Button-3>', lambda e, f=temp_file: show_context_menu(e, f))
        
        # Adicionar ao notebook
        self.notebook.add(frame, text=tab_name)
    
    def on_closing(self):
        """Limpeza ao fechar a aplicação"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except:
                pass
        self.root.destroy()

def main():
    # Verificar se pycryptodome está instalado
    try:
        from Crypto.Cipher import AES
    except ImportError:
        print("Instalando dependências necessárias...")
        import subprocess
        subprocess.check_call(['pip', 'install', 'pycryptodome'])
        print("Dependências instaladas. Reinicie o programa.")
        return
    
    root = tk.Tk()
    app = JSONViewerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
