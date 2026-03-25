import tkinter as tk
from tkinter import messagebox, scrolledtext
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os

class CryptoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cripto Mobile")
        self.root.geometry("450x800")  # Corrigido: adicionado "x" entre largura e altura
        self.root.configure(bg='#f5f7fa')
        
        # Configurar estilo
        self.root.option_add('*Font', '-apple-system 10')
        
        # Container principal com scrollbar
        self.canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Container principal
        self.container = self.scrollable_frame
        
        # Título
        title = tk.Label(
            self.container,
            text="🔐 Cripto Mobile",
            font=('-apple-system', 24, 'bold'),
            bg='white',
            fg='#1e293b'
        )
        title.pack(pady=(0, 24))
        
        # Seção de Criptografia
        self.create_encrypt_section()
        
        # Seção de Descriptografia
        self.create_decrypt_section()
        
        # Configurar eventos
        self.setup_events()
    
    def create_encrypt_section(self):
        """Cria a seção de criptografia"""
        # Título da seção
        encrypt_title = tk.Label(
            self.container,
            text="📝 Criptografar",
            font=('-apple-system', 18, 'bold'),
            bg='white',
            fg='#334155',
            anchor='w'
        )
        encrypt_title.pack(fill='x', pady=(0, 8))
        
        # Campo de texto plano
        self.plain_text = scrolledtext.ScrolledText(
            self.container,
            height=5,
            font=('-apple-system', 14),
            bg='#f8fafc',
            fg='#0f172a',
            relief='flat',
            bd=1.5,
            highlightthickness=1.5,
            highlightbackground='#e2e8f0',
            highlightcolor='#3b82f6'
        )
        self.plain_text.pack(fill='x', pady=(0, 12))
        self.plain_text.insert('1.0', "Digite o texto...")
        self.plain_text.bind('<FocusIn>', lambda e: self.clear_placeholder(e, self.plain_text, "Digite o texto..."))
        self.plain_text.bind('<FocusOut>', lambda e: self.set_placeholder(e, self.plain_text, "Digite o texto..."))
        
        # Campo de senha
        self.encrypt_password = tk.Entry(
            self.container,
            font=('-apple-system', 14),
            bg='#f8fafc',
            fg='#0f172a',
            relief='flat',
            bd=1.5,
            highlightthickness=1.5,
            highlightbackground='#e2e8f0',
            highlightcolor='#3b82f6',
            show='•'
        )
        self.encrypt_password.pack(fill='x', pady=(0, 12))
        self.encrypt_password.insert(0, "Senha")
        self.encrypt_password.bind('<FocusIn>', lambda e: self.clear_password_placeholder(e, self.encrypt_password))
        self.encrypt_password.bind('<FocusOut>', lambda e: self.set_password_placeholder(e, self.encrypt_password))
        
        # Botão de criptografar
        encrypt_btn = tk.Button(
            self.container,
            text="Criptografar",
            font=('-apple-system', 17, 'bold'),
            bg='#3b82f6',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.encrypt_text
        )
        encrypt_btn.pack(fill='x', pady=(0, 12))
        
        # Frame para texto criptografado e botão de cópia
        encrypt_frame = tk.Frame(self.container, bg='white')
        encrypt_frame.pack(fill='x', pady=(0, 20))
        
        # Label do campo
        encrypt_label_frame = tk.Frame(encrypt_frame, bg='white')
        encrypt_label_frame.pack(fill='x')
        
        encrypt_label = tk.Label(
            encrypt_label_frame,
            text="Texto Criptografado:",
            font=('-apple-system', 12),
            bg='white',
            fg='#334155',
            anchor='w'
        )
        encrypt_label.pack(side='left')
        
        # Botão de copiar
        self.copy_encrypt_btn = tk.Button(
            encrypt_label_frame,
            text="📋 Copiar",
            font=('-apple-system', 11),
            bg='#f1f5f9',
            fg='#3b82f6',
            relief='flat',
            bd=1,
            cursor='hand2',
            command=lambda: self.copy_to_clipboard(self.encrypted_text, "criptografado")
        )
        self.copy_encrypt_btn.pack(side='right')
        
        # Campo de texto criptografado
        self.encrypted_text = scrolledtext.ScrolledText(
            encrypt_frame,
            height=4,
            font=('-apple-system', 12),
            bg='#f1f5f9',
            fg='#334155',
            relief='flat',
            bd=1.5,
            highlightthickness=1.5,
            highlightbackground='#cbd5e1',
            state='normal'
        )
        self.encrypted_text.pack(fill='x', pady=(5, 0))
        self.encrypted_text.insert('1.0', "Texto criptografado aparecerá aqui")
        self.encrypted_text.configure(state='disabled')
        
        # Bind para selecionar texto ao clicar
        self.encrypted_text.bind('<Button-1>', lambda e: self.select_all_text(e, self.encrypted_text))
        
        # Menu de contexto para copiar
        self.create_context_menu(self.encrypted_text, "criptografado")
    
    def create_decrypt_section(self):
        """Cria a seção de descriptografia"""
        # Título da seção
        decrypt_title = tk.Label(
            self.container,
            text="🔓 Descriptografar",
            font=('-apple-system', 18, 'bold'),
            bg='white',
            fg='#334155',
            anchor='w'
        )
        decrypt_title.pack(fill='x', pady=(0, 8))
        
        # Campo de texto criptografado
        self.cipher_text = scrolledtext.ScrolledText(
            self.container,
            height=5,
            font=('-apple-system', 12),
            bg='#f8fafc',
            fg='#0f172a',
            relief='flat',
            bd=1.5,
            highlightthickness=1.5,
            highlightbackground='#e2e8f0',
            highlightcolor='#3b82f6'
        )
        self.cipher_text.pack(fill='x', pady=(0, 12))
        self.cipher_text.insert('1.0', "Cole o texto criptografado...")
        self.cipher_text.bind('<FocusIn>', lambda e: self.clear_placeholder(e, self.cipher_text, "Cole o texto criptografado..."))
        self.cipher_text.bind('<FocusOut>', lambda e: self.set_placeholder(e, self.cipher_text, "Cole o texto criptografado..."))
        
        # Campo de senha
        self.decrypt_password = tk.Entry(
            self.container,
            font=('-apple-system', 14),
            bg='#f8fafc',
            fg='#0f172a',
            relief='flat',
            bd=1.5,
            highlightthickness=1.5,
            highlightbackground='#e2e8f0',
            highlightcolor='#3b82f6',
            show='•'
        )
        self.decrypt_password.pack(fill='x', pady=(0, 12))
        self.decrypt_password.insert(0, "Senha")
        self.decrypt_password.bind('<FocusIn>', lambda e: self.clear_password_placeholder(e, self.decrypt_password))
        self.decrypt_password.bind('<FocusOut>', lambda e: self.set_password_placeholder(e, self.decrypt_password))
        
        # Botão de descriptografar
        decrypt_btn = tk.Button(
            self.container,
            text="Descriptografar",
            font=('-apple-system', 17, 'bold'),
            bg='#3b82f6',
            fg='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.decrypt_text
        )
        decrypt_btn.pack(fill='x', pady=(0, 12))
        
        # Frame para texto descriptografado e botão de cópia
        decrypt_frame = tk.Frame(self.container, bg='white')
        decrypt_frame.pack(fill='x', pady=(0, 0))
        
        # Label do campo
        decrypt_label_frame = tk.Frame(decrypt_frame, bg='white')
        decrypt_label_frame.pack(fill='x')
        
        decrypt_label = tk.Label(
            decrypt_label_frame,
            text="Texto Descriptografado:",
            font=('-apple-system', 12),
            bg='white',
            fg='#334155',
            anchor='w'
        )
        decrypt_label.pack(side='left')
        
        # Botão de copiar
        self.copy_decrypt_btn = tk.Button(
            decrypt_label_frame,
            text="📋 Copiar",
            font=('-apple-system', 11),
            bg='#f1f5f9',
            fg='#3b82f6',
            relief='flat',
            bd=1,
            cursor='hand2',
            command=lambda: self.copy_to_clipboard(self.decrypted_text, "descriptografado")
        )
        self.copy_decrypt_btn.pack(side='right')
        
        # Campo de texto descriptografado
        self.decrypted_text = scrolledtext.ScrolledText(
            decrypt_frame,
            height=4,
            font=('-apple-system', 14),
            bg='#f1f5f9',
            fg='#334155',
            relief='flat',
            bd=1.5,
            highlightthickness=1.5,
            highlightbackground='#cbd5e1',
            state='normal'
        )
        self.decrypted_text.pack(fill='x', pady=(5, 0))
        self.decrypted_text.insert('1.0', "Texto descriptografado aparecerá aqui")
        self.decrypted_text.configure(state='disabled')
        
        # Bind para selecionar texto ao clicar
        self.decrypted_text.bind('<Button-1>', lambda e: self.select_all_text(e, self.decrypted_text))
        
        # Menu de contexto para copiar
        self.create_context_menu(self.decrypted_text, "descriptografado")
    
    def create_context_menu(self, text_widget, field_name):
        """Cria menu de contexto para copiar texto"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Copiar", command=lambda: self.copy_to_clipboard(text_widget, field_name))
        menu.add_separator()
        menu.add_command(label="Selecionar Tudo", command=lambda: self.select_all_text(None, text_widget))
        
        def show_context_menu(event):
            menu.post(event.x_root, event.y_root)
        
        text_widget.bind('<Button-3>', show_context_menu)  # Botão direito do mouse
        # Para Mac com trackpad
        text_widget.bind('<Control-Button-1>', show_context_menu)
    
    def copy_to_clipboard(self, text_widget, field_name):
        """Copia o texto do widget para a área de transferência"""
        try:
            content = self.get_text_content(text_widget)
            
            # Verificar se há conteúdo válido
            if not content or content in ["Texto criptografado aparecerá aqui", "Texto descriptografado aparecerá aqui"]:
                messagebox.showwarning("Aviso", f"Não há texto {field_name} para copiar!")
                return
            
            # Copiar para a área de transferência
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.root.update()  # Mantém o conteúdo após fechar o app
            
            # Feedback visual no botão
            if field_name == "criptografado":
                original_text = self.copy_encrypt_btn.cget('text')
                self.copy_encrypt_btn.config(text="✓ Copiado!", bg='#86efac', fg='#166534')
                self.root.after(2000, lambda: self.copy_encrypt_btn.config(text=original_text, bg='#f1f5f9', fg='#3b82f6'))
            else:
                original_text = self.copy_decrypt_btn.cget('text')
                self.copy_decrypt_btn.config(text="✓ Copiado!", bg='#86efac', fg='#166534')
                self.root.after(2000, lambda: self.copy_decrypt_btn.config(text=original_text, bg='#f1f5f9', fg='#3b82f6'))
            
            # Feedback no campo
            text_widget.configure(bg='#e0f2fe')
            self.root.after(300, lambda: text_widget.configure(bg='#f1f5f9'))
            
            messagebox.showinfo("Sucesso", f"✅ Texto {field_name} copiado para a área de transferência!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar o texto: {str(e)}")
    
    def encrypt_text(self):
        """Criptografa o texto usando AES"""
        plain_text = self.get_text_content(self.plain_text)
        password = self.encrypt_password.get()
        
        if not plain_text or plain_text == "Digite o texto...":
            messagebox.showwarning("Aviso", "📝 Digite um texto para criptografar")
            self.plain_text.focus()
            return
        
        if not password or password == "Senha":
            messagebox.showwarning("Aviso", "🔑 Digite uma senha")
            self.encrypt_password.focus()
            return
        
        try:
            # Gerar salt aleatório
            salt = os.urandom(16)
            
            # Derivar chave usando PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            
            # Gerar IV aleatório
            iv = os.urandom(16)
            
            # Criar cipher
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            
            # Criptografar
            encrypted = encryptor.update(plain_text.encode('utf-8')) + encryptor.finalize()
            
            # Combinar salt + iv + texto criptografado e codificar em base64
            combined = salt + iv + encrypted
            encrypted_text = base64.b64encode(combined).decode('utf-8')
            
            # Atualizar campo de texto
            self.update_text_field(self.encrypted_text, encrypted_text)
            
            # Feedback visual
            self.encrypted_text.configure(bg='#f0fdf4')
            self.root.after(300, lambda: self.encrypted_text.configure(bg='#f1f5f9'))
            
            messagebox.showinfo("Sucesso", "✅ Texto criptografado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criptografar: {str(e)}")
    
    def decrypt_text(self):
        """Descriptografa o texto usando AES"""
        cipher_text = self.get_text_content(self.cipher_text)
        password = self.decrypt_password.get()
        
        if not cipher_text or cipher_text == "Cole o texto criptografado...":
            messagebox.showwarning("Aviso", "🔐 Cole o texto criptografado")
            self.cipher_text.focus()
            return
        
        if not password or password == "Senha":
            messagebox.showwarning("Aviso", "🔑 Digite a senha")
            self.decrypt_password.focus()
            return
        
        try:
            # Decodificar base64
            combined = base64.b64decode(cipher_text)
            
            # Extrair salt, iv e texto criptografado
            salt = combined[:16]
            iv = combined[16:32]
            encrypted = combined[32:]
            
            # Derivar chave usando PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            key = kdf.derive(password.encode('utf-8'))
            
            # Criar cipher
            cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            
            # Descriptografar
            decrypted = decryptor.update(encrypted) + decryptor.finalize()
            decrypted_text = decrypted.decode('utf-8')
            
            # Atualizar campo de texto
            self.update_text_field(self.decrypted_text, decrypted_text)
            
            # Feedback visual de sucesso
            self.decrypted_text.configure(bg='#f0fdf4')
            self.root.after(300, lambda: self.decrypted_text.configure(bg='#f1f5f9'))
            
            messagebox.showinfo("Sucesso", "✅ Texto descriptografado com sucesso!")
            
        except Exception as e:
            self.update_text_field(self.decrypted_text, "")
            messagebox.showerror("Erro", "❌ Falha na descriptografia. Verifique a senha e o texto.")
            # Feedback visual de erro
            self.decrypted_text.configure(bg='#fef2f2')
            self.root.after(300, lambda: self.decrypted_text.configure(bg='#f1f5f9'))
    
    def get_text_content(self, text_widget):
        """Obtém o conteúdo do widget de texto"""
        content = text_widget.get('1.0', 'end-1c')
        return content.strip()
    
    def update_text_field(self, text_widget, content):
        """Atualiza o campo de texto"""
        text_widget.configure(state='normal')
        text_widget.delete('1.0', 'end')
        text_widget.insert('1.0', content)
        text_widget.configure(state='disabled')
    
    def clear_placeholder(self, event, widget, placeholder):
        """Limpa o placeholder ao focar"""
        if widget.get('1.0', 'end-1c') == placeholder:
            widget.delete('1.0', 'end')
    
    def set_placeholder(self, event, widget, placeholder):
        """Restaura o placeholder se estiver vazio"""
        if not widget.get('1.0', 'end-1c').strip():
            widget.delete('1.0', 'end')
            widget.insert('1.0', placeholder)
    
    def clear_password_placeholder(self, event, widget):
        """Limpa o placeholder da senha ao focar"""
        if widget.get() == "Senha":
            widget.delete(0, 'end')
    
    def set_password_placeholder(self, event, widget):
        """Restaura o placeholder da senha se estiver vazio"""
        if not widget.get():
            widget.insert(0, "Senha")
    
    def select_all_text(self, event, text_widget):
        """Seleciona todo o texto ao clicar"""
        text_widget.configure(state='normal')
        text_widget.tag_add('sel', '1.0', 'end')
        text_widget.configure(state='disabled')
        return 'break'
    
    def setup_events(self):
        """Configura eventos adicionais"""
        # Permitir Ctrl+A para selecionar tudo
        def select_all(event, text_widget):
            text_widget.configure(state='normal')
            text_widget.tag_add('sel', '1.0', 'end')
            text_widget.configure(state='disabled')
            return 'break'
        
        self.encrypted_text.bind('<Control-a>', lambda e: select_all(e, self.encrypted_text))
        self.decrypted_text.bind('<Control-a>', lambda e: select_all(e, self.decrypted_text))
        
        # Permitir Ctrl+C para copiar
        def copy_text(event, text_widget, field_name):
            self.copy_to_clipboard(text_widget, field_name)
            return 'break'
        
        self.encrypted_text.bind('<Control-c>', lambda e: copy_text(e, self.encrypted_text, "criptografado"))
        self.decrypted_text.bind('<Control-c>', lambda e: copy_text(e, self.decrypted_text, "descriptografado"))

def main():
    root = tk.Tk()
    app = CryptoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
