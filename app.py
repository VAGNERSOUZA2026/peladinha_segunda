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
# FUNÇÃO PARA GERAR COMPROVANTE SINTÉTICO PARA TESTES
# -----------------------------------------------------------------------------
def gerar_comprovante_teste(nome_jogadora, valor, data_str):
    img = Image.new('RGB', (400, 250), color=(245, 247, 250))
    d = ImageDraw.Draw(img)
    
    d.rectangle([(10, 10), (390, 240)], outline=(15, 23, 42), width=3)
    d.rectangle([(10, 10), (390, 50)], fill=(15, 23, 42))
    d.text((20, 20), "COMPROVANTE DE TESTE - PIX", fill=(255, 255, 255))
    
    d.text((30, 70), f"Pagador: {nome_jogadora}", fill=(15, 23, 42))
    d.text((30, 100), f"Recebedor: Peladinha FC", fill=(15, 23, 42))
    d.text((30, 130), f"Valor: R$ {valor:.2f}", fill=(34, 197, 94))
    d.text((30, 160), f"Data: {data_str}", fill=(100, 116, 139))
    d.text((30, 190), f"Status: SIMULAÇÃO DE TESTE", fill=(239, 68, 68))
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

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

if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])

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

# Garantir campo de pagamento em jogadoras antigas
for j in st.session_state.jogadoras:
    if "status_pagamento" not in j:
        j["status_pagamento"] = "Pendente"

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
    "💸 Pagamento & Pix",
    "📜 Regulamento",
    "📋 Elenco de Jogadoras"
]

if st.session_state.admin_logged:
    lista_menu.insert(2, "📊 Fluxo de Caixa (Admin)")

lista_menu.append("⚙️ Painel Admin")
menu = st.sidebar.radio("Ir para:", lista_menu)

# -----------------------------------------------------------------------------
# ÁREA DA JOGADORA
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
                        "contato": "", "status": "Ativo", "status_pagamento": "Pendente"
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
# PÁGINA 3: FLUXO DE CAIXA
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
# PÁGINA 4: PAGAMENTO & PIX
# -----------------------------------------------------------------------------
elif menu == "💸 Pagamento & Pix":
    st.subheader("💸 Dados para Pagamento & Envio de Comprovante")
    
    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        st.markdown("### 🔑 Informações do Pix")
        st.info(f"**Chave Pix:** `{st.session_state.avisos.get('pix')}`")
        st.write(f"📅 **Vencimento:** {st.session_state.avisos.get('vencimento')}")
        st.write(f"💬 **Recado:** {st.session_state.avisos.get('recado')}")

    with col_p2:
        st.markdown("### 📤 Enviar Comprovante")
        
        if not st.session_state.usuario_logado:
            st.warning("⚠️ **Faça login na barra lateral para enviar seu comprovante!**")
        else:
            jogadora_atual = next((j for j in st.session_state.jogadoras if j["nome"] == st.session_state.usuario_logado), None)
            
            status_p = jogadora_atual.get("status_pagamento", "Pendente") if jogadora_atual else "Pendente"
            
            if status_p == "Pago":
                st.success(f"✅ **Seu pagamento do mês ({mes_vigente_str}) já está APROVADO!**")
            else:
                st.warning(f"Status Atual: **{status_p}**")
                
                with st.form("form_upload_comprovante", clear_on_submit=True):
                    file_up = st.file_uploader("Selecione a foto ou PDF do Comprovante:", type=["png", "jpg", "jpeg"])
                    valor_pago = st.number_input("Valor Pago (R$)", value=39.90 if jogadora_atual.get("tipo") == "Mensalista" else 15.00, step=5.0)
                    btn_env = st.form_submit_button("📤 Enviar Comprovante para Análise", use_container_width=True)
                    
                    if btn_env and file_up:
                        img_bytes = file_up.read()
                        b64_img = base64.b64encode(img_bytes).decode("utf-8")
                        
                        st.session_state.comprovantes.append({
                            "id": f"COMP_{random.randint(1000, 9999)}",
                            "jogadora": st.session_state.usuario_logado,
                            "data_envio": hoje_str,
                            "hora_envio": hoje_dt.strftime("%H:%M"),
                            "valor": valor_pago,
                            "status": "Em Análise",
                            "imagem_b64": b64_img
                        })
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success("Comprovante enviado com sucesso! O administrador irá analisar em breve.")
                        st.rerun()

    # Histórico de comprovantes do usuário
    if st.session_state.usuario_logado:
        st.markdown("---")
        st.markdown("### 📋 Meus Comprovantes Enviados")
        meus_comp = [c for c in st.session_state.comprovantes if c["jogadora"] == st.session_state.usuario_logado]
        if not meus_comp:
            st.caption("Você ainda não enviou nenhum comprovante este mês.")
        else:
            for c in reversed(meus_comp):
                badge = "🟡" if c['status'] == "Em Análise" else ("🟢" if c['status'] == "Aprovado" else "🔴")
                st.write(f"{badge} **Data:** {c['data_envio']} às {c['hora_envio']} | **Valor:** R$ {c['valor']:.2f} | **Status:** {c['status']}")

