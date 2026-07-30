import random
import urllib.parse
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Pelada da Galera ⚽", page_icon="⚽", layout="wide"
)

# Estilização Personalizada
st.markdown(
    """
    <style>
    .main-header {
        text-align: center;
        color: #1E3A8A;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .card-time {
        background-color: #F8FAFC;
        border-radius: 12px;
        padding: 15px;
        border-left: 5px solid #2563EB;
        margin-bottom: 10px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    .destaque-fora {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        color: #991B1B;
        padding: 8px;
        border-radius: 6px;
        font-weight: bold;
        margin-top: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- USUÁRIOS E SENHAS PARA TESTE ---
# Cada jogadora tem seu usuário e senha. A administradora é a "admin".
USUARIOS = {
    "admin": {"senha": "123", "nome": "Esposa (Admin)", "perfil": "admin"},
    "fernanda": {
        "senha": "123",
        "nome": "Fernanda (Capitã)",
        "perfil": "jogadora",
    },
    "mariana": {"senha": "123", "nome": "Mariana", "perfil": "jogadora"},
    "carla": {"senha": "123", "nome": "Carla", "perfil": "jogadora"},
    "juliana": {"senha": "123", "nome": "Juliana", "perfil": "jogadora"},
    "patricia": {"senha": "123", "nome": "Patrícia", "perfil": "jogadora"},
    "camila": {"senha": "123", "nome": "Camila", "perfil": "jogadora"},
}

# --- ESTADO DE SESSÃO ---
if "usuario_logado" not in st.session_state:
  st.session_state.usuario_logado = None

if "jogadoras" not in st.session_state:
  st.session_state.jogadoras = [
      {
          "nome": "Fernanda (Capitã)",
          "posicao": "Linha",
          "tipo": "Mensalista",
          "pagou": True,
      },
      {
          "nome": "Mariana",
          "posicao": "Goleira",
          "tipo": "Mensalista",
          "pagou": True,
      },
      {"nome": "Carla", "posicao": "Linha", "tipo": "Avulsa", "pagou": False},
      {"nome": "Juliana", "posicao": "Linha", "tipo": "Avulsa", "pagou": True},
      {"nome": "Patrícia", "posicao": "Linha", "tipo": "Avulsa", "pagou": True},
      {"nome": "Camila", "posicao": "Linha", "tipo": "Avulsa", "pagou": False},
  ]

if "resultado_sorteio" not in st.session_state:
  st.session_state.resultado_sorteio = None

# --- BARRA LATERAL (LOGIN / PERFIL) ---
with st.sidebar:
  st.header("👤 ÁREA DE ACESSO")

  if st.session_state.usuario_logado is None:
    st.subheader("Fazer Login")
    user_input = (
        st.text_input("Usuário:").strip().lower()
    )  # ex: fernanda ou admin
    senha_input = st.text_input("Senha:", type="password")

    if st.button("Entrar", use_container_width=True):
      if user_input in USUARIOS and USUARIOS[user_input]["senha"] == senha_input:
        st.session_state.usuario_logado = USUARIOS[user_input]
        st.success(f"Bem-vinda, {USUARIOS[user_input]['nome']}!")
        st.rerun()
      else:
        st.error("Usuário ou senha incorretos.")
  else:
    usr = st.session_state.usuario_logado
    st.success(f"Logged in: **{usr['nome']}**")
    if usr["perfil"] == "admin":
      st.info("⭐ Acesso de Administradora")
    else:
      st.caption("Acesso Jogadora")

    if st.button("Sair / Trocar Usuário", use_container_width=True):
      st.session_state.usuario_logado = None
      st.rerun()

st.markdown(
    "<h1 class='main-header'>⚽ PELADA DA GALERA</h1>", unsafe_allow_html=True
)
st.caption(
    "Organização de Jogos, Presença e Divisão Justa de Times",
    unsafe_allow_html=True,
)
st.markdown("---")

# Abas Principais
aba_lista, aba_sorteio, aba_financeiro = st.tabs(
    ["📋 Lista de Presença", "🎲 Sorteio & Rodízio", "💰 Pix / Financeiro"]
)

# -------------------------------------------------------------
# ABA 1: LISTA DE PRESENÇA
# -------------------------------------------------------------
with aba_lista:
  st.subheader("📌 Confirmar Presença no Próximo Jogo")

  usr_atual = st.session_state.usuario_logado

  if usr_atual is None:
    st.warning("⚠️ Faça login no menu lateral para confirmar sua presença.")
  else:
    # Verifica se o usuário logado já está na lista
    nomes_na_lista = [j["nome"] for j in st.session_state.jogadoras]
    ja_na_lista = usr_atual["nome"] in nomes_na_lista

    if not ja_na_lista:
      st.write(f"Olá, **{usr_atual['nome']}**! Confirme sua vaga abaixo:")
      with st.form("form_minha_presenca"):
        c1, c2 = st.columns(2)
        with c1:
          posicao = st.selectbox("Sua Posição:", ["Linha", "Goleira"])
        with c2:
          tipo = st.selectbox("Tipo:", ["Avulsa", "Mensalista"])

        if st.form_submit_button(
            "✅ Confirmar Minha Presença", use_container_width=True
        ):
          st.session_state.jogadoras.append({
              "nome": usr_atual["nome"],
              "posicao": posicao,
              "tipo": tipo,
              "pagou": False,
          })
          st.success("Sua presença foi confirmada!")
          st.rerun()
    else:
      st.info(f"✅ **{usr_atual['nome']}**, você já está confirmada na lista!")

  st.markdown("---")
  st.write("### Lista Atual de Confirmadas:")

  if st.session_state.jogadoras:
    for idx, j in enumerate(st.session_state.jogadoras):
      col_nome, col_info, col_acao = st.columns([3, 2, 1])

      with col_nome:
        st.write(f"**{idx + 1}. {j['nome']}** ({j['posicao']})")

      with col_info:
        status_pag = "✅ Pago" if j["pagou"] else "❌ Pendente"
        st.write(f"{j['tipo']} | {status_pag}")

      with col_acao:
        # A jogadora pode remover a SI MESMA, ou o ADMIN pode remover QUALQUER UMA
        e_o_proprio_usuario = (
            usr_atual is not None and usr_atual["nome"] == j["nome"]
        )
        e_admin = usr_atual is not None and usr_atual["perfil"] == "admin"

        if e_o_proprio_usuario or e_admin:
          if st.button("🗑️ Sair", key=f"del_{idx}"):
            st.session_state.jogadoras.pop(idx)
            st.toast("Nome removido da lista!")
            st.rerun()
  else:
    st.info("Nenhuma jogadora confirmada ainda.")

# -------------------------------------------------------------
# ABA 2: SORTEADOR E RODÍZIO DE TIMES
# -------------------------------------------------------------
with aba_sorteio:
  st.subheader("🎲 Divisão Automática e Sorteio de Rodízio")

  jogadoras_confirmadas = st.session_state.jogadoras
  qtd_confirmadas = len(jogadoras_confirmadas)

  st.write(f"Total de confirmadas: **{qtd_confirmadas} jogadoras**")

  if qtd_confirmadas < 4:
    st.info("Cadastre pelo menos 4 jogadoras para sorteio.")
  else:
    num_times = st.radio("Quantidade de Times:", [2, 3], horizontal=True)

    if st.button("🔄 Sortear Times e Reserva Justa", use_container_width=True):
      lista_nomes = [j["nome"] for j in jogadoras_confirmadas]
      random.shuffle(lista_nomes)

      # Distribui entre os times
      times_estruturados = {}
      for i in range(num_times):
        times_estruturados[f"Time {i+1}"] = {
            "jogadores": lista_nomes[i::num_times],
            "fora_primeira_rodada": None,
        }

      # Regra de Justiça: Se o time tiver mais de 5 jogadoras de linha, sorteia quem fica de fora primeiro
      for nome_time, dados in times_estruturados.items():
        if len(dados["jogadores"]) > 5:
          # Sorteia aleatoriamente 1 pessoa deste time para começar fora
          dados["fora_primeira_rodada"] = random.choice(dados["jogadores"])

      st.session_state.resultado_sorteio = times_estruturados

    # EXIBIÇÃO DOS RESULTADOS
    if st.session_state.resultado_sorteio:
      st.markdown("---")
      cols_times = st.columns(len(st.session_state.resultado_sorteio))

      texto_zap = "⚽ *PELADA - TIMES E SORTEIO DO RODÍZIO* ⚽\n\n"

      for idx, (nome_time, dados) in enumerate(
          st.session_state.resultado_sorteio.items()
      ):
        jogadores = dados["jogadores"]
        fora = dados["fora_primeira_rodada"]

        texto_zap += f"👕 *{nome_time.upper()}* ({len(jogadores)} jogadoras)\n"

        with cols_times[idx]:
          html_jogadores = ""
          for nome_j in jogadores:
            if nome_j == fora:
              html_jogadores += f"<p style='margin:4px 0;'>• <b>{nome_j}</b> (⚠️ Res. 1º jogo)</p>"
            else:
              html_jogadores += f"<p style='margin:4px 0;'>• <b>{nome_j}</b></p>"

          st.markdown(
              f"""
                        <div class='card-time'>
                            <h3 style='color:#1E3A8A; margin:0;'>👕 {nome_time}</h3>
                            <hr style='margin: 8px 0;'>
                            {html_jogadores}
                        </div>
                    """,
              unsafe_allow_html=True,
          )

          if fora:
            st.markdown(
                f"<div class='destaque-fora'>🎲 **Sorteio do Banco:** {fora} começa fora na 1ª partida desse time!</div>",
                unsafe_allow_html=True,
            )

        for nome_j in jogadores:
          if nome_j == fora:
            texto_zap += f"• {nome_j} *(⚠️ Começa fora no rodízio)*\n"
          else:
            texto_zap += f"• {nome_j}\n"

        texto_zap += "\n"

      texto_zap += "📢 *REGRA DO RODÍZIO:* No time com 6 jogadoras, quem perde/sai faz o rodízio na ordem do sorteio sem injustiça!\n"

      # Botão WhatsApp
      texto_encoded = urllib.parse.quote(texto_zap)
      url_whatsapp = f"https://api.whatsapp.com/send?text={texto_encoded}"

      st.markdown("---")
      st.markdown(
          f"""
            <a href="{url_whatsapp}" target="_blank" style="
                display: block;
                width: 100%;
                background-color: #25D366;
                color: white;
                padding: 12px;
                text-align: center;
                text-decoration: none;
                font-size: 1.1rem;
                font-weight: bold;
                border-radius: 8px;
                box-shadow: 0px 3px 6px rgba(0,0,0,0.16);
            ">📲 Compartilhar Divisão no WhatsApp</a>
        """,
          unsafe_allow_html=True,
      )

# -------------------------------------------------------------
# ABA 3: FINANCEIRO
# -------------------------------------------------------------
with aba_financeiro:
  st.subheader("💰 Pagamentos do Pix")
  st.write("Chave Pix da Quadra: **(31) 99999-9999**")

  if st.session_state.jogadoras:
    df_fin = pd.DataFrame(st.session_state.jogadoras)
    df_fin["pagou"] = df_fin["pagou"].map({True: "✅ Pago", False: "❌ Pendente"})
    st.dataframe(df_fin[["nome", "tipo", "pagou"]], use_container_width=True)
