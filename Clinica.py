import sqlite3
import customtkinter as ctk
from tkinter import messagebox, ttk
import pandas as pd
from tkinter import filedialog
from PIL import Image, ImageDraw

# Configurações iniciais
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Funções do banco de dados
def conectar():
    return sqlite3.connect('Banco_clinica.db')

def criar_tabela():
    conn = conectar()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        idade INTEGER NOT NULL,
        peso REAL NOT NULL,
        altura REAL NOT NULL,
        imc TEXT NOT NULL,
        sexo TEXT NOT NULL,
        cpf TEXT NOT NULL UNIQUE
    )
    ''')
    conn.commit()
    conn.close()

def calcular_imc(peso, altura):
    if altura > 0:
        imc = peso / (altura ** 2)
        return f"{imc:.1f} kg/m²"
    return "0.0 kg/m²"

def inserir_paciente():
    nome = entry_nome.get()
    idade = entry_idade.get()
    peso = entry_peso.get()
    altura = entry_altura.get()
    cpf = entry_cpf.get()
    sexo = sexo_var.get()
    
    if nome and idade and peso and altura and cpf and sexo:
        try:
            peso = float(peso)
            altura = float(altura)
            imc = calcular_imc(peso, altura)
            conn = conectar()
            c = conn.cursor()
            c.execute('''
            INSERT INTO pacientes (nome, idade, peso, altura, imc, sexo, cpf)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nome, int(idade), peso, altura, imc, sexo, cpf))
            conn.commit()
            conn.close()
            messagebox.showinfo('Sucesso', 'Paciente cadastrado com sucesso!')
            mostrar_pacientes()
        except sqlite3.IntegrityError:
            messagebox.showerror('Erro', 'CPF já cadastrado!')
    else:
        messagebox.showwarning('Atenção', 'Preencha todos os campos!')

def mostrar_pacientes():
    """Mostra apenas as colunas ID, Nome e Idade na aba de Cadastro."""
    for row in tree_cadastro.get_children():
        tree_cadastro.delete(row)
    
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT id, nome, idade FROM pacientes')  # Apenas essas colunas
    pacientes = c.fetchall()
    
    for paciente in pacientes:
        tree_cadastro.insert("", "end", values=paciente)
    
    conn.close()



