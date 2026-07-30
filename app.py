import random
import urllib.parse
from datetime import datetime, time
import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(
    page_title="Pelada Feminina ⚽", page_icon="⚽", layout="wide"
)

# Estilização Personalizada
st.markdown(
    """
    <style>
    .main-header { text-align: center; color: #1E3A8A; font-weight: 800; margin-bottom: 5px; }
    .card-time { background-color: #F8FAFC; border-radius: 12px; padding: 15px; border-left: 5px solid #2563EB; margin-bottom: 10px; }
    .destaque-fora { background-color: #FEF2F2; border: 1px solid #FECACA; color: #991B1B; padding: 8px; border-radius: 6px; font-weight: bold; margin-top: 8px; }
    </style>
""",
    unsafe_allow_html=True,
)

# --- BASE DE DADOS EM SESSÃO ---
if "usuarios_db" not in st.session_state:
  st.session_state.usuarios_db = {
      "admin": {"senha": "123", "nome": "Esposa (Admin)", "perfil": "admin"},
      "patricia": {"senha": "123", "nome": "Patrícia", "perfil": "jogadora"},
      "fernanda": {"senha": "123", "nome": "Fernanda", "perfil": "jogadora"},
  }

if "jogadoras" not in st.session_state:
  st.session_state.jogadoras = [
      {"nome": "Fernanda", "tipo": "Mensalista", "pagou": True},
      {"nome": "Patrícia", "tipo": "Avulsa", "pagou": False},
      {"nome": "Mariana", "tipo": "Mensalista", "pagou": True},
      {"nome": "Carla", "tipo": "Avulsa", "pagou": False},
      {"nome": "Juliana", "tipo": "Avulsa", "pagou": True},
  ]

if "limite_vagas" not in st.session_state:
  st.session_state.limite_vagas = 10

if "hora_limite" not in st.session_state:
  st.session_state.hora_limite = time(18, 0)

if "usuario_logado" not in st.session_state:
  st.session_state.usuario_logado = None

if "resultado_sorteio" not in st.session_state:
  st.session_state.resultado_sorteio = None

# --- BARRA LATERAL (LOGIN E CONFIGURADOS DO ADMIN) ---
with st.sidebar:
  st.header("👤 ÁREA DE ACESSO")

  if st.session_state.usuario_logado is None:
    aba_login, aba_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])

    with aba_login:
      user_input = st.text_input("Usuário:").strip().lower()
      senha_input = st.text_input("Senha:", type="password")
      if st.button("Entrar", use_container_width=True):
        db = st.session_state.usuarios_db
        if user_input in db and db[user_input]["senha"] == senha_input:
          st.session_state.usuario_logado = db[user_input]
          st.success(f"Bem-vinda, {db[user_input]['nome']}!")
          st.rerun()
        else:
          st.error("Usuário ou senha incorretos.")

    with aba_cadastro:
      novo_nome = st.text_input("Nome Completo:")
      novo_user = st.text_input("Escolha um Usuário:").strip().lower()
      nova_senha = st.text_input("Escolha uma Senha:", type="password")
      if st.button("Cadastrar", use_container_width=True):
        if (
            novo_nome.strip()
            and novo_user.strip()
            and nova_senha.strip()
        ):
          if novo_user in st.session_state.usuarios_db:
            st.error("Este usuário já existe!")
          else:
            st.session_state.usuarios_db[novo_user] = {
                "senha": nova_senha,
                "nome": novo_nome,
                "perfil": "jogadora",
            }
            st.success("Conta criada! Volte e faça login.")
        else:
          st.error("Preencha todos os campos.")

  else:
    usr = st.session_state.usuario_logado
    st.success(f"Logada: **{usr['nome']}**")

    if usr["perfil"] == "admin":
      st.markdown("---")
      st.subheader("⚙️ Painel da Administradora")
      st.session_state.limite_vagas = st.number_input(
          "Limite de Vagas Principais:",
          value=st.session_state.limite_vagas,
          min_value=2,
      )
      st.session_state.hora_limite = st.time_input(
          "Horário Limite de Confirmação:", value=st.session_state.hora_limite
      )

    if st.button("Sair / Trocar Usuário", use_container_width=True):
      st.session_state.usuario_logado = None
      st.rerun()

# --- CABEÇALHO ---
st.markdown(
    "<h1 class='main-header'>⚽ PELADA FEMININA</h1>", unsafe_allow_html=True
)
st.caption("Organização do Jogo, Lista de Presença e Sorteio")
st.markdown("---")

aba_lista, aba_sorteio, aba_financeiro = st.tabs(
    ["📋 Lista de Presença", "🎲 Sorteio de Times", "💰 Pix & Cobrança"]
)

