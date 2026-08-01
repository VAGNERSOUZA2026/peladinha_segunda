import streamlit as st
import pandas as pd
import json
import os
import random
import urllib.parse
from datetime import datetime, timezone, timedelta
import html

# -----------------------------------------------------------------------------
# FUSO HORÁRIO BRASIL (UTC-3)
# -----------------------------------------------------------------------------
FUSO_BRASIL = timezone(timedelta(hours=-3))

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
# FUNÇÃO PARA CORREÇÃO AUTOMÁTICA DE DIGITAÇÃO DE NOMES
# -----------------------------------------------------------------------------
def formatar_nome_proprio(texto):
    if not texto:
        return ""
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
# FUNÇÃO PARA GERAR DOCUMENTO DO CONTRATO
# -----------------------------------------------------------------------------
def gerar_documento_contrato(nome, doc, whats, cidade, valor, data_ass, assinatura):
    conteudo_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Contrato - Peladinha FC</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; color: #333; line-height: 1.6; }}
        h2 {{ text-align: center; color: #0F172A; text-transform: uppercase; margin-bottom: 30px; }}
        .section {{ margin-bottom: 20px; }}
        .section-title {{ font-weight: bold; color: #0F172A; }}
        .box {{ border: 1px solid #CCC; padding: 15px; border-radius: 5px; background: #F9F9F9; margin-top: 20px; }}
        .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #777; }}
    </style>
</head>
<body>
    <h2>CONTRATO DE PRESTAÇÃO DE SERVIÇOS E LICENCIAMENTO DE SOFTWARE</h2>
    
    <div class="section">
        <span class="section-title">1. CONTRATANTE:</span><br>
        <b>Nome:</b> {html.escape(nome)}<br>
        <b>CPF/CNPJ:</b> {html.escape(doc)}<br>
        <b>WhatsApp:</b> {html.escape(whats)}<br>
        <b>Cidade/UF:</b> {html.escape(cidade)}
    </div>

    <div class="section">
        <span class="section-title">2. CONTRATADO:</span><br>
        Desenvolvedor: Vagner Souza (Ciência da Computação)<br>
        WhatsApp: (31) 98968-4010
    </div>

    <div class="section">
        <span class="section-title">3. OBJETO DO CONTRATO:</span><br>
        Disponibilização de licença de uso do aplicativo web "Peladinha FC" para gestão de presenças, sorteio de times e controle financeiro de peladas.
    </div>

    <div class="section">
        <span class="section-title">4. VALOR E PAGAMENTO:</span><br>
        O CONTRATANTE pagará o valor mensal de R$ {valor:.2f}, até o dia 10 de cada mês via Pix.
    </div>

    <div class="box">
        <span class="section-title">5. ACEITE E ASSINATURA ELETRÔNICA:</span><br>
        O CONTRATANTE declara ter lido e concordado com todos os termos deste instrumento contratual.<br><br>
        <b>Data do Aceite:</b> {data_ass}<br>
        <b>Assinado Digitalmente por:</b> {html.escape(assinatura)}
    </div>

    <div class="footer">
        Documento gerado eletronicamente através da plataforma Peladinha FC.
    </div>
</body>
</html>"""
    return conteudo_html.encode('utf-8')

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

    .card-team {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-top: 5px solid #EC4899;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .contract-box {
        background-color: #F8FAFC;
        border: 1px solid #CBD5E1;
        padding: 20px;
        border-radius: 10px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        color: #1E293B;
        height: 300px;
        overflow-y: scroll;
        margin-bottom: 15px;
    }

    .developer-footer {
        background: #0F172A;
        color: #94A3B8;
        text-align: center;
        padding: 12px;
        border-radius: 10px;
        margin-top: 30px;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# FUNÇÕES DE LEITURA E SALVAMENTO DE DADOS (JSON)
# -----------------------------------------------------------------------------
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
AVISOS_FILE = "avisos.json"
FINANCE_FILE = "financeiro.json"
ADMINS_FILE = "administradores.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"

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

# -----------------------------------------------------------------------------
# INICIALIZAÇÃO DE ESTADO DO SISTEMA
# -----------------------------------------------------------------------------
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "administradores" not in st.session_state:
    def_admins = [{"nome": "Admin Principal", "login": "admin", "senha": "1980", "principal": True}]
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
        {"topico": "📌 1. Prioridade nas Vagas", "regrinha": "As jogadoras MENSALISTAS têm prioridade absoluta até às 17:00."},
        {"topico": "⏳ 2. Promoção de Avulsas", "regrinha": "Às 17:00, se as 15 vagas não forem preenchidas por mensalistas, as jogadoras avulsas da fila de espera são promovidas automaticamente para a lista principal."},
        {"topico": "🎲 3. Sorteio de Times", "regrinha": "Às 18:00 o sorteio automático dos times é realizado."},
        {"topico": "💸 4. Mensalidades e Pagamento", "regrinha": "As mensalidades devem ser pagas via Pix até a data estipulada de vencimento."},
        {"topico": "🔄 5. Encerramento da Lista", "regrinha": "Às 20:00 a lista de presença e os sorteios são zerados automaticamente para a próxima rodada."}
    ])

if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "admin_logged" not in st.session_state:
    st.session_state.admin_logged = False

if "admin_nome" not in st.session_state:
    st.session_state.admin_nome = ""

if "is_principal_admin" not in st.session_state:
    st.session_state.is_principal_admin = False

if "simulacao_ativa" not in st.session_state:
    st.session_state.simulacao_ativa = False
if "hora_simulada" not in st.session_state:
    st.session_state.hora_simulada = 16
if "minuto_simulado" not in st.session_state:
    st.session_state.minuto_simulado = 30

# -----------------------------------------------------------------------------
# PROCESSAMENTO DA HORA VIGENTE
# -----------------------------------------------------------------------------
if st.session_state.simulacao_ativa and st.session_state.is_principal_admin:
    hoje_dt = datetime.now(FUSO_BRASIL).replace(
        hour=st.session_state.hora_simulada, 
        minute=st.session_state.minuto_simulado
    )
else:
    hoje_dt = datetime.now(FUSO_BRASIL)

hoje_str = hoje_dt.strftime("%d/%m/%Y")
mes_vigente_str = hoje_dt.strftime("%m/%Y")
data_hoje_id = hoje_dt.strftime("%Y-%m-%d")
limite_vagas_at = st.session_state.avisos.get("limite_vagas", 15)

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
# MENU LATERAL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.title("📌 Navegação")

lista_menu = [
    "📌 Presença no Jogo", 
    "🔀 Sorteio de Times",
    "📸 Foto do Jogo",
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras"
]

if st.session_state.admin_logged:
    lista_menu.insert(3, "📊 Fluxo de Caixa (Admin)")

lista_menu.append("⚙️ Painel Admin")
menu = st.sidebar.radio("Ir para:", lista_menu)

# -----------------------------------------------------------------------------
# ÁREA DA JOGADORA (LOGIN & CADASTRO COM AUTOCORREÇÃO DE NOME)
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.title("👤 Área da Jogadora")

if st.session_state.usuario_logado:
    st.sidebar.success(f"Logada: **{st.session_state.usuario_logado}**")
    if st.sidebar.button("🚪 Sair da Conta"):
        st.session_state.usuario_logado = None
        st.rerun()
else:
    tab_log, tab_cad = st.sidebar.tabs(["Entrar", "Cadastrar"])
    
    with tab_log:
        with st.form("form_login_player"):
            l_user = st.text_input("Login")
            l_pass = st.text_input("Senha", type="password")
            btn_log = st.form_submit_button("🔑 Entrar", use_container_width=True)
            
            if btn_log:
                user_found = next((j for j in st.session_state.jogadoras if j.get("login") == l_user and j.get("senha") == l_pass), None)
                if user_found:
                    st.session_state.usuario_logado = user_found["nome"]
                    st.rerun()
                else:
                    st.error("Login ou senha incorretos!")

    with tab_cad:
        with st.form("form_cad_player", clear_on_submit=True):
            c_nome_raw = st.text_input("Seu Nome *")
            c_nasc = st.text_input("Nascimento (DD/MM) *")
            c_user = st.text_input("Escolha um Login *")
            c_pass = st.text_input("Escolha uma Senha *", type="password")
            btn_cad = st.form_submit_button("📝 Criar Conta", use_container_width=True)
            
            if btn_cad:
                if c_nome_raw and c_user and c_pass:
                    nome_formatado = formatar_nome_proprio(c_nome_raw)
                    st.session_state.jogadoras.append({
                        "nome": nome_formatado, "nascimento": c_nasc.strip(),
                        "login": c_user.strip(), "senha": c_pass.strip(),
                        "tipo": "Avulso", "mes_vigente": mes_vigente_str,
                        "contato": "", "status": "Ativo"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Conta criada para **{nome_formatado}**! Faça login.")
                    st.rerun()

# -----------------------------------------------------------------------------
# ÁREA DO ADMINISTRADOR
# -----------------------------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🔒 Área do Administrador")

if not st.session_state.admin_logged:
    with st.sidebar.form("form_login_admin"):
        adm_input = st.text_input("Senha Admin", type="password")
        btn_adm = st.form_submit_button("Acessar Como Admin", use_container_width=True)
        if btn_adm:
            admin_match = next((adm for adm in st.session_state.administradores if adm.get("senha") == adm_input), None)
            if adm_input == "1980" or admin_match:
                st.session_state.admin_logged = True
                st.session_state.admin_nome = admin_match["nome"] if admin_match else "Admin Principal"
                st.session_state.is_principal_admin = (adm_input == "1980" or (admin_match and admin_match.get("principal", False)))
                st.rerun()
            else:
                st.error("Senha incorreta!")
else:
    badge_type = " (Dev/Master)" if st.session_state.is_principal_admin else ""
    st.sidebar.info(f"🔑 Logado como **{st.session_state.admin_nome}**{badge_type}")
    if st.sidebar.button("Sair do Admin"):
        st.session_state.admin_logged = False
        st.session_state.is_principal_admin = False
        st.session_state.simulacao_ativa = False
        st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA 1: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
if menu == "📌 Presença no Jogo":
    limite = st.session_state.avisos.get("limite_vagas", 15)
    hora_atual = hoje_dt.hour

    st.markdown(f"""
    <div class='card-notice'>
        📢 <b>AVISOS DA PELADA:</b> Limitado a <b>{limite} vagas</b>.<br>
        ⭐ <b>Mensalistas têm prioridade até às 17:00.</b><br>
        🎲 <b>Sorteio Oficial:</b> Realizado automaticamente às <b>18:00</b>.
    </div>
    """, unsafe_allow_html=True)

    col_lista, col_acoes = st.columns([1, 1])
    lista_atual = st.session_state.presencas

    mensalistas_lista = [p for p in lista_atual if obter_tipo_p(p) == "Mensalista"]
    avulsas_lista = [p for p in lista_atual if obter_tipo_p(p) == "Avulso"]

    if hora_atual < 17:
        confirmadas = mensalistas_lista[:limite]
        espera = mensalistas_lista[limite:] + avulsas_lista
    else:
        vagas_sobrando = limite - len(mensalistas_lista)
        if vagas_sobrando > 0:
            confirmadas = mensalistas_lista + avulsas_lista[:vagas_sobrando]
            espera = avulsas_lista[vagas_sobrando:]
        else:
            confirmadas = mensalistas_lista[:limite]
            espera = mensalistas_lista[limite:] + avulsas_lista

    with col_lista:
        st.subheader("📋 Lista de Presença")
        st.markdown(f"### 🟢 Confirmadas ({len(confirmadas)}/{limite})")
        if not confirmadas:
            st.info("Nenhuma jogadora confirmada ainda.")
        else:
            for i, p in enumerate(confirmadas, 1):
                st.write(f"**{i}.** {obter_nome_p(p)} `[{obter_tipo_p(p)}]` — *(às {obter_hora_p(p)})*")

        st.markdown("---")
        st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
        if not espera:
            st.caption("Nenhuma jogadora na fila de espera.")
        else:
            for i, p in enumerate(espera, 1):
                st.write(f"**{i}º na espera:** {obter_nome_p(p)} `[{obter_tipo_p(p)}]` — *(às {obter_hora_p(p)})*")

    with col_acoes:
        st.subheader("✍️ Minha Presença")
        pode_mexer = st.session_state.usuario_logado or st.session_state.admin_logged

        if not pode_mexer:
            st.warning("⚠️ **Faça Login na Área da Jogadora para confirmar presença!**")
        else:
            with st.form("form_presenca_express"):
                if st.session_state.admin_logged and not st.session_state.usuario_logado:
                    nomes_cad = [j["nome"] for j in st.session_state.jogadoras]
                    jogadora_sel = st.selectbox("Selecione a jogadora:", nomes_cad) if nomes_cad else None
                else:
                    jogadora_sel = st.session_state.usuario_logado
                    st.write(f"Conectada como: **{jogadora_sel}**")

                c1, c2 = st.columns(2)
                btn_confirmar = c1.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                btn_cancelar = c2.form_submit_button("❌ Cancelar Presença", use_container_width=True)

            if jogadora_sel:
                dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == jogadora_sel), None)
                tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"
                ja_na_lista = any(obter_nome_p(p) == jogadora_sel for p in st.session_state.presencas)

                if btn_confirmar:
                    if ja_na_lista:
                        st.warning("Seu nome já está na lista!")
                    else:
                        st.session_state.presencas.append({
                            "nome": jogadora_sel, 
                            "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()

                if btn_cancelar:
                    if ja_na_lista:
                        st.session_state.presencas = [p for p in st.session_state.presencas if obter_nome_p(p) != jogadora_sel]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada!")
                        st.rerun()

# -----------------------------------------------------------------------------
# PÁGINA 2: SORTEIO DE TIMES
# -----------------------------------------------------------------------------
elif menu == "🔀 Sorteio de Times":
    st.subheader("🔀 Sorteio de Times")
    tab_oficial, tab_quadra = st.tabs(["🏆 Sorteio Oficial", "⚡ Ajuste Rápido de Quadra"])

    with tab_oficial:
        sorteio_salvo = st.session_state.sorteio_oficial
        if sorteio_salvo and "times" in sorteio_salvo:
            st.success(f"✅ **Sorteio Oficial ({sorteio_salvo.get('hora', '')})**")
            cols = st.columns(len(sorteio_salvo["times"]))
            for idx, (nome_time, membros) in enumerate(sorteio_salvo["times"].items()):
                with cols[idx]:
                    st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                    for item in membros:
                        st.write(f"• **{item}**")
                    st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("⏰ Sorteio Oficial realizado automaticamente às **18:00**.")

    with tab_quadra:
        st.write("### ⚡ Sorteio na Quadra")
        limite = st.session_state.avisos.get("limite_vagas", 15)
        conf_objs = st.session_state.presencas[:limite]
        todas_conf = [obter_nome_p(p) for p in conf_objs]

        if not todas_conf:
            st.info("Nenhuma jogadora confirmada.")
        else:
            presentes = st.multiselect("Marque quem chegou:", todas_conf, default=todas_conf)
            qtd_t_q = st.slider("Dividir em quantos times?", 2, 4, 2)

            if st.button("🎲 Sortear Quadra", use_container_width=True):
                temp = presentes.copy()
                random.shuffle(temp)
                times_q = [[] for _ in range(qtd_t_q)]
                for idx, p in enumerate(temp):
                    times_q[idx % qtd_t_q].append(p)

                cols_q = st.columns(qtd_t_q)
                for i, t in enumerate(times_q):
                    with cols_q[i]:
                        st.markdown(f"<div class='card-team'><h3>⚽ Time {i+1}</h3>", unsafe_allow_html=True)
                        for item in t:
                            st.write(f"• **{item}**")
                        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA 3: FOTO DO JOGO (CÂMERA E ENVIO VIA WHATSAPP OPTIMIZADO)
# -----------------------------------------------------------------------------
elif menu == "📸 Foto do Jogo":
    st.subheader("📸 Registro da Pelada & Envio no WhatsApp")
    st.caption("Tire a foto da galera no final do jogo ou selecione da galeria para enviar!")

    foto_capturada = st.camera_input("📷 Acionar Câmera do Celular/PC")
    foto_upload = st.file_uploader("🖼️ Ou escolha uma foto da Galeria", type=["jpg", "jpeg", "png"])

    foto_final = foto_capturada if foto_capturada is not None else foto_upload

    if foto_final is not None:
        bytes_foto = foto_final.getvalue()
        
        st.image(bytes_foto, caption="Foto Selecionada", use_column_width=True)
        
        st.success("✅ **Foto Pronta!**")
        
        # Passo a Passo para o usuário
        st.markdown("""
        #### 📲 Como enviar pelo celular/PC:
        1. Clique no botão abaixo **'📥 Baixar Foto'** para salvar a imagem no seu aparelho.
        2. Clique em **'💬 Abrir WhatsApp'** para abrir a conversa com o número **(31) 98968-4010**.
        3. No WhatsApp, toque no ícone de **Anexo/Câmera** e envie a foto baixada!
        """)

        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            st.download_button(
                label="📥 1º Baixar Foto para o Celular",
                data=bytes_foto,
                file_name=f"Foto_PeladinhaFC_{hoje_dt.strftime('%d_%m_%Y')}.jpg",
                mime="image/jpeg",
                use_container_width=True
            )

        legenda_padrao = f"📸 Registro da Peladinha FC do dia {hoje_str}! ⚽🔥"
        msg_foto_wa = f"{legenda_padrao}\n\n_Enviado pelo App Peladinha FC_"
        
        # Link nativo otimizado para abrir direto o aplicativo do WhatsApp em celular/PC
        wa_numero_teste = "5531989684010"
        wa_foto_link = f"https://wa.me/{wa_numero_teste}?text={urllib.parse.quote(msg_foto_wa)}"

        with col_f2:
            st.markdown(f"""
                <a href="{wa_foto_link}" target="_blank" style="text-decoration: none;">
                    <div style="background-color: #25D366; color: white; padding: 10px 15px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 0.95rem; line-height: 1.4;">
                        💬 2º Abrir WhatsApp (31 98968-4010)
                    </div>
                </a>
            """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PÁGINA 4: FLUXO DE CAIXA
# -----------------------------------------------------------------------------
elif menu == "📊 Fluxo de Caixa (Admin)":
    st.subheader("📊 Fluxo de Caixa do Clube")
    col_f1, col_f2 = st.columns([1, 1.3])
    with col_f1:
        with st.form("form_financeiro"):
            tipo_trans = st.selectbox("Tipo", ["Entrada (Receita)", "Saída (Despesa)"])
            desc_trans = st.text_input("Descrição")
            valor_trans = st.number_input("Valor (R$)", min_value=0.0, step=5.0)
            data_trans = st.date_input("Data", datetime.now(FUSO_BRASIL))
            btn_fin = st.form_submit_button("Registrar Transação")
            
            if btn_fin and valor_trans > 0:
                st.session_state.financeiro.append({
                    "data": data_trans.strftime("%d/%m/%Y"),
                    "tipo": tipo_trans,
                    "descricao": desc_trans,
                    "valor": valor_trans
                })
                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                st.success("Registrado!")
                st.rerun()

    with col_f2:
        if st.session_state.financeiro:
            df_fin = pd.DataFrame(st.session_state.financeiro)
            st.dataframe(df_fin, use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 5: PAGAMENTO & PIX
# -----------------------------------------------------------------------------
elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Dados para Pagamento")
    st.info(f"🔑 **Chave Pix:** {st.session_state.avisos.get('pix')}")
    st.write(f"📅 **Vencimento:** {st.session_state.avisos.get('vencimento')}")
    st.write(f"💬 **Recado:** {st.session_state.avisos.get('recado')}")

# -----------------------------------------------------------------------------
# PÁGINA 6: REGULAMENTO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno do Clube")
    for item in st.session_state.regulamento:
        st.markdown(f"#### {item['topico']}")
        st.write(item['regrinha'])

# -----------------------------------------------------------------------------
# PÁGINA 7: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Cadastrado")
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df[["nome", "tipo", "nascimento", "status"]], use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 8: PAINEL ADMIN
# -----------------------------------------------------------------------------
elif menu == "⚙️ Painel Admin":
    st.subheader("⚙️ Painel do Administrador")
    if not st.session_state.admin_logged:
        st.error("🔒 Faça login como Admin na barra lateral para acessar esta área!")
    else:
        tabs_titulos = []
        if st.session_state.is_principal_admin:
            tabs_titulos.append("🧪 Laboratório de Testes (Dev)")
        
        tabs_titulos.extend([
            "📜 Contrato de Serviço",
            "⚙️ Configurações Gerais", 
            "➕ Cadastrar Jogadora", 
            "📋 Gerenciar Elenco"
        ])

        tabs_objetos = st.tabs(tabs_titulos)
        idx_tab = 0
        
        if st.session_state.is_principal_admin:
            with tabs_objetos[idx_tab]:
                st.markdown("### 🧪 Central de Simulação & Testes")
                st.session_state.simulacao_ativa = st.checkbox("🟢 Ativar Simulação de Horário", value=st.session_state.simulacao_ativa)
                if st.session_state.simulacao_ativa:
                    st.session_state.hora_simulada = st.slider("Hora Simulada:", 0, 23, st.session_state.hora_simulada)
            idx_tab += 1

        # --- TAB: CONTRATO ---
        with tabs_objetos[idx_tab]:
            st.markdown("### 📜 Contrato de Prestação de Serviços & Licenciamento")

            c_cnt1, c_cnt2 = st.columns([1, 1])

            with c_cnt1:
                st.markdown("#### 📝 Dados do Contratante")
                cnt_nome_in = st.text_input("Nome Completo do Responsável *")
                cnt_doc = st.text_input("CPF ou CNPJ *")
                cnt_whats = st.text_input("WhatsApp do Responsável *")
                cnt_cidade_in = st.text_input("Cidade / UF *", value="Contagem - MG")
                cnt_valor = st.number_input("Valor da Mensalidade (R$)", value=39.90, step=5.0)

            cnt_nome = formatar_nome_proprio(cnt_nome_in)
            cnt_cidade = formatar_nome_proprio(cnt_cidade_in)

            contrato_texto = f"""
CONTRATO DE PRESTAÇÃO DE SERVIÇOS E LICENCIAMENTO DE SOFTWARE

1. CONTRATANTE:
Nome: {cnt_nome if cnt_nome else '[Aguardando Preenchimento]'}
CPF/CNPJ: {cnt_doc if cnt_doc else '[Aguardando Preenchimento]'}
WhatsApp: {cnt_whats if cnt_whats else '[Aguardando Preenchimento]'}
Cidade/UF: {cnt_cidade}

2. CONTRATADO:
Desenvolvedor: Vagner Souza (Ciência da Computação)
WhatsApp: (31) 98968-4010

3. OBJETO DO CONTRATO:
Disponibilização de licença de uso do aplicativo web "Peladinha FC" para gestão de presenças, sorteio de times e controle financeiro.

4. VALOR E PAGAMENTO:
O CONTRATANTE pagará o valor mensal de R$ {cnt_valor:.2f}, até o dia 10 de cada mês via Pix.

5. ASSINATURA E ACEITE:
Ao marcar a opção de aceite e clicar no botão abaixo, o CONTRATANTE declara estar de acordo com todos os termos deste contrato.
Data do Aceite: {hoje_str}
            """

            with c_cnt2:
                st.markdown("#### 📄 Termos do Contrato")
                st.markdown(f"<div class='contract-box'><pre>{contrato_texto}</pre></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("#### ✍️ Assinatura Eletrônica & Envio")

            c_ass1, c_ass2 = st.columns([1, 1])
            with c_ass1:
                ass_nome_in = st.text_input("Digite seu Nome Completo para Assinar *")
                ass_nome = formatar_nome_proprio(ass_nome_in)
                aceite_box = st.checkbox("Li e aceito os termos do contrato de prestação de serviço acima.")

            with c_ass2:
                if cnt_nome and cnt_doc and ass_nome and aceite_box:
                    st.success("✅ **Contrato assinado e validado!**")
                    
                    doc_bytes = gerar_documento_contrato(cnt_nome, cnt_doc, cnt_whats, cnt_cidade, cnt_valor, hoje_str, ass_nome)
                    
                    st.download_button(
                        label="📄 Baixar Contrato Oficial Assinado",
                        data=doc_bytes,
                        file_name=f"Contrato_PeladinhaFC_{cnt_nome.replace(' ', '_')}.html",
                        mime="text/html",
                        use_container_width=True
                    )

                    msg_wa = (
                        f"⚽ *NOVO CONTRATO ASSINADO - PELADINHA FC*\n\n"
                        f"*Contratante:* {cnt_nome}\n"
                        f"*CPF/CNPJ:* {cnt_doc}\n"
                        f"*WhatsApp:* {cnt_whats}\n"
                        f"*Cidade/UF:* {cnt_cidade}\n"
                        f"*Valor Mensal:* R$ {cnt_valor:.2f}\n"
                        f"*Data da Assinatura:* {hoje_str}\n"
                        f"*Assinado Por:* {ass_nome}\n\n"
                        f"Declaro aceite integral aos termos do contrato prestado por Vagner Souza."
                    )
                    
                    wa_link = f"https://wa.me/5531989684010?text={urllib.parse.quote(msg_wa)}"
                    
                    st.markdown(f"""
                        <a href="{wa_link}" target="_blank" style="text-decoration: none;">
                            <div style="background-color: #25D366; color: white; padding: 12px 20px; border-radius: 8px; text-align: center; font-weight: bold; font-size: 1.0rem; margin-top: 10px;">
                                📲 Notificar Vagner Souza pelo WhatsApp
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    st.info("💡 Preencha os campos obrigatórios, a assinatura e marque o aceite para gerar o documento e botão de envio.")

        idx_tab += 1

        # --- TAB: CONFIGURAÇÕES GERAIS ---
        with tabs_objetos[idx_tab]:
            st.markdown("### ⚙️ Ajustes do App")
            limite_v = st.number_input("Limite de Vagas:", value=st.session_state.avisos.get("limite_vagas", 15))
            pix_v = st.text_input("Chave Pix:", value=st.session_state.avisos.get("pix", ""))
            venc_v = st.text_input("Vencimento Mensalidade:", value=st.session_state.avisos.get("vencimento", ""))
            recado_v = st.text_area("Recado no Painel:", value=st.session_state.avisos.get("recado", ""))
            
            if st.button("💾 Salvar Configurações"):
                st.session_state.avisos["limite_vagas"] = int(limite_v)
                st.session_state.avisos["pix"] = pix_v
                st.session_state.avisos["vencimento"] = venc_v
                st.session_state.avisos["recado"] = recado_v
                salvar_dados(AVISOS_FILE, st.session_state.avisos)
                st.success("Configurações atualizadas!")
        idx_tab += 1

        # --- TAB: CADASTRAR JOGADORA ---
        with tabs_objetos[idx_tab]:
            st.markdown("### ➕ Cadastrar Nova Jogadora")
            with st.form("form_admin_cad_jog"):
                adm_nome_raw = st.text_input("Nome Completo")
                adm_tipo_j = st.selectbox("Tipo de Jogadora", ["Mensalista", "Avulso"])
                adm_nasc_j = st.text_input("Data de Nascimento (DD/MM)")
                adm_user_j = st.text_input("Login de Acesso")
                adm_pass_j = st.text_input("Senha", type="password")
                
                btn_adm_cad = st.form_submit_button("Salvar Jogadora")
                if btn_adm_cad and adm_nome_raw:
                    adm_nome_fmt = formatar_nome_proprio(adm_nome_raw)
                    st.session_state.jogadoras.append({
                        "nome": adm_nome_fmt,
                        "tipo": adm_tipo_j,
                        "nascimento": adm_nasc_j.strip(),
                        "login": adm_user_j.strip(),
                        "senha": adm_pass_j.strip(),
                        "mes_vigente": mes_vigente_str,
                        "contato": "",
                        "status": "Ativo"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Jogadora **{adm_nome_fmt}** cadastrada com sucesso!")
        idx_tab += 1

        # --- TAB: GERENCIAR ELENCO ---
        with tabs_objetos[idx_tab]:
            st.markdown("### 📋 Gerenciar Elenco Cadastrado")
            if st.session_state.jogadoras:
                df_adm = pd.DataFrame(st.session_state.jogadoras)
                st.dataframe(df_adm, use_container_width=True)

# -----------------------------------------------------------------------------
# RODAPÉ
# -----------------------------------------------------------------------------
st.markdown("<div class='developer-footer'>Desenvolvido por <b>Vagner Souza / Ciência da Computação</b></div>", unsafe_allow_html=True)
