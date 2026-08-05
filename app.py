import streamlit as st
import pandas as pd
import json
import os
import random
import string
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
# CONFIGURAÇÃO DA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Peladinha FC | Gestão de Futebol Feminino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS CUSTOMIZADA
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }

    .hero-banner {
        background: linear-gradient(rgba(15, 23, 42, 0.75), rgba(15, 23, 42, 0.85)), 
                    url('https://images.unsplash.com/photo-1518091043644-c1d4457512c6?q=80&w=1200&auto=format&fit=crop');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 25px 15px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
        margin-bottom: 20px;
    }
    .hero-title { font-size: 2.0rem; font-weight: 800; margin-bottom: 5px; color: #FFFFFF; }
    .hero-subtitle { font-size: 0.9rem; font-weight: 300; color: #E2E8F0; }

    .card-notice {
        background: #FEF3C7;
        border-left: 6px solid #F59E0B;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        color: #78350F;
    }

    .card-bday {
        background: linear-gradient(135deg, #FCE7F3 0%, #FBCFE8 100%);
        border-left: 6px solid #EC4899;
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        color: #831843;
        text-align: center;
        font-size: 1.1rem;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
    }

    .card-team {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #EC4899;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .card-fin-entrada {
        background: #F0FDF4;
        border: 1px solid #BBF7D0;
        border-left: 5px solid #22C55E;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .card-fin-saida {
        background: #FEF2F2;
        border: 1px solid #FECACA;
        border-left: 5px solid #EF4444;
        padding: 12px 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
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
TOKENS_ADMIN_FILE = "tokens_admin.json"

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
    def_admins = [{"nome": "Desenvolvedor", "login": "admin", "senha": "1980", "principal": True}]
    st.session_state.administradores = carregar_dados(ADMINS_FILE, def_admins)
if "tokens_admin" not in st.session_state:
    st.session_state.tokens_admin = carregar_dados(TOKENS_ADMIN_FILE, [])
if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "vencimento": "Todo dia 10 de cada mês",
        "recado": "Favor chegarem 10 minutos antes para organizar o jogo!",
        "pix": "peladinhafc@email.com",
        "limite_vagas": 15
    })
if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "Mensalistas confirmando até as 17:00 de segunda têm prioridade na lista principal. Avulsas vão para a fila de espera e sobem após esse horário se houver vagas."},
        {"topico": "⏳ 2. Fila de Espera", "regrinha": "Jogadoras avulsas entram na fila de espera por ordem de chegada."},
        {"topico": "❌ 3. Desistências", "regrinha": "Ao cancelar, a primeira da fila é incluída no jogo."},
        {"topico": "💸 4. Mensalidades", "regrinha": "Pagas via Pix até a data estipulada."}
    ])
if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None
if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False
if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""
if "admin_principal" not in st.session_state:
    st.session_state.admin_principal = False
if "aba_ativa" not in st.session_state:
    st.session_state.aba_ativa = "Entrar"
if "msg_cadastro_sucesso" not in st.session_state:
    st.session_state.msg_cadastro_sucesso = False
if "msg_admin_cad_sucesso" not in st.session_state:
    st.session_state.msg_admin_cad_sucesso = False
