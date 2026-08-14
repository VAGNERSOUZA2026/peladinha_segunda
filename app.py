import streamlit as st
import pandas as pd
import json
import os
import random
from datetime import datetime, timedelta, timezone

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE FUSO HORÁRIO E DATAS
# -----------------------------------------------------------------------------
fuso_br = timezone(timedelta(hours=-3))
hoje_dt = datetime.now(fuso_br)
hoje_str = hoje_dt.strftime("%d/%m")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA (SEM SIDEBAR)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Resenha & Gestão",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    .app-header {
        background: #FFFFFF;
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 25px;
        border: 1px solid #E2E8F0;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 10px;
    }
    .app-subtitle {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .card-team {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 4px solid #0D9488;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.02);
    }

    div.stButton > button {
        background-color: #0D9488 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #0F766E !important;
        width: 100% !important;
        box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button:hover {
        background-color: #0F766E !important;
    }

    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PERSISTÊNCIA DE DADOS (JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
COMPROVANTES_FILE = "comprovantes.json"

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def salvar_dados(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except:
        pass

# Inicialização do Session State
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [
        {"descricao": "Mensalidade da Quadra (Fixa)", "valor": 300.00, "tipo": "Saída", "data": hoje_str}
    ])
if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state:
    st.session_state.administradores = carregar_dados(ADMINS_FILE, [
        {"nome": "Admin Principal", "login": "admin", "senha": "1980"}
    ])
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10", 
        "pix": "peladinhafc@email.com", 
        "limite_vagas": 15,
        "valor_mensalidade": 80.00,
        "valor_avulsa": 25.00
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {
            "topico": "📌 1. Horários, Confirmação e Limite de Vagas", 
            "regrinha": "As mensalistas têm prioridade absoluta para confirmar presença na lista principal até às **17:30 de segunda-feira**. Caso as mensalistas não preencham o limite total de vagas (15 vagas) até este horário limite, as avulsas que confirmaram presença mais cedo sobem automaticamente para a lista principal respeitando a ordem cronológica de confirmação."
        },
        {
            "topico": "⚖️ 2. Sorteio de Times (Regra Oficial)", 
            "regrinha": "O sorteio principal dos times acontece de forma automatizada pelo sistema às segundas-feiras às **18:30** (ou manualmente através da painel de administração). O formato oficial é composto por **5 jogadoras por time**, totalizando **3 times** na quadra (15 atletas). Adicionalmente, as jogadoras presentes podem acionar a função de **Sorteio Paralelo na Quadra** a qualquer momento."
        },
        {
            "topico": "🤝 3. Normas de Convivência e Conduta na Peladinha", 
            "regrinha": "• **Respeito Mútuo:** O ambiente da peladinha é voltado para o esporte, lazer e integração. Qualquer forma de agressão verbal, falta de respeito com colegas, adversárias ou com a organização não será tolerada.\n• **Pontualidade:** Chegar com antecedência para que as partidas comecem no horário estipulado pela quadra.\n• **Fair Play:** O espírito esportivo deve prevalecer em todas as disputas dentro de quadra.\n• **Penalidade:** O descumprimento grave das regras de convivência resultará em advertência e, em caso de reincidência, na **exclusão definitiva** da jogadora do grupo e do aplicativo."
        },
        {
            "topico": "💸 4. Regras de Pagamento e Inadimplência", 
            "regrinha": "O pagamento das mensalidades deve ser efetuado via Pix até o dia de vencimento estipulado (dia 10 de cada mês). O comprovante precisa obrigatoriamente ser enviado pelo aplicativo na aba 'Pagamento & Pix' para validação da administração e atualização automática no Fluxo de Caixa do grupo."
        }
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "🏠 Início"
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "cargo_logado" not in st.session_state:
    st.session_state.cargo_logado = None

# -----------------------------------------------------------------------------
# TELA DE AUTENTICAÇÃO E ENTRADA
# -----------------------------------------------------------------------------
if not st.session_state.usuario_logado:
    st.markdown("""
    <div class='app-header'>
        <div style='font-size: 3rem;'>⚽</div>
        <div class='app-subtitle'>Peladinha FC</div>
        <div class='app-title'>Resenha & Gestão</div>
    </div>
    """, unsafe_allow_html=True)

    tab_entrar, tab_cadastrar, tab_dev = st.tabs(["🔑 Entrar", "📝 Criar Conta", "🛠️ Dev"])

    with tab_entrar:
        st.write("### Acesse sua conta")
        with st.form("form_login_geral"):
            u_login = st.text_input("Usuário ou Login")
            u_senha = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("ENTRAR")
            
            if btn_entrar:
                if u_login == "Dev" and u_senha == "1980":
                    st.session_state.usuario_logado = "Desenvolvedor"
                    st.session_state.cargo_logado = "Desenvolvedor"
                    st.rerun()
                
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == u_login and adm.get("senha") == u_senha), None)
                if admin_encontrado:
                    st.session_state.usuario_logado = admin_encontrado["nome"]
                    st.session_state.cargo_logado = "Administrador"
                    st.rerun()
                
                jogadora_encontrada = next((j for j in st.session_state.jogadoras if j.get("login") == u_login and j.get("senha") == u_senha), None)
                if jogadora_encontrada:
                    st.session_state.usuario_logado = jogadora_encontrada["nome"]
                    st.session_state.cargo_logado = "Jogadora"
                    st.rerun()
                
                st.error("Usuário ou senha inválidos!")

    with tab_cadastrar:
        st.write("### Cadastro de Nova Jogadora")
        with st.form("form_novo_cadastro", clear_on_submit=True):
            c_nome = st.text_input("Nome Completo *")
            c_nasc = st.text_input("Data de Nascimento (DD/MM)", placeholder="Ex: 22/07")
            c_tipo = st.selectbox("Tipo de Jogadora", ["Mensalista", "Avulsa"])
            c_login = st.text_input("Criar Login *")
            c_senha = st.text_input("Criar Senha *", type="password")
            btn_cad = st.form_submit_button("CADASTRAR")
            
            if btn_cad:
                if c_nome and c_login and c_senha:
                    if any(j.get("login") == c_login for j in st.session_state.jogadoras):
                        st.error("Este login já está em uso.")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(),
                            "nascimento": c_nasc.strip(),
                            "tipo": c_tipo,
                            "login": c_login.strip(),
                            "senha": c_senha.strip(),
                            "status_pagamento": "Pendente",
                            "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Cadastro realizado com sucesso! Vá na aba 'Entrar'.")
                else:
                    st.error("Preencha todos os campos obrigatórios.")

    with tab_dev:
        st.write("### Acesso Restrito do Desenvolvedor")
        with st.form("form_login_dev_seguro"):
            senha_dev_input = st.text_input("Senha de Desenvolvedor", type="password")
            btn_entrar_dev = st.form_submit_button("Acessar Painel Dev")
            if btn_entrar_dev:
                if senha_dev_input == "1980":
                    st.session_state.usuario_logado = "Desenvolvedor"
                    st.session_state.cargo_logado = "Desenvolvedor"
                    st.rerun()
                else:
                    st.error("Senha de desenvolvedor incorreta!")

    st.stop()