# -------------------------------------------------------------
# ABA 1: LISTA DE PRESENÇA
# -------------------------------------------------------------
with aba_lista:
  st.subheader("📌 Confirmação de Presença")

  usr_atual = st.session_state.usuario_logado
  hora_atual = datetime.now().time()
  passou_do_horario = hora_atual > st.session_state.hora_limite

  vagas_max = st.session_state.limite_vagas
  confirmadas = st.session_state.jogadoras[:vagas_max]
  fila_espera = st.session_state.jogadoras[vagas_max:]

  c1, c2, c3 = st.columns(3)
  c1.metric("Confirmadas", f"{len(confirmadas)} / {vagas_max}")
  c2.metric("Fila de Espera", f"{len(fila_espera)}")
  c3.metric(
      "Horário Limite", st.session_state.hora_limite.strftime("%H:%M")
  )

  if passou_do_horario:
    st.warning(
        "⏰ **Horário limite atingido!** Novos cadastros irão para a Fila de"
        " Espera."
    )

  # INCLUSÃO MANUAL PELO ADMIN OU AUTO-CONFIRMAÇÃO PELA JOGADORA
  if usr_atual and usr_atual["perfil"] == "admin":
    with st.expander("➕ **(ADMIN) Adicionar Jogadora Manualmente**"):
      with st.form("form_admin_add"):
        nome_manual = st.text_input("Nome da Jogadora:")
        tipo_manual = st.selectbox("Tipo:", ["Mensalista", "Avulsa"])
        pago_manual = st.checkbox("Já pagou o Pix?")

        if st.form_submit_button("Confirmar Entrada"):
          if nome_manual.strip():
            st.session_state.jogadoras.append({
                "nome": nome_manual.strip(),
                "tipo": tipo_manual,
                "pagou": pago_manual,
            })
            st.success(f"{nome_manual} adicionada à lista!")
            st.rerun()

  elif usr_atual is None:
    st.info("⚠️ Faça login na barra lateral para se colocar na lista.")
  else:
    nomes_na_lista = [j["nome"] for j in st.session_state.jogadoras]
    if usr_atual["nome"] not in nomes_na_lista:
      with st.form("form_presenca"):
        tipo = st.selectbox("Tipo de Participação:", ["Avulsa", "Mensalista"])
        if st.form_submit_button(
            "✅ Confirmar Minha Presença", use_container_width=True
        ):
          st.session_state.jogadoras.append(
              {"nome": usr_atual["nome"], "tipo": tipo, "pagou": False}
          )
          st.success("Presença adicionada!")
          st.rerun()
    else:
      st.info(f"✅ **{usr_atual['nome']}**, você já está na lista de presença!")

  st.markdown("---")
  st.write("### 🟢 Lista Principal (Confirmadas)")

  if confirmadas:
    for idx, j in enumerate(confirmadas):
      col_num, col_nome, col_tipo, col_pix, col_acao = st.columns(
          [0.5, 3, 2, 2, 1.5]
      )

      with col_num:
        st.write(f"**{idx + 1}.**")
      with col_nome:
        st.write(f"**{j['nome']}**")

      # EDIÇÃO EXCLUSIVA DO ADMIN OU VISUALIZAÇÃO
      with col_tipo:
        if usr_atual and usr_atual["perfil"] == "admin":
          novo_tipo = st.selectbox(
              "Tipo",
              ["Avulsa", "Mensalista"],
              index=0 if j["tipo"] == "Avulsa" else 1,
              key=f"tipo_{idx}",
              label_visibility="collapsed",
          )
          if novo_tipo != j["tipo"]:
            j["tipo"] = novo_tipo
            st.rerun()
        else:
          st.write(f"🏷️ {j['tipo']}")

      with col_pix:
        if usr_atual and usr_atual["perfil"] == "admin":
          novo_pix = st.checkbox("Pago Pix", value=j["pagou"], key=f"pix_{idx}")
          if novo_pix != j["pagou"]:
            j["pagou"] = novo_pix
            st.rerun()
        else:
          st.write("✅ Pago" if j["pagou"] else "❌ Pendente")

      with col_acao:
        if (
            usr_atual
            and (usr_atual["nome"] == j["nome"] or usr_atual["perfil"] == "admin")
        ):
          if st.button("🗑️ Sair", key=f"del_{idx}"):
            st.session_state.jogadoras.pop(idx)
            st.toast("Nome removido! Caso houvesse fila, a 1ª da fila subiu.")
            st.rerun()

  # FILA DE ESPERA (CASO A LISTA EXCEDA O LIMITE DE VAGAS)
  if fila_espera:
    st.markdown("---")
    st.write("### ⏳ Fila de Espera (Suplentes)")
    for idx_f, j_f in enumerate(fila_espera):
      col_f_num, col_f_nome, col_f_tipo, col_f_acao = st.columns(
          [0.5, 3, 2, 1.5]
      )
      with col_f_num:
        st.write(f"**{idx_f + 1}º**")
      with col_f_nome:
        st.write(f"{j_f['nome']}")
      with col_f_tipo:
        st.write(f"{j_f['tipo']}")
      with col_f_acao:
        pos_real = vagas_max + idx_f
        if (
            usr_atual
            and (usr_atual["nome"] == j_f["nome"] or usr_atual["perfil"] == "admin")
        ):
          if st.button("🗑️ Sair", key=f"del_f_{pos_real}"):
            st.session_state.jogadoras.pop(pos_real)
            st.rerun()

