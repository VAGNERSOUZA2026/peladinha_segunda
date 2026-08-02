import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse
import base64
from io import BytesIO
from PIL import Image, ImageDraw
from datetime import datetime, timezone, timedelta
import html

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE SESSÃO E PÁGINA (TEMA DARK ESTILO APP)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FUSO_BRASIL = timezone(timedelta(hours=-3))

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT DARK BASEADO NAS IMAGENS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif;
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }

    .stApp {
        background-color: #0F172A;
    }

    /* Cards Grid */
    .app-card {
        background-color: #1E293B;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #334155;
        transition: transform 0.2s, border-color 0.2s;
        min-height: 140px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    
    .app-card:hover {
        border-color: #0EA5E9;
        transform: translateY(-2px);
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-top: 8px;
        margin-bottom: 4px;
    }

    .card-desc {
        font-size: 0.82rem;
        color: #94A3B8;
        line-height: 1.3;
    }

    .badge-pro {
        background-color: #0EA5E9;
        color: #FFFFFF;
        font-size: 0.65rem;
        font-weight: 800;
        padding: 2px 8px;
        border-radius: 6px;
        float: right;
    }

    .stat-box {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }

    .stat-value-green { font-size: 1.4rem; font-weight: 800; color: #22C55E; }
    .stat-value-red { font-size: 1.4rem; font-weight: 800; color: #EF4444; }
    .stat-value-blue { font-size: 1.4rem; font-weight: 800; color: #38BDF8; }

    /* Estilo para Botões Streamlit */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
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
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

def formatar_nome_proprio(texto):
    if not texto: return ""
    palavras_minusculas = {'de', 'da', 'do', 'dos', 'das', 'e'}
    palavras = texto.strip().split()
    resultado = []
    for idx, palavra in enumerate(palavras):
        palavra_lower = palavra.lower()
        if idx > 0 and palavra_lower in palavras_minusculas:
            resultado.append(palavra_lower)
        else:
            resultado.append(palavra_lower.capitalize())
    return " ".join(resultado)

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTADO DO SISTEMA (PERSISTENTE NA SESSÃO)
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [
        {"nome": "Vagner Ferreira de Souza", "tipo": "Mensalista", "status": "Ativo", "status_pagamento": "Pago", "nascimento": "03/08", "login": "vagner", "senha": "123"}
    ])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])

if "administradores" not in st.session_state:
    def_admins = [{"nome": "Vagner Souza (Admin)", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10",
        "recado": "Jogos todas as segundas-feiras!",
        "pix_chave": "31989684010",
        "pix_nome": "Vagner Ferreira de Souza",
        "pix_banco": "PicPay",
        "limite_vagas": 15
    })

if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 Prioridade Mensalistas", "regrinha": "Mensalistas têm vaga garantida na lista até às 17:00 de segunda-feira."},
        {"topico": "⏳ Promoção de Diaristas", "regrinha": "Às 17:00 as vagas remanescentes são preenchidas pelas diaristas da fila de espera."},
        {"topico": "🎲 Sorteio Oficial", "regrinha": "O sorteio dos times ocorre às 18:00 de forma equilibrada."},
        {"topico": "💸 Mensalidade / Diária", "regrinha": "Pagamentos via Pix para Vagner Souza (PicPay). Comprovantes enviados pelo app."}
    ])

if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

# Manter login ativo mesmo atualizando
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "tela_atual" not in st.session_state:
    st.session_state.tela_atual = "Home"

hoje_dt = datetime.now(FUSO_BRASIL)
hoje_str = hoje_dt.strftime("%d/%m/%Y")
mes_vigente_str = hoje_dt.strftime("%m/%Y")

# -----------------------------------------------------------------------------
# CABEÇALHO DO APP
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚽ Resenha")
    st.caption("peladinhas fc • Edição Feminina")