def gerar_relatorio():
    """Gera um relatório com todas as colunas e adiciona botões de Editar e Excluir."""
    relatorio_janela = ctk.CTk()
    relatorio_janela.title("Relatório de Pacientes")
    relatorio_janela.geometry("800x350")

    columns = ('ID', 'Nome', 'Idade', 'Peso', 'Altura', 'IMC', 'Sexo', 'CPF')
    tree_relatorio = ttk.Treeview(relatorio_janela, columns=columns, show='headings')
    tree_relatorio.grid(row=0, columnspan=3, pady=10, sticky="nsew")

    # Ajustando as colunas
    tree_relatorio.heading("ID", text="ID")
    tree_relatorio.column("ID", width=50, anchor="center")
    tree_relatorio.heading("Nome", text="Nome")
    tree_relatorio.column("Nome", width=200, anchor="center")
    tree_relatorio.heading("Idade", text="Idade")
    tree_relatorio.column("Idade", width=80, anchor="center")
    tree_relatorio.heading("Peso", text="Peso (kg)")
    tree_relatorio.column("Peso", width=80, anchor="center")
    tree_relatorio.heading("Altura", text="Altura (m)")
    tree_relatorio.column("Altura", width=80, anchor="center")
    tree_relatorio.heading("IMC", text="IMC")
    tree_relatorio.column("IMC", width=100, anchor="center")
    tree_relatorio.heading("Sexo", text="Sexo")
    tree_relatorio.column("Sexo", width=80, anchor="center")
    tree_relatorio.heading("CPF", text="CPF")
    tree_relatorio.column("CPF", width=120, anchor="center")

    # Preencher a tabela com os dados
    conn = conectar()
    c = conn.cursor()
    c.execute('SELECT * FROM pacientes')
    pacientes = c.fetchall()
    
    for paciente in pacientes:
        tree_relatorio.insert("", "end", values=paciente)
    
    conn.close()

    # Função para excluir paciente
    def excluir_paciente():
        try:
            selecionado = tree_relatorio.selection()[0]
            valores = tree_relatorio.item(selecionado, "values")
            paciente_id = valores[0]

            resposta = messagebox.askyesno("Confirmação", "Deseja excluir este paciente?")
            if resposta:
                conn = conectar()
                c = conn.cursor()
                c.execute("DELETE FROM pacientes WHERE id=?", (paciente_id,))
                conn.commit()
                conn.close()
                tree_relatorio.delete(selecionado)
                messagebox.showinfo("Sucesso", "Paciente excluído com sucesso!")
        except IndexError:
            messagebox.showwarning("Atenção", "Selecione um paciente para excluir!")

    # Função para editar paciente
    def editar_paciente():
        try:
            selecionado = tree_relatorio.selection()[0]
            valores = tree_relatorio.item(selecionado, "values")
            paciente_id, nome, idade, peso, altura, imc, sexo, cpf = valores

            # Criar janela de edição
            editar_janela = ctk.CTkToplevel(relatorio_janela)
            editar_janela.title("Editar Paciente")
            editar_janela.geometry("300x450")

            # Campos de entrada para edição
            ctk.CTkLabel(editar_janela, text="Nome:").pack(pady=5)
            entry_nome = ctk.CTkEntry(editar_janela)
            entry_nome.insert(0, nome)
            entry_nome.pack(pady=5)

            ctk.CTkLabel(editar_janela, text="Idade:").pack(pady=5)
            entry_idade = ctk.CTkEntry(editar_janela)
            entry_idade.insert(0, idade)
            entry_idade.pack(pady=5)

            ctk.CTkLabel(editar_janela, text="Peso (kg):").pack(pady=5)
            entry_peso = ctk.CTkEntry(editar_janela)
            entry_peso.insert(0, peso)
            entry_peso.pack(pady=5)

            ctk.CTkLabel(editar_janela, text="Altura (m):").pack(pady=5)
            entry_altura = ctk.CTkEntry(editar_janela)
            entry_altura.insert(0, altura)
            entry_altura.pack(pady=5)

            ctk.CTkLabel(editar_janela, text="Sexo:").pack(pady=5)
            sexo_var = ctk.StringVar(value=sexo)
            option_sexo = ctk.CTkOptionMenu(editar_janela, variable=sexo_var, values=["Masculino", "Feminino"])
            option_sexo.pack(pady=5)

            # Função para salvar alterações
            def salvar_edicao():
                novo_nome = entry_nome.get()
                nova_idade = entry_idade.get()
                novo_peso = entry_peso.get()
                nova_altura = entry_altura.get()
                novo_sexo = sexo_var.get()

                if novo_nome and nova_idade and novo_peso and nova_altura:
                    novo_imc = calcular_imc(float(novo_peso), float(nova_altura))

                    conn = conectar()
                    c = conn.cursor()
                    c.execute('''
                        UPDATE pacientes
                        SET nome=?, idade=?, peso=?, altura=?, imc=?, sexo=?
                        WHERE id=?
                    ''', (novo_nome, nova_idade, novo_peso, nova_altura, novo_imc, novo_sexo, paciente_id))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Sucesso", "Paciente atualizado com sucesso!")
                    editar_janela.destroy()
                    relatorio_janela.destroy()
                    gerar_relatorio()  # Atualiza a janela com os dados editados
                else:
                    messagebox.showwarning("Atenção", "Preencha todos os campos!")

            # Botão para salvar edição
            ctk.CTkButton(editar_janela, text="Salvar Alterações", command=salvar_edicao).pack(pady=20)

        except IndexError:
            messagebox.showwarning("Atenção", "Selecione um paciente para editar!")
    
    #     def exportar_para_excel():
    #      """Exporta os dados do relatório para um arquivo Excel."""
    #         #Obter os dados do Treeview
    #      dados = []
    #      for item in tree_relatorio.get_children():
    #      valores = tree_relatorio.item(item, "values")
    #      dados.append(valores)
    
    #  # Criar um DataFrame do pandas
    #     colunas = ['ID', 'Nome', 'Idade', 'Peso', 'Altura', 'IMC', 'Sexo', 'CPF']
    #     df = pd.DataFrame(dados, columns=colunas)

    #   #Abrir um diálogo para escolher onde salvar o arquivo
    #      arquivo_excel = filedialog.asksaveasfilename(
    #      defaultextension=".xlsx",
    #      filetypes=[("Planilha Excel", "*.xlsx")],
    #      title="Salvar Relatório"
    #  )

    #  if arquivo_excel:  # Se o usuário escolher um local, salvar o arquivo
    #      df.to_excel(arquivo_excel, index=False, engine='openpyxl')
    #      messagebox.showinfo("Sucesso", "Relatório exportado para Excel com sucesso!")

   # Criando um frame para os botões e alinhando à direita
    frame_botoes = ctk.CTkFrame(relatorio_janela)
    frame_botoes.grid(row=1, column=2, pady=10, sticky="e")

    # Botão Editar
    btn_editar = ctk.CTkButton(frame_botoes, text="Editar", command=editar_paciente, width=120, height=40)
    btn_editar.pack(side="right", padx=5)

    # Botão Excluir
    btn_excluir = ctk.CTkButton(frame_botoes, text="Excluir", command=excluir_paciente, width=120, height=40)
    btn_excluir.pack(side="right")
    
    # #Botão para exportar relatório
    # btn_exportar = ctk.CTkButton(frame_botoes, text="Exportar para Excel", command=exportar_para_excel, width=180, height=40)
    # btn_exportar.pack(side="right", padx=5)

    relatorio_janela.mainloop()