# -----------------------------------------------------------------------------
# CABEÇALHO DO APLICATIVO LOGADO
# -----------------------------------------------------------------------------
st.markdown(f"""
<div class='app-header' style='padding: 15px; display: flex; justify-content: space-between; align-items: center;'>
    <div>
        <div class='app-subtitle'>Peladinha FC | Usuário: <b>{st.session_state.usuario_logado} ({st.session_state.cargo_logado})</b></div>
    </div>
</div>
""", unsafe_allow_html=True)

col_sair1, col_sair2 = st.columns([4, 1])
with col_sair2:
    if st.button("🚪 Sair"):
        st.session_state.usuario_logado = None
        st.session_state.cargo_logado = None
        st.session_state.pagina_atual = "🏠 Início"
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVEGAÇÃO DE PÁGINAS / CARDS PRINCIPAIS
# -----------------------------------------------------------------------------
menu = st.session_state.pagina_atual

if menu != "🏠 Início":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_atual = "🏠 Início"
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# TELA INICIAL (MENU DE CARDS)
# -----------------------------------------------------------------------------
if menu == "🏠 Início":
    st.subheader("Escolha abaixo a opção desejada:")
    
    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("📌 Presença no Jogo\n\nConfirme sua vaga ou ausência", use_container_width=True):
            st.session_state.pagina_atual = "📌 Presença no Jogo"
            st.rerun()
            
        if st.button("🔀 Sorteio de Times\n\nAcompanhe o sorteio em tempo real", use_container_width=True):
            st.session_state.pagina_atual = "🔀 Sorteio de Times"
            st.rerun()

        if st.button("📜 Regulamento\n\nRegras, horários e conduta", use_container_width=True):
            st.session_state.pagina_atual = "📜 Regulamento"
            st.rerun()

        if st.button("🎂 Aniversariantes\n\nAniversariantes do mês", use_container_width=True):
            st.session_state.pagina_atual = "🎂 Aniversariantes"
            st.rerun()

    with c2:
        if st.button("📋 Elenco de Jogadoras\n\nLista de atletas e categorias", use_container_width=True):
            st.session_state.pagina_atual = "📋 Elenco de Jogadoras"
            st.rerun()

        if st.button("💸 Pagamento & Pix\n\nCopie a chave Pix e envie comprovante", use_container_width=True):
            st.session_state.pagina_atual = "💸 Pagamento & Pix"
            st.rerun()

        if st.session_state.cargo_logado in ["Administrador", "Desenvolvedor"]:
            if st.button("📊 Fluxo de Caixa\n\nDespesas e receitas do grupo", use_container_width=True):
                st.session_state.pagina_atual = "📊 Fluxo de Caixa"
                st.rerun()

            if st.button("⚙️ Painel Admin\n\nGerenciamento de cadastros e acessos", use_container_width=True):
                st.session_state.pagina_atual = "⚙️ Painel Admin"
                st.rerun()

        if st.session_state.cargo_logado == "Desenvolvedor":
            if st.button("🛠️ Área do Desenvolvedor\n\nConfigurações globais e sistema", use_container_width=True):
                st.session_state.pagina_atual = "🛠️ Área do Desenvolvedor"
                st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