# -------------------------------------------------------------
# ABA 2: SORTEADOR DE TIMES (100% ALEATÓRIO)
# -------------------------------------------------------------
with aba_sorteio:
  st.subheader("🎲 Sorteio Totalmente Aleatório")

  jogadoras_validas = st.session_state.jogadoras[
      : st.session_state.limite_vagas
  ]

  if len(jogadoras_validas) < 4:
    st.info("Necessário pelo menos 4 jogadoras na lista principal.")
  else:
    num_times = st.radio("Quantidade de Times:", [2, 3], horizontal=True)

    if st.button("🔄 Sortear Coletes na Sorte", use_container_width=True):
      lista_temp = [j["nome"] for j in jogadoras_validas]
      random.shuffle(lista_temp)

      times_dict = {}
      for i in range(num_times):
        time_jogadores = lista_temp[i::num_times]
        fora = (
            random.choice(time_jogadores)
            if len(time_jogadores) > 5
            else None
        )
        times_dict[f"Time {i+1}"] = {
            "jogadores": time_jogadores,
            "fora_1o_jogo": fora,
        }

      st.session_state.resultado_sorteio = times_dict

    if st.session_state.resultado_sorteio:
      st.markdown("---")
      cols_times = st.columns(len(st.session_state.resultado_sorteio))

      texto_zap = "⚽ *TIMES SORTEADOS DA PELADA* ⚽\n\n"

      for idx, (nome_time, dados) in enumerate(
          st.session_state.resultado_sorteio.items()
      ):
        jogs = dados["jogadores"]
        fora = dados["fora_1o_jogo"]

        texto_zap += f"👕 *{nome_time.upper()}*\n"
        with cols_times[idx]:
          html_j = "".join([
              (
                  f"<p>• <b>{nome}</b> (⚠️ Res. 1º jogo)</p>"
                  if nome == fora
                  else f"<p>• <b>{nome}</b></p>"
              )
              for nome in jogs
          ])
          st.markdown(
              f"<div class='card-time'><h3>👕 {nome_time}</h3>{html_j}</div>",
              unsafe_allow_html=True,
          )

        for nome in jogs:
          texto_zap += (
              f"• {nome} *(Reserva 1º jogo)*\n"
              if nome == fora
              else f"• {nome}\n"
          )
        texto_zap += "\n"

      texto_encoded = urllib.parse.quote(texto_zap)
      st.markdown(
          f'<a href="https://api.whatsapp.com/send?text={texto_encoded}"'
          ' target="_blank" style="background:#25D366; color:white; padding:12px;'
          " display:block; text-align:center; font-weight:bold;"
          ' border-radius:8px; text-decoration:none;">📲 Compartilhar Times no'
          " WhatsApp</a>",
          unsafe_allow_html=True,
      )

# -------------------------------------------------------------
# ABA 3: FINANCEIRO & COBRANÇA
# -------------------------------------------------------------
with aba_financeiro:
  st.subheader("💰 Gestão de Pix")

  pendentes = [
      j for j in st.session_state.jogadoras if not j["pagou"]
  ]

  if pendentes:
    st.warning(f"⚠️ Existem **{len(pendentes)} pagamentos pendentes**.")

    msg_cobranca = (
        "📢 *LEMBRETE DE PIX DA PELADA* ⚽\n\nMeninas, segue a lista de quem"
        " ainda não confirmou o Pix:\n"
    )
    for p in pendentes:
      msg_cobranca += f"• {p['nome']} ({p['tipo']})\n"
    msg_cobranca += (
        "\n📌 *Chave Pix:* (31) 99999-9999\nPor favor, enviem o comprovante!"
    )

    encoded_cob = urllib.parse.quote(msg_cobranca)
    st.markdown(
        f'<a href="https://api.whatsapp.com/send?text={encoded_cob}"'
        ' target="_blank" style="background:#DC2626; color:white; padding:10px;'
        " display:inline-block; font-weight:bold; border-radius:8px;"
        ' text-decoration:none;">📲 Cobrar Pendentes no WhatsApp</a>',
        unsafe_allow_html=True,
    )
  else:
    st.success("🎉 Todos os Pix foram pagos!")
