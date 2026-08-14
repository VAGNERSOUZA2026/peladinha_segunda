import streamlit as st
import pandas as pd
import json
import os
import random
import base64
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
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Resenha & Gestão",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Função robusta para converter imagem local em Base64
def obter_imagem_base64(caminhos):
    for caminho in caminhos:
        if os.path.exists(caminho):
            with open(caminho, "rb") as f:
                data = f.read()
            return base64.b64encode(data).decode("utf-8")
    return None

img_base64 = obter_imagem_base64(["images (1).jpg", "images (1)_2.jpg", "fundo.jpg"])
bg_url = 'url("data:image/jpeg;base64,' + img_base64 + '")' if img_base64 else 'none'

# ESTILIZAÇÃO GERAL E CORREÇÃO DAS ABAS (TABS) - SEM F-STRING GLOBAL
css_estilo = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    [data-testid="stSidebar"] {
        display: none;
    }

    /* Imagem de Fundo em Tela Cheia */
    .stApp {
        background: linear-gradient(rgba(15, 15, 19, 0.82), rgba(15, 15, 19, 0.88)), BACKGROUND_URL_PLACEHOLDER;
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    /* Forçar visibilidade e contraste de títulos, textos e labels */
    h1, h2, h3, h4, h5, h6, label, .stMarkdown p, span {
        color: #FFFFFF !important;
    }

    /* CORREÇÃO DAS ABAS DO STREAMLIT (Criar Conta e Dev) */
    [data-baseweb="tab"] {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    [data-baseweb="tab"] div {
        color: #FFFFFF !important;
    }
    [aria-selected="true"] {
        color: #EC4899 !important;
        border-bottom-color: #EC4899 !important;
    }

    .app-header {
        background: rgba(24, 24, 32, 0.85);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid rgba(236, 72, 153, 0.4);
        box-shadow: 0px 4px 15px rgba(236, 72, 153, 0.2);
        text-align: center;
        backdrop-filter: blur(8px);
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFFFFF !important;
        margin-top: 5px;
    }
    .app-subtitle {
        font-size: 0.8rem;
        color: #EC4899 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
    }

    .card-team {
        background: rgba(24, 24, 32, 0.92) !important;
        border: 1px solid rgba(236, 72, 153, 0.5) !important;
        border-top: 4px solid #EC4899 !important;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.6);
        color: #FFFFFF !important;
        backdrop-filter: blur(8px);
    }
    .card-team h3, .card-team b, .card-team p, .card-team span {
        color: #FFFFFF !important;
    }

    div.stButton > button {
        background-color: #EC4899 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #DB2777 !important;
        width: 100% !important;
        box-shadow: 0px 3px 6px rgba(236, 72, 153, 0.4);
    }
    div.stButton > button:hover {
        background-color: #DB2777 !important;
    }

    div[data-testid="stFormSubmitButton"] > button {
        background-color: #EC4899 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: rgba(24, 24, 32, 0.9) !important;
        color: #FFFFFF !important;
        border: 1px solid #EC4899 !important;
        border-radius: 8px !important;
    }
</style>
"""
# Substitui o marcador pela url da imagem de forma segura
css_estilo = css_estilo.replace("BACKGROUND_URL_PLACEHOLDER", bg_url)
st.markdown(css_estilo, unsafe_allow_html=True)

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
            "topico": "📌 1. Horários, Confirmação e Validação de Categoria", 
            "regrinha": "O cadastro de nova jogadora como 'Mensalista' fica pendente de aprovação prévia do Administrador para evitar fraudes ou má-fé na ocupação de vagas. As mensalistas aprovadas têm prioridade absoluta até às **17:30 de segunda-feira**."
        },
        {
            "topico": "⚖️ 2. Sorteio de Times (Regra Oficial)", 
            "regrinha": "O sorteio principal acontece automaticamente às segundas-feiras às **18:30** ou via painel de administração (5 jogadoras por time, 3 times)."
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
        <div style='font-size: 2.5rem;'>⚽🔥</div>
        <div class='app-subtitle'>Peladinha FC</div>
        <div class='app-title'>Mais que futebol, uma conexão!</div>
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
                        status_tipo_inicial = "Aprovada" if c_tipo == "Avulsa" else "Pendente Admin"
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(),
                            "nascimento": c_nasc.strip(),
                            "tipo": c_tipo,
                            "tipo_status": status_tipo_inicial,
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
        st.write("### Acesso Desenvolvedor")
        with st.form("form_login_dev_seguro"):
            senha_dev_input = st.text_input("Senha de Desenvolvedor", type="password")
            btn_entrar_dev = st.form_submit_button("Acessar Painel Dev")
            if btn_entrar_dev:
                if senha_dev_input == "1980":
                    st.session_state.usuario_logado = "Desenvolvedor"
                    st.session_state.cargo_logado = "Desenvolvedor"
                    st.rerun()
                else:
                    st.error("Senha incorreta!")

    st.stop()

# -----------------------------------------------------------------------------
# CABEÇALHO DO APLICATIVO LOGADO
# -----------------------------------------------------------------------------
st.markdown(
    "<div class='app-header' style='padding: 15px; display: flex; justify-content: space-between; align-items: center;'>"
    "<div><div class='app-subtitle'>Peladinha FC | Atleta: <b>" + str(st.session_state.usuario_logado) + " (" + str(st.session_state.cargo_logado) + ")</b></div></div>"
    "</div>",
    unsafe_allow_html=True
)

col_sair1, col_sair2 = st.columns([4, 1])
with col_sair2:
    if st.button("🚪 Sair"):
        st.session_state.usuario_logado = None
        st.session_state.cargo_logado = None
        st.session_state.pagina_atual = "🏠 Início"
        st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# NAVEGAÇÃO DE PÁGINAS
# -----------------------------------------------------------------------------
menu = st.session_state.pagina_atual

if menu != "🏠 Início":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_atual = "🏠 Início"
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# TELA INICIAL
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

            if st.button("⚙️ Painel Admin\n\nValidação de perfis e presenças", use_container_width=True):
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
            st.write("Jogadora logada: **" + str(jogadora_atual_nome) + "**")
            
            registro_presenca = next((p for p in st.session_state.presencas if p["nome"] == jogadora_atual_nome), None)
            ja_confirmada = registro_presenca is not None
            
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
                st.info("Você já está com presença confirmada!")
                c_aus = st.button("❌ Desconfirmar / Informar Ausência", use_container_width=True)
                if c_aus:
                    st.session_state.presencas = [p for p in st.session_state.presencas if p["nome"] != jogadora_atual_nome]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.warning("Presença cancelada.")
                    st.rerun()
        else:
            st.info("Modo Admin/Dev: Gerencie presenças livremente pelo 'Painel Admin'.")

    with col_B:
        st.write("### 📋 Status da Lista")
        lista_ordenada = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        mensalistas_confirmadas = []
        avulsas_confirmadas = []
        
        for p in lista_ordenada:
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            status_tipo_aprovado = j_info.get("tipo_status", "Aprovada") if j_info else "Aprovada"
            
            if tipo == "Mensalista" and status_tipo_aprovado == "Aprovada":
                mensalistas_confirmadas.append(p)
            else:
                avulsas_confirmadas.append(p)

        combinada = mensalistas_confirmadas + avulsas_confirmadas
        principal = combinada[:limite]
        espera = combinada[limite:]

        st.write("**🟢 Lista Principal (" + str(len(principal)) + "/" + str(limite) + ")**")
        for idx, p in enumerate(principal, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            st.markdown("<div class='card-team'><b>" + str(idx) + ".</b> " + p['nome'] + " <code>[" + tipo + "]</code> — <i>Conf: " + p['hora'] + "</i></div>", unsafe_allow_html=True)

        st.write("**⏳ Fila de Espera (" + str(len(espera)) + ")**")
        for idx, p in enumerate(espera, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            st.markdown("<div class='card-team'><b>" + str(idx) + "º espera:</b> " + p['nome'] + " <code>[" + tipo + "]</code></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times em Tempo Real")
    sorteio_atual = st.session_state.sorteio_oficial
    if sorteio_atual and "times" in sorteio_atual:
        st.write("### Sorteio Vigente (" + str(sorteio_atual.get('tipo', 'Principal')) + " - " + str(sorteio_atual.get('data')) + ")")
        cols = st.columns(len(sorteio_atual["times"]))
        for idx, (t_nome, membros) in enumerate(sorteio_atual["times"].items()):
            with cols[idx]:
                st.markdown("<div class='card-team'><h3>⚽ " + t_nome + "</h3>", unsafe_allow_html=True)
                for m in membros:
                    st.markdown("• " + m)
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Nenhum sorteio realizado para hoje ainda.")

    st.markdown("---")
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
            st.success("Sorteio realizado!")
            st.rerun()
        else:
            st.error("Jogadoras insuficientes.")

# -----------------------------------------------------------------------------
# PÁGINA: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco de Jogadoras")
    for j in st.session_state.jogadoras:
        status_aprov = j.get('tipo_status', 'Aprovada')
        st.markdown("<div class='card-team'><b>⚽ " + j['nome'] + "</b> — Categoria: <code>[" + j.get('tipo', 'Avulsa') + "]</code> (" + status_aprov + ") | Pagamento: <b>" + j.get('status_pagamento', 'Pendente') + "</b></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: PAGAMENTO & PIX
# -----------------------------------------------------------------------------
elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamento & Chave Pix")
    pix_chave = st.session_state.avisos.get("pix", "peladinhafc@email.com")
    st.markdown(
        "<div class='card-team'>"
        "<h3>💳 Dados para Transferência</h3>"
        "<p><b>Chave Pix:</b> <code>" + pix_chave + "</code></p>"
        "</div>",
        unsafe_allow_html=True
    )

    with st.form("form_comprovante", clear_on_submit=True):
        c_nome_jogadora = st.selectbox("Seu Nome", [j["nome"] for j in st.session_state.jogadoras])
        c_mes = st.text_input("Mês Referente", value=mes_vigente_str)
        c_semana = st.selectbox("Semana Referente", ["Semana 1", "Semana 2", "Semana 3", "Semana 4", "Semana 5"])
        c_ano = st.text_input("Ano Referente", value=ano_vigente_str)
        
        if st.form_submit_button("Enviar Comprovante"):
            st.session_state.comprovantes.append({
                "jogadora": c_nome_jogadora,
                "mes": c_mes,
                "semana": c_semana,
                "ano": c_ano,
                "status": "Pendente de Aprovação",
                "valor": float(st.session_state.avisos.get("valor_mensalidade", 80.00))
            })
            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
            st.success("Comprovante enviado com sucesso!")

# -----------------------------------------------------------------------------
# PÁGINA: REGULAMENTO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno")
    for reg in st.session_state.regulamento:
        st.markdown("<div class='card-team'><h3>" + reg['topico'] + "</h3><p>" + reg['regrinha'] + "</p></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: ANIVERSARIANTES
# -----------------------------------------------------------------------------
elif menu == "🎂 Aniversariantes":
    st.subheader("🎂 Aniversariantes do Mês")
    mes_atual_s = hoje_dt.strftime("/%m")
    aniversariantes = [j for j in st.session_state.jogadoras if j.get("nascimento", "").endswith(mes_atual_s)]
    for j in aniversariantes:
        st.markdown("<div class='card-team'>🎉 <b>" + j['nome'] + "</b> — Nascimento: <code>" + j.get('nascimento') + "</code></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA: FLUXO DE CAIXA
# -----------------------------------------------------------------------------
elif menu == "📊 Fluxo de Caixa":
    st.subheader("📊 Fluxo de Caixa / Financeiro")
    comprovantes_aprovados = [c for c in st.session_state.comprovantes if c.get("status") == "Aprovado"]
    total_comprovantes = sum(float(c.get("valor", 80.00)) for c in comprovantes_aprovados)
    total_saidas = sum(float(d.get("valor", 0)) for d in st.session_state.financeiro if d.get("tipo") == "Saída")
    st.metric(label="Balanço Geral", value="R$ " + str(total_comprovantes - total_saidas))

# -----------------------------------------------------------------------------
# PÁGINA: PAINEL ADMIN
# -----------------------------------------------------------------------------
elif menu == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel de Administração")
    tab_adm_perf, tab_adm_pres, tab_adm_comp, tab_adm_reg = st.tabs(["👥 Validar Mensalistas", "📌 Presenças", "💳 Comprovantes", "📜 Regulamento"])

    with tab_adm_perf:
        st.write("### 👥 Aprovação de Mensalistas")
        for idx_j, j_item in enumerate(st.session_state.jogadoras):
            if j_item.get("tipo") == "Mensalista" and j_item.get("tipo_status", "Aprovada") != "Aprovada":
                col_ap1, col_ap2 = st.columns([2, 1])
                with col_ap1:
                    st.markdown("• **" + j_item['nome'] + "**")
                with col_ap2:
                    if st.button("✅ Aprovar", key="aprovar_m_" + str(idx_j)):
                        j_item["tipo_status"] = "Aprovada"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.rerun()

    with tab_adm_pres:
        st.write("### 📌 Presenças")
        with st.form("form_admin_incluir_presenca", clear_on_submit=True):
            nome_j_man = st.text_input("Nome da Jogadora")
            if st.form_submit_button("Adicionar Presença"):
                if nome_j_man:
                    st.session_state.presencas.append({
                        "nome": nome_j_man.strip(),
                        "hora": hoje_dt.strftime("%H:%M:%S"),
                        "dt_confirmacao": hoje_dt.isoformat(),
                        "mes": mes_vigente_str,
                        "semana": "Semana 1"
                    })
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.rerun()

    with tab_adm_comp:
        st.write("### 🛡️ Comprovantes")
        for idx, comp in enumerate(st.session_state.comprovantes):
            if comp.get("status") == "Pendente de Aprovação":
                if st.button("Aprovar de " + comp['jogadora'], key="aprov_" + str(idx)):
                    comp["status"] = "Aprovado"
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.rerun()

    with tab_adm_reg:
        st.write("### 📜 Regulamento")
        with st.form("form_novo_reg", clear_on_submit=True):
            t = st.text_input("Título")
            x = st.text_area("Texto")
            if st.form_submit_button("Adicionar Regra"):
                if t and x:
                    st.session_state.regulamento.append({"topico": t, "regrinha": x})
                    salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                    st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA: ÁREA DO DESENVOLVEDOR
# -----------------------------------------------------------------------------
elif menu == "🛠️ Área do Desenvolvedor":
    st.subheader("🛠️ Área do Desenvolvedor")
    if st.button("🔄 Resetar Dados de Fábrica"):
        for f_path in [DATA_FILE, PRESENCAS_FILE, COMPROVANTES_FILE, FINANCE_FILE, REGULAMENTO_FILE]:
            if os.path.exists(f_path): os.remove(f_path)
        st.success("Resetado!")
        st.rerun()
