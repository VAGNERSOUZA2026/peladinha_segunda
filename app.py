import urllib.parse
import pandas as pd
import random
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
    </style>
""",
    unsafe_allow_html=True,
)

# --- SENHA DO ADMINISTRADOR ---
SENHA_ADMIN = "1234"  # 👈 Altere para a senha que a sua esposa desejar

# Estado de Sessão
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
  ]

if "admin_logado" not in st.session_state:
  st.session_state.admin_logado = False

if "times_sorteados" not in st.session_state:
  st.session_state.times_sorteados = None

# --- MENU LATERAL (LOGIN ADMIN) ---
with st.sidebar:
  st.header("🔑 Área Administrativa")
  if not st.session_state.admin_logado:
    senha_input = st.text_input("Senha do Admin:", type="password")
    if st.button("Entrar como Admin", use_container_width=True):
      if senha_input == SENHA_ADMIN:
        st.session_state.admin_logado = True
        st.success("Logado como Admin!")
        st.rerun()
      else:
        st.error("Senha incorreta!")
  else:
    st.success("🟢 Modo Admin Ativo")
    if st.button("Sair do Modo Admin", use_container_width=True):
      st.session_state.admin_logado = False
      st.rerun()

st.markdown(
    "<h1 class='main-header'>⚽ PELADA DA GALERA</h1>", unsafe_allow_html=True
)
st.caption(
    "Organização de Jogos, Lista de Presença e Sorteio de Times",
    unsafe_allow_html=True,
)
st.markdown("---")

# Abas Principais
aba_lista, aba_sorteio, aba_financeiro = st.tabs(
    ["📋 Lista de Presença", "🎲 Sorteio de Times", "💰 Pix / Financeiro"]
)

# -------------------------------------------------------------
# ABA 1: LISTA DE PRESENÇA
# -------------------------------------------------------------
with aba_lista:
  st.subheader("📌 Confirmar Presença no Próximo Jogo")

  LIMITE_VAGAS = 14
  confirmadas = len(st.session_state.jogadoras)
  vagas_restantes = LIMITE_VAGAS - confirmadas

  col_metric1, col_metric2 = st.columns(2)
  col_metric1.metric("Confirmadas", f"{confirmadas} / {LIMITE_VAGAS}")
  col_metric2.metric("Vagas Restantes", f"{max(0, vagas_restantes)}")

  if vagas_restantes <= 0:
    st.warning(
        "⚠️ Lista Cheia! Os próximos cadastros entrarão na Fila de Espera."
    )

  # Form de Confirmação
  with st.form("form_presenca"):
    st.write("### Colocar nome na lista:")
    c1, c2 = st.columns(2)
    with c1:
      nome = st.text_input("Nome da Jogadora:")
      posicao = st.selectbox("Posição:", ["Linha", "Goleira"])
    with c2:
      tipo = st.selectbox("Tipo:", ["Mensalista", "Avulsa"])
      pagou = st.checkbox("Já pagou o Pix?")

    btn_confirmar = st.form_submit_button(
        "✅ Confirmar Presença", use_container_width=True
    )

    if btn_confirmar:
      if nome.strip():
        nova = {
            "nome": nome.strip(),
            "posicao": posicao,
            "tipo": tipo,
            "pagou": pagou,
        }
        st.session_state.jogadoras.append(nova)
        st.success(f"✅ {nome} adicionada à lista!")
        st.rerun()
      else:
        st.error("Digite o nome para confirmar.")

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
        # Apenas o Admin pode excluir
        if st.session_state.admin_logado:
          if st.button("🗑️ Excluir", key=f"del_{idx}"):
            st.session_state.jogadoras.pop(idx)
            st.toast("Jogadora removida com sucesso!")
            st.rerun()

  else:
    st.info("Nenhuma jogadora confirmada ainda.")

# -------------------------------------------------------------
# ABA 2: SORTEADOR DE TIMES
# -------------------------------------------------------------
with aba_sorteio:
  st.subheader("🎲 Divisão Automática de Times")

  if len(st.session_state.jogadoras) < 4:
    st.info("Cadastre pelo menos 4 jogadoras para poder sortear os times.")
  else:
    num_times = st.radio("Quantidade de Times:", [2, 3], horizontal=True)

    if st.button("🔄 Sortear Coletes Agora!", use_container_width=True):
      lista_copia = [j["nome"] for j in st.session_state.jogadoras]
      random.shuffle(lista_copia)

      times_dict = {}
      for i in range(num_times):
        times_dict[f"Time {i+1}"] = lista_copia[i::num_times]

      st.session_state.times_sorteados = times_dict

    # Exibição dos Times Sorteados
    if st.session_state.times_sorteados:
      st.markdown("---")
      cols_times = st.columns(len(st.session_state.times_sorteados))

      texto_zap = "⚽ *TIMES SORTEADOS DA PELADA* ⚽\n\n"

      for idx, (nome_time, jogadoras_time) in enumerate(
          st.session_state.times_sorteados.items()
      ):
        texto_zap += f"👕 *{nome_time.upper()}*\n"
        with cols_times[idx]:
          st.markdown(
              f"""
                        <div class='card-time'>
                            <h3 style='color:#1E3A8A; margin:0;'>👕 {nome_time}</h3>
                            <hr style='margin: 8px 0;'>
                            {"".join([f"<p style='margin:4px 0;'>• <b>{nome}</b></p>" for nome in jogadoras_time])}
                        </div>
                    """,
              unsafe_allow_html=True,
          )

        for nome_j in jogadoras_time:
          texto_zap += f"• {nome_j}\n"
        texto_zap += "\n"

      # Botão para Publicar no WhatsApp
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
            ">📲 Publicar Times no WhatsApp</a>
        """,
          unsafe_allow_html=True,
      )

# -------------------------------------------------------------
# ABA 3: FINANCEIRO
# -------------------------------------------------------------
with aba_financeiro:
  st.subheader("💰 Pagamentos do Pix")
  st.write("Chave Pix da Quadra: **(31) 99999-9999** (Sua Esposa)")

  if st.session_state.jogadoras:
    pagas = sum(1 for j in st.session_state.jogadoras if j["pagou"])
    pendentes = len(st.session_state.jogadoras) - pagas

    st.write(f"• **Pagas:** {pagas}")
    st.write(f"• **Pendentes:** {pendentes}")
  else:
    st.write("Sem registros no momento.")
