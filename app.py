import streamlit as st
import json
import os
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão de Futebol", layout="wide")

# --- CSS PERSONALIZADO (ROSA E PRETO) ---
st.markdown("""
    <style>
    .card-rosa {
        background-color: #FFC0CB !important;
        padding: 20px;
        border-radius: 15px;
        color: black !important;
        border: 2px solid #FF69B4;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #FFC0CB !important;
        color: black !important;
        border: 1px solid #FF69B4 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE DADOS ---
def carregar_dados():
    if not os.path.exists("atletas.json"):
        return []
    with open("atletas.json", "r") as f:
        return json.load(f)

def salvar_dados(atletas):
    with open("atletas.json", "w") as f:
        json.dump(atletas, f)

# Inicializar session state
if 'atletas' not in st.session_state:
    st.session_state.atletas = carregar_dados()

# --- FUNÇÃO ANIVERSARIANTES ---
def exibir_aniversariantes(atletas):
    st.markdown("---")
    st.subheader("🎂 Aniversariantes do Mês")
    mes_atual = datetime.now().month
    aniversariantes = [a for a in atletas if a.get('nasc') and int(a['nasc'].split('/')[1]) == mes_atual]
    
    if aniversariantes:
        for a in aniversariantes:
            st.markdown(f'<div class="card-rosa">🎈 Parabéns, {a["nome"]}! Hoje é dia de celebrar!</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma aniversariante neste mês.")

# --- INTERFACE PRINCIPAL ---
st.title("⚽ Gestão do Time Feminino")

# Menu Lateral
menu = st.sidebar.radio("Navegação", ["Dashboard", "Cadastrar Atleta"])

if menu == "Dashboard":
    exibir_aniversariantes(st.session_state.atletas)
    
    st.subheader("Elenco")
    for atleta in st.session_state.atletas:
        st.markdown(f'''
            <div class="card-rosa">
                Nome: {atleta['nome']} <br>
                Data Nasc: {atleta['nasc']}
            </div>
        ''', unsafe_allow_html=True)

elif menu == "Cadastrar Atleta":
    st.subheader("Adicionar Nova Jogadora")
    with st.form("form_atleta"):
        nome = st.text_input("Nome da Jogadora")
        data_nasc = st.date_input("Data de Nascimento", min_value=datetime(1970, 1, 1))
        btn_salvar = st.form_submit_button("Salvar")
        
        if btn_salvar:
            nova_atleta = {
                "nome": nome,
                "nasc": data_nasc.strftime("%d/%m/%Y")
            }
            st.session_state.atletas.append(nova_atleta)
            salvar_dados(st.session_state.atletas)
            st.success("Atleta cadastrada!")
            st.rerun()

# --- RODAPÉ ---
st.sidebar.markdown("---")
st.sidebar.write("Sistema Rosa v1.0")
