import streamlit as st
import pandas as pd
import json
import os
import random
import base64
from datetime import datetime, timezone, timedelta

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE SESSÃO E PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed"
)

FUSO_BRASIL = timezone(timedelta(hours=-3))

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (MELHORIA DE LEITURA E BOTÕES INTEGRADOS)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif;
        background-color: #0B132B !important;
        color: #FFFFFF !important;
    }

    .stApp {
        background-color: #0B132B;
    }

    /* Melhora de legibilidade para textos do Streamlit */
    p, span, label, div {
        color: #E2E8F0 !important;
        font-size: 1rem;
    }

    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    /* Card Personalizado */
    .card-box {
        background-color: #1C2541;
        border: 1px solid #3A506B;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 10px;
    }

    .card-title-text {
        font-size: 1.25rem;
        font-weight: 700;
        color: #38BDF8 !important;
        margin-bottom: 6px;
    }

    .card-desc-text {
        font-size: 0.9rem;
        color: #CBD5E1 !important;
        line-height: 1.4;
    }

    /* Botão integrado ao card */
    div.stButton > button {
        width: 100%;
        background-color: #1C2541 !important;
        color: #38BDF8 !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        font-weight: 700 !important;
        transition: all 0.2s ease;
    }
    
    div.stButton > button:hover {
        background-color: #38BDF8 !important;
        color: #0B132B !important;
    }

    /* Métrica / Destaque */
    .stat-card {
        background-color: #1C2541;
        border: 1px solid #3A506B;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
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

# -----------------------------------------------------------------------------
# ESTADO DA SESSÃO
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [
        {"nome": "Vagner Ferreira de Souza", "tipo": "Mensalista", "status": "Ativo", "login": "vagner", "senha": "123"}
    ])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "pix_chave": "31989684010",
        "pix_nome": "Vagner Ferreira de Souza",
        "pix_banco": "PicPay",
        "limite_vagas": 15
    })

if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 Prioridade Mensalistas", "regrinha": "Mensalistas têm vaga garantida na lista até às 17:00 de segunda-feira."},
        {"topico": "⏳ Promoção de Diaristas", "regrinha": "Às 17:00 as vagas remanescentes são preenchidas pelas diaristas da fila de espera."},
        {"topico": "🎲 Sorteio Oficial", "regrinha": "O sorteio dos times ocorre às 18:00 de forma equilibrada."}
    ])

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
    st.caption("peladinhas fc • Painel do Grupo")

with col_h2:
    if st.session_state.usuario_logado:
        st.write(f"👤 **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair", key="btn_logout"):
            st.session_state.usuario_logado = None
            st.rerun()
    elif st.session_state.admin_logged:
        st.write("🔑 **Modo Admin**")
        if st.button("🚪 Sair Admin", key="btn_logout_adm"):
            st.session_state.admin_logged = False
            st.rerun()
    else:
        if st.button("🔑 Entrar / Login", key="btn_login_top"):
            st.session_state.tela_atual = "Login"
            st.rerun()

st.markdown("---")

# -----------------------------------------------------------------------------
# TELA DE LOGIN
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
                    st.error("Senha incorreta!")

    if st.button("⬅️ Voltar ao Início"):
        st.session_state.tela_atual = "Home"
        st.rerun()

