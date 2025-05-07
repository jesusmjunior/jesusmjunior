import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from PIL import Image
import io
import uuid

# Configuração da página
st.set_page_config(
    page_title="Jarvis IMEI - Visitas Detalhadas",
    page_icon="🗺️",
    layout="wide"
)

# Função para criar banco de dados e tabelas
def inicializar_banco():
    conn = sqlite3.connect('jarvis_imei.db')
    cursor = conn.cursor()
    
    # Criar tabela VisitasDB se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS VisitasDB (
        id_visita TEXT PRIMARY KEY,
        nome_local TEXT,
        data DATE,
        compromisso TEXT,
        foto BLOB,
        id_projeto TEXT
    )
    ''')
    
    # Criar tabela ProjetosDB se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ProjetosDB (
        id_projeto TEXT PRIMARY KEY,
        nome_projeto TEXT,
        descricao TEXT
    )
    ''')
    
    # Criar tabela ContatosDB se não existir
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ContatosDB (
        id_contato TEXT PRIMARY KEY,
        nome_contato TEXT,
        telefone TEXT,
        email TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

# Inicializa o banco de dados
inicializar_banco()

# Funções para o banco de dados
def adicionar_visita(id_visita, nome_local, data, compromisso, foto, id_projeto):
    """Adiciona uma nova visita ao banco de dados"""
    conn = sqlite3.connect('jarvis_imei.db')
    cursor = conn.cursor()
    
    # Convertendo a imagem para BLOB se for fornecida
    foto_blob = None
    if foto is not None:
        foto_blob = foto.getvalue()
    
    # Inserir na tabela VisitasDB
    cursor.execute('''
    INSERT INTO VisitasDB (id_visita, nome_local, data, compromisso, foto, id_projeto)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (id_visita, nome_local, data, compromisso, foto_blob, id_projeto))
    
    conn.commit()
    conn.close()
    return True

def listar_visitas():
    """Retorna todas as visitas cadastradas"""
    conn = sqlite3.connect('jarvis_imei.db')
    df = pd.read_sql_query("SELECT * FROM VisitasDB", conn)
    conn.close()
    return df

def obter_detalhes_visita(id_visita):
    """Obtém os detalhes de uma visita específica"""
    conn = sqlite3.connect('jarvis_imei.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM VisitasDB WHERE id_visita = ?", (id_visita,))
    visita = cursor.fetchone()
    
    # Consultar detalhes do projeto relacionado
    if visita and visita[5]:  # Se tem id_projeto
        cursor.execute("SELECT * FROM ProjetosDB WHERE id_projeto = ?", (visita[5],))
        projeto = cursor.fetchone()
    else:
        projeto = None
    
    # Consultar contatos associados ao projeto
    contatos = None
    if visita and visita[5]:
        cursor.execute('''
        SELECT c.* FROM ContatosDB c
        JOIN ProjetosDB p ON c.id_projeto = p.id_projeto
        WHERE p.id_projeto = ?
        ''', (visita[5],))
        contatos = cursor.fetchall()
    
    conn.close()
    return visita, projeto, contatos

def adicionar_projeto(id_projeto, nome_projeto, descricao):
    """Adiciona um novo projeto ao banco de dados"""
    conn = sqlite3.connect('jarvis_imei.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO ProjetosDB (id_projeto, nome_projeto, descricao)
    VALUES (?, ?, ?)
    ''', (id_projeto, nome_projeto, descricao))
    
    conn.commit()
    conn.close()
    return True

def listar_projetos():
    """Lista todos os projetos disponíveis"""
    conn = sqlite3.connect('jarvis_imei.db')
    df = pd.read_sql_query("SELECT * FROM ProjetosDB", conn)
    conn.close()
    return df

def adicionar_contato(id_contato, nome_contato, telefone, email, id_projeto=None):
    """Adiciona um novo contato ao banco de dados"""
    conn = sqlite3.connect('jarvis_imei.db')
    cursor = conn.cursor()
    
    # Alterar a tabela ContatosDB para incluir id_projeto se necessário
    cursor.execute("PRAGMA table_info(ContatosDB)")
    colunas = cursor.fetchall()
    colunas_nomes = [col[1] for col in colunas]
    
    if "id_projeto" not in colunas_nomes:
        cursor.execute("ALTER TABLE ContatosDB ADD COLUMN id_projeto TEXT")
    
    cursor.execute('''
    INSERT INTO ContatosDB (id_contato, nome_contato, telefone, email, id_projeto)
    VALUES (?, ?, ?, ?, ?)
    ''', (id_contato, nome_contato, telefone, email, id_projeto))
    
    conn.commit()
    conn.close()
    return True

def listar_contatos():
    """Lista todos os contatos disponíveis"""
    conn = sqlite3.connect('jarvis_imei.db')
    df = pd.read_sql_query("SELECT * FROM ContatosDB", conn)
    conn.close()
    return df

# Interfaces de usuário
def cadastrar_visita_ui():
    """Interface para cadastro de visitas"""
    with st.form("formulario_visita"):
        # Gerar ID único para a visita
        id_visita = f"V{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        col1, col2 = st.columns(2)
        
        with col1:
            nome_local = st.text_input("Nome do Local")
            data = st.date_input("Data da Visita")
        
        with col2:
            compromisso = st.text_area("Descrição do Compromisso")
        
        # Upload de foto
        foto_file = st.file_uploader("Foto do Local", type=["jpg", "jpeg", "png"])
        
        # Selecionar projeto relacionado
        projetos_df = listar_projetos()
        if not projetos_df.empty:
            projetos = projetos_df["id_projeto"].tolist()
            projetos_nomes = projetos_df["nome_projeto"].tolist()
            opcoes_projetos = [f"{id} - {nome}" for id, nome in zip(projetos, projetos_nomes)]
            
            projeto_selecionado = st.selectbox(
                "Projeto Relacionado", 
                options=opcoes_projetos
            )
            
            # Extrair o ID do projeto da opção selecionada
            id_projeto = projeto_selecionado.split(" - ")[0]
        else:
            id_projeto = None
            st.warning("Não há projetos cadastrados. Você pode cadastrar um projeto na seção 'Gerenciar Projetos'.")
        
        submitted = st.form_submit_button("Cadastrar Visita")
        
        if submitted:
            if nome_local and data:
                # Processar a foto se foi enviada
                foto_bytes = None
                if foto_file is not None:
                    foto_bytes = foto_file
                
                # Salvar no banco
                if adicionar_visita(id_visita, nome_local, data, compromisso, foto_bytes, id_projeto):
                    st.success(f"Visita a {nome_local} cadastrada com sucesso!")
                    # Limpar o formulário usando rerun
                    st.experimental_rerun()
            else:
                st.error("Nome do local e data são obrigatórios.")

def visualizar_visitas_ui():
    """Interface para visualização das visitas"""
    # Listar todas as visitas
    try:
        visitas_df = listar_visitas()
        
        if not visitas_df.empty:
            # Converter a coluna de foto para indicar se existe ou não
            visitas_df["tem_foto"] = visitas_df["foto"].apply(lambda x: "Sim" if x is not None else "Não")
            
            # Remover a coluna BLOB da foto para exibição
            visitas_display = visitas_df[["id_visita", "nome_local", "data", "compromisso", "tem_foto", "id_projeto"]]
            st.dataframe(visitas_display)
            
            # Selecionar uma visita para ver detalhes
            visita_selecionada = st.selectbox(
                "Selecione uma visita para ver detalhes",
                options=visitas_df["id_visita"].tolist()
            )
            
            if visita_selecionada:
                visita, projeto, contatos = obter_detalhes_visita(visita_selecionada)
                
                if visita:
                    st.subheader(f"Detalhes da Visita: {visita[1]}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Data:** {visita[2]}")
                        st.write(f"**Compromisso:** {visita[3]}")
                        if projeto:
                            st.write(f"**Projeto:** {projeto[1]}")
                            st.write(f"**Descrição do Projeto:** {projeto[2]}")
                        
                        # Exibir contatos relacionados
                        if contatos:
                            st.subheader("Contatos Associados")
                            for contato in contatos:
                                st.write(f"**Nome:** {contato[1]}")
                                st.write(f"**Telefone:** {contato[2]}")
                                st.write(f"**Email:** {contato[3]}")
                    
                    with col2:
                        if visita[4]:  # Se tem foto
                            try:
                                img = Image.open(io.BytesIO(visita[4]))
                                st.image(img, caption=f"Foto de {visita[1]}")
                            except Exception as e:
                                st.error(f"Erro ao exibir a imagem: {e}")
                        else:
                            st.info("Não há foto para esta visita.")
        else:
            st.info("Não há visitas cadastradas.")
    except Exception as e:
        st.error(f"Erro ao carregar visitas: {e}")
        st.info("Se este é o primeiro uso, tente cadastrar uma visita primeiro.")

def gerenciar_projetos_ui():
    """Interface para gerenciamento de projetos"""
    st.subheader("Adicionar Novo Projeto")
    
    with st.form("formulario_projeto"):
        # Gerar ID do projeto automaticamente
        id_projeto = f"P{str(uuid.uuid4())[:8].upper()}"
        st.text_input("ID do Projeto", value=id_projeto, disabled=True)
        
        nome_projeto = st.text_input("Nome do Projeto")
        descricao = st.text_area("Descrição do Projeto")
        
        submitted = st.form_submit_button("Adicionar Projeto")
        
        if submitted:
            if nome_projeto:
                if adicionar_projeto(id_projeto, nome_projeto, descricao):
                    st.success(f"Projeto {nome_projeto} adicionado com sucesso!")
                    # Limpar o formulário usando rerun
                    st.experimental_rerun()
            else:
                st.error("Nome do projeto é obrigatório.")
    
    # Listar projetos existentes
    st.subheader("Projetos Cadastrados")
    try:
        projetos_df = listar_projetos()
        
        if not projetos_df.empty:
            st.dataframe(projetos_df)
        else:
            st.info("Não há projetos cadastrados.")
    except Exception as e:
        st.error(f"Erro ao carregar projetos: {e}")

def gerenciar_contatos_ui():
    """Interface para gerenciamento de contatos"""
    st.subheader("Adicionar Novo Contato")
    
    with st.form("formulario_contato"):
        # Gerar ID do contato automaticamente
        id_contato = f"C{str(uuid.uuid4())[:8].upper()}"
        st.text_input("ID do Contato", value=id_contato, disabled=True)
        
        nome_contato = st.text_input("Nome do Contato")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")
        
        # Selecionar projeto relacionado
        projetos_df = listar_projetos()
        if not projetos_df.empty:
            projetos = projetos_df["id_projeto"].tolist()
            projetos_nomes = projetos_df["nome_projeto"].tolist()
            opcoes_projetos = ["Nenhum"] + [f"{id} - {nome}" for id, nome in zip(projetos, projetos_nomes)]
            
            projeto_selecionado = st.selectbox(
                "Projeto Relacionado", 
                options=opcoes_projetos
            )
            
            # Extrair o ID do projeto da opção selecionada
            if projeto_selecionado != "Nenhum":
                id_projeto = projeto_selecionado.split(" - ")[0]
            else:
                id_projeto = None
        else:
            id_projeto = None
            st.warning("Não há projetos cadastrados.")
        
        submitted = st.form_submit_button("Adicionar Contato")
        
        if submitted:
            if nome_contato:
                if adicionar_contato(id_contato, nome_contato, telefone, email, id_projeto):
                    st.success(f"Contato {nome_contato} adicionado com sucesso!")
                    # Limpar o formulário usando rerun
                    st.experimental_rerun()
            else:
                st.error("Nome do contato é obrigatório.")
    
    # Listar contatos existentes
    st.subheader("Contatos Cadastrados")
    try:
        contatos_df = listar_contatos()
        
        if not contatos_df.empty:
            st.dataframe(contatos_df)
        else:
            st.info("Não há contatos cadastrados.")
    except Exception as e:
        st.error(f"Erro ao carregar contatos: {e}")

def main():
    """Função principal da aplicação"""
    st.title("Jarvis IMEI - Sistema de Visitas Detalhadas")
    
    # Adicionar imagem de logo na barra lateral
    st.sidebar.image("https://via.placeholder.com/200x100?text=Jarvis+IMEI", use_column_width=True)
    
    menu = ["Home", "Cadastrar Visita", "Visualizar Visitas", "Gerenciar Projetos", "Gerenciar Contatos"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    # Adicionar informações na barra lateral
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        **Jarvis IMEI**
        
        Sistema de gerenciamento de visitas profissionais, 
        projetos e contatos.
        
        Versão 1.0
        """
    )
    
    if choice == "Home":
        st.subheader("Home")
        st.write("Bem-vindo ao sistema de gerenciamento de visitas profissionais do Jarvis IMEI.")
        
        # Exibir uma imagem ilustrativa
        st.image("https://via.placeholder.com/800x400?text=Jarvis+IMEI+-+Sistema+de+Visitas", 
                caption="Sistema de Visitas Detalhadas")
        
        # Dashboard resumido
        st.subheader("Dashboard")
        col1, col2, col3 = st.columns(3)
        
        try:
            # Contagem de visitas
            with col1:
                num_visitas = len(listar_visitas())
                st.metric("Total de Visitas", num_visitas)
                
            # Contagem de projetos
            with col2:
                num_projetos = len(listar_projetos())
                st.metric("Total de Projetos", num_projetos)
                
            # Contagem de contatos
            with col3:
                num_contatos = len(listar_contatos())
                st.metric("Total de Contatos", num_contatos)
                
            # Visitas recentes
            st.subheader("Visitas Recentes")
            visitas_df = listar_visitas()
            if not visitas_df.empty:
                # Ordenar por data (mais recente primeiro) e pegar as 5 primeiras
                visitas_df['data'] = pd.to_datetime(visitas_df['data'])
                visitas_recentes = visitas_df.sort_values(by='data', ascending=False).head(5)
                
                # Exibir visitas recentes
                for i, row in visitas_recentes.iterrows():
                    st.write(f"**{row['nome_local']}** - {row['data'].strftime('%d/%m/%Y')}")
                    with st.expander("Detalhes"):
                        st.write(f"Compromisso: {row['compromisso']}")
                        if row['id_projeto']:
                            st.write(f"ID do Projeto: {row['id_projeto']}")
            else:
                st.info("Não há visitas cadastradas.")
                
        except Exception as e:
            st.error(f"Erro ao carregar dados para o dashboard: {e}")
            st.info("Se este é o primeiro uso, cadastre alguns dados para visualizar o dashboard.")
    
    elif choice == "Cadastrar Visita":
        st.subheader("Cadastrar Nova Visita")
        cadastrar_visita_ui()
        
    elif choice == "Visualizar Visitas":
        st.subheader("Visualizar Visitas Cadastradas")
        visualizar_visitas_ui()
        
    elif choice == "Gerenciar Projetos":
        st.subheader("Gerenciar Projetos")
        gerenciar_projetos_ui()
        
    elif choice == "Gerenciar Contatos":
        st.subheader("Gerenciar Contatos")
        gerenciar_contatos_ui()

# Executar o aplicativo
if __name__ == '__main__':
    main()