# -----------------------------------------------------------------------------
# PÁGINA 5: REGULAMENTO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Interno do Clube")
    for item in st.session_state.regulamento:
        st.markdown(f"#### {item['topico']}")
        st.write(item['regrinha'])

# -----------------------------------------------------------------------------
# PÁGINA 6: ELENCO DE JOGADORAS
# -----------------------------------------------------------------------------
elif menu == "📋 Elenco de Jogadoras":
    st.subheader("📋 Elenco Cadastrado & Status de Pagamento")
    if st.session_state.jogadoras:
        df = pd.DataFrame(st.session_state.jogadoras)
        st.dataframe(df[["nome", "tipo", "status_pagamento", "nascimento", "status"]], use_container_width=True)

# -----------------------------------------------------------------------------
# PÁGINA 7: PAINEL ADMIN
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
            "💳 Aprovar Comprovantes",
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

                st.markdown("---")
                st.markdown("### 🧪 Gerador de Comprovantes de Teste")
                st.caption("Simule o envio de comprovantes de pagamento para testar a aprovação/recusa sem precisar carregar fotos reais.")
                
                nomes_jog = [j["nome"] for j in st.session_state.jogadoras]
                if not nomes_jog:
                    st.info("Cadastre jogadoras para testar o envio de comprovantes.")
                else:
                    col_t1, col_t2 = st.columns(2)
                    with col_t1:
                        j_teste = st.selectbox("Selecione a Jogadora para o Teste:", nomes_jog)
                        val_teste = st.number_input("Valor do Comprovante (R$):", value=39.90, step=5.0)
                    with col_t2:
                        st.write(" ")
                        st.write(" ")
                        if st.button("🚀 Gerar & Enviar Comprovante de Teste", use_container_width=True):
                            b64_sim = gerar_comprovante_teste(j_teste, val_teste, hoje_str)
                            st.session_state.comprovantes.append({
                                "id": f"TESTE_{random.randint(1000, 9999)}",
                                "jogadora": j_teste,
                                "data_envio": hoje_str,
                                "hora_envio": hoje_dt.strftime("%H:%M"),
                                "valor": val_teste,
                                "status": "Em Análise",
                                "imagem_b64": b64_sim
                            })
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.success(f"Comprovante de TESTE gerado para **{j_teste}**! Confira na aba '💳 Aprovar Comprovantes'.")

                st.markdown("---")
                st.markdown("### 💥 ZERAR TODOS OS DADOS DE TESTE DA DEMO")
                st.warning("⚠️ **Atenção:** Ao clicar no botão abaixo, a lista de presenças, os comprovantes enviados, os lançamentos do caixa e os sorteios serão completamente ZERADOS para a próxima demonstração.")
                
                col_m1, col_m2 = st.columns([1, 1])
                with col_m1:
                    manter_jogadoras = st.checkbox("Manter o cadastro das Jogadoras", value=True)
                
                # BOTÃO QUE ZERA OS DADOS
                if st.button("💥 APAGAR TUDO E ZERAR SISTEMA", use_container_width=True, type="primary"):
                    # 1. Zerar Presenças
                    st.session_state.presencas = []
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    
                    # 2. Zerar Comprovantes
                    st.session_state.comprovantes = []
                    salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)

                    # 3. Zerar Financeiro
                    st.session_state.financeiro = []
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)

                    # 4. Zerar Sorteio
                    st.session_state.sorteio_oficial = {}
                    salvar_dados(SORTEIO_FILE, st.session_state.sorteio_oficial)

                    # 5. Resetar Status de Pagamento das Jogadoras
                    for j in st.session_state.jogadoras:
                        j["status_pagamento"] = "Pendente"
                    
                    if not manter_jogadoras:
                        st.session_state.jogadoras = []
                    
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)

                    st.success("🎉 **TODOS OS DADOS FORAM ZERADOS COM SUCESSO! O APP ESTÁ PRONTO PARA A DEMONSTRAÇÃO.**")
                    st.rerun()

            idx_tab += 1

        # --- TAB: APROVAR COMPROVANTES ---
        with tabs_objetos[idx_tab]:
            st.markdown("### 💳 Análise e Aprovação de Comprovantes")
            
            pendentes = [c for c in st.session_state.comprovantes if c.get("status") == "Em Análise"]
            
            if not pendentes:
                st.info("🎉 Nenhum comprovante pendente de análise no momento!")
            else:
                for comp in pendentes:
                    with st.expander(f"📄 Comprovante de {comp['jogadora']} — R$ {comp['valor']:.2f} ({comp['data_envio']} às {comp['hora_envio']})", expanded=True):
                        c_img, c_info = st.columns([1, 1])
                        
                        with c_img:
                            if "imagem_b64" in comp and comp["imagem_b64"]:
                                try:
                                    img_data = base64.b64decode(comp["imagem_b64"])
                                    st.image(img_data, caption=f"Comprovante {comp['id']}", use_container_width=True)
                                except Exception:
                                    st.error("Erro ao carregar a imagem do comprovante.")
                        
                        with c_info:
                            st.write(f"**Jogadora:** {comp['jogadora']}")
                            st.write(f"**Valor Informado:** R$ {comp['valor']:.2f}")
                            st.write(f"**Data de Envio:** {comp['data_envio']} às {comp['hora_envio']}")
                            
                            c_btn1, c_btn2 = st.columns(2)
                            
                            if c_btn1.button(f"✅ Aprovar Pagamento", key=f"ap_{comp['id']}", use_container_width=True):
                                comp["status"] = "Aprovado"
                                # Atualizar status da jogadora para PAGO
                                for j in st.session_state.jogadoras:
                                    if j["nome"] == comp["jogadora"]:
                                        j["status_pagamento"] = "Pago"
                                
                                # Lançar no Caixa Automático
                                st.session_state.financeiro.append({
                                    "data": hoje_str,
                                    "tipo": "Entrada (Receita)",
                                    "descricao": f"Mensalidade/Pix - {comp['jogadora']}",
                                    "valor": comp["valor"]
                                })
                                
                                salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                                salvar_dados(DATA_FILE, st.session_state.jogadoras)
                                salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                                st.success(f"Pagamento de **{comp['jogadora']}** APROVADO com sucesso!")
                                st.rerun()

                            if c_btn2.button(f"❌ Recusar Comprovante", key=f"rec_{comp['id']}", use_container_width=True):
                                comp["status"] = "Recusado"
                                salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                                st.warning(f"Comprovante de **{comp['jogadora']}** recusado.")
                                st.rerun()

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
                    
                    num_wa = "5531989684010"
                    txt_enc = urllib.parse.quote(msg_wa)
                    
                    link_mob = f"whatsapp://send?phone={num_wa}&text={txt_enc}"
                    link_pc = f"https://wa.me/{num_wa}?text={txt_enc}"

                    col_cnt_w1, col_cnt_w2 = st.columns(2)
                    with col_cnt_w1:
                        st.link_button("📱 Abrir no App (Celular)", link_mob, use_container_width=True)
                    with col_cnt_w2:
                        st.link_button("💻 WhatsApp Web (PC)", link_pc, use_container_width=True)
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
                        "status": "Ativo",
                        "status_pagamento": "Pendente"
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
