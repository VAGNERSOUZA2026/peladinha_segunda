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
# CONFIGURAÇÃO DA PÁGINA (TEMA ESCURO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão Inteligente",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA (BOTÕES LEGÍVEIS E ALTO CONTRASTE)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
    }

    .stApp {
        background-color: #111827;
        color: #F3F4F6;
    }

    .app-header {
        background: #1F2937;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #374151;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3);
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
    }
    .app-subtitle {
        font-size: 0.85rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .dashboard-card {
        background-color: #1F2937;
        border: 1px solid #374151;
        border-radius: 16px;
        padding: 20px;
        height: 100%;
        color: #FFFFFF;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.2);
        transition: all 0.2s ease-in-out;
        margin-bottom: 15px;
    }
    .dashboard-card:hover {
        border-color: #0D9488;
        transform: translateY(-3px);
        box-shadow: 0px 6px 15px rgba(13, 148, 136, 0.2);
    }

    .card-notice {
        background: #1F2937;
        border-left: 5px solid #0D9488;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #E5E7EB;
        border-top: 1px solid #374151;
        border-right: 1px solid #374151;
        border-bottom: 1px solid #374151;
    }

    .card-team {
        background: #1F2937;
        border: 1px solid #374151;
        border-top: 4px solid #0D9488;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 15px;
    }

    /* Cores e Legibilidade dos Botões de Ação de Presença */
    div.stButton > button:first-child {
        background-color: #0D9488 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: 1px solid #14B8A6 !important;
        padding: 10px 20px !important;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
    }
    div.stButton > button:first-child:hover {
        background-color: #0F766E !important;
        border-color: #2DD4BF !important;
    }

    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #374151 !important;
        color: #FFFFFF !important;
        border: 1px solid #4B5563 !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TRATAMENTO DE DADOS (ARQUIVOS JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
COMPROVANTES_FILE = "comprovantes.json"
UPLOAD_DIR = "comprovantes_imgs"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

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

def obter_nome_p(p):
    return p["nome"] if isinstance(p, dict) else p

def obter_hora_p(p):
    return p.get("hora", "") if isinstance(p, dict) else ""

def obter_tipo_p(p):
    return p.get("tipo", "Avulso") if isinstance(p, dict) else "Avulso"

if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])
if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])
if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])
if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])
if "administradores" not in st.session_state:
    def_admins = [{"nome": "Administrador Principal", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 15
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda têm prioridade na lista principal. Ao cancelar e voltar, vai para o fim da fila."},
        {"topico": "⏳ 2. Fila de Espera", "regrinha": "Quem confirmar após as 17:00 ou exceder o limite vai para a fila de espera."},
        {"topico": "❌ 3. Desistências", "regrinha": "Ao cancelar, a vaga é repassada imediatamente."},
        {"topico": "💸 4. Mensalidades", "regrinha": "Pagas via Pix até a data estipulada."}
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "🏠 Início"
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""
if "msg_cadastro_sucesso" not in st.session_state:
    st.session_state.msg_cadastro_sucesso = False

# -----------------------------------------------------------------------------
# CABEÇALHO DO APLICATIVO
# -----------------------------------------------------------------------------
st.markdown("""
<div class='app-header'>
    <div class='app-subtitle'>peladinha fc</div>
    <div class='app-title'>Resenha & Gestão</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# BARRA LATERAL (AUTENTICAÇÃO E CADASTRO)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Acesso & Contas")
    
    if st.session_state.usuario_logado:
        st.success(f"Jogadora: **{st.session_state.usuario_logado}**")
        if st.button("🚪 Sair da Conta", use_container_width=True):
            st.session_state.usuario_logado = None
            st.rerun()
    else:
        st.subheader("🔑 Entrar na Jogadora")
        if st.session_state.msg_cadastro_sucesso:
            st.success("Cadastro realizado! Faça login abaixo.")
            st.session_state.msg_cadastro_sucesso = False
            
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    st.session_state.usuario_logado = user_found["nome"]
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")

        st.markdown("---")
        st.subheader("📝 Cadastrar Nova Jogadora")
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_tipo = st.selectbox("Tipo:", ["Avulso", "Mensalista"])
            c_user = st.text_input("Login *")
            c_pass = st.text_input("Senha *", type="password")
            if st.form_submit_button("Criar Conta", use_container_width=True):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Login já em uso!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": c_tipo, "mes_vigente": mes_vigente_str, "status": "Ativo"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.session_state.msg_cadastro_sucesso = True
                        st.rerun()
                else:
                    st.error("Preencha os campos obrigatórios!")

    st.markdown("---")
    st.subheader("🔒 Área do Administrador")
    if not st.session_state.admin_logged:
        with st.form("form_login_admin"):
            adm_user = st.text_input("Login Admin")
            adm_pass = st.text_input("Senha Admin", type="password")
            if st.form_submit_button("Acessar Admin", use_container_width=True):
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm.get("login") == adm_user and adm.get("senha") == adm_pass), None)
                if admin_encontrado:
                    st.session_state.admin_logged = True
                    st.session_state.admin_nome = admin_encontrado["nome"]
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
    else:
        st.info(f"Logado como Admin: **{st.session_state.admin_nome}**")
        if st.button("Sair do Admin", use_container_width=True):
            st.session_state.admin_logged = False
            st.session_state.admin_nome = ""
            st.rerun()

# -----------------------------------------------------------------------------
# NAVEGAÇÃO ENTRE TELAS
# -----------------------------------------------------------------------------
menu = st.session_state.pagina_atual

if menu != "🏠 Início":
    if st.button("⬅️ Voltar ao Início"):
        st.session_state.pagina_atual = "🏠 Início"
        st.rerun()
    st.markdown("---")

# -----------------------------------------------------------------------------
# RENDERIZAÇÃO DAS PÁGINAS
# -----------------------------------------------------------------------------
if menu == "🏠 Início":
    col_topo1, col_topo2 = st.columns([3, 1])
    with col_topo2:
        if st.session_state.admin_logged:
            if st.button("⚙️ Painel Admin"):
                st.session_state.pagina_atual = "⚙️ Painel Admin"
                st.rerun()

    c1, c2 = st.columns(2)
    
    with c1:
        if st.button("📌 **Presença no Jogo**\n\nConfirme ou altere sua vaga na pelada.", use_container_width=True, key="btn_card_presenca"):
            st.session_state.pagina_atual = "📌 Presença no Jogo"
            st.rerun()
            
        if st.button("🔀 **Sorteio de Times**\n\nVeja a distribuição oficial ou da quadra.", use_container_width=True, key="btn_card_sorteio"):
            st.session_state.pagina_atual = "🔀 Sorteio de Times"
            st.rerun()

        if st.button("📜 **Regulamento**\n\nConheça as regras e prioridades do grupo.", use_container_width=True, key="btn_card_regulamento"):
            st.session_state.pagina_atual = "📜 Regulamento"
            st.rerun()

    with c2:
        if st.button("🎂 **Aniversariantes**\n\nVeja quem faz aniversário no mês corrente.", use_container_width=True, key="btn_card_aniversariantes"):
            st.session_state.pagina_atual = "🎂 Aniversariantes"
            st.rerun()

        if st.button("💸 **Pagamento & Pix**\n\nChave Pix e envio de comprovantes.", use_container_width=True, key="btn_card_pagamento"):
            st.session_state.pagina_atual = "💸 Pagamento & Pix"
            st.rerun()

        if st.button("📋 **Elenco de Jogadoras**\n\nConsulte todas as atletas cadastradas.", use_container_width=True, key="btn_card_elenco"):
            st.session_state.pagina_atual = "📋 Elenco de Jogadoras"
            st.rerun()

    if st.session_state.admin_logged:
        st.markdown("---")
        if st.button("📊 Abrir Fluxo de Caixa (Admin)", use_container_width=True):
            st.session_state.pagina_atual = "📊 Fluxo de Caixa"
            st.rerun()

elif menu == "📌 Presença no Jogo":
    st.subheader("📌 Presença no Jogo")
    limite = st.session_state.avisos.get("limite_vagas", 15)
    
    jogadoras_ativas = [j for j in st.session_state.jogadoras if j.get("status") != "Inativo"]
    nomes_ativas = {j["nome"] for j in jogadoras_ativas}
    presencas_ativas = [p for p in st.session_state.presencas if obter_nome_p(p) in nomes_ativas]
    
    # Ordenação considerando a regra do fim da fila em caso de reconfirmação
    lista_atual = sorted(presencas_ativas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
    
    # Separando mensalistas e avulsas conforme horário limite (Segunda-feira 17:00)
    mensalistas = []
    avulsas = []
    
    for p in lista_atual:
        tipo = obter_tipo_p(p)
        dt_conf_str = p.get("dt_confirmacao", "")
        atrasada_mensalista = False
        
        if dt_conf_str:
            try:
                dt_obj = datetime.fromisoformat(dt_conf_str)
                # Verifica se confirmou após segunda-feira 17:00
                if dt_obj.weekday() == 0 and dt_obj.hour >= 17:
                    atrasada_mensalista = True
            except:
                pass
                
        if tipo == "Mensalista" and not atrasada_mensalista:
            mensalistas.append(p)
        else:
            avulsas.append(p)
    
    confirmadas = mensalistas[:limite]
    espera = mensalistas[limite:] + avulsas

    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        st.write(f"### 🟢 Confirmadas ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.info("Nenhuma jogadora confirmada.")
        for i, p in enumerate(confirmadas, 1):
            st.markdown(f"<div class='card-team'><b>{i}.</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]` — <i>{obter_hora_p(p)}</i></div>", unsafe_allow_html=True)

        st.write(f"### ⏳ Fila de Espera ({len(espera)})")
        for i, p in enumerate(espera, 1):
            st.markdown(f"<div class='card-team'><b>{i}º:</b> {obter_nome_p(p)} `[{obter_tipo_p(p)}]`</div>", unsafe_allow_html=True)

    with col_l2:
        st.write("### ✍️ Gerenciar Minha Presença")
        if not st.session_state.usuario_logado:
            st.warning("Faça login na barra lateral para confirmar presença.")
        else:
            j_nome = st.session_state.usuario_logado
            dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == j_nome), None)
            tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"
            
            # Verifica posição atual da usuária
            pos_conf = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == j_nome), None)
            pos_esp = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == j_nome), None)
            
            if pos_conf:
                st.success(f"🎉 Você está na **Lista Principal** na posição **{pos_conf}**!")
            elif pos_esp:
                st.warning(f"⏳ Você está na **Fila de Espera** na posição **{pos_esp}º**.")
            else:
                st.info("ℹ️ Você não está confirmada no momento.")

            with st.form("form_pres"):
                c_ok = st.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                c_canc = st.form_submit_button("❌ Cancelar Presença", use_container_width=True)

            ja_na_lista = (pos_conf is not None or pos_esp is not None)

            if c_ok:
                # Remove registro anterior para recolocá-lo ao fim da fila (regra de reconfirmação / perda de prioridade)
                st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_nome]
                
                st.session_state.presencas.append({
                    "nome": j_nome, 
                    "hora": hoje_dt.strftime("%H:%M"),
                    "tipo": tipo_j,
                    "dt_confirmacao": hoje_dt.isoformat() # Atualiza para o horário atual, mandando para o fim da fila
                })
                salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                st.success("Presença registrada/atualizada com sucesso! (Movida para o fim da fila de preferências)")
                st.rerun()

            if c_canc:
                if ja_na_lista:
                    st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != j_nome]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.info("Presença cancelada com sucesso!")
                    st.rerun()
                else:
                    st.error("Seu nome não está na lista para ser cancelado.")

elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    sorteio_salvo = st.session_state.sorteio_oficial
    if sorteio_salvo and "times" in sorteio_salvo:
        cols = st.columns(len(sorteio_salvo["times"]))
        for idx, (nome_time, membros) in enumerate(sorteio_salvo["times"].items()):
            with cols[idx]:
                st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                for item in membros:
                    st.markdown(f"• **{item}**")
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Nenhum sorteio oficial gerado ainda.")

    if st.session_state.admin_logged:
        st.markdown("---")
        if st.button("🎲 Executar Sorteio Agora", use_container_width=True):
            confirmadas_nomes = [obter_nome_p(p) for p in st.session_state.presencas]
            if len(confirmadas_nomes) >= 2:
                random.shuffle(confirmadas_nomes)
                res_times = {"Time 1": confirmadas_nomes[::2], "Time 2": confirmadas_nomes[1::2]}
                st.session_state.sorteio_oficial = {"data": data_hoje_id, "hora": hoje_dt.strftime('%H:%M'), "times": res_times}
                salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                st.success("Sorteio realizado!")
                st.rerun()

elif menu == "🎂 Aniversariantes":
    st.subheader("🎂 Aniversariantes do Mês")
    mes_atual_num = hoje_dt.strftime("/%m")
    aniversariantes_mes = [j for j in st.session_state.jogadoras if j.get("nascimento", "").endswith(mes_atual_num)]
    
    if not aniversariantes_mes:
        st.info("Nenhuma aniversariante cadastrada para este mês.")
    else:
        for j in aniversariantes_mes:
            st.markdown(f"""
            <div class='card-team'>
                🎉 <b>{j['nome']}</b> — Data: <code>{j.get('nascimento')}</code>
            </div>
            """, unsafe_allow_html=True)

elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamentos e Chave Pix")
    st.markdown(f"""
    <div class='card-notice'>
        📌 <b>Chave Pix Oficial:</b> <code>{st.session_state.avisos.get('pix', 'peladinhafc@email.com')}</code><br>
        Vencimento: <b>{st.session_state.avisos.get('vencimento', 'Todo dia 10')}</b>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.usuario_logado:
        with st.form("form_comp", clear_on_submit=True):
            comp_obs = st.text_input("Observação (Ex: Mensalidade)")
            arquivo_img = st.file_uploader("Comprovante (Imagem)", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("Enviar Comprovante", use_container_width=True):
                if arquivo_img:
                    path = os.path.join(UPLOAD_DIR, f"{st.session_state.usuario_logado}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    with open(path, "wb") as f:
                        f.write(arquivo_img.getbuffer())
                    st.session_state.comprovantes.append({"jogadora": st.session_state.usuario_logado, "mes": mes_vigente_str, "obs": comp_obs, "arquivo": path, "data": hoje_dt.strftime("%d/%m/%Y")})
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                    st.success("Comprovante enviado com sucesso!")

elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno")
    for reg in st.session_state.regulamento:
        st.markdown(f"""
        <div class='card-team'>
            <h3 style='color: #0D9488;'>{reg['topico']}</h3>
            <p>{reg['regrinha']}</p>
        </div>
        """, unsafe_allow_html=True)

elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco de Jogadoras")
    for j in st.session_state.jogadoras:
        st.markdown(f"""
        <div class='card-team'>
            <b>⚽ {j['nome']}</b><br>
            <small>Tipo: `{j.get('tipo', 'Avulso')}` | Nascimento: {j.get('nascimento', 'N/A')}</small>
        </div>
        """, unsafe_allow_html=True)

elif menu == "⚙️ Painel Admin":
    if not st.session_state.admin_logged:
        st.error("Acesso restrito.")
    else:
        st.subheader("⚙️ Painel de Administração")
        with st.form("form_cfg"):
            limite_v = st.number_input("Limite de Vagas", value=int(st.session_state.avisos.get("limite_vagas", 15)))
            pix_val = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
            if st.form_submit_button("Salvar Configurações"):
                st.session_state.avisos["limite_vagas"] = limite_v
                st.session_state.avisos["pix"] = pix_val
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Salvo com sucesso!")

elif menu == "📊 Fluxo de Caixa":
    if not st.session_state.admin_logged:
        st.error("Acesso restrito.")
    else:
        st.subheader("📊 Fluxo de Caixa")
        df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor"])
        st.dataframe(df_fin, use_container_width=True)
        with st.form("form_cx", clear_on_submit=True):
            desc = st.text_input("Descrição")
            tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
            val = st.number_input("Valor (R$)", min_value=0.0)
            if st.form_submit_button("Adicionar Lançamento"):
                st.session_state.financeiro.append({"data": hoje_dt.strftime("%d/%m/%Y"), "descricao": desc, "tipo": tipo, "valor": val})
                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                st.success("Adicionado!")
                st.rerun()