def iniciar_sistema():
    global entry_nome, entry_idade, entry_peso, entry_altura, entry_cpf, tree_cadastro, sexo_var
    
    janela = ctk.CTk()
    janela.title('Clínica VidaPlena')
    janela.geometry("380x585")
    
    # Criando o gerenciador de abas
    abas = ctk.CTkTabview(janela)
    abas.grid(row=0, column=0, padx=10, pady=10, sticky="nw")  # Alinha as abas à esquerda
    
    # Criando as abas
    abas.add("Cadastro")
    abas.add("Relatório")
    
    # -------------------------
    # ABA CADASTRO
    cadastro_frame = abas.tab("Cadastro")
    
    campos = [
        ("Nome", "entry_nome"),
        ("Idade", "entry_idade"),
        ("Peso (kg)", "entry_peso"),
        ("Altura (m)", "entry_altura"),
        ("CPF", "entry_cpf"),
    ]
    
    for i, (label_text, var_name) in enumerate(campos):
        label = ctk.CTkLabel(cadastro_frame, text=label_text + ":")
        label.grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = ctk.CTkEntry(cadastro_frame, width=250)
        entry.grid(row=i, column=1, padx=10, pady=5)
        globals()[var_name] = entry

    # Adicionando opção de gênero
    ctk.CTkLabel(cadastro_frame, text="Sexo:").grid(row=len(campos), column=0, padx=10, pady=5, sticky="w")
    sexo_var = ctk.StringVar(value="Masculino")
    ctk.CTkOptionMenu(cadastro_frame, variable=sexo_var, values=["Masculino", "Feminino"]).grid(row=len(campos), column=1, padx=10, pady=5, sticky="e")


    # Botão Salvar
    ctk.CTkButton(cadastro_frame, text='Salvar', command=inserir_paciente).grid(row=len(campos) + 1, column=1, padx=10, pady=10, sticky="e")
    
  # Tabela (Treeview) na aba Cadastro mostrando apenas ID, Nome e Idade
    tree_cadastro = ttk.Treeview(cadastro_frame, columns=("ID", "Nome", "Idade"), show="headings")
    tree_cadastro.grid(row=len(campos) + 2, columnspan=2, pady=10, sticky="nsew")

   
    tree_cadastro.heading("ID", text="ID")
    tree_cadastro.column("ID", width=40, anchor="center")  

    tree_cadastro.heading("Nome", text="Nome")
    tree_cadastro.column("Nome", width=250, anchor="center") 

    tree_cadastro.heading("Idade", text="Idade")
    tree_cadastro.column("Idade", width=50, anchor="center") 

    for col in tree_cadastro["columns"]:
        tree_cadastro.heading(col, text=col)
        tree_cadastro.column(col, width=100, stretch=True)

    # -------------------------
    # ABA RELATÓRIO
    relatorio_frame = abas.tab("Relatório")
    ctk.CTkButton(relatorio_frame, text="Gerar Relatório", command=gerar_relatorio).grid(row=0, column=0, pady=10)

    criar_tabela()
    mostrar_pacientes()
    
    janela.mainloop()