elif menu == "📌 Presença no Jogo":
    st.subheader("📌 Confirmação de Presença")
    limite = int(st.session_state.avisos.get("limite_vagas", 15))
    
    jogadora_atual_nome = st.session_state.usuario_logado if st.session_state.cargo_logado == "Jogadora" else None

    col_A, col_B = st.columns([1, 1])
    
    with col_A:
        st.write("### ✍️ Sua Ação")
        if st.session_state.cargo_logado == "Jogadora":
            st.write(f"Jogadora logada: **{jogadora_atual_nome}**")
            c_pres = st.button("✅ Confirmar Presença", use_container_width=True)
            c_aus = st.button("❌ Informar Ausência", use_container_width=True)
            
            if c_pres:
                st.session_state.presencas = [p for p in st.session_state.presencas if p["nome"] != jogadora_atual_nome]
                st.session_state.presencas.append({
                    "nome": jogadora_atual_nome,
                    "hora": hoje_dt.strftime("%H:%M:%S"),
                    "dt_confirmacao": hoje_dt.isoformat()
                })
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.success("Presença confirmada com sucesso!")
                st.rerun()
                
            if c_aus:
                st.session_state.presencas = [p for p in st.session_state.presencas if p["nome"] != jogadora_atual_nome]
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.warning("Que pena! Aguardamos você na próxima.")
        else:
            st.info("Modo Admin/Dev: A gestão de presenças individuais é feita pelas próprias jogadoras.")

    with col_B:
        st.write("### 📋 Status da Lista")
        
        lista_ordenada = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        mensalistas_confirmadas = []
        avulsas_confirmadas = []
        
        for p in lista_ordenada:
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            
            atrasada_mensalista = False
            dt_conf_str = p.get("dt_confirmacao", "")
            if dt_conf_str:
                try:
                    dt_obj = datetime.fromisoformat(dt_conf_str)
                    if dt_obj.weekday() == 0 and (dt_obj.hour > 17 or (dt_obj.hour == 17 and dt_obj.minute > 30)):
                        atrasada_mensalista = True
                except:
                    pass

            if tipo == "Mensalista" and not atrasada_mensalista:
                mensalistas_confirmadas.append(p)
            else:
                avulsas_confirmadas.append(p)

        combinada = mensalistas_confirmadas + avulsas_confirmadas
        principal = combinada[:limite]
        espera = combinada[limite:]

        st.write(f"**🟢 Lista Principal ({len(principal)}/{limite})**")
        for idx, p in enumerate(principal, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            st.markdown(f"<div class='card-team'><b>{idx}.</b> {p['nome']} `[{tipo}]` — <i>Conf: {p['hora']}</i></div>", unsafe_allow_html=True)

        st.write(f"**⏳ Fila de Espera ({len(espera)})**")
        for idx, p in enumerate(espera, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            st.markdown(f"<div class='card-team'><b>{idx}º espera:</b> {p['nome']} `[{tipo}]`</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times em Tempo Real")
    st.info("Regra: 5 jogadoras por time num total de 3 times (Total de 15 jogadoras). Sorteio principal automático às segundas às 18:30 ou manual pelo Admin. Sorteio paralelo na quadra permitido por qualquer jogadora presente.")

    sorteio_atual = st.session_state.sorteio_oficial
    if sorteio_atual and "times" in sorteio_atual:
        st.write(f"### Sorteio Vigente ({sorteio_atual.get('tipo', 'Principal')} - {sorteio_atual.get('data')})")
        cols = st.columns(len(sorteio_atual["times"]))
        for idx, (t_nome, membros) in enumerate(sorteio_atual["times"].items()):
            with cols[idx]:
                st.markdown(f"<div class='card-team'><h3>⚽ {t_nome}</h3>", unsafe_allow_html=True)
                for m in membros:
                    st.markdown(f"• {m}")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Nenhum sorteio realizado para hoje ainda.")

    st.markdown("---")
    st.write("### 🎲 Executar Sorteio")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("Executar Sorteio Principal (Admin)", use_container_width=True):
            nomes_disp = [p["nome"] for p in st.session_state.presencas]
            if len(nomes_disp) >= 3:
                random.shuffle(nomes_disp)
                t1 = nomes_disp[0:5]
                t2 = nomes_disp[5:10]
                t3 = nomes_disp[10:15] if len(nomes_disp) >= 15 else nomes_disp[10:]
                
                st.session_state.sorteio_oficial = {
                    "tipo": "Principal",
                    "data": hoje_str,
                    "times": {"Time 1": t1, "Time 2": t2, "Time 3": t3}
                }
                salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                st.success("Sorteio principal realizado com sucesso!")
                st.rerun()
            else:
                st.error("Jogadoras insuficientes para o sorteio principal.")

    with col_s2:
        if st.button("🎲 Sorteio Paralelo na Quadra (Presentes)", use_container_width=True):
            nomes_disp = [p["nome"] for p in st.session_state.presencas]
            if len(nomes_disp) >= 3:
                random.shuffle(nomes_disp)
                t1 = nomes_disp[0:5]
                t2 = nomes_disp[5:10]
                t3 = nomes_disp[10:15] if len(nomes_disp) >= 15 else nomes_disp[10:]
                
                st.session_state.sorteio_oficial = {
                    "tipo": "Paralelo na Quadra",
                    "data": hoje_str,
                    "times": {"Time A": t1, "Time B": t2, "Time C": t3}
                }
                salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                st.success("Sorteio paralelo realizado!")
                st.rerun()
            else:
                st.error("Poucas jogadoras presentes para o sorteio paralelo.")

# -----------------------------------------------------------------------------
# PÁGINA: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco de Jogadoras")
    if not st.session_state.jogadoras:
        st.info("Nenhuma jogadora cadastrada.")
    else:
        for j in st.session_state.jogadoras:
            st.markdown(f"<div class='card-team'><b>⚽ {j['nome']}</b> — Categoria: `[{j.get('tipo', 'Avulsa')}]` | Pagamento: <b>{j.get('status_pagamento', 'Pendente')}</b><br><small>Nascimento: {j.get('nascimento', 'N/A')}</small></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: PAGAMENTO & PIX
# -----------------------------------------------------------------------------
elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamento & Chave Pix")
    pix_chave = st.session_state.avisos.get("pix", "peladinhafc@email.com")
    vencimento = st.session_state.avisos.get("vencimento", "Todo dia 10")
    
    st.markdown(f"""
    <div class='card-team'>
        <h3>💳 Dados para Transferência</h3>
        <p><b>Chave Pix:</b> <code>{pix_chave}</code></p>
        <p><b>Vencimento:</b> {vencimento}</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("### 📤 Enviar Comprovante de Pagamento")
    with st.form("form_comprovante", clear_on_submit=True):
        c_nome_jogadora = st.selectbox("Seu Nome", [j["nome"] for j in st.session_state.jogadoras])
        c_mes = st.text_input("Mês Referente", value=mes_vigente_str)
        arquivo_up = st.file_uploader("Enviar Imagem do Comprovante", type=["png", "jpg", "jpeg"])
        
        btn_env_comp = st.form_submit_button("Enviar Comprovante")
        if btn_env_comp:
            st.session_state.comprovantes.append({
                "jogadora": c_nome_jogadora,
                "mes": c_mes,
                "status": "Pendente de Aprovação",
                "valor": float(st.session_state.avisos.get("valor_mensalidade", 80.00))
            })
            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
            st.success("Comprovante enviado com sucesso! O administrador irá validar em breve.")

# -----------------------------------------------------------------------------
# PÁGINA: REGULAMENTO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno & Conduta")
    for reg in st.session_state.regulamento:
        st.markdown(f"<div class='card-team'><h3>{reg['topico']}</h3><p>{reg['regrinha']}</p></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: ANIVERSARIANTES
# -----------------------------------------------------------------------------
elif menu == "🎂 Aniversariantes":
    st.subheader("🎂 Aniversariantes do Mês")
    mes_atual_s = hoje_dt.strftime("/%m")
    aniversariantes = [j for j in st.session_state.jogadoras if j.get("nascimento", "").endswith(mes_atual_s)]
    
    if not aniversariantes:
        st.info("Nenhuma aniversariante cadastrada para este mês.")
    else:
        for j in aniversariantes:
            st.markdown(f"<div class='card-team'>🎉 <b>{j['nome']}</b> — Nascimento: <code>{j.get('nascimento')}</code></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: FLUXO DE CAIXA (ADMIN / DEV)
# -----------------------------------------------------------------------------
elif menu == "📊 Fluxo de Caixa":
    if st.session_state.cargo_logado not in ["Administrador", "Desenvolvedor"]:
        st.error("Acesso restrito aos administradores.")
    else:
        st.subheader("📊 Fluxo de Caixa / Financeiro")
        
        mensalistas_cadastradas = sorted([j for j in st.session_state.jogadoras if j.get("tipo") == "Mensalista"], key=lambda x: x["nome"])
        
        st.write("### 🟢 Receitas - Mensalistas (Ordem Alfabética)")
        for m in mensalistas_cadastradas:
            st.markdown(f"• **{m['nome']}** — Status: `{m.get('status_pagamento', 'Pendente')}`")

        # Exibir comprovantes aprovados integrados nas receitas
        st.write("### 💵 Entradas via Comprovantes Aprovados")
        comprovantes_aprovados = [c for c in st.session_state.comprovantes if c.get("status") == "Aprovado"]
        total_comprovantes = 0.0
        if not comprovantes_aprovados:
            st.info("Nenhum comprovante aprovado registrado ainda.")
        else:
            for comp in comprovantes_aprovados:
                v_comp = float(comp.get("valor", 80.00))
                total_comprovantes += v_comp
                st.markdown(f"<div class='card-team'>🟢 <b>Mensalidade / Pix:</b> {comp['jogadora']} (Mês: {comp['mes']}) — R$ {v_comp:.2f}</div>", unsafe_allow_html=True)

        st.write("### 🟢 Receitas - Avulsas")
        qtd_avulsas_jogo = st.number_input("Quantidade de Avulsas no Jogo", min_value=0, value=0)
        valor_avulsa_unit = st.number_input("Valor Unitário da Avulsa (R$)", min_value=0.0, value=25.0)
        total_avulsas_calc = qtd_avulsas_jogo * valor_avulsa_unit
        st.info(f"Total arrecadado com Avulsas: **R$ {total_avulsas_calc:.2f}**")

        st.markdown("---")
        st.write("### 🔴 Despesas")
        total_saidas = 0.0
        for f in st.session_state.financeiro:
            if f.get("tipo") == "Saída":
                val_saida = float(f.get('valor', 0))
                total_saidas += val_saida
                st.markdown(f"<div class='card-team'>🔴 <b>{f.get('descricao')}</b> — R$ {val_saida:.2f}</div>", unsafe_allow_html=True)

        with st.form("form_nova_despesa", clear_on_submit=True):
            d_desc = st.text_input("Nome da Nova Despesa")
            d_val = st.number_input("Valor da Despesa (R$)", min_value=0.0, format="%.2f")
            if st.form_submit_button("Adicionar Despesa"):
                if d_desc and d_val > 0:
                    st.session_state.financeiro.append({"descricao": d_desc, "valor": d_val, "tipo": "Saída", "data": hoje_str})
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Despesa adicionada!")
                    st.rerun()

        st.markdown("---")
        total_entradas_geral = total_comprovantes + total_avulsas_calc
        saldo_final = total_entradas_geral - total_saidas
        st.metric(label="Saldo Geral do Caixa", value=f"R$ {saldo_final:.2f}", delta=f"Entradas: R$ {total_entradas_geral:.2f} | Saídas: R$ {total_saidas:.2f}")

# -----------------------------------------------------------------------------
# PÁGINA: PAINEL ADMIN
# -----------------------------------------------------------------------------
elif menu == "⚙️ Painel Admin":
    if st.session_state.cargo_logado not in ["Administrador", "Desenvolvedor"]:
        st.error("Acesso restrito.")
    else:
        st.subheader("⚙️ Painel de Administração")
        
        st.write("### 🛡️ Validação de Comprovantes Pix")
        if not st.session_state.comprovantes:
            st.info("Nenhum comprovante pendente.")
        else:
            for idx, comp in enumerate(st.session_state.comprovantes):
                if comp.get("status") == "Pendente de Aprovação":
                    st.markdown(f"<div class='card-team'><b>Jogadora:</b> {comp['jogadora']} | <b>Mês:</b> {comp['mes']}</div>", unsafe_allow_html=True)
                    if st.button(f"Aprovar Pagamento de {comp['jogadora']}", key=f"aprov_{idx}"):
                        comp["status"] = "Aprovado"
                        for j in st.session_state.jogadoras:
                            if j["nome"] == comp["jogadora"]:
                                j["status_pagamento"] = "Pago"
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Pagamento aprovado, status atualizado e integrado ao Fluxo de Caixa!")
                        st.rerun()

        st.markdown("---")
        st.write("### 📝 Gerenciar Cadastros de Jogadoras e Administradores")
        
        with st.form("form_cad_geral_admin", clear_on_submit=True):
            cg_nome = st.text_input("Nome Completo *")
            cg_nasc = st.text_input("Nascimento (DD/MM)")
            cg_tipo = st.selectbox("Categoria", ["Mensalista", "Avulsa"])
            cg_papel = st.selectbox("Papel no Sistema", ["Jogadora", "Administrador"])
            cg_login = st.text_input("Login *")
            cg_senha = st.text_input("Senha *", type="password")
            
            if st.form_submit_button("Cadastrar Usuário"):
                if cg_nome and cg_login and cg_senha:
                    if cg_papel == "Administrador":
                        if len(st.session_state.administradores) >= 3:
                            st.error("O limite máximo de 3 administradores já foi atingido.")
                        else:
                            st.session_state.administradores.append({"nome": cg_nome, "login": cg_login, "senha": cg_senha})
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.success("Administrador cadastrado com sucesso!")
                            st.rerun()
                    else:
                        st.session_state.jogadoras.append({
                            "nome": cg_nome, "nascimento": cg_nasc, "tipo": cg_tipo,
                            "login": cg_login, "senha": cg_senha, "status_pagamento": "Pendente", "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Jogadora cadastrada com sucesso!")
                        st.rerun()
                else:
                    st.error("Preencha todos os campos obrigatórios.")

# -----------------------------------------------------------------------------
# PÁGINA: ÁREA DO DESENVOLVEDOR
# -----------------------------------------------------------------------------
elif menu == "🛠️ Área do Desenvolvedor":
    if st.session_state.cargo_logado != "Desenvolvedor":
        st.error("Acesso exclusivo do Desenvolvedor.")
    else:
        st.subheader("🛠️ Área do Desenvolvedor - Configurações Globais")
        st.info("Aqui você gerencia todo o ecossistema e credenciais do aplicativo.")
        
        st.write("### 🔑 Administradores Atuais (Total: 3 máx)")
        for idx, adm in enumerate(st.session_state.administradores, 1):
            st.markdown(f"• **Admin {idx}:** {adm.get('nome')} (Login: `{adm.get('login')}`)")

        if st.button("🔄 Resetar Dados de Exemplo / Fábrica"):
            if os.path.exists(DATA_FILE): os.remove(DATA_FILE)
            if os.path.exists(PRESENCAS_FILE): os.remove(PRESENCAS_FILE)
            if os.path.exists(COMPROVANTES_FILE): os.remove(COMPROVANTES_FILE)
            if os.path.exists(FINANCE_FILE): os.remove(FINANCE_FILE)
            st.success("Sistema resetado com sucesso!")
            st.rerun()
