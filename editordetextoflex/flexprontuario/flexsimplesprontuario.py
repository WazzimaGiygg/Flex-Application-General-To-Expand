import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from cryptography.fernet import Fernet
import base64
import hashlib
import os
from datetime import datetime

class ProntuarioManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciamento de Prontuários")
        self.root.geometry("1200x800")
        
        # Desabilitar menu de contexto
        self.root.bind("<Button-3>", lambda e: "break")
        
        # Estrutura de dados
        self.data = {
            'title': 'Novo Prontuário',
            'description': '',
            'sections': []
        }
        self.current_file = None
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar menu
        self.create_menu()
        
        # Criar interface
        self.create_widgets()
        
        # Atualizar título da janela
        self.update_window_title()
        
    def setup_styles(self):
        # Configurar cores
        self.bg_color = "#f4f4f4"
        self.button_color = "#007BFF"
        self.button_hover = "#0056b3"
        
        self.root.configure(bg=self.bg_color)
        
        # Criar estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('Custom.TButton', 
                       background=self.button_color,
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       padding=6)
        style.map('Custom.TButton',
                 background=[('active', self.button_hover)])
        
        style.configure('Editor.TFrame', background='white')
        
        # Configurar fontes para LabelFrame
        style.configure('TLabelframe', background='#f4f4f4')
        style.configure('TLabelframe.Label', background='#f4f4f4', foreground='#333', font=('Arial', 10, 'bold'))
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo Prontuário", command=self.new_document, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.load, accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar", command=self.save, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Como", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Ferramentas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ferramentas", menu=tools_menu)
        tools_menu.add_command(label="Salvar com Criptografia", command=self.save_encrypted)
        tools_menu.add_command(label="Abrir com Criptografia", command=self.load_encrypted)
        tools_menu.add_separator()
        tools_menu.add_command(label="Imprimir", command=self.print_document)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
        
        # Atalhos de teclado
        self.root.bind_all("<Control-n>", lambda e: self.new_document())
        self.root.bind_all("<Control-o>", lambda e: self.load())
        self.root.bind_all("<Control-s>", lambda e: self.save())
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Editor container
        editor_frame = ttk.Frame(main_frame, style='Editor.TFrame')
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Informações do prontuário
        info_frame = ttk.Frame(editor_frame)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Título do prontuário
        title_label = tk.Label(info_frame, text="Título do Prontuário:", 
                              font=('Arial', 12, 'bold'), bg='white')
        title_label.pack(anchor=tk.W)
        
        self.title_entry = ttk.Entry(info_frame, width=50, font=('Arial', 14))
        self.title_entry.pack(fill=tk.X, pady=(0, 10))
        self.title_entry.bind('<KeyRelease>', self.update_title)
        
        # Descrição
        desc_label = tk.Label(info_frame, text="Descrição:", 
                             font=('Arial', 10, 'bold'), bg='white')
        desc_label.pack(anchor=tk.W)
        
        self.description_text = ScrolledText(info_frame, height=4, width=50, 
                                            font=('Arial', 10), bg='white')
        self.description_text.pack(fill=tk.X, pady=(0, 10))
        self.description_text.bind('<KeyRelease>', self.update_description)
        
        # Separador
        ttk.Separator(editor_frame, orient='horizontal').pack(fill=tk.X, padx=10, pady=5)
        
        # Novo item container
        new_item_frame = ttk.LabelFrame(editor_frame, text="Adicionar Nova Seção")
        new_item_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Linha para título e formato
        title_row = ttk.Frame(new_item_frame)
        title_row.pack(fill=tk.X, pady=5, padx=5)
        
        title_label = tk.Label(title_row, text="Título da seção:", bg='#f4f4f4')
        title_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.section_title = ttk.Entry(title_row, width=40)
        self.section_title.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        format_label = tk.Label(title_row, text="Formato:", bg='#f4f4f4')
        format_label.pack(side=tk.LEFT, padx=(10, 5))
        
        self.title_format = ttk.Combobox(title_row, 
                                        values=["Título 1 (Principal)", "Título 2 (Subseção)", "Parágrafo"], 
                                        state="readonly", width=20)
        self.title_format.pack(side=tk.LEFT)
        self.title_format.set("Título 1 (Principal)")
        
        content_label = tk.Label(new_item_frame, text="Conteúdo da seção:", bg='#f4f4f4')
        content_label.pack(anchor=tk.W, pady=(10, 5), padx=5)
        
        self.section_content = ScrolledText(new_item_frame, height=8, width=50, 
                                           font=('Arial', 10), bg='white')
        self.section_content.pack(fill=tk.X, pady=(0, 5), padx=5)
        
        # Botão adicionar seção
        add_btn_frame = ttk.Frame(new_item_frame)
        add_btn_frame.pack(pady=10)
        
        add_item_btn = ttk.Button(add_btn_frame, text="➕ Adicionar Seção", 
                                  command=self.add_section, style='Custom.TButton', width=20)
        add_item_btn.pack()
        
        # Lista de seções
        sections_frame = ttk.LabelFrame(editor_frame, text="Seções do Prontuário")
        sections_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas e scrollbar para a lista de seções
        canvas = tk.Canvas(sections_frame, bg='white')
        scrollbar = ttk.Scrollbar(sections_frame, orient="vertical", command=canvas.yview)
        self.sections_container = ttk.Frame(canvas)
        
        self.sections_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.sections_container, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Atualizar largura do canvas quando redimensionado
        def configure_canvas(event):
            canvas.itemconfig(1, width=event.width)
        
        canvas.bind("<Configure>", configure_canvas)
        
        # Botões principais
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        buttons = [
            ("💾 Salvar", self.save),
            ("🔒 Salvar Criptografado", self.save_encrypted),
            ("📂 Abrir", self.load),
            ("🔓 Abrir Criptografado", self.load_encrypted),
            ("🖨️ Imprimir", self.print_document)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(buttons_frame, text=text, command=command, style='Custom.TButton')
            btn.pack(side=tk.LEFT, padx=2)
        
        # Campo de senha
        password_frame = ttk.Frame(main_frame)
        password_frame.pack(fill=tk.X, pady=5)
        
        password_label = tk.Label(password_frame, text="Senha para criptografia:", bg='#f4f4f4')
        password_label.pack(side=tk.LEFT, padx=5)
        
        self.password_entry = ttk.Entry(password_frame, show="*", width=25)
        self.password_entry.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W, bg='#e0e0e0')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def new_document(self):
        """Criar um novo prontuário"""
        if self.data['sections'] and messagebox.askyesno("Novo Prontuário", 
                                                         "Tem certeza? Todas as alterações não salvas serão perdidas!"):
            self.data = {
                'title': 'Novo Prontuário',
                'description': '',
                'sections': []
            }
            self.current_file = None
            
            # Limpar campos
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, 'Novo Prontuário')
            self.description_text.delete(1.0, tk.END)
            
            # Atualizar lista
            self.refresh_sections_list()
            self.update_window_title()
            self.status_bar.config(text="Novo prontuário criado")
            
    def update_title(self, event=None):
        """Atualizar título do prontuário"""
        self.data['title'] = self.title_entry.get()
        self.update_window_title()
        
    def update_description(self, event=None):
        """Atualizar descrição do prontuário"""
        self.data['description'] = self.description_text.get(1.0, tk.END).strip()
        
    def update_window_title(self):
        """Atualizar título da janela"""
        title = self.data.get('title', 'Prontuário')
        if self.current_file:
            self.root.title(f"{title} - {os.path.basename(self.current_file)}")
        else:
            self.root.title(f"{title} - Gerenciamento de Prontuários")
            
    def add_section(self):
        """Adicionar nova seção"""
        title = self.section_title.get().strip()
        format_text = self.title_format.get()
        content = self.section_content.get(1.0, tk.END).strip()
        
        if title or content:
            # Mapear formato
            format_map = {
                "Título 1 (Principal)": "h1",
                "Título 2 (Subseção)": "h2",
                "Parágrafo": "p"
            }
            
            new_section = {
                'title': title if title else "Seção sem título",
                'titleFormat': format_map.get(format_text, "h1"),
                'content': content if content else "Sem conteúdo"
            }
            
            self.data['sections'].append(new_section)
            
            # Limpar campos
            self.section_title.delete(0, tk.END)
            self.section_content.delete(1.0, tk.END)
            
            # Atualizar lista
            self.refresh_sections_list()
            self.status_bar.config(text="Seção adicionada com sucesso")
        else:
            messagebox.showwarning("Aviso", "Digite pelo menos um título ou conteúdo para a seção!")
            
    def refresh_sections_list(self):
        """Atualizar lista de seções"""
        # Limpar container
        for widget in self.sections_container.winfo_children():
            widget.destroy()
        
        # Adicionar cada seção
        for i, section in enumerate(self.data['sections']):
            section_frame = tk.Frame(self.sections_container, relief=tk.RIDGE, borderwidth=1, bg='#f9f9f9')
            section_frame.pack(fill=tk.X, pady=5, padx=5)
            
            # Cabeçalho com título e botão remover
            header_frame = tk.Frame(section_frame, bg='#f9f9f9')
            header_frame.pack(fill=tk.X, padx=5, pady=2)
            
            # Título com formatação
            if section['titleFormat'] == 'h1':
                title_font = ('Arial', 14, 'bold')
                title_color = '#0066CC'
            elif section['titleFormat'] == 'h2':
                title_font = ('Arial', 12, 'bold')
                title_color = '#0099CC'
            else:
                title_font = ('Arial', 11)
                title_color = '#666666'
                
            title_label = tk.Label(header_frame, text=section['title'], 
                                  font=title_font, fg=title_color, bg='#f9f9f9')
            title_label.pack(side=tk.LEFT)
            
            # Botão remover
            remove_btn = ttk.Button(header_frame, text="Remover", 
                                   command=lambda idx=i: self.remove_section(idx))
            remove_btn.pack(side=tk.RIGHT)
            
            # Conteúdo
            content_text = ScrolledText(section_frame, height=min(8, max(3, section['content'].count('\n') + 2)), 
                                       width=50, font=('Arial', 10), bg='white')
            content_text.insert(1.0, section['content'])
            content_text.configure(state='disabled')
            content_text.pack(fill=tk.X, padx=5, pady=5)
            
    def remove_section(self, index):
        """Remover seção específica"""
        if messagebox.askyesno("Remover Seção", "Deseja remover esta seção?"):
            del self.data['sections'][index]
            self.refresh_sections_list()
            self.status_bar.config(text="Seção removida")
            
    def save(self):
        """Salvar prontuário"""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_as()
            
    def save_as(self):
        """Salvar prontuário como"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.save_to_file(file_path)
            
    def save_to_file(self, file_path):
        """Salvar dados em arquivo"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
                
            self.current_file = file_path
            self.update_window_title()
            self.status_bar.config(text=f"Arquivo salvo: {os.path.basename(file_path)}")
            messagebox.showinfo("Sucesso", "Prontuário salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
                
    def save_encrypted(self):
        """Salvar prontuário criptografado"""
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Aviso", "Digite uma senha para criptografar!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".enc",
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                json_data = json.dumps(self.data, ensure_ascii=False)
                
                # Criptografar
                key = hashlib.sha256(password.encode()).digest()
                fernet_key = base64.urlsafe_b64encode(key[:32])
                cipher = Fernet(fernet_key)
                
                encrypted_data = cipher.encrypt(json_data.encode('utf-8'))
                
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
                    
                self.status_bar.config(text=f"Arquivo criptografado salvo: {os.path.basename(file_path)}")
                messagebox.showinfo("Sucesso", "Prontuário criptografado salvo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo criptografado: {str(e)}")
                
    def load(self):
        """Carregar prontuário"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            self.load_from_file(file_path)
            
    def load_from_file(self, file_path):
        """Carregar dados de arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            self.data = loaded_data
            
            # Atualizar interface
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, self.data.get('title', 'Prontuário'))
            
            self.description_text.delete(1.0, tk.END)
            self.description_text.insert(1.0, self.data.get('description', ''))
            
            self.refresh_sections_list()
            
            self.current_file = file_path
            self.update_window_title()
            self.status_bar.config(text=f"Arquivo carregado: {os.path.basename(file_path)}")
            messagebox.showinfo("Sucesso", "Prontuário carregado com sucesso!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar arquivo: {str(e)}")
                
    def load_encrypted(self):
        """Carregar prontuário criptografado"""
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Aviso", "Digite a senha para descriptografar!")
            return
            
        file_path = filedialog.askopenfilename(
            filetypes=[("Encrypted files", "*.enc"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    encrypted_data = f.read()
                
                # Descriptografar
                key = hashlib.sha256(password.encode()).digest()
                fernet_key = base64.urlsafe_b64encode(key[:32])
                cipher = Fernet(fernet_key)
                
                decrypted_data = cipher.decrypt(encrypted_data)
                loaded_data = json.loads(decrypted_data.decode('utf-8'))
                
                self.data = loaded_data
                
                # Atualizar interface
                self.title_entry.delete(0, tk.END)
                self.title_entry.insert(0, self.data.get('title', 'Prontuário'))
                
                self.description_text.delete(1.0, tk.END)
                self.description_text.insert(1.0, self.data.get('description', ''))
                
                self.refresh_sections_list()
                
                self.current_file = file_path
                self.update_window_title()
                self.status_bar.config(text=f"Arquivo criptografado carregado: {os.path.basename(file_path)}")
                messagebox.showinfo("Sucesso", "Prontuário criptografado carregado com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar arquivo criptografado: {str(e)}")
                
    def print_document(self):
        """Imprimir prontuário"""
        if not self.data['sections']:
            messagebox.showwarning("Aviso", "Não há seções para imprimir!")
            return
            
        # Criar janela de visualização de impressão
        print_window = tk.Toplevel(self.root)
        print_window.title(f"Visualização de Impressão - {self.data['title']}")
        print_window.geometry("800x600")
        
        # Text widget para conteúdo
        text_widget = ScrolledText(print_window, wrap=tk.WORD, font=('Arial', 10))
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Preparar conteúdo
        content = f"\n{'='*70}\n"
        content += f"{self.data['title'].upper()}\n"
        content += f"{'='*70}\n\n"
        
        if self.data['description']:
            content += f"Descrição:\n{self.data['description']}\n\n"
        
        content += f"{'─'*70}\n\n"
        
        for i, section in enumerate(self.data['sections'], 1):
            if section['titleFormat'] == 'h1':
                content += f"\n{section['title'].upper()}\n"
                content += f"{'─'*50}\n"
            elif section['titleFormat'] == 'h2':
                content += f"\n{section['title']}\n"
                content += f"{'─'*40}\n"
            else:
                content += f"\n{section['title']}\n"
            
            content += f"\n{section['content']}\n"
            content += f"\n{'─'*50}\n"
        
        text_widget.insert(1.0, content)
        text_widget.configure(state='disabled')
        
        # Botão para imprimir
        def print_content():
            try:
                text_widget.configure(state='normal')
                text_widget.event_generate("<<Print>>")
                text_widget.configure(state='disabled')
            except:
                messagebox.showinfo("Impressão", "Selecione a impressora na janela que aparecerá.")
                
        print_btn = ttk.Button(print_window, text="🖨️ Imprimir", command=print_content)
        print_btn.pack(pady=10)
        
    def show_about(self):
        """Mostrar informações sobre o programa"""
        about_text = """Gerenciamento de Prontuários
Versão 2.0 - Single Document Mode

Um sistema completo para gerenciamento de prontuários com:
• Título e descrição do documento
• Seções organizadas com formatação hierárquica
• Suporte a criptografia (AES-256)
• Impressão com visualização
• Salvamento em JSON

Funcionalidades:
• Adicionar/remover seções
• Três níveis de formatação (Título 1, Título 2, Parágrafo)
• Salvar com ou sem criptografia
• Atalhos de teclado (Ctrl+N, Ctrl+O, Ctrl+S)

Desenvolvido em Python com Tkinter"""
        
        messagebox.showinfo("Sobre", about_text)

def main():
    root = tk.Tk()
    app = ProntuarioManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()
