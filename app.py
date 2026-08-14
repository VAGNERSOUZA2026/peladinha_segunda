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
ano_vigente_str = hoje_dt.strftime("%Y")

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
        {"descricao": "Aluguel da Quadra", "valor": 300.00, "tipo": "Saída", "mes": mes_vigente_str, "semana": "Semana 1", "ano": ano_vigente_str, "data": hoje_str}
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
            "regrinha": "O sorteio principal dos times acontece de forma automatizada pelo sistema às segundas-feiras às **18:30** (ou manualmente através do painel de administração). O formato oficial é composto por **5 jogadoras por time**, totalizando **3 times** na quadra (15 atletas). Adicionalmente, as jogadoras presentes podem acionar a função de **Sorteio Paralelo na Quadra** a qualquer momento."
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
            if st.button("📊 Fluxo de Caixa\n\nDespesas, receitas e gráficos", use_container_width=True):
                st.session_state.pagina_atual = "📊 Fluxo de Caixa"
                st.rerun()

            if st.button("⚙️ Painel Admin\n\nGerenciamento de presenças, atletas e regras", use_container_width=True):
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
            
            ja_confirmada = any(p["nome"] == jogadora_atual_nome for p in st.session_state.presencas)
            
            if not ja_confirmada:
                c_pres = st.button("✅ Confirmar Presença", use_container_width=True)
                if c_pres:
                    st.session_state.presencas.append({
                        "nome": jogadora_atual_nome,
                        "hora": hoje_dt.strftime("%H:%M:%S"),
                        "dt_confirmacao": hoje_dt.isoformat(),
                        "mes": mes_vigente_str,
                        "semana": "Semana 1"
                    })
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.success("Presença confirmada com sucesso!")
                    st.rerun()
            else:
                st.info("Você já confirmou presença!")
                c_aus = st.button("❌ Desconfirmar / Informar Ausência", use_container_width=True)
                if c_aus:
                    st.session_state.presencas = [p for p in st.session_state.presencas if p["nome"] != jogadora_atual_nome]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.warning("Presença cancelada com sucesso.")
                    st.rerun()
        else:
            st.info("🛠️ **Painel do Administrador:** Adicione ou remova atletas diretamente por aqui visualizando a lista ao lado.")
            
            with st.form("form_add_presenca_rapida", clear_on_submit=True):
                st.write("#### Inserir Atleta na Lista")
                nome_para_adicionar = st.selectbox("Selecionar Atleta Cadastrada", [j["nome"] for j in st.session_state.jogadoras])
                btn_inserir_p = st.form_submit_button("Adicionar Presença")
                if btn_inserir_p:
                    if not any(p["nome"] == nome_para_adicionar for p in st.session_state.presencas):
                        st.session_state.presencas.append({
                            "nome": nome_para_adicionar,
                            "hora": hoje_dt.strftime("%H:%M:%S"),
                            "dt_confirmacao": hoje_dt.isoformat(),
                            "mes": mes_vigente_str,
                            "semana": "Semana 1"
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"{nome_para_adicionar} adicionada à lista!")
                        st.rerun()
                    else:
                        st.warning("Esta jogadora já está na lista.")

            with st.form("form_cadastrar_inserir_rapido", clear_on_submit=True):
                st.write("#### Incluir Nova Jogadora (Avulsa)")
                novo_nome_avulso = st.text_input("Nome Completo da Nova Atleta")
                btn_cad_avulso = st.form_submit_button("Incluir")
                if btn_cad_avulso:
                    if novo_nome_avulso.strip():
                        nome_limpo = novo_nome_avulso.strip()
                        # Cadastra explicitamente como Avulsa no sistema para garantir que nunca seja tratada como Mensalista
                        if not any(j["nome"].lower() == nome_limpo.lower() for j in st.session_state.jogadoras):
                            st.session_state.jogadoras.append({
                                "nome": nome_limpo,
                                "nascimento": "",
                                "tipo": "Avulsa",
                                "login": nome_limpo.lower().replace(" ", "_"),
                                "senha": "123",
                                "status_pagamento": "Pendente",
                                "status": "Ativo"
                            })
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        else:
                            # Se já existe, força o tipo para Avulsa caso estivesse incorreto
                            for j in st.session_state.jogadoras:
                                if j["nome"].lower() == nome_limpo.lower():
                                    j["tipo"] = "Avulsa"
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        
                        # Adiciona na presença
                        if not any(p["nome"].lower() == nome_limpo.lower() for p in st.session_state.presencas):
                            st.session_state.presencas.append({
                                "nome": nome_limpo,
                                "hora": hoje_dt.strftime("%H:%M:%S"),
                                "dt_confirmacao": hoje_dt.isoformat(),
                                "mes": mes_vigente_str,
                                "semana": "Semana 1"
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success(f"{nome_limpo} incluída com sucesso na lista!")
                            st.rerun()
                        else:
                            st.warning("Essa atleta já está na lista de presença.")
                    else:
                        st.error("Informe o nome da atleta.")

    with col_B:
        st.write("### 📋 Status da Lista")
        
        lista_ordenada = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        mensalistas_confirmadas = []
        avulsas_confirmadas = []
        
        for p in lista_ordenada:
            j_info = next((j for j in st.session_state.jogadoras if j["nome"].lower() == p["nome"].lower()), None)
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

            # Separação rigorosa e isolada por tipo
            if tipo == "Mensalista" and not atrasada_mensalista:
                mensalistas_confirmadas.append(p)
            else:
                avulsas_confirmadas.append(p)

        # Regra de posicionamento: Mensalistas priorizadas na principal, avulsas entram após ou na espera conforme ordem cronológica
        combinada = mensalistas_confirmadas + avulsas_confirmadas
        principal = combinada[:limite]
        espera = combinada[limite:]

        st.write(f"**🟢 Lista Principal ({len(principal)}/{limite})**")
        for idx, p in enumerate(principal, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"].lower() == p["nome"].lower()), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            hora_conf = p.get("hora", "")
            
            if st.session_state.cargo_logado in ["Administrador", "Desenvolvedor"]:
                col_p_nome, col_p_del = st.columns([4, 1])
                with col_p_nome:
                    st.markdown(f"<b>{idx}.</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i>", unsafe_allow_html=True)
                with col_p_del:
                    if st.button("❌", key=f"del_prin_{p['nome']}"):
                        st.session_state.presencas = [item for item in st.session_state.presencas if item["nome"] != p["nome"]]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                st.markdown(f"<div class='card-team'><b>{idx}.</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i></div>", unsafe_allow_html=True)

        st.write(f"**⏳ Fila de Espera ({len(espera)})**")
        for idx, p in enumerate(espera, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"].lower() == p["nome"].lower()), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            hora_conf = p.get("hora", "")
            
            if st.session_state.cargo_logado in ["Administrador", "Desenvolvedor"]:
                col_e_nome, col_e_del = st.columns([4, 1])
                with col_e_nome:
                    st.markdown(f"<b>{idx}º esp:</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i>", unsafe_allow_html=True)
                with col_e_del:
                    if st.button("❌", key=f"del_esp_{p['nome']}"):
                        st.session_state.presencas = [item for item in st.session_state.presencas if item["nome"] != p["nome"]]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                st.markdown(f"<div class='card-team'><b>{idx}º espera:</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i></div>", unsafe_allow_html=True)

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
        c_semana = st.selectbox("Semana Referente", ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"])
        c_ano = st.text_input("Ano Referente", value=ano_vigente_str)
        arquivo_up = st.file_uploader("Enviar Imagem do Comprovante", type=["png", "jpg", "jpeg"])
        
        btn_env_comp = st.form_submit_button("Enviar Comprovante")
        if btn_env_comp:
            st.session_state.comprovantes.append({
                "jogadora": c_nome_jogadora,
                "mes": c_mes,
                "semana": c_semana,
                "ano": c_ano,
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
        st.subheader("📊 Fluxo de Caixa / Financeiro & Gráficos")
        
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_ano = st.text_input("Filtrar por Ano", value=ano_vigente_str)
        with col_f2:
            filtro_mes = st.text_input("Filtrar por Mês (MM/AAAA)", value=mes_vigente_str)
        with col_f3:
            filtro_semana = st.selectbox("Filtrar por Semana", ["Todas", "Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"])

        st.markdown("---")
        
        st.write("### 🟢 Entradas (Receitas)")
        comprovantes_aprovados = [c for c in st.session_state.comprovantes if c.get("status") == "Aprovado"]
        
        comp_filtrados = []
        for comp in comprovantes_aprovados:
            c_ano = comp.get("ano", ano_vigente_str)
            c_mes = comp.get("mes", mes_vigente_str)
            c_sem = comp.get("semana", "Semana 1")
            
            match_ano = (not filtro_ano) or (c_ano == filtro_ano)
            match_mes = (not filtro_mes) or (c_mes == filtro_mes)
            match_sem = (filtro_semana == "Todas") or (c_sem == filtro_semana)
            
            if match_ano and match_mes and match_sem:
                comp_filtrados.append(comp)

        total_comprovantes = 0.0
        if not comp_filtrados:
            st.info("Nenhuma entrada de Pix/Comprovante aprovado para o filtro selecionado.")
        else:
            for comp in comp_filtrados:
                v_comp = float(comp.get("valor", 80.00))
                total_comprovantes += v_comp
                st.markdown(f"<div class='card-team'>🟢 <b>Pix / Mensalidade:</b> {comp['jogadora']} — R$ {v_comp:.2f} <br><small>Mês: {comp.get('mes')} | {comp.get('semana', 'Semana 1')} | Ano: {comp.get('ano', ano_vigente_str)}</small></div>", unsafe_allow_html=True)

        st.write("#### Entradas Avulsas")
        qtd_avulsas_jogo = st.number_input("Quantidade de Avulsas no Período", min_value=0, value=0)
        valor_avulsa_unit = st.number_input("Valor Unitário da Avulsa (R$)", min_value=0.0, value=25.0)
        total_avulsas_calc = qtd_avulsas_jogo * valor_avulsa_unit
        st.info(f"Total arrecadado com Avulsas no filtro: **R$ {total_avulsas_calc:.2f}**")

        st.write("#### 📊 Gráfico de Receitas por Semana")
        dados_receita_graf = []
        for c in comp_filtrados:
            dados_receita_graf.append({"Semana": c.get("semana", "Semana 1"), "Receita Pix": float(c.get("valor", 80))})
        if dados_receita_graf:
            df_rec = pd.DataFrame(dados_receita_graf).groupby("Semana").sum()
            st.bar_chart(df_rec)
        else:
            st.info("Sem dados suficientes para o gráfico de receitas na semana.")

        st.markdown("---")
        st.write("### 📊 Gráfico de Frequência de Jogadoras (Mensalistas vs Avulsas)")
        
        dados_grafico_freq = []
        for p in st.session_state.presencas:
            j_info = next((j for j in st.session_state.jogadoras if j["nome"].lower() == p["nome"].lower()), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            p_mes = p.get("mes", mes_vigente_str)
            p_sem = p.get("semana", "Semana 1")
            
            match_ano = (not filtro_ano) or (p_mes.endswith(filtro_ano))
            match_mes = (not filtro_mes) or (p_mes == filtro_mes)
            match_sem = (filtro_semana == "Todas") or (p_sem == filtro_semana)
            
            if match_ano and match_mes and match_sem:
                dados_grafico_freq.append({"Semana": p_sem, "Tipo": tipo, "Contagem": 1})

        if dados_grafico_freq:
            df_freq = pd.DataFrame(dados_grafico_freq)
            df_pivot = df_freq.pivot_table(index="Semana", columns="Tipo", values="Contagem", aggfunc="sum", fill_value=0)
            st.dataframe(df_pivot, use_container_width=True)
            st.bar_chart(df_pivot)
        else:
            st.info("Nenhum registro de presença para o filtro selecionado.")

        st.markdown("---")
        st.write("### 🔴 Despesas & Lançamentos (Totalmente Editáveis)")
        
        despesas_filtradas = []
        for idx_orig, d in enumerate(st.session_state.financeiro):
            if d.get("tipo") == "Saída":
                d_ano = d.get("ano", ano_vigente_str)
                d_mes = d.get("mes", mes_vigente_str)
                d_sem = d.get("semana", "Semana 1")
                
                match_ano = (not filtro_ano) or (d_ano == filtro_ano)
                match_mes = (not filtro_mes) or (d_mes == filtro_mes)
                match_sem = (filtro_semana == "Todas") or (d_sem == filtro_semana)
                
                if match_ano and match_mes and match_sem:
                    despesas_filtradas.append((idx_orig, d))

        total_saidas = 0.0
        if not despesas_filtradas:
            st.info("Nenhuma despesa registrada para este filtro.")
        else:
            for idx_orig, f in despesas_filtradas:
                val_saida = float(f.get('valor', 0))
                total_saidas += val_saida
                
                with st.expander(f"🔴 {f.get('descricao')} — R$ {val_saida:.2f} ({f.get('mes')} | {f.get('semana')})"):
                    with st.form(f"form_editar_despesa_{idx_orig}"):
                        nova_desc = st.text_input("Descrição da Despesa", value=f.get("descricao", ""))
                        novo_val = st.number_input("Valor (R$)", min_value=0.0, value=val_saida)
                        novo_mes = st.text_input("Mês (MM/AAAA)", value=f.get("mes", mes_vigente_str))
                        nova_sem = st.selectbox("Semana", ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"], index=["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"].index(f.get("semana", "Semana 1")) if f.get("semana") in ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"] else 0)
                        novo_ano = st.text_input("Ano", value=f.get("ano", ano_vigente_str))
                        
                        col_b1, col_b2 = st.columns(2)
                        with col_b1:
                            btn_salvar_desp = st.form_submit_button("💾 Salvar Alterações")
                        with col_b2:
                            btn_excluir_desp = st.form_submit_button("🗑️ Excluir Despesa")
                            
                        if btn_salvar_desp:
                            st.session_state.financeiro[idx_orig]["descricao"] = nova_desc
                            st.session_state.financeiro[idx_orig]["valor"] = float(novo_val)
                            st.session_state.financeiro[idx_orig]["mes"] = novo_mes
                            st.session_state.financeiro[idx_orig]["semana"] = nova_sem
                            st.session_state.financeiro[idx_orig]["ano"] = novo_ano
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                            st.success("Despesa atualizada com sucesso!")
                            st.rerun()
                            
                        if btn_excluir_desp:
                            del st.session_state.financeiro[idx_orig]
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                            st.warning("Despesa excluída com sucesso!")
                            st.rerun()

        st.markdown("---")
        st.write("### ➕ Adicionar Nova Despesa")
        with st.form("form_nova_despesa", clear_on_submit=True):
            n_desc = st.text_input("Descrição (Ex: Água, Gelo, Quadra)")
            n_val = st.number_input("Valor (R$)", min_value=0.0, value=50.0)
            n_mes = st.text_input("Mês (MM/AAAA)", value=mes_vigente_str)
            n_sem = st.selectbox("Semana", ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"])
            n_ano = st.text_input("Ano", value=ano_vigente_str)
            
            btn_add_desp = st.form_submit_button("Adicionar Despesa")
            if btn_add_desp:
                if n_desc:
                    st.session_state.financeiro.append({
                        "descricao": n_desc,
                        "valor": float(n_val),
                        "tipo": "Saída",
                        "mes": n_mes,
                        "semana": n_sem,
                        "ano": n_ano,
                        "data": hoje_str
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Despesa adicionada com sucesso!")
                    st.rerun()
                else:
                    st.error("Informe a descrição da despesa.")

        st.markdown("---")
        total_entradas_geral = total_comprovantes + total_avulsas_calc
        saldo_liquido = total_entradas_geral - total_saidas
        
        st.write("### 📊 Balanço Financeiro Geral do Período")
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric("Total Entradas", f"R$ {total_entradas_geral:.2f}")
        with col_res2:
            st.metric("Total Saídas", f"R$ {total_saidas:.2f}")
        with col_res3:
            st.metric("Saldo Líquido", f"R$ {saldo_liquido:.2f}", delta=f"R$ {saldo_liquido:.2f}")

# -----------------------------------------------------------------------------
# PÁGINA: PAINEL ADMIN (ADMIN / DEV)
# -----------------------------------------------------------------------------
elif menu == "⚙️ Painel Admin":
    if st.session_state.cargo_logado not in ["Administrador", "Desenvolvedor"]:
        st.error("Acesso restrito aos administradores.")
    else:
        st.subheader("⚙️ Painel de Administração e Gestão")
        
        tab_adm1, tab_adm2, tab_adm3 = st.tabs(["👥 Gerenciar Jogadoras", "✅ Aprovar Comprovantes", "📝 Configurações & Regras"])
        
        with tab_adm1:
            st.write("### Atletas Cadastradas")
            for idx, j in enumerate(st.session_state.jogadoras):
                with st.expander(f"{j['nome']} (`{j.get('tipo', 'Avulsa')}`)"):
                    with st.form(f"form_edit_jogadora_{idx}"):
                        e_nome = st.text_input("Nome", value=j["nome"])
                        e_nasc = st.text_input("Nascimento (DD/MM)", value=j.get("nascimento", ""))
                        e_tipo = st.selectbox("Tipo", ["Mensalista", "Avulsa"], index=0 if j.get("tipo", "Avulsa") == "Mensalista" else 1)
                        e_status = st.selectbox("Status Pagamento", ["Pendente", "Pago", "Isenta"], index=["Pendente", "Pago", "Isenta"].index(j.get("status_pagamento", "Pendente")) if j.get("status_pagamento") in ["Pendente", "Pago", "Isenta"] else 0)
                        
                        col_j1, col_j2 = st.columns(2)
                        with col_j1:
                            btn_salvar_j = st.form_submit_button("Salvar Alterações")
                        with col_j2:
                            btn_excluir_j = st.form_submit_button("Excluir Jogadora")
                            
                        if btn_salvar_j:
                            st.session_state.jogadoras[idx]["nome"] = e_nome
                            st.session_state.jogadoras[idx]["nascimento"] = e_nasc
                            st.session_state.jogadoras[idx]["tipo"] = e_tipo
                            st.session_state.jogadoras[idx]["status_pagamento"] = e_status
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success("Dados atualizados!")
                            st.rerun()
                            
                        if btn_excluir_j:
                            del st.session_state.jogadoras[idx]
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.warning("Jogadora excluída!")
                            st.rerun()

        with tab_adm2:
            st.write("### Comprovantes Enviados para Aprovação")
            comprovantes_pendentes = [c for c in st.session_state.comprovantes if c.get("status") == "Pendente de Aprovação"]
            if not comprovantes_pendentes:
                st.info("Nenhum comprovante pendente no momento.")
            else:
                for idx, comp in enumerate(st.session_state.comprovantes):
                    if comp.get("status") == "Pendente de Aprovação":
                        with st.container():
                            st.markdown(f"<div class='card-team'><b>Jogadora:</b> {comp['jogadora']} | <b>Mês:</b> {comp['mes']} | <b>{comp.get('semana', 'Semana 1')}</b> | <b>Valor:</b> R$ {comp.get('valor', 80.00):.2f}</div>", unsafe_allow_html=True)
                            col_p1, col_p2 = st.columns(2)
                            with col_p1:
                                if st.button(f"✅ Aprovar", key=f"aprovar_{idx}"):
                                    st.session_state.comprovantes[idx]["status"] = "Aprovado"
                                    for j in st.session_state.jogadoras:
                                        if j["nome"] == comp["jogadora"]:
                                            j["status_pagamento"] = "Pago"
                                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                                    st.success(f"Comprovante de {comp['jogadora']} aprovado!")
                                    st.rerun()
                            with col_p2:
                                if st.button(f"❌ Rejeitar", key=f"rejeitar_{idx}"):
                                    st.session_state.comprovantes[idx]["status"] = "Rejeitado"
                                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                                    st.warning("Comprovante rejeitado.")
                                    st.rerun()

        with tab_adm3:
            st.write("### Configurações de Avisos e Regras")
            with st.form("form_config_geral"):
                cfg_venc = st.text_input("Vencimento", value=st.session_state.avisos.get("vencimento", "Todo dia 10"))
                cfg_pix = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", "peladinhafc@email.com"))
                cfg_limite = st.number_input("Limite de Vagas Principal", min_value=1, value=int(st.session_state.avisos.get("limite_vagas", 15)))
                cfg_v_mensal = st.number_input("Valor Mensalidade (R$)", min_value=0.0, value=float(st.session_state.avisos.get("valor_mensalidade", 80.00)))
                cfg_v_avulsa = st.number_input("Valor Avulsa (R$)", min_value=0.0, value=float(st.session_state.avisos.get("valor_avulsa", 25.00)))
                
                btn_salvar_cfg = st.form_submit_button("Salvar Configurações")
                if btn_salvar_cfg:
                    st.session_state.avisos["vencimento"] = cfg_venc
                    st.session_state.avisos["pix"] = cfg_pix
                    st.session_state.avisos["limite_vagas"] = int(cfg_limite)
                    st.session_state.avisos["valor_mensalidade"] = float(cfg_v_mensal)
                    st.session_state.avisos["valor_avulsa"] = float(cfg_v_avulsa)
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações salvas com sucesso!")
                    st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA: ÁREA DO DESENVOLVEDOR
# -----------------------------------------------------------------------------
elif menu == "🛠️ Área do Desenvolvedor":
    if st.session_state.cargo_logado != "Desenvolvedor":
        st.error("Acesso restrito ao desenvolvedor.")
    else:
        st.subheader("🛠️ Painel Avançado do Desenvolvedor")
        st.warning("Área destinada a manutenções globais, reset de dados e logs do sistema.")
        
        col_dev1, col_dev2 = st.columns(2)
        with col_dev1:
            if st.button("🗑️ Resetar Lista de Presenças", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.success("Presenças resetadas.")
                st.rerun()
                
        with col_dev2:
            if st.button("🔄 Recarregar Dados dos Arquivos", use_container_width=True):
                st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
                st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
                st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
                st.success("Dados recarregados do disco com sucesso!")
                st.rerun()