with col_h2:
    if st.session_state.usuario_logado:
        st.write(f"👤 **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair"):
            st.session_state.usuario_logado = None
            st.rerun()
    elif st.session_state.admin_logged:
        st.write("🔑 **Admin Ativo**")
        if st.button("🚪 Sair Admin"):
            st.session_state.admin_logged = False
            st.rerun()
    else:
        if st.button("🔑 Entrar / Login"):
            st.session_state.tela_atual = "Login"
            st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# TELA DE LOGIN / CADASTRO
# -----------------------------------------------------------------------------
if st.session_state.tela_atual == "Login":
    st.subheader("🔑 Acesso ao Sistema")
    t_log, t_adm = st.tabs(["Jogadora", "Administrador"])

    with t_log:
        with st.form("form_login"):
            l_u = st.text_input("Login")
            l_s = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user = next((j for j in st.session_state.jogadoras if j.get("login") == l_u and j.get("senha") == l_s), None)
                if user:
                    st.session_state.usuario_logado = user["nome"]
                    st.session_state.tela_atual = "Home"
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")

    with t_adm:
        with st.form("form_admin_login"):
            a_s = st.text_input("Senha de Administrador", type="password")
            if st.form_submit_button("Acessar Como Admin", use_container_width=True):
                if a_s == "1980":
                    st.session_state.admin_logged = True
                    st.session_state.tela_atual = "Painel Admin"
                    st.rerun()
                else:
                    st.error("Senha de admin incorreta!")

    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA PRINCIPAL (GRID DE CARDS / INTERFACE DO PRINT)
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Home":
    col1, col2 = st.columns(2)

    with col1:
        # Card 1: Regulamento (Substituiu Últimas Peladas)
        st.markdown("""
        <div class='app-card'>
            <div class='card-title'>📜 Regulamento</div>
            <div class='card-desc'>Consulte as regras de presença, horários e prioridades da pelada.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Regulamento", key="btn_reg"):
            st.session_state.tela_atual = "Regulamento"
            st.rerun()

        # Card 2: Sorteio do Time (Substituiu Seleção do Dia)
        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>🔀 Sorteio do Time</div>
            <div class='card-desc'>Visualização dos times sorteados ou divisão rápida de quadra.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Sorteio", key="btn_sor"):
            st.session_state.tela_atual = "Sorteio"
            st.rerun()

        # Card 3: Pagamento Pix (Substituiu Raio-X)
        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>💸 Pagamento Pix</div>
            <div class='card-desc'>Chave Pix do beneficiário Vagner Souza (PicPay) e envio de comprovantes.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Realizar Pagamento", key="btn_pix"):
            st.session_state.tela_atual = "Pagamento Pix"
            st.rerun()

    with col2:
        # Card 4: Confirmar Presença (Substituiu Aniversariantes)
        st.markdown("""
        <div class='app-card'>
            <div class='card-title'>📌 Confirmar Presença</div>
            <div class='card-desc'>Garanta sua vaga na lista da próxima segunda-feira.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Confirmar Minha Vaga", key="btn_pre"):
            st.session_state.tela_atual = "Confirmar Presenca"
            st.rerun()

        # Card 5: Elenco (Substituiu Rankings)
        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>📋 Elenco de Jogadoras</div>
            <div class='card-desc'>Lista de mensalistas, diaristas e status do grupo.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Elenco", key="btn_ele"):
            st.session_state.tela_atual = "Elenco"
            st.rerun()

        # Card 6: Painel Admin (Substituiu Churrascos)
        st.markdown("""
        <div class='app-card'>
            <span class='badge-pro'>PRO</span>
            <div class='card-title'>⚙️ Painel Admin</div>
            <div class='card-desc'>Gestão de mensalistas/diaristas, fluxo de caixa e aprovações.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Painel Administrativo", key="btn_adm_panel"):
            st.session_state.tela_atual = "Painel Admin"
            st.rerun()

# -----------------------------------------------------------------------------
# TELA: CONFIRMAR PRESENÇA
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Lista de Presença da Próxima Pelada")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()

    limite = st.session_state.avisos.get("limite_vagas", 15)
    
    col_l, col_a = st.columns([1.2, 1])
    
    with col_l:
        st.markdown(f"### 🟢 Vagas Confirmadas ({len(st.session_state.presencas)}/{limite})")
        if not st.session_state.presencas:
            st.info("Nenhuma jogadora confirmou presença ainda.")
        else:
            for i, p in enumerate(st.session_state.presencas, 1):
                nome_p = p["nome"] if isinstance(p, dict) else p
                tipo_p = p.get("tipo", "Diarista") if isinstance(p, dict) else "Diarista"
                st.write(f"**{i}.** {nome_p} `[{tipo_p}]`")

    with col_a:
        st.markdown("### ✍️ Marcar / Cancelar")
        with st.form("form_p", clear_on_submit=False):
            if st.session_state.usuario_logado:
                nome_c = st.session_state.usuario_logado
                st.write(f"Jogadora: **{nome_c}**")
            else:
                # Seleção e uso de enter
                jogadoras_ativas = [j["nome"] for j in st.session_state.jogadoras if j.get("status", "Ativo") == "Ativo"]
                nome_c = st.selectbox("Selecione seu nome:", jogadoras_ativas)

            c1, c2 = st.columns(2)
            btn_add = c1.form_submit_button("👍 Confirmar (Enter)")
            btn_rem = c2.form_submit_button("❌ Cancelar")

            if btn_add and nome_c:
                j_obj = next((j for j in st.session_state.jogadoras if j["nome"] == nome_c), None)
                tipo_str = j_obj.get("tipo", "Diarista") if j_obj else "Diarista"
                
                if not any((p["nome"] if isinstance(p, dict) else p) == nome_c for p in st.session_state.presencas):
                    st.session_state.presencas.append({"nome": nome_c, "tipo": tipo_str, "hora": hoje_dt.strftime("%H:%M")})
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.success("Presença confirmada!")
                    st.rerun()

            if btn_rem and nome_c:
                st.session_state.presencas = [p for p in st.session_state.presencas if (p["nome"] if isinstance(p, dict) else p) != nome_c]
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.info("Presença removida!")
                st.rerun()

# -----------------------------------------------------------------------------
# TELA: PAGAMENTO PIX
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Pagamento Pix":
    st.subheader("💸 Pagamento Pix & Comprovantes")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()

    col_px1, col_px2 = st.columns(2)

    with col_px1:
        st.markdown("### 🔑 Dados do Beneficiário")
        st.info(f"""
        **Beneficiário:** {st.session_state.avisos.get('pix_nome', 'Vagner Ferreira de Souza')}  
        **Instituição:** {st.session_state.avisos.get('pix_banco', 'PicPay')}  
        **Chave Pix (Celular):** `{st.session_state.avisos.get('pix_chave', '31989684010')}`
        """)

        # Botão/Campo para facilitar cópia direta
        st.text_input("Copiar Chave Pix:", value=st.session_state.avisos.get('pix_chave', '31989684010'), key="copy_pix")
        st.caption("🔒 Confira sempre o nome do beneficiário **Vagner Ferreira de Souza (PicPay)** antes de confirmar a transferência.")

    with col_px2:
        st.markdown("### 📤 Enviar Comprovante")
        with st.form("form_comp"):
            nome_pagador = st.text_input("Seu Nome:", value=st.session_state.usuario_logado if st.session_state.usuario_logado else "")
            val_pag = st.number_input("Valor Pago (R$):", value=39.90, step=5.0)
            file_up = st.file_uploader("Anexe o Comprovante", type=["png", "jpg", "jpeg", "pdf"])
            if st.form_submit_button("Enviar Comprovante (Enter)"):
                if nome_pagador and file_up:
                    b64_img = base64.b64encode(file_up.read()).decode("utf-8")
                    st.session_state.comprovantes.append({
                        "id": f"COMP_{random.randint(1000,9999)}",
                        "jogadora": nome_pagador,
                        "valor": val_pag,
                        "data": hoje_str,
                        "status": "Em Análise",
                        "imagem_b64": b64_img
                    })
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("Comprovante enviado com sucesso!")

# -----------------------------------------------------------------------------
# TELA: PAINEL ADMIN (COM GESTÃO DE ELENCO E FLUXO DE CAIXA COMPLETO)
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Painel Admin":
    st.subheader("⚙️ Painel de Administração")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()

    if not st.session_state.admin_logged:
        st.warning("🔒 Digite a senha do Administrador para continuar:")
        with st.form("form_pass_adm"):
            pwd = st.text_input("Senha Admin", type="password")
            if st.form_submit_button("Acessar Admin"):
                if pwd == "1980":
                    st.session_state.admin_logged = True
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
    else:
        tab_elenco, tab_caixa, tab_comp, tab_conf = st.tabs([
            "📋 Gestão do Elenco", 
            "📊 Fluxo de Caixa", 
            "💳 Comprovantes", 
            "⚙️ Configurações"
        ])

        # --- TAB: GESTÃO DO ELENCO (MENSALISTA/DIARISTA, ATIVO/INATIVO, EXCLUIR) ---
        with tab_elenco:
            st.markdown("### 📋 Gerenciar Elenco & Modalidades")
            
            # Adicionar Jogadora
            with st.expander("➕ Cadastrar Nova Jogadora"):
                with st.form("form_add_j"):
                    n_j = st.text_input("Nome Completo")
                    t_j = st.selectbox("Categoria", ["Mensalista", "Diarista"])
                    s_j = st.selectbox("Status", ["Ativo", "Inativo"])
                    if st.form_submit_button("Cadastrar Jogadora"):
                        if n_j:
                            st.session_state.jogadoras.append({
                                "nome": formatar_nome_proprio(n_j),
                                "tipo": t_j,
                                "status": s_j,
                                "status_pagamento": "Pendente",
                                "nascimento": "",
                                "login": n_j.lower().replace(" ", ""),
                                "senha": "123"
                            })
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success("Jogadora cadastrada!")
                            st.rerun()

            st.markdown("---")
            st.markdown("#### Lista de Jogadoras Cadastradas")

            for idx, j in enumerate(st.session_state.jogadoras):
                with st.container():
                    c_n, c_t, c_s, c_del = st.columns([2.5, 1.5, 1.5, 1])
                    
                    with c_n:
                        st.write(f"**{j['nome']}**")
                    
                    with c_t:
                        # Alterar Categoria
                        tipo_atual = j.get("tipo", "Diarista")
                        novo_tipo = st.selectbox("Categoria", ["Mensalista", "Diarista"], index=0 if tipo_atual == "Mensalista" else 1, key=f"tipo_{idx}")
                        if novo_tipo != tipo_atual:
                            j["tipo"] = novo_tipo
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.rerun()

                    with c_s:
                        # Alterar Status (Ativo / Inativo)
                        status_atual = j.get("status", "Ativo")
                        novo_status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if status_atual == "Ativo" else 1, key=f"status_{idx}")
                        if novo_status != status_atual:
                            j["status"] = novo_status
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.rerun()

                    with c_del:
                        if st.button("🗑️", key=f"del_{idx}"):
                            st.session_state.jogadoras.pop(idx)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.rerun()
                    st.markdown("<hr style='margin:5px 0;'>", unsafe_allow_html=True)

        # --- TAB: FLUXO DE CAIXA (MÊS, ANUAL, EDITAR, EXCLUIR) ---
        with tab_caixa:
            st.markdown("### 📊 Fluxo de Caixa Completo")

            # Métrica Totais
            df_cx = pd.DataFrame(st.session_state.financeiro)
            
            tot_rec = sum(item["valor"] for item in st.session_state.financeiro if item["tipo"] == "Entrada (Receita)")
            tot_des = sum(item["valor"] for item in st.session_state.financeiro if item["tipo"] == "Saída (Despesa)")
            saldo_anual = tot_rec - tot_des

            m1, m2, m3 = st.columns(3)
            m1.markdown(f"<div class='stat-box'><div class='card-desc'>Receita Anual</div><div class='stat-value-green'>R$ {tot_rec:.2f}</div></div>", unsafe_allow_html=True)
            m2.markdown(f"<div class='stat-box'><div class='card-desc'>Despesa Anual</div><div class='stat-value-red'>R$ {tot_des:.2f}</div></div>", unsafe_allow_html=True)
            m3.markdown(f"<div class='stat-box'><div class='card-desc'>Saldo Geral Anual</div><div class='stat-value-blue'>R$ {saldo_anual:.2f}</div></div>", unsafe_allow_html=True)

            st.markdown("---")
            with st.form("form_lancar_caixa"):
                st.markdown("#### ➕ Novo Lançamento")
                col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
                tp_trans = col_f1.selectbox("Tipo", ["Entrada (Receita)", "Saída (Despesa)"])
                ds_trans = col_f2.text_input("Descrição")
                vl_trans = col_f3.number_input("Valor (R$)", min_value=0.0, step=5.0)
                if st.form_submit_button("Lançar no Caixa (Enter)"):
                    if vl_trans > 0:
                        st.session_state.financeiro.append({
                            "id": f"FIN_{random.randint(1000,9999)}",
                            "data": hoje_str,
                            "mes": mes_vigente_str,
                            "tipo": tp_trans,
                            "descricao": ds_trans,
                            "valor": vl_trans
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento efetuado!")
                        st.rerun()

            st.markdown("---")
            st.markdown("#### 📝 Lançamentos (Editar / Excluir)")
            for idx_f, item_f in enumerate(st.session_state.financeiro):
                cf1, cf2, cf3, cf4 = st.columns([1, 2, 1, 1])
                cf1.write(f"📅 {item_f.get('data', hoje_str)}")
                cf2.write(f"**{item_f.get('descricao')}** ({item_f.get('tipo')})")
                cf3.write(f"R$ {item_f.get('valor'):.2f}")
                if cf4.button("🗑️ Excluir", key=f"delfin_{idx_f}"):
                    st.session_state.financeiro.pop(idx_f)
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.rerun()

        # --- TAB: COMPROVANTES ---
        with tab_comp:
            st.markdown("### 💳 Análise de Comprovantes")
            for comp in st.session_state.comprovantes:
                st.write(f"📄 **{comp['jogadora']}** — R$ {comp['valor']:.2f} | Status: `{comp['status']}`")

        # --- TAB: CONFIGURAÇÕES ---
        with tab_conf:
            st.markdown("### ⚙️ Ajustes do Pix & Sistema")
            with st.form("form_cfg"):
                p_nome = st.text_input("Nome do Beneficiário Pix", value=st.session_state.avisos.get("pix_nome", "Vagner Ferreira de Souza"))
                p_banco = st.text_input("Instituição / Banco", value=st.session_state.avisos.get("pix_banco", "PicPay"))
                p_chave = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix_chave", "31989684010"))
                lim_v = st.number_input("Limite de Vagas", value=st.session_state.avisos.get("limite_vagas", 15))
                if st.form_submit_button("Salvar Configurações"):
                    st.session_state.avisos["pix_nome"] = p_nome
                    st.session_state.avisos["pix_banco"] = p_banco
                    st.session_state.avisos["pix_chave"] = p_chave
                    st.session_state.avisos["limite_vagas"] = int(lim_v)
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas com sucesso!")

# -----------------------------------------------------------------------------
# OUTRAS TELAS: REGULAMENTO, SORTEIO, ELENCO
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Regulamento":
    st.subheader("📜 Regulamento Interno")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()
    for r in st.session_state.regulamento:
        st.markdown(f"#### {r['topico']}")
        st.write(r['regrinha'])

elif st.session_state.tela_atual == "Sorteio":
    st.subheader("🔀 Sorteio de Times")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()
    st.info("Utilize a ferramenta para montar e organizar as equipes para o próximo jogo.")

elif st.session_state.tela_atual == "Elenco":
    st.subheader("📋 Elenco Cadastrado")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()
    df_e = pd.DataFrame(st.session_state.jogadoras)
    st.dataframe(df_e[["nome", "tipo", "status"]], use_container_width=True)
