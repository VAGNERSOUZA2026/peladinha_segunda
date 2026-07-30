import random
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
    </style>
""",
    unsafe_allow_html=True,
)

# Estado de Sessão para as Jogadoras
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

# --- ABA 1: LISTA DE PRESENÇA ---
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
    df = pd.DataFrame(st.session_state.jogadoras)
    df["pagou"] = df["pagou"].map({True: "✅ Pago", False: "❌ Pendente"})
    st.dataframe(df, use_container_width=True)
  else:
    st.info("Nenhuma jogadora confirmada ainda.")

# --- ABA 2: SORTEADOR DE TIMES ---
with aba_sorteio:
  st.subheader("🎲 Divisão Automática de Times")

  if len(st.session_state.jogadoras) < 4:
    st.info("Cadastre pelo menos 4 jogadoras para poder sortear os times.")
  else:
    num_times = st.radio("Quantidade de Times:", [2, 3], horizontal=True)

    if st.button("🔄 Sortear Coletes Agora!", use_container_width=True):
      lista_copia = [j["nome"] for j in st.session_state.jogadoras]
      random.shuffle(lista_copia)

      st.markdown("---")
      cols_times = st.columns(num_times)

      for i in range(num_times):
        time_jogadoras = lista_copia[i::num_times]
        with cols_times[i]:
          st.markdown(
              f"""
                        <div class='card-time'>
                            <h3 style='color:#1E3A8A; margin:0;'>👕 Time {i+1}</h3>
                            <hr style='margin: 8px 0;'>
                            {"".join([f"<p style='margin:4px 0;'>• <b>{nome}</b></p>" for nome in time_jogadoras])}
                        </div>
                    """,
              unsafe_allow_html=True,
          )

# --- ABA 3: FINANCEIRO ---
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