# -----------------------------------------------------------------------------
# TELA PRINCIPAL (CARDS LIMPOS E DIRETO AO PONTO)
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Home":
    col1, col2 = st.columns(2)

    with col1:
        # Card Regulamento
        st.markdown("""
        <div class='card-box'>
            <div class='card-title-text'>📜 Regulamento</div>
            <div class='card-desc-text'>Consulte as regras de presença, horários e prioridades.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar Regulamento ➔", key="c_reg"):
            st.session_state.tela_atual = "Regulamento"
            st.rerun()

        # Card Sorteio
        st.markdown("""
        <div class='card-box'>
            <div class='card-title-text'>🔀 Sorteio do Time</div>
            <div class='card-desc-text'>Visualização dos times sorteados ou divisão rápida.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Sorteio ➔", key="c_sor"):
            st.session_state.tela_atual = "Sorteio"
            st.rerun()

        # Card Pagamento
        st.markdown("""
        <div class='card-box'>
            <div class='card-title-text'>💸 Pagamento Pix</div>
            <div class='card-desc-text'>Chave Pix Vagner Souza (PicPay) e envio de comprovantes.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Pagamento Pix ➔", key="c_pix"):
            st.session_state.tela_atual = "Pagamento Pix"
            st.rerun()

    with col2:
        # Card Presença
        st.markdown("""
        <div class='card-box'>
            <div class='card-title-text'>📌 Confirmar Presença</div>
            <div class='card-desc-text'>Garanta sua vaga na lista da próxima segunda-feira.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Confirmar Presença ➔", key="c_pre"):
            st.session_state.tela_atual = "Confirmar Presenca"
            st.rerun()

        # Card Elenco
        st.markdown("""
        <div class='card-box'>
            <div class='card-title-text'>📋 Elenco de Jogadoras</div>
            <div class='card-desc-text'>Lista de mensalistas, diaristas e status do grupo.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Ver Elenco ➔", key="c_ele"):
            st.session_state.tela_atual = "Elenco"
            st.rerun()

        # Card Admin
        st.markdown("""
        <div class='card-box'>
            <div class='card-title-text'>⚙️ Painel Admin</div>
            <div class='card-desc-text'>Gestão de mensalistas, fluxo de caixa e comprovantes.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Painel Admin ➔", key="c_adm"):
            st.session_state.tela_atual = "Painel Admin"
            st.rerun()

# -----------------------------------------------------------------------------
# TELA: CONFIRMAR PRESENÇA
# -----------------------------------------------------------------------------
elif st.session_state.tela_atual == "Confirmar Presenca":
    st.subheader("📌 Lista de Presença")
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
        with st.form("form_p"):
            if st.session_state.usuario_logado:
                nome_c = st.session_state.usuario_logado
                st.write(f"Jogadora Logada: **{nome_c}**")
            else:
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
# TELA: PAGAMENTO PIX (REQUER LOGIN)
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

        st.text_input("Copiar Chave Pix:", value=st.session_state.avisos.get('pix_chave', '31989684010'), key="copy_pix")
        st.caption("🔒 Confira sempre o nome do beneficiário **Vagner Ferreira de Souza (PicPay)** antes de enviar.")

    with col_px2:
        st.markdown("### 📤 Enviar Comprovante")
        
        # EXIGE LOGIN PARA ENVIAR COMPROVANTE
        if not st.session_state.usuario_logado:
            st.warning("⚠️ Você precisa estar logada para enviar o comprovante de pagamento.")
            if st.button("🔑 Ir para Tela de Login"):
                st.session_state.tela_atual = "Login"
                st.rerun()
        else:
            st.success(f"Logada como: **{st.session_state.usuario_logado}**")
            with st.form("form_comp"):
                val_pag = st.number_input("Valor Pago (R$):", value=39.90, step=5.0)
                file_up = st.file_uploader("Anexe a imagem do Comprovante", type=["png", "jpg", "jpeg"])
                
                if st.form_submit_button("Enviar Comprovante (Enter)"):
                    if file_up:
                        b64_img = base64.b64encode(file_up.read()).decode("utf-8")
                        st.session_state.comprovantes.append({
                            "id": f"COMP_{random.randint(1000,9999)}",
                            "jogadora": st.session_state.usuario_logado,
                            "valor": val_pag,
                            "data": hoje_str,
                            "status": "Em Análise",
                            "imagem_b64": b64_img
                        })
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success("Comprovante enviado com sucesso para análise!")
                        st.rerun()
                    else:
                        st.error("Por favor, selecione um arquivo de imagem.")

# -----------------------------------------------------------------------------
# TELA: PAINEL ADMIN (APROVAÇÃO DE COMPROVANTES E EDITIONS)
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
            "💳 Confirmar Comprovantes", 
            "⚙️ Configurações"
        ])

        # --- TAB: GESTÃO DO ELENCO ---
        with tab_elenco:
            st.markdown("### 📋 Gerenciar Elenco & Modalidades")
            with st.expander("➕ Cadastrar Nova Jogadora"):
                with st.form("form_add_j"):
                    n_j = st.text_input("Nome Completo")
                    t_j = st.selectbox("Categoria", ["Mensalista", "Diarista"])
                    s_j = st.selectbox("Status", ["Ativo", "Inativo"])
                    if st.form_submit_button("Cadastrar Jogadora"):
                        if n_j:
                            st.session_state.jogadoras.append({
                                "nome": n_j.strip().title(),
                                "tipo": t_j,
                                "status": s_j,
                                "login": n_j.lower().replace(" ", ""),
                                "senha": "123"
                            })
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success("Jogadora cadastrada!")
                            st.rerun()

            st.markdown("---")
            for idx, j in enumerate(st.session_state.jogadoras):
                c_n, c_t, c_s, c_del = st.columns([2.5, 1.5, 1.5, 1])
                c_n.write(f"**{j['nome']}**")
                
                # Mudar Categoria
                novo_tipo = c_t.selectbox("Categoria", ["Mensalista", "Diarista"], index=0 if j.get("tipo") == "Mensalista" else 1, key=f"t_{idx}")
                if novo_tipo != j.get("tipo"):
                    j["tipo"] = novo_tipo
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.rerun()

                # Mudar Status
                novo_status = c_s.selectbox("Status", ["Ativo", "Inativo"], index=0 if j.get("status") == "Ativo" else 1, key=f"s_{idx}")
                if novo_status != j.get("status"):
                    j["status"] = novo_status
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.rerun()

                if c_del.button("🗑️ Excluir", key=f"d_{idx}"):
                    st.session_state.jogadoras.pop(idx)
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.rerun()

        # --- TAB: FLUXO DE CAIXA ---
        with tab_caixa:
            st.markdown("### 📊 Fluxo de Caixa Completo")
            tot_rec = sum(item["valor"] for item in st.session_state.financeiro if item["tipo"] == "Entrada (Receita)")
            tot_des = sum(item["valor"] for item in st.session_state.financeiro if item["tipo"] == "Saída (Despesa)")
            saldo_anual = tot_rec - tot_des

            m1, m2, m3 = st.columns(3)
            m1.metric("Receita Anual", f"R$ {tot_rec:.2f}")
            m2.metric("Despesa Anual", f"R$ {tot_des:.2f}")
            m3.metric("Saldo Geral", f"R$ {saldo_anual:.2f}")

            st.markdown("---")
            with st.form("form_lancar_caixa"):
                st.markdown("#### ➕ Novo Lançamento Manual")
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
            st.markdown("#### 📝 Extrato do Caixa")
            for idx_f, item_f in enumerate(st.session_state.financeiro):
                cf1, cf2, cf3, cf4 = st.columns([1, 2, 1, 1])
                cf1.write(f"📅 {item_f.get('data', hoje_str)}")
                cf2.write(f"**{item_f.get('descricao')}** ({item_f.get('tipo')})")
                cf3.write(f"R$ {item_f.get('valor'):.2f}")
                if cf4.button("🗑️ Rem", key=f"delfin_{idx_f}"):
                    st.session_state.financeiro.pop(idx_f)
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.rerun()

        # --- TAB: CONFIRMAR COMPROVANTES (SISTEMA DE APROVAÇÃO) ---
        with tab_comp:
            st.markdown("### 💳 Confirmar e Aprovar Pagamentos")
            if not st.session_state.comprovantes:
                st.info("Nenhum comprovante enviado ainda.")
            else:
                for idx_c, comp in enumerate(st.session_state.comprovantes):
                    with st.expander(f"📄 {comp['jogadora']} — R$ {comp['valor']:.2f} [{comp['status']}]"):
                        st.write(f"**Data de Envio:** {comp['data']}")
                        st.write(f"**Status Atual:** `{comp['status']}`")
                        
                        if "imagem_b64" in comp:
                            try:
                                img_bytes = base64.b64decode(comp["imagem_b64"])
                                st.image(img_bytes, caption=f"Comprovante de {comp['jogadora']}", width=300)
                            except Exception:
                                st.warning("Não foi possível carregar a imagem do comprovante.")

                        col_ap1, col_ap2, col_ap3 = st.columns(3)
                        
                        # Botão APROVAR
                        if col_ap1.button("✅ Aprovar Pagamento", key=f"ap_{idx_c}"):
                            comp["status"] = "Confirmado"
                            # Adiciona automaticamente na Receita do Caixa
                            st.session_state.financeiro.append({
                                "id": f"FIN_{random.randint(1000,9999)}",
                                "data": hoje_str,
                                "mes": mes_vigente_str,
                                "tipo": "Entrada (Receita)",
                                "descricao": f"Pagamento - {comp['jogadora']}",
                                "valor": comp['valor']
                            })
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                            st.success("Pagamento aprovado e registrado no Caixa!")
                            st.rerun()

                        # Botão REJEITAR
                        if col_ap2.button("❌ Rejeitar", key=f"rej_{idx_c}"):
                            comp["status"] = "Recusado"
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.warning("Comprovante recusado.")
                            st.rerun()

                        # Botão APAGAR
                        if col_ap3.button("🗑️ Excluir", key=f"delc_{idx_c}"):
                            st.session_state.comprovantes.pop(idx_c)
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.rerun()

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
                    st.success("Configurações atualizadas!")

# -----------------------------------------------------------------------------
# OUTRAS TELAS
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
    st.info("Ferramenta de sorteio e divisão de equipes das jogadoras confirmadas.")

elif st.session_state.tela_atual == "Elenco":
    st.subheader("📋 Elenco Cadastrado")
    if st.button("⬅️ Voltar"):
        st.session_state.tela_atual = "Home"
        st.rerun()
    df_e = pd.DataFrame(st.session_state.jogadoras)
    st.dataframe(df_e[["nome", "tipo", "status"]], use_container_width=True)
