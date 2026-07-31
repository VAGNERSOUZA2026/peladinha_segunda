import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão de Futebol Feminino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (LAYOUT MODERNO & FEMININO)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* Banner Principal */
    .hero-banner {
        background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                    url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 25px;
    }
    .hero-title { font-size: 2.2rem; font-weight: 800; margin-bottom: 5px; color: #FFFFFF; }
    .hero-subtitle { font-size: 1.0rem; font-weight: 300; color: #E2E8F0; }

    /* Cards Informativos */
    .card-notice {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 6px solid #F59E0B;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
    
    .card-pix {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 2px dashed #10B981;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
    }

    .card-team {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #EC4899;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }

    .card-alert {
        background-color: #EFF6FF;
        border-left: 6px solid #3B82F6;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Rodapé Customizado */
    .developer-footer {
        background: #0F172A;
        color: #94A3B8;
        text-align: center;
        padding: 15px;
        border-radius: 12px;
        margin-top: 40px;
        font-size: 0.9rem;
    }
    .developer-footer b { color: #38BDF8; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TRATAMENTO DE DADOS (ARQUIVOS JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"

def carregar_dados(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def salvar_dados(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 10
    })

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# Lista filtrada de jogadoras ativas
jogadoras_cadastradas_ativas = [j["nome"] for j in st.session_state.jogadoras if j.get("status", "Ativo") == "Ativo"]
presencas_validas = [nome for nome in st.session_state.presencas if nome in jogadoras_cadastradas_ativas]

# -----------------------------------------------------------------------------
# BANNER DA APLICAÇÃO
# -----------------------------------------------------------------------------
st.markdown("""
<div class='hero-banner'>
    <div class='hero-title'>⚽ PELADINHA FC</div>
    <div class='hero-subtitle'>Gestão Inteligente & Sorteio de Futebol Feminino</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL & ÁREA DE LOGIN DA JOGADORA
# -----------------------------------------------------------------------------
st.sidebar.title("👤 Área do Usuário")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada como: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair do Perfil"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    tab_login, tab_cadastro = st.sidebar.tabs(["Entrar", "Criar Conta"])
    
    with tab_login:
        login_input = st.text_input("Login", key="l_user")
        senha_input = st.text_input("Senha", type="password", key="l_pass")
        if st.button("🔑 Entrar"):
            user_found = next((j for j in st.session_state.jogadoras if j.get("login") == login_input and j.get("senha") == senha_input), None)
            if user_found:
                st.session_state.usuario_logado = user_found["nome"]
                st.sidebar.success(f"Bem-vinda, {user_found['nome']}!")
                st.rerun()
            else:
                st.sidebar.error("Login ou senha incorretos!")

    with tab_cadastro:
        cad_nome = st.text_input("Seu Nome Completo")
        cad_user = st.text_input("Escolha um Login")
        cad_pass = st.text_input("Escolha uma Senha", type="password")
        cad_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"])
        cad_contato = st.text_input("WhatsApp")

        if st.button("📝 Cadastrar"):
            if cad_nome and cad_user and cad_pass:
                if any(j.get("login") == cad_user for j in st.session_state.jogadoras):
                    st.sidebar.error("Esse login já está em uso!")
                else:
                    st.session_state.jogadoras.append({
                        "nome": cad_nome.strip(),
                        "login": cad_user.strip(),
                        "senha": cad_pass.strip(),
                        "tipo": cad_tipo,
                        "contato": cad_contato.strip(),
                        "status": "Ativo"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.sidebar.success("Conta criada! Agora faça seu login.")
                    st.rerun()
            else:
                st.sidebar.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.title("📌 Navegação")
menu = st.sidebar.radio("Ir para:", [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times", 
    "📊 Fluxo de Caixa",
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras", 
    "⚙️ Painel Admin"
])

# LOGIN ADMIN
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Acesso Restrito (Admin)")
if not st.session_state.admin_logged:
    senha_admin = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar como Admin"):
        if senha_admin == "1980":
            st.session_state.admin_logged = True
            st.sidebar.success("Modo Admin Ativo!")
            st.rerun()
        else:
            st.sidebar.error("Senha incorreta")
else:
    st.sidebar.info("🔑 Modo Admin Ativado")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.rerun()

# CRÉDITOS DO DESENVOLVEDOR NA SIDEBAR
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.85rem; color: #64748B; text-align: center;'>
    👨‍💻 <b>Desenvolvido por:</b><br>
    <span style='color: #0284C7; font-weight: 600;'>Vagner Souza / Ciência da Computação</span>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PÁGINA 1: CONFIRMAR PRESENÇA (RESTRINGIDA POR LOGIN)
# -----------------------------------------------------------------------------
if menu == "📌 Presença no Jogo":
    limite = st.session_state.avisos.get("limite_vagas", 10)

    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>MURAL DE AVISOS DO GRUPO:</b><br>
        🎯 <b>Limite de Vagas:</b> {limite} jogadoras<br>
        📅 <b>Vencimento Mensalidade:</b> {st.session_state.avisos.get('vencimento')}<br>
        💡 <b>Lembrete:</b> {st.session_state.avisos.get('recado')}
    </div>
    """, unsafe_allow_html=True)

    col_c1, col_c2 = st.columns([2, 1])

    with col_c1:
        st.subheader("✅ Marcar ou Desmarcar Presença")
        
        # VERIFICAÇÃO DE PERMISSÃO: Precisa ser Usuário Logado ou Admin
        pode_alterar = st.session_state.usuario_logado is not None or st.session_state.admin_logged

        if not pode_alterar:
            st.warning("🔒 **Acesso restrito:** Para confirmar ou desmarcar sua presença na lista, você precisa **fazer login no menu lateral** ou ser um Administrador.")
        else:
            # Se for Admin, pode selecionar qualquer jogadora. Se for jogadora comum, altera apenas o próprio perfil.
            if st.session_state.admin_logged and not st.session_state.usuario_logado:
                st.info("🔑 **Modo Admin:** Selecione a jogadora que deseja gerenciar.")
                jogadora_sel = st.selectbox("Selecione a jogadora:", jogadoras_cadastradas_ativas) if jogadoras_cadastradas_ativas else None
            else:
                jogadora_sel = st.session_state.usuario_logado
                st.success(f"Gerenciando presença de: **{jogadora_sel}**")

            if jogadora_sel:
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button("👍 Confirmar Presença", use_container_width=True):
                        if jogadora_sel in presencas_validas:
                            st.warning("Já está na lista de presença!")
                        else:
                            presencas_validas.append(jogadora_sel)
                            st.session_state.presencas = presencas_validas
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            
                            if len(presencas_validas) <= limite:
                                st.success(f"🎉 {jogadora_sel} confirmada na lista principal!")
                            else:
                                st.warning(f"⚠️ Vagas esgotadas! {jogadora_sel} entrou na **Fila de Espera**.")
                            st.rerun()

                with c_btn2:
                    if st.button("❌ Cancelar Presença", use_container_width=True):
                        if jogadora_sel in presencas_validas:
                            estava_no_principal = presencas_validas.index(jogadora_sel) < limite
                            
                            presencas_validas.remove(jogadora_sel)
                            st.session_state.presencas = presencas_validas
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.info(f"{jogadora_sel} foi removida da lista.")

                            if estava_no_principal and len(presencas_validas) >= limite:
                                promovida = presencas_validas[limite - 1]
                                st.balloons()
                                st.success(f"🚀 **{promovida}** subiu automaticamente para a lista principal!")
                            
                            st.rerun()
                        else:
                            st.error("O nome não está na lista de presença.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🛠️ Gestão Rápida (Admin)")
            if st.button("🚨 Zerar Toda a Lista do Jogo", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.warning("Lista de presenças zerada!")
                st.rerun()

    with col_c2:
        confirmadas = presencas_validas[:limite]
        espera = presencas_validas[limite:]

        st.subheader(f"📋 Confirmadas ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.write("Nenhuma presença confirmada.")
        else:
            for idx, nome in enumerate(confirmadas, 1):
                st.write(f"**{idx}.** {nome}")

        if espera:
            st.markdown("---")
            st.subheader(f"⏳ Fila de Espera ({len(espera)})")
            for idx, nome in enumerate(espera, 1):
                st.write(f"**{idx}.** {nome} *(Aguardando vaga)*")


# -----------------------------------------------------------------------------
# PÁGINA 2: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Divisão e Sorteio de Times")

    tab_oficial, tab_atraso = st.tabs(["⭐ Sorteio Geral (Confirmadas)", "⏱️ Sorteio Provisório (Quem Já Chegou)"])

    limite = st.session_state.avisos.get("limite_vagas", 10)
    confirmadas = presencas_validas[:limite]

    with tab_oficial:
        st.write(f"Total de jogadoras na lista principal: **{len(confirmadas)}**")
        
        modo_sorteio = st.radio("Modo de Divisão:", ["🤖 Automático (Calculado pelo sistema)", "✍️ Escolher Número de Times Manualmente"], horizontal=True)

        qtd_times = 2
        if modo_sorteio == "✍️ Escolher Número de Times Manualmente":
            qtd_times = st.slider("Dividir em quantos times?", 2, 6, 2, key="qtd_oficial")
        else:
            total = len(confirmadas)
            if total >= 18:
                qtd_times = 4
            elif total >= 13:
                qtd_times = 3
            else:
                qtd_times = 2
            st.info(f"💡 O sistema definiu **{qtd_times} times** com base nas {total} jogadoras confirmadas.")

        if st.button("🎲 Sortear Times Agora", use_container_width=True):
            if len(confirmadas) < qtd_times:
                st.error(f"Número insuficiente de jogadoras para dividir em {qtd_times} times.")
            else:
                lista_temp = confirmadas.copy()
                random.shuffle(lista_temp)
                
                times = [[] for _ in range(qtd_times)]
                for idx, p in enumerate(lista_temp):
                    times[idx % qtd_times].append(p)
                
                cols = st.columns(qtd_times)
                tamanhos = []
                for i, t in enumerate(times):
                    tamanhos.append(len(t))
                    with cols[i]:
                        st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1} ({len(t)})</h3>", unsafe_allow_html=True)
                        for item in t:
                            st.write(f"• **{item}**")
                        st.markdown("</div>", unsafe_allow_html=True)

                if len(set(tamanhos)) > 1:
                    min_jog, max_jog = min(tamanhos), max(tamanhos)
                    st.markdown(f"""
                    <div class='card-alert'>
                        ⚖️ <b>SUGESTÃO PARA DESIGUALDADE NUMÉRICA:</b><br>
                        A divisão resultou em times com <b>{min_jog}</b> e <b>{max_jog}</b> jogadoras.<br>
                        💡 <b>Recomendação de Rodízio:</b> O(s) time(s) maior(es) pode(m) fazer rodízio de substituição a cada gol ou tempo.
                    </div>
                    """, unsafe_allow_html=True)

    with tab_atraso:
        st.info("💡 Marque apenas quem está **presente na quadra agora**.")
        presentes_quadra = st.multiselect("Quem já chegou no campo/quadra?", presencas_validas)
        
        if st.button("⚡ Gerar Times Rápidos", use_container_width=True):
            if len(presentes_quadra) < 2:
                st.error("Selecione pelo menos 2 jogadoras.")
            else:
                random.shuffle(presentes_quadra)
                meio = len(presentes_quadra) // 2
                t1, t2 = presentes_quadra[:meio], presentes_quadra[meio:]
                
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"<div class='card-team'><h3>🔴 Time Colete ({len(t1)})</h3>", unsafe_allow_html=True)
                    for p in t1: st.write(f"• {p}")
                    st.markdown("</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<div class='card-team'><h3>🔵 Time Sem Colete ({len(t2)})</h3>", unsafe_allow_html=True)
                    for p in t2: st.write(f"• {p}")
                    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PÁGINA 3: FLUXO DE CAIXA E PRESTAÇÃO DE CONTAS
# -----------------------------------------------------------------------------
elif menu == "📊 Fluxo de Caixa":
    st.subheader("📊 Fluxo de Caixa & Prestação de Contas")

    df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor"])
    
    total_entradas = df_fin[df_fin["tipo"] == "Entrada"]["valor"].sum() if not df_fin.empty else 0.0
    total_saidas = df_fin[df_fin["tipo"] == "Saída"]["valor"].sum() if not df_fin.empty else 0.0
    saldo_atual = total_entradas - total_saidas

    # Métricas Superiores
    m1, m2, m3 = st.columns(3)
    m1.metric("🟢 Total Receitas", f"R$ {total_entradas:.2f}")
    m2.metric("🔴 Total Despesas", f"R$ {total_saidas:.2f}")
    m3.metric("💰 Saldo Atual", f"R$ {saldo_atual:.2f}")

    st.markdown("---")

    col_f1, col_f2 = st.columns([2, 1])

    with col_f1:
        st.write("### 📜 Histórico de Lançamentos")
        if not df_fin.empty:
            df_exibicao = df_fin.copy()
            df_exibicao["valor"] = df_exibicao["valor"].apply(lambda v: f"R$ {v:.2f}")
            st.dataframe(df_exibicao, use_container_width=True)
        else:
            st.info("Nenhum lançamento registrado no momento.")

    with col_f2:
        if st.session_state.admin_logged:
            tab_novo, tab_editar, tab_excluir = st.tabs(["➕ Novo", "✏️ Editar", "🗑️ Excluir"])

            # ---- ABA 1: NOVO LANÇAMENTO ----
            with tab_novo:
                st.write("#### Novo Lançamento")
                with st.form("form_fin_novo", clear_on_submit=True):
                    f_data = st.text_input("Data (DD/MM/AAAA)", value="30/07/2026")
                    f_desc = st.text_input("Descrição (ex: Mensalidade Fulana)")
                    f_tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
                    f_valor = st.number_input("Valor (R$)", min_value=0.01, step=5.0)

                    if st.form_submit_button("💾 Salvar Registro", use_container_width=True):
                        st.session_state.financeiro.append({
                            "data": f_data,
                            "descricao": f_desc,
                            "tipo": f_tipo,
                            "valor": float(f_valor)
                        })
                        salvar_dados(FINAN
