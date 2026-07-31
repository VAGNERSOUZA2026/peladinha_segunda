import streamlit as st
import pandas as pd
import json
import os
import random

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
    /* Estilo Geral e Fontes */
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
        padding: 35px 20px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 25px;
    }
    .hero-title { font-size: 2.5rem; font-weight: 800; margin-bottom: 5px; color: #FFFFFF; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
    .hero-subtitle { font-size: 1.1rem; font-weight: 300; color: #E2E8F0; }

    /* Cards Informativos */
    .card-notice {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 6px solid #F59E0B;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    .card-pix {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border: 2px dashed #10B981;
        padding: 25px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0px 4px 12px rgba(16, 185, 129, 0.1);
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
    .developer-footer b { color: #F43F5E; }
    .developer-footer a { color: #38BDF8; text-decoration: none; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TRATAMENTO DE DADOS (ARQUIVOS JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"

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

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo! BOM DIVERTIMENTO!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 10
    })

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

# Lista filtrada de jogadoras ativas e cadastradas
jogadoras_cadastradas_ativas = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
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
# MENU LATERAL
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")
menu = st.sidebar.radio("Ir para:", [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times", 
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras", 
    "⚙️ Painel Admin"
])

# LOGIN ADMIN
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Acesso Restrito")
if not st.session_state.admin_logged:
    senha = st.sidebar.text_input("Senha Admin", type="password")
    if st.sidebar.button("Entrar como Admin"):
        if senha == "1980":
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

# RODAPÉ DO DESENVOLVEDOR NA SIDEBAR
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style='font-size: 0.8rem; color: #64748B; text-align: center;'>
    👨‍💻 <b>Desenvolvido por:</b><br>
    <b>Ciência da Computação</b><br>
    <span style='color: #0284C7; font-weight: 600;'>Vagner Souza</span><br>
    📞 (31) 98968-4010
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PÁGINA 1: CONFIRMAR PRESENÇA
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
        if not jogadoras_cadastradas_ativas:
            st.warning("Nenhuma jogadora ativa cadastrada no Painel Admin.")
        else:
            jogadora_sel = st.selectbox("Selecione seu nome na lista:", jogadoras_cadastradas_ativas)
            
            c_btn1, c_btn2 = st.columns(2)
            with c_btn1:
                if st.button("👍 Confirmar Presença", use_container_width=True):
                    if jogadora_sel in presencas_validas:
                        st.warning("Você já está na lista!")
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
                if st.button("❌ Cancelar Minha Presença", use_container_width=True):
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
                        st.error("Seu nome não está na lista de presença.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🛠️ Gestão de Presença (Admin)")
            
            jogadora_admin_sel = st.selectbox("Selecionar Jogadora (Admin):", jogadoras_cadastradas_ativas, key="admin_presence")
            ca1, ca2 = st.columns(2)
            with ca1:
                if st.button("➕ Confirmar para Jogadora", use_container_width=True):
                    if jogadora_admin_sel not in presencas_validas:
                        presencas_validas.append(jogadora_admin_sel)
                        st.session_state.presencas = presencas_validas
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"Presença de {jogadora_admin_sel} adicionada!")
                        st.rerun()
            with ca2:
                if st.button("🗑️ Remover do Jogo (Admin)", use_container_width=True):
                    if jogadora_admin_sel in presencas_validas:
                        estava_no_principal = presencas_validas.index(jogadora_admin_sel) < limite
                        presencas_validas.remove(jogadora_admin_sel)
                        st.session_state.presencas = presencas_validas
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.warning(f"{jogadora_admin_sel} removida da lista!")
                        
                        if estava_no_principal and len(presencas_validas) >= limite:
                            promovida = presencas_validas[limite - 1]
                            st.success(f"🚀 **{promovida}** subiu automaticamente da fila de espera!")
                        st.rerun()

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
        
        modo_sorteio = st.radio("Modo de Divisão de Times:", ["🤖 Automático (Calculado pelo sistema)", "✍️ Escolher Número de Times Manualmente"], horizontal=True)

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
                    min_jog = min(tamanhos)
                    max_jog = max(tamanhos)
                    st.markdown(f"""
                    <div class='card-alert'>
                        ⚖️ <b>SUGESTÃO PARA DESIGUALDADE NUMÉRICA:</b><br>
                        A divisão resultou em times com <b>{min_jog}</b> e <b>{max_jog}</b> jogadoras.<br>
                        💡 <b>Recomendação de Rodízio:</b> O(s) time(s) maior(es) pode(m) fazer rodízio de substituição a cada gol ou tempo, garantindo minutos iguais para todas!
                    </div>
                    """, unsafe_allow_html=True)

    with tab_atraso:
        st.info("💡 Marque apenas quem está **presente na quadra agora** para iniciar o jogo sem atrasos.")
        
        presentes_quadra = st.multiselect("Quem já chegou no campo/quadra?", presencas_validas)
        
        if st.button("⚡ Gerar Times para Começar Agora", use_container_width=True):
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
# PÁGINA 3: PIX E PAGAMENTO
# -----------------------------------------------------------------------------
elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Chave Pix para Pagamento")
    chave_pix = st.session_state.avisos.get("pix", "Não informada")

    st.markdown(f"""
    <div class='card-pix'>
        <h3>💰 Chave Pix Oficial do Grupo</h3>
        <p style='font-size: 1.6rem; font-weight: bold; color: #047857;'>{chave_pix}</p>
        <p><b>Vencimento:</b> {st.session_state.avisos.get('vencimento')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.text_input("Copiar Chave Pix:", value=chave_pix)


# -----------------------------------------------------------------------------
# PÁGINA 4: REGULAMENTO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento do Grupo")
    
    st.markdown("""
    ### ⚠️ Diretrizes e Boa Convivência
    
    1. **Respeito em Primeiro Lugar:** Não serão toleradas ofensas ou agressões.
    2. **Compromisso com Horário:** Chegue com antecedência para aquecimento.
    3. **Confirmação e Fila:** Cancelamentos promovem automaticamente quem está na fila de espera.
    4. **Jogo Limpo (Fair Play):** Evite jogadas divididas com risco de lesão.
    """)


# -----------------------------------------------------------------------------
# PÁGINA 5: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("🏃‍♀️ Elenco de Cadastradas")
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df[['nome', 'tipo', 'contato', 'status']], use_container_width=True, hide_index=True)
    else:
        st.info("Nenhuma jogadora cadastrada.")


# -----------------------------------------------------------------------------
# PÁGINA 6: PAINEL ADMIN
# -----------------------------------------------------------------------------
elif menu == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel do Administrador")
    
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita! Digite a senha no menu lateral para acessar.")
    else:
        t_cad, t_ger, t_avisos = st.tabs(["➕ Cadastrar Jogadora", "✏️ Gerenciar Jogadoras", "📢 Lembretes, Limite de Vagas & Pix"])
        
        with t_cad:
            st.subheader("Cadastrar Nova Jogadora")
            with st.form("cad_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    nome = st.text_input("Nome Completo *")
                    tipo = st.selectbox("Categoria *", ["Mensalista", "Avulso"])
                with col2:
                    contato = st.text_input("WhatsApp / Contato")
                    status = st.selectbox("Status *", ["Ativo", "Inativo"])
                
                if st.form_submit_button("💾 Salvar Cadastro", use_container_width=True):
                    if nome.strip():
                        st.session_state.jogadoras.append({
                            "nome": nome.strip(),
                            "posicao": "Jogadora",
                            "tipo": tipo,
                            "contato": contato.strip(),
                            "status": status
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"**{nome}** cadastrada com sucesso!")
                        st.rerun()

        with t_ger:
            st.subheader("Editar ou Excluir Jogadora")
            if st.session_state.jogadoras:
                nomes = [j["nome"] for j in st.session_state.jogadoras]
                sel_j = st.selectbox("Escolha uma jogadora:", nomes)
                idx = next(i for i, item in enumerate(st.session_state.jogadoras) if item["nome"] == sel_j)
                j_atual = st.session_state.jogadoras[idx]
                
                with st.form("edit_form"):
                    e_nome = st.text_input("Nome", value=j_atual["nome"])
                    e_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"], index=["Mensalista", "Avulso"].index(j_atual.get("tipo", "Mensalista")))
                    e_contato = st.text_input("Contato", value=j_atual.get("contato", ""))
                    e_status = st.selectbox("Status", ["Ativo", "Inativo"], index=["Ativo", "Inativo"].index(j_atual.get("status", "Ativo")))
                    
                    b1, b2 = st.columns(2)
                    if b1.form_submit_button("🔄 Atualizar Dados", use_container_width=True):
                        nome_antigo = j_atual["nome"]
                        novo_nome = e_nome.strip()

                        if nome_antigo in st.session_state.presencas:
                            p_idx = st.session_state.presencas.index(nome_antigo)
                            st.session_state.presencas[p_idx] = novo_nome
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)

                        st.session_state.jogadoras[idx] = {
                            "nome": novo_nome,
                            "posicao": "Jogadora",
                            "tipo": e_tipo,
                            "contato": e_contato.strip(),
                            "status": e_status
                        }
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Dados atualizados!")
                        st.rerun()
                        
                    if b2.form_submit_button("❌ Excluir do Cadastro Definitivamente", use_container_width=True):
                        nome_deletado = j_atual["nome"]
                        del st.session_state.jogadoras[idx]
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)

                        if nome_deletado in st.session_state.presencas:
                            st.session_state.presencas.remove(nome_deletado)
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)

                        st.warning(f"**{nome_deletado}** foi excluída de todo o sistema!")
                        st.rerun()

        with t_avisos:
            st.subheader("📢 Configurar Lembretes, Limite de Vagas e Pix")
            with st.form("form_avisos"):
                limite_v = st.number_input("Limite de Jogadoras no Dia:", min_value=2, max_value=50, value=st.session_state.avisos.get("limite_vagas", 10))
                venc = st.text_input("Dia de Vencimento:", value=st.session_state.avisos.get("vencimento", ""))
                rec = st.text_area("Lembrete / Recado do Grupo:", value=st.session_state.avisos.get("recado", ""))
                pix = st.text_input("Chave Pix:", value=st.session_state.avisos.get("pix", ""))
                
                if st.form_submit_button("💾 Salvar Configurações", use_container_width=True):
                    st.session_state.avisos = {
                        "limite_vagas": int(limite_v),
                        "vencimento": venc,
                        "recado": rec,
                        "pix": pix
                    }
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas!")
                    st.rerun()

# -----------------------------------------------------------------------------
# RODAPÉ FIXO DO DESENVOLVEDOR NO CORPO PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class='developer-footer'>
    💻 Desenvolvido por <b>Ciência da Computação</b> — <b>Vagner Souza</b> | 📱 <a href='https://wa.me/5531989684010' target='_blank'>(31) 98968-4010</a>
</div>
""", unsafe_allow_html=True)
