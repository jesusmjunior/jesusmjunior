import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import os
from PIL import Image
import io

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

# Interface principal
def main():
    st.title("Jarvis IMEI - Sistema de Visitas Detalhadas")
    
    menu = ["Home", "Cadastrar Visita", "Visualizar Visitas", "Gerenciar Projetos", "Gerenciar Contatos"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Home":
        st.subheader("Home")
        st.write("Bem-vindo ao sistema de gerenciamento de visitas profissionais do Jarvis IMEI.")
        st.image("https://via.placeholder.com/600x300?text=Jarvis+IMEI", caption="Sistema de Visitas")
    
    elif choice == "Cadastrar Visita":
        st.subheader("Cadastrar Nova Visita")
        # Aqui vamos implementar a lógica de cadastro
        
    elif choice == "Visualizar Visitas":
        st.subheader("Visualizar Visitas Cadastradas")
        # Aqui vamos implementar a visualização das visitas
        
    elif choice == "Gerenciar Projetos":
        st.subheader("Gerenciar Projetos")
        # Gerenciamento de projetos
        
    elif choice == "Gerenciar Contatos":
        st.subheader("Gerenciar Contatos")
        # Gerenciamento de contatos

if __name__ == '__main__':
    main()