def janela_login():
    global login_janela, campo_usuario, campo_senha, resultando_login

    # login_janela = ctk.CTk()
    # login_janela.title("Login")
    # login_janela.geometry("320x240")  # Ajustando o tamanho da tela de login

    ctk.CTkLabel(login_janela, text="Usuário:").grid(row=0, column=0, padx=10, pady=20, sticky="w")
    campo_usuario = ctk.CTkEntry(login_janela, width=200)
    campo_usuario.grid(row=0, column=1, padx=20, pady=10)

    ctk.CTkLabel(login_janela, text="Senha:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    campo_senha = ctk.CTkEntry(login_janela, show="*", width=200)
    campo_senha.grid(row=1, column=1, padx=10, pady=10)

    # Botão "Entrar"
    ctk.CTkButton(login_janela, text="Entrar", command=validar_login, width=150, height=40).grid(row=2, column=1, columnspan=2, pady=12)

    # Mensagem de erro abaixo do botão
    resultando_login = ctk.CTkLabel(login_janela, text="")
    resultando_login.grid(row=3, column=1, columnspan=2, pady=10)

    login_janela.mainloop()

def validar_login():
    global login_janela
    usuario = campo_usuario.get()
    senha = campo_senha.get()
    if usuario == "felipe" and senha == "1234":
        login_janela.destroy()
        iniciar_sistema()
    else:
        resultando_login.configure(text='Login incorreto!', text_color='red')


# Criando a janela de login
login_janela = ctk.CTk()
login_janela.title('Login')
login_janela.geometry('340x390')  # Aumentei a altura para caber a logo

# trabalando com teste de inserir imagem de logo na tela de login
# Caminho da imagem original
# caminho_imagem = "C:/Users/User/Desktop/projeto_clinica/Projet_clinica/Logo_clinica.png"

# # Abrindo a imagem
# imagem = Image.open(caminho_imagem).convert("RGBA")

# # Criando uma máscara circular
# mascara = Image.new("L", imagem.size, 0)
# draw = ImageDraw.Draw(mascara)
# tamanho = min(imagem.size)  # Tamanho do círculo
# draw.ellipse((0, 0, tamanho, tamanho), fill=255)

# # Aplicando a máscara na imagem
# imagem_redonda = Image.new("RGBA", imagem.size, (0, 0, 0, 0))
# imagem_redonda.paste(imagem, mask=mascara)

# # Salvando ou carregando diretamente no CustomTkinter
# imagem_redonda.save("C:/Users/User/Desktop/projeto_clinica/Projet_clinica/Logo_clinica_redonda.png")



# # Carregar a imagem da logo
imagem_logo = ctk.CTkImage(light_image=Image.open("C:/Users/User/Desktop/projeto_clinica/Projet_clinica/Logo_clinica_redonda.png"), size=(150, 150))

 # Exibir a imagem na tela de login
label_logo = ctk.CTkLabel(login_janela, image=imagem_logo, text="")  # Define text="" para exibir apenas a imagem
label_logo.pack(pady=10)  # Espaçamento da logo

# Campos de login
campo_usuario = ctk.CTkEntry(login_janela, placeholder_text='Usuário')
campo_usuario.pack(pady=10)

campo_senha = ctk.CTkEntry(login_janela, placeholder_text='Senha', show="*")
campo_senha.pack(pady=10)

ctk.CTkButton(login_janela, text='Login', command=validar_login).pack(pady=10)

resultando_login = ctk.CTkLabel(login_janela, text='')
resultando_login.pack(pady=5)

login_janela.mainloop()



janela_login()