if "edit_fin_idx_temp" not in st.session_state:
    st.session_state.edit_fin_idx_temp = None

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
# MENSAGEM DE BOAS-VINDAS PARA NOVAS JOGADORAS
# -----------------------------------------------------------------------------
if st.session_state.usuario_logado:
    dados_usuario_atual = next((j for j in st.session_state.jogadoras if j["nome"] == st.session_state.usuario_logado), None)
    
    if dados_usuario_atual and not dados_usuario_atual.get("boas_vindas_vista", False):
        st.markdown(f"""
        <div class='card-notice' style='background: #ECFDF5; border-left: 6px solid #10B981; color: #065F46;'>
            🎉 <b>Seja muito bem-vinda ao Peladinha FC, {st.session_state.usuario_logado}!</b><br>
            Ficamos muito felizes com a sua chegada ao nosso time. Para garantir sua vaga nos jogos, lembre-se de acessar a aba <b>📌 Presença no Jogo</b> e confirmar sua participação. Bom jogo e muitos gols! ⚽✨
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("👍 Entendido, vamos lá!"):
            dados_usuario_atual["boas_vindas_vista"] = True
            salvar_dados(DATA_FILE, st.session_state.jogadoras)
            st.rerun()

# -----------------------------------------------------------------------------
# ANIVERSARIANTES DO DIA
# -----------------------------------------------------------------------------
aniversariantes_hoje = [j["nome"] for j in st.session_state.jogadoras if j.get("nascimento", "").strip() == hoje_str]
if aniversariantes_hoje:
    nomes_aniver = " e ".join(aniversariantes_hoje)
    st.balloons()
    st.markdown(f"""
    <div class='card-bday'>
        🎂 🎉 <b>PARABÉNS, {nomes_aniver.upper()}!</b> 🎉 🎂<br>
        O Peladinha FC deseja a você um FELIZ ANIVERSÁRIO! Muita saúde e gols! ⚽🎈
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MENU LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")
lista_menu = ["📌 Presença no Jogo", "🔀 Sorteio de Times", "💸 Pagamento & Pix", "📜 Regulamento", "📋 Elenco de Jogadoras"]
if st.session_state.admin_logged:
    lista_menu.insert(2, "📊 Fluxo de Caixa (Admin)")
lista_menu.append("⚙️ Painel Admin")

menu = st.sidebar.radio("Ir para:", lista_menu)

st.sidebar.markdown("---")
st.sidebar.title("👤 Área da Jogadora")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair da Conta"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    tab_log, tab_cad = st.sidebar.tabs(["Entrar", "Cadastrar"] if st.session_state.aba_ativa == "Entrar" else ["Cadastrar", "Entrar"])
    with tab_log:
        if st.session_state.msg_cadastro_sucesso:
            st.success("🎉 Cadastro realizado com sucesso! Aguarde a aprovação de um Administrador.")
            st.session_state.msg_cadastro_sucesso = False
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            if st.form_submit_button("🔑 Entrar", use_container_width=True):
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    if user_found.get("status") == "Ativo":
                        st.session_state.usuario_logado = user_found["nome"]
                        user_found["primeiro_acceso"] = False
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.rerun()
                    else:
                        st.warning("⚠️ Seu cadastro está pendente de aprovação pela administração.")
                else:
                    st.error("Login ou senha incorretos!")
    with tab_cad:
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *", placeholder="Ex: 15/05")
            c_tipo = st.selectbox("Deseja se cadastrar como:", ["Avulso", "Mensalista"])
            c_user = st.text_input("Escolha um Login *")
            c_pass = st.text_input("Escolha uma Senha *", type="password")
            if st.form_submit_button("📝 Criar Conta", use_container_width=True):
                if c_nome and c_user and c_pass:
                    if any(j.get("login") == c_user.strip() for j in st.session_state.jogadoras):
                        st.error("Este Login já está em uso. Escolha outro!")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": c_nome.strip(), "nascimento": c_nasc.strip(),
                            "login": c_user.strip(), "senha": c_pass.strip(),
                            "tipo": c_tipo, "mes_vigente": mes_vigente_str,
                            "contato": "", "status": "Pendente",
                            "boas_vindas_vista": False
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.session_state.aba_ativa = "Entrar"
                        st.session_state.msg_cadastro_sucesso = True
                        st.rerun()
                else:
                    st.error("Preencha Nome, Login e Senha!")

st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    tab_adm_login, tab_adm_cad = st.sidebar.tabs(["Entrar Admin", "Cadastrar Admin"])
    
    with tab_adm_login:
        with st.form("form_login_admin"):
            adm_input = st.text_input("Login ou Senha Admin", type="password")
            if st.form_submit_button("Acessar Como Admin", use_container_width=True):
                admin_encontrado = next((adm for adm in st.session_state.administradores if adm_input in [adm.get("senha"), adm.get("login")]), None)
                if admin_encontrado or adm_input == "1980":
                    st.session_state.admin_logged = True
                    st.session_state.admin_nome = admin_encontrado["nome"] if admin_encontrado else "Desenvolvedor"
                    st.session_state.admin_principal = admin_encontrado.get("principal", False) if admin_encontrado else True
                    st.rerun()
                else:
                    st.error("Senha/Login Admin incorreto!")

    with tab_adm_cad:
        if st.session_state.msg_admin_cad_sucesso:
            st.success("🎉 Administrador cadastrado com sucesso! Faça login na aba ao lado.")
            st.session_state.msg_admin_cad_sucesso = False
        
        st.caption("🔒 O cadastro requer uma **Senha/Token Temporário** gerado pelo Administrador Principal.")
        with st.form("form_cad_admin_publico", clear_on_submit=True):
            cad_a_nome = st.text_input("Nome do Admin")
            cad_a_login = st.text_input("Login Desejado")
            cad_a_senha = st.text_input("Senha Desejada", type="password")
            cad_a_token = st.text_input("Token Temporário de Acesso", type="password")
            
            if st.form_submit_button("📝 Registrar Admin", use_container_width=True):
                if cad_a_nome and cad_a_login and cad_a_senha and cad_a_token:
                    token_obj = next((t for t in st.session_state.tokens_admin if t.get("token") == cad_a_token.strip() and not t.get("usado", False)), None)
                    if token_obj or (len(st.session_state.administradores) == 0 and cad_a_token.strip() == "1980"):
                        if any(a.get("login") == cad_a_login.strip() for a in st.session_state.administradores):
                            st.error("Este login de administrador já está em uso!")
                        else:
                            if token_obj:
                                token_obj["usado"] = True
                                salvar_dados(TOKENS_ADMIN_FILE, st.session_state.tokens_admin)
                            
                            st.session_state.administradores.append({
                                "nome": cad_a_nome.strip(),
                                "login": cad_a_login.strip(),
                                "senha": cad_a_senha.strip(),
                                "principal": False
                            })
                            salvar_dados(ADMINS_FILE, st.session_state.administradores)
                            st.session_state.msg_admin_cad_sucesso = True
                            st.rerun()
                    else:
                        st.error("Token temporário inválido, já utilizado ou incorreto!")
                else:
                    st.error("Preencha todos os campos para cadastrar o admin.")
else:
    cargo_str = "Admin Principal" if st.session_state.admin_principal else "Admin Secundário"
    st.sidebar.info(f"🔑 Admin: **{st.session_state.admin_nome}**\n\n*{cargo_str}*")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.session_state.admin_nome = ""
        st.session_state.admin_principal = False
        st.rerun()

# -----------------------------------------------------------------------------
# LÓGICA DE ORDENAÇÃO DE PRESENÇA
# -----------------------------------------------------------------------------
jogadoras_ativas = [j for j in st.session_state.jogadoras if j.get("status") == "Ativo"]
nomes_ativas = {j["nome"] for j in jogadoras_ativas}

presencas_ativas = [p for p in st.session_state.presencas if obter_nome_p(p) in nomes_ativas]

lista_atual = sorted(presencas_ativas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
mensalistas = [p for p in lista_atual if p.get("tipo") == "Mensalista"]
avulsas = [p for p in lista_atual if p.get("tipo") == "Avulso"]
limite = st.session_state.avisos.get("limite_vagas", 15)

confirmadas = mensalistas[:limite]
espera = mensalistas[limite:] + avulsas

passou_prazo = hoje_dt.weekday() == 0 and hoje_dt.hour >= 17

if passou_prazo and len(confirmadas) < limite:
    vagas_sobrando = limite - len(confirmadas)
    promovidas = espera[:vagas_sobrando]
    confirmadas.extend(promovidas)
    espera = espera[vagas_sobrando:]

# -----------------------------------------------------------------------------
# SORTEIO AUTOMÁTICO
# -----------------------------------------------------------------------------
if hoje_dt.weekday() == 0 and (hoje_dt.hour > 18 or (hoje_dt.hour == 18 and hoje_dt.minute >= 30)):
    sorteio_salvo = st.session_state.sorteio_oficial
    if sorteio_salvo.get("data") != data_hoje_id:
        nomes_confirmadas = [obter_nome_p(p) for p in confirmadas]
        if len(nomes_confirmadas) >= 2:
            random.shuffle(nomes_confirmadas)
            qtd_t = 2
            res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
            for idx, p in enumerate(nomes_confirmadas):
                res_times[f"Time {idx % qtd_t + 1}"].append(p)
            
            st.session_state.sorteio_oficial = {
                "data": data_hoje_id,
                "hora": f"{hoje_dt.strftime('%H:%M')} (Automático)",
                "times": res_times
            }
            salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)

# -----------------------------------------------------------------------------
# PÁGINAS DO SISTEMA
# -----------------------------------------------------------------------------
if menu == "📌 Presença no Jogo":
    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>AVISOS:</b> Limitado a <b>{limite} vagas</b>. <br>
        ⭐ <b>Mensalistas têm prioridade até SEGUNDA-FEIRA às 17:00!</b> Avulsas ficam na fila de espera e sobem após esse horário caso haja vagas.<br>
        💡 <i>{st.session_state.avisos.get('recado')}</i><br>
        ⏰ <i>Sorteio oficial automático: <b>Segunda-feira às 18:30</b>.</i>
    </div>
    """, unsafe_allow_html=True)

    col_lista, col_acoes = st.columns([1, 1])

    with col_lista:
        st.subheader("📋 Lista de Presença")
        st.markdown(f"### 🟢 Confirmadas no Jogo ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.info("Nenhuma jogadora confirmada ainda.")
        else:
            for i, p in enumerate(confirmadas, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                st.write(f"**{i}.** {nome_p} `[{tipo_p}]` — *(às {hora_p})*")

        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        if not espera:
            st.caption("Nenhuma jogadora na fila de espera.")
        else:
            for i, p in enumerate(espera, 1):
                nome_p, hora_p, tipo_p = obter_nome_p(p), obter_hora_p(p), obter_tipo_p(p)
                badge = "🏃 Avulsa" if tipo_p == "Avulso" else "⭐ Mensalista"
                st.write(f"**{i}º na espera:** {nome_p} `[{badge}]` — *(às {hora_p})*")

    with col_acoes:
        st.subheader("✍️ Marcar Minha Presença")
        if not (st.session_state.usuario_logado or st.session_state.admin_logged):
            st.warning("⚠️ **Faça Login no menu lateral para confirmar presença!**")
        else:
            with st.form("form_presenca_express"):
                if st.session_state.admin_logged and not st.session_state.usuario_logado:
                    nomes_cad = [j["nome"] for j in jogadoras_ativas]
                    jogadora_sel = st.selectbox("Selecione a jogadora para alterar:", nomes_cad) if nomes_cad else None
                else:
                    jogadora_sel = st.session_state.usuario_logado
                    st.write(f"Conectada como: **{jogadora_sel}**")

                c1, c2 = st.columns(2)
                btn_confirmar = c1.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                btn_cancelar = c2.form_submit_button("❌ Cancelar Presença", use_container_width=True)

            if jogadora_sel:
                dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == jogadora_sel), None)
                tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"

                pos_confirmada = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == jogadora_sel), None)
                pos_espera = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == jogadora_sel), None)

                if pos_confirmada:
                    st.success(f"🎉 **VOCÊ ESTÁ NO JOGO!** Posição **{pos_confirmada}**.")
                elif pos_espera:
                    st.warning(f"⏳ **VOCÊ ESTÁ NA FILA DE ESPERA!** Posição **{pos_espera}º**.")

                ja_na_lista = pos_confirmada is not None or pos_espera is not None

                if btn_confirmar:
                    if ja_na_lista:
                        st.warning("Seu nome já está registrado na lista!")
                    else:
                        st.session_state.presencas.append({
                            "nome": jogadora_sel, 
                            "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j,
                            "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()

                if btn_cancelar:
                    if ja_na_lista:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != jogadora_sel]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Seu nome não está na lista.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.subheader("🚨 Ações de Admin")
            if st.button("🧹 Zerar Toda a Lista", use_container_width=True):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.session_state.sorteio_oficial = {}
                salvar_dados(SORTEIO_FILE, {})
                st.warning("Lista e sorteios zerados!")
                st.rerun()

elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    tab_oficial, tab_quadra = st.tabs(["🏆 Sorteio Oficial (Pré-Jogo)", "⚡ Ajuste Rápido de Quadra"])

    with tab_oficial:
        sorteio_salvo = st.session_state.sorteio_oficial
        if sorteio_salvo and "times" in sorteio_salvo:
            st.success(f"✅ **Sorteio Oficial Realizado ({sorteio_salvo.get('hora', '')})**")
            cols = st.columns(len(sorteio_salvo["times"]))
            for idx, (nome_time, membros) in enumerate(sorteio_salvo["times"].items()):
                with cols[idx]:
                    st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                    for item in membros:
                        st.write(f"• **{item}**")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("⏰ O Sorteio Oficial é realizado automaticamente às **Segundas-feiras, às 18:30**.")

        if st.session_state.admin_logged:
            st.markdown("---")
            st.write("#### 🛠️ Forçar Novo Sorteio (Admin)")
            confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
            qtd_t = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_oficial")
            if st.button("🎲 Executar Sorteio Agora", use_container_width=True):
                if len(confirmadas_nomes) < qtd_t:
                    st.error("Número insuficiente de confirmadas.")
                else:
                    temp = confirmadas_nomes.copy()
                    random.shuffle(temp)
                    res_times = {f"Time {i+1}": [] for i in range(qtd_t)}
                    for idx, p in enumerate(temp):
                        res_times[f"Time {idx % qtd_t + 1}"].append(p)
                    
                    st.session_state.sorteio_oficial = {
                        "data": data_hoje_id, "hora": f"{hoje_dt.strftime('%H:%M')} (Manual)", "times": res_times
                    }
                    salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)
                    st.rerun()

    with tab_quadra:
        st.write("### ⚡ Sorteio na Quadra")
        confirmadas_nomes = [obter_nome_p(p) for p in confirmadas]
        if not confirmadas_nomes:
            st.info("Nenhuma jogadora confirmada na lista principal.")
        else:
            presentes = st.multiselect("Marque as jogadoras presentes na quadra:", confirmadas_nomes, default=confirmadas_nomes)
            qtd_t_q = st.slider("Dividir em quantos times?", 2, 4, 2, key="slider_quadra")
            if st.button("🎲 Sortear Apenas Presentes", use_container_width=True):
                if len(presentes) < qtd_t_q:
                    st.error("Selecione mais jogadoras.")
                else:
                    temp = presentes.copy()
                    random.shuffle(temp)
                    times_q = [[] for _ in range(qtd_t_q)]
                    for idx, p in enumerate(temp):
                        times_q[idx % qtd_t_q].append(p)
                    cols_q = st.columns(qtd_t_q)
                    for i, t in enumerate(times_q):
                        with cols_q[i]:
                            st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1} (Quadra)</h3>", unsafe_allow_html=True)
                            for item in t:
                                st.write(f"• **{item}**")
                            st.markdown("</div>", unsafe_allow_html=True)

elif menu == "📊 Fluxo de Caixa (Admin)":
    if not st.session_state.admin_logged:
        st.error("🔒 Área restrita aos administradores!")
    else:
        st.subheader("📊 Fluxo de Caixa Avançado")
        df_fin = pd.DataFrame(st.session_state.financeiro) if st.session_state.financeiro else pd.DataFrame(columns=["data", "descricao", "tipo", "valor", "categoria"])
        
        if not df_fin.empty and "categoria" not in df_fin.columns:
            df_fin["categoria"] = "Outros"
            for item in st.session_state.financeiro:
                if "categoria" not in item:
                    item["categoria"] = "Outros"

        if not df_fin.empty:
            df_fin["mes_ano"] = df_fin["data"].apply(lambda x: x[3:10] if isinstance(x, str) and len(x) >= 10 else "Geral")
            meses_disp = df_fin["mes_ano"].unique().tolist()
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                mes_sel = st.selectbox("📅 Filtrar por Mês/Ano:", ["Todos"] + meses_disp)
            with c_f2:
                tipo_sel = st.selectbox("🏷️ Filtrar por Tipo:", ["Todos", "Entrada", "Saída"])

            df_fin_filtrado = df_fin.copy()
            if mes_sel != "Todos":
                df_fin_filtrado = df_fin_filtrado[df_fin_filtrado["mes_ano"] == mes_sel]
            if tipo_sel != "Todos":
                df_fin_filtrado = df_fin_filtrado[df_fin_filtrado["tipo"] == tipo_sel]
        else:
            df_fin_filtrado = df_fin
            mes_sel, tipo_sel = "Todos", "Todos"

        total_in = df_fin_filtrado[df_fin_filtrado["tipo"] == "Entrada"]["valor"].sum() if not df_fin_filtrado.empty else 0.0
        total_out = df_fin_filtrado[df_fin_filtrado["tipo"] == "Saída"]["valor"].sum() if not df_fin_filtrado.empty else 0.0
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🟢 Entradas", f"R$ {total_in:.2f}")
        m2.metric("🔴 Saídas", f"R$ {total_out:.2f}")
        m3.metric("💰 Saldo do Período", f"R$ {total_in - total_out:.2f}")

        st.markdown("---")
        
        tab_list_fin, tab_add_fin, tab_cat_fin, tab_edit_fin = st.tabs([
            "📜 Extrato em Cards Interativos", 
            "➕ Novo Lançamento", 
            "📊 Resumo por Categoria", 
            "✏️ Editar / Excluir"
        ])

        with tab_list_fin:
            st.write("### 🗂️ Lançamentos Financeiros")
            if not st.session_state.financeiro:
                st.info("Nenhum lançamento cadastrado.")
            else:
                indices_filtrados = []
                for idx, item in enumerate(st.session_state.financeiro):
                    item_mes = item.get("data", "")[3:10] if len(item.get("data", "")) >= 10 else "Geral"
                    item_tipo = item.get("tipo", "Entrada")
                    
                    passou_mes = (mes_sel == "Todos" or item_mes == mes_sel)
                    passou_tipo = (tipo_sel == "Todos" or item_tipo == tipo_sel)
                    
                    if passou_mes and passou_tipo:
                        indices_filtrados.append(idx)

                if not indices_filtrados:
                    st.info("Nenhum registro encontrado para este filtro.")
                else:
                    for i_real in indices_filtrados:
                        reg = st.session_state.financeiro[i_real]
                        t_tipo = reg.get("tipo", "Entrada")
                        t_cat = reg.get("categoria", "Outros")
                        t_desc = reg.get("descricao", "Sem descrição")
                        t_data = reg.get("data", "")
                        t_val = reg.get("valor", 0.0)

                        css_card = "card-fin-entrada" if t_tipo == "Entrada" else "card-fin-saida"
                        sinal = "+" if t_tipo == "Entrada" else "-"

                        c_card_info, c_card_btn1, c_card_btn2 = st.columns([5, 1, 1])
                        
                        with c_card_info:
                            st.markdown(f"""
                            <div class='{css_card}'>
                                <b>[{t_data}] {t_cat}</b> — {t_desc}<br>
                                <span style='font-size: 1.1rem; font-weight: bold; color: {"#16A34A" if t_tipo=="Entrada" else "#DC2626"};'>
                                    {sinal} R$ {t_val:.2f}
                                </span>
                            </div>
                            """, unsafe_allow_html=True)

                        with c_card_btn1:
                            if st.button("✏️", key=f"btn_edit_card_{i_real}", help="Editar este lançamento"):
                                st.session_state.edit_fin_idx_temp = i_real
                                st.rerun()

                        with c_card_btn2:
                            if st.button("🗑️", key=f"btn_del_card_{i_real}", help="Excluir este lançamento"):
                                st.session_state.financeiro.pop(i_real)
                                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                                st.success("Lançamento excluído com sucesso!")
                                st.rerun()

        with tab_add_fin:
            categorias_entrada = ["Mensalidade", "Avulsa", "Doação / Patrocínio", "Outras Entradas"]
            categorias_saida = ["Aluguel de Quadra", "Água / Gelo", "Material Esportivo (Bolas/Coletes)", "Premiação / Troféus", "Outras Saídas"]

            with st.form("form_fin_melhorado", clear_on_submit=True):
                f_data = st.text_input("Data (DD/MM/AAAA)", value=hoje_dt.strftime("%d/%m/%Y"))
                f_tipo = st.selectbox("Tipo de Lançamento", ["Entrada", "Saída"])
                
                if f_tipo == "Entrada":
                    f_cat = st.selectbox("Categoria", categorias_entrada)
                else:
                    f_cat = st.selectbox("Categoria", categorias_saida)

                f_desc = st.text_input("Descrição / Nome")
                f_valor = st.number_input("Valor (R$)", min_value=0.01, step=5.0)
                
                if st.form_submit_button("💾 Salvar Lançamento no Caixa", use_container_width=True):
                    if f_desc:
                        st.session_state.financeiro.append({
                            "data": f_data,
                            "tipo": f_tipo,
                            "categoria": f_cat,
                            "descricao": f_desc,
                            "valor": f_valor
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento efetuado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Preencha a descrição do lançamento.")

        with tab_cat_fin:
            st.write("### 📊 Resumo Financeiro por Categoria")
            if not st.session_state.financeiro:
                st.info("Sem dados financeiros para exibir.")
            else:
                df_cat = pd.DataFrame(st.session_state.financeiro)
                resumo_cat = df_cat.groupby(["tipo", "categoria"])["valor"].sum().reset_index()
                st.dataframe(resumo_cat, use_container_width=True)

        with tab_edit_fin:
            st.write("### ✏️ Gerenciamento Direto de Lançamentos")
            if st.session_state.edit_fin_idx_temp is not None and st.session_state.edit_fin_idx_temp < len(st.session_state.financeiro):
                idx_e = st.session_state.edit_fin_idx_temp
                reg_e = st.session_state.financeiro[idx_e]
                
                with st.form("form_edit_fin_direto"):
                    st.write(f"Editando Lançamento #{idx_e}")
                    e_data = st.text_input("Data", value=reg_e.get("data", ""))
                    e_tipo = st.selectbox("Tipo", ["Entrada", "Saída"], index=0 if reg_e.get("tipo")=="Entrada" else 1)
                    e_cat = st.text_input("Categoria", value=reg_e.get("categoria", ""))
                    e_desc = st.text_input("Descrição", value=reg_e.get("descricao", ""))
                    e_val = st.number_input("Valor (R$)", value=float(reg_e.get("valor", 0.0)), step=1.0)
                    
                    if st.form_submit_button("💾 Atualizar Registro"):
                        st.session_state.financeiro[idx_e] = {
                            "data": e_data,
                            "tipo": e_tipo,
                            "categoria": e_cat,
                            "descricao": e_desc,
                            "valor": e_val
                        }
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.session_state.edit_fin_idx_temp = None
                        st.success("Atualizado com sucesso!")
                        st.rerun()
            else:
                st.info("Selecione o ícone de edição (✏️) em um card na aba de extrato para modificá-lo aqui.")

elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Pagamentos e Chave Pix")
    st.markdown(f"""
    <div class='card-notice'>
        📌 <b>Informações para Pagamento:</b><br>
        • Vencimento das mensalidades: <b>{st.session_state.avisos.get('vencimento')}</b><br>
        • Chave Pix: <b>{st.session_state.avisos.get('pix')}</b><br>
        💡 <i>Após realizar o Pix, envie o comprovante para validação da administração.</i>
    </div>
    """, unsafe_allow_html=True)

    with st.form("form_comprovante", clear_on_submit=True):
        c_nome_comp = st.text_input("Seu Nome Completo")
        c_mes_ref = st.text_input("Mês de Referência", value=mes_vigente_str)
        c_valor_comp = st.number_input("Valor Pago (R$)", min_value=0.0, step=5.0)
        c_obs = st.text_area("Observações (Opcional)")
        
        if st.form_submit_button("📤 Enviar Comprovante", use_container_width=True):
            if c_nome_comp:
                st.session_state.comprovantes.append({
                    "nome": c_nome_comp,
                    "mes": c_mes_ref,
                    "valor": c_valor_comp,
                    "obs": c_obs,
                    "data": hoje_dt.strftime("%d/%m/%Y"),
                    "status": "Pendente"
                })
                salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                st.success("Comprovante enviado com sucesso para análise!")
            else:
                st.error("Por favor, preencha o seu nome.")

elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno do Peladinha FC")
    for reg in st.session_state.regulamento:
        st.markdown(f"""
        <div class='card-team'>
            <h4>{reg.get('topico')}</h4>
            <p>{reg.get('regrinha')}</p>
        </div>
        """, unsafe_allow_html=True)

elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Cadastrado")
    if not st.session_state.jogadoras:
        st.info("Nenhuma jogadora cadastrada no sistema.")
    else:
        df_j = pd.DataFrame(st.session_state.jogadoras)
        cols_visiveis = [c for c in ["nome", "tipo", "nascimento", "status", "mes_vigente"] if c in df_j.columns]
        st.dataframe(df_j[cols_visiveis], use_container_width=True)

elif menu == "⚙️ Painel Admin":
    if not st.session_state.admin_logged:
        st.warning("⚠️ Faça login como Administrador na barra lateral para acessar as configurações.")
    else:
        st.subheader("⚙️ Painel de Controle da Administração")
        tab_ap_jog, tab_ap_comp, tab_ap_av, tab_ap_reg, tab_ap_tok = st.tabs([
            "👥 Aprovar Jogadoras", 
            "🧾 Validar Comprovantes", 
            "📢 Avisos & Pix", 
            "📜 Editar Regulamento",
            "🔑 Gerar Tokens Admin"
        ])

        with tab_ap_jog:
            st.write("### Aprovação de Cadastros de Jogadoras")
            pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
            if not pendentes:
                st.info("Nenhuma jogadora pendente de aprovação.")
            else:
                for idx, j in enumerate(st.session_state.jogadoras):
                    if j.get("status") == "Pendente":
                        col_j1, col_j2, col_j3 = st.columns([3, 1, 1])
                        col_j1.write(f"**{j['nome']}** (`{j.get('tipo', 'Avulso')}`) — Login: {j.get('login')}")
                        if col_j2.button("✅ Aprovar", key=f"apr_{idx}"):
                            j["status"] = "Ativo"
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.success(f"Jogadora {j['nome']} aprovada!")
                            st.rerun()
                        if col_j3.button("❌ Recusar", key=f"rec_{idx}"):
                            st.session_state.jogadoras.pop(idx)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.warning("Cadastro removido.")
                            st.rerun()

        with tab_ap_comp:
            st.write("### Comprovantes Enviados")
            if not st.session_state.comprovantes:
                st.info("Nenhum comprovante enviado.")
            else:
                for idx, c in enumerate(st.session_state.comprovantes):
                    st.write(f"**{c['nome']}** — Mês: {c['mes']} — Valor: R$ {c['valor']:.2f} — Status: **{c.get('status', 'Pendente')}**")
                    if c.get("status") == "Pendente":
                        if st.button(f"Validar Comprovante de {c['nome']}", key=f"val_comp_{idx}"):
                            c["status"] = "Aprovado"
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.success("Comprovante validado!")
                            st.rerun()

        with tab_ap_av:
            st.write("### Configurar Avisos, Vagas e Pix")
            with st.form("form_config_avisos"):
                novo_recado = st.text_input("Recado do Dia / Aviso Principal", value=st.session_state.avisos.get("recado", ""))
                novo_venc = st.text_input("Data de Vencimento", value=st.session_state.avisos.get("vencimento", ""))
                novo_pix = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
                novo_limite = st.number_input("Limite de Vagas no Jogo", min_value=1, max_value=50, value=int(st.session_state.avisos.get("limite_vagas", 15)))
                
                if st.form_submit_button("💾 Salvar Alterações"):
                    st.session_state.avisos["recado"] = novo_recado
                    st.session_state.avisos["vencimento"] = novo_venc
                    st.session_state.avisos["pix"] = novo_pix
                    st.session_state.avisos["limite_vagas"] = int(novo_limite)
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas com sucesso!")
                    st.rerun()

        with tab_ap_reg:
            st.write("### Gerenciar Regulamento")
            with st.form("form_novo_topico_reg"):
                t_tit = st.text_input("Título do Tópico")
                t_desc = st.text_area("Regra Detalhada")
                if st.form_submit_button("➕ Adicionar Regra"):
                    if t_tit and t_desc:
                        st.session_state.regulamento.append({"topico": t_tit, "regrinha": t_desc})
                        salvar_dados(REGULAMENTO_FILE, st.session_state.regulamento)
                        st.success("Regra adicionada!")
                        st.rerun()

        with tab_ap_tok:
            st.write("### Gerar Token Temporário para Novos Admins")
            if not st.session_state.admin_principal:
                st.warning("⚠️ Apenas o Administrador Principal pode gerar tokens de acesso para outros admins.")
            else:
                if st.button("🔑 Gerar Novo Token de Cadastro"):
                    novo_token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    st.session_state.tokens_admin.append({"token": novo_token, "usado": False})
                    salvar_dados(TOKENS_ADMIN_FILE, st.session_state.tokens_admin)
                    st.success(f"Token gerado com sucesso: **{novo_token}** (Forneça este código para o novo administrador).")
                
                st.write("#### Tokens Existentes:")
                if not st.session_state.tokens_admin:
                    st.caption("Nenhum token gerado.")
                else:
                    for t in st.session_state.tokens_admin:
                        estado = "🔴 Utilizado" if t.get("usado") else "🟢 Disponível"
                        st.write(f"Token: `{t['token']}` — Status: {estado}")
