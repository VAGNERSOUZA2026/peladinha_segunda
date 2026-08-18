import streamlit as st
import os
import json
import random
from datetime import datetime

# Configuração da Página
st.set_page_config(
    page_title="Peladinha FC",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS Personalizada
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .card-team {
        background-color: #1F2937;
        padding: 1.2rem;
        border-radius: 0.75rem;
        border: 1px solid #374151;
        margin-bottom: 1rem;
    }
    h1, h2, h3 {
        color: #F472B6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Arquivos de Persistência de Dados
DATA_FILE = "jogadoras.json"
PRESENCAS_FILE = "presencas.json"
ADMINS_FILE = "administradores.json"
FINANCE_FILE = "financeiro.json"
COMPROVANTES_FILE = "comprovantes.json"
AVISOS_FILE = "avisos.json"
REGULAMENTO_FILE = "regulamento.json"
SORTEIO_FILE = "sorteio.json"
UPLOAD_DIR = "comprovantes_uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Funções de Carregamento e Salvamento
def carregar_dados(arquivo, default):
    if os.path.exists(arquivo):
        try:
            with open(arquivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def salvar_dados(arquivo, dados):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

# Inicialização do Session State
if "jogadoras" not in st.session_state:
    st.session_state.jogadoras = carregar_dados(DATA_FILE, [])

if "presencas" not in st.session_state:
    st.session_state.presencas = carregar_dados(PRESENCAS_FILE, [])

if "administradores" not in st.session_state:
    st.session_state.administradores = carregar_dados(ADMINS_FILE, [
        {"nome": "Admin Master", "login": "admin", "senha": "123", "celular": "5531999999999"}
    ])

if "financeiro" not in st.session_state:
    st.session_state.financeiro = carregar_dados(FINANCE_FILE, [])

if "comprovantes" not in st.session_state:
    st.session_state.comprovantes = carregar_dados(COMPROVANTES_FILE, [])

if "avisos" not in st.session_state:
    st.session_state.avisos = carregar_dados(AVISOS_FILE, {
        "limite_vagas": 15,
        "pix": "peladinhafc@email.com",
        "vencimento": "Todo dia 10",
        "valor_mensalidade": 50.00,
        "valor_avulso": 15.00
    })

if "regulamento" not in st.session_state:
    st.session_state.regulamento = carregar_dados(REGULAMENTO_FILE, [
        {"topico": "📌 1. Confirmação", "regrinha": "A confirmação deve ser feita até a segunda-feira às 17h."},
        {"topico": "📌 2. Pagamento", "regrinha": "Mensalidades vencem todo dia 10."},
        {"topico": "📌 3. Faltas", "regrinha": "Avisar com antecedência em caso de imprevistos."}
    ])

if "sorteio_oficial" not in st.session_state:
    st.session_state.sorteio_oficial = carregar_dados(SORTEIO_FILE, {})

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "perfil_logado" not in st.session_state:
    st.session_state.perfil_logado = None

if "pagina_atual" not in st.session_state:
    st.session_state.pagina_atual = "home"

hoje_dt = datetime.now()

# Funções Auxiliares
def obter_nome_p(p):
    if isinstance(p, dict):
        return p.get("nome", "")
    return str(p)

def obter_tipo_p(p):
    if isinstance(p, dict):
        return p.get("tipo", "Avulso")
    return "Avulso"

# Tela de Login / Autenticação
if not st.session_state.usuario_logado:
    st.markdown("<h1 style='text-align: center;'>⚽ Peladinha FC — Login</h1>", unsafe_allow_html=True)
    tab_l1, tab_l2, tab_l3 = st.tabs(["🔑 Entrar", "📝 Cadastrar Atleta", "👑 Acesso Admin/Dev"])
    
    with tab_l1:
        st.write("### Identificação de Jogadora")
        login_nome = st.selectbox("Selecione seu Nome", ["Selecione..."] + [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo"])
        senha_jog = st.text_input("Senha", type="password", key="senha_jog_login")
        if st.button("Entrar no Sistema"):
            if login_nome != "Selecione...":
                j_obj = next((j for j in st.session_state.jogadoras if j["nome"] == login_nome), None)
                if j_obj and j_obj.get("senha") == senha_jog:
                    st.session_state.usuario_logado = login_nome
                    st.session_state.perfil_logado = "Jogadora"
                    st.success(f"Bem-vinda, {login_nome}!")
                    st.rerun()
                else:
                    st.error("Senha incorreta!")
            else:
                st.warning("Selecione um nome válido.")

    with tab_l2:
        st.write("### Cadastro de Nova Atleta")
        with st.form("form_novo_cadastro"):
            novo_nome = st.text_input("Nome Completo *")
            novo_login = st.text_input("Nome de Usuário (Login) *")
            novo_senha = st.text_input("Senha *", type="password")
            novo_nasc = st.text_input("Data de Nascimento (DD/MM/AAAA)")
            novo_tipo = st.selectbox("Tipo de Atleta", ["Avulso", "Mensalista"])
            
            if st.form_submit_button("Solicitar Cadastro"):
                if novo_nome.strip() and novo_login.strip() and novo_senha.strip():
                    if any(j["login"] == novo_login.strip() for j in st.session_state.jogadoras):
                        st.error("Este login já está em uso.")
                    else:
                        st.session_state.jogadoras.append({
                            "nome": novo_nome.strip(),
                            "login": novo_login.strip(),
                            "senha": novo_senha.strip(),
                            "nascimento": novo_nasc.strip(),
                            "tipo": novo_tipo,
                            "quitado": "Não",
                            "status": "Pendente"
                        })
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success("Cadastro solicitado com sucesso! Aguarde a aprovação de um Administrador.")
                else:
                    st.error("Preencha todos os campos obrigatórios (*).")

    with tab_l3:
        st.write("### Acesso Administrativo ou Desenvolvedor")
        adm_user = st.text_input("Login Admin/Dev")
        adm_pass = st.text_input("Senha Admin/Dev", type="password")
        if st.button("Entrar como Admin/Dev"):
            if adm_user == "dev" and adm_pass == "dev123":
                st.session_state.usuario_logado = "Desenvolvedor"
                st.session_state.perfil_logado = "Dev"
                st.success("Logado como Desenvolvedor (Acesso Total)!")
                st.rerun()
            else:
                adm_encontrado = next((a for a in st.session_state.administradores if a["login"] == adm_user and a["senha"] == adm_pass), None)
                if adm_encontrado:
                    st.session_state.usuario_logado = adm_encontrado["nome"]
                    st.session_state.perfil_logado = "Admin"
                    st.success(f"Logado como Administrador: {adm_encontrado['nome']}!")
                    st.rerun()
                else:
                    st.error("Credenciais inválidas para Administrador/Dev.")

else:
    # Barra Lateral / Menu de Navegação
    st.sidebar.markdown(f"### ⚽ Peladinha FC\nLogada: **{st.session_state.usuario_logado}** (`{st.session_state.perfil_logado}`)")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🏠 Início & Regulamento", use_container_width=True):
        st.session_state.pagina_atual = "home"
    if st.sidebar.button("🙋‍♀️ Lista de Presença", use_container_width=True):
        st.session_state.pagina_atual = "presenca"
    if st.sidebar.button("🔀 Sorteio de Times", use_container_width=True):
        st.session_state.pagina_atual = "sorteio"
    if st.sidebar.button("📋 Elenco de Atletas", use_container_width=True):
        st.session_state.pagina_atual = "elenco"
    if st.sidebar.button("💸 Pagamentos & Pix", use_container_width=True):
        st.session_state.pagina_atual = "pagamento"
    if st.sidebar.button("📊 Fluxo de Caixa", use_container_width=True):
        st.session_state.pagina_atual = "caixa"
        
    if st.session_state.perfil_logado in ["Admin", "Dev"]:
        if st.sidebar.button("🛠️ Painel de Gerenciamento", use_container_width=True):
            st.session_state.pagina_atual = "gerenciamento"
            
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
        st.session_state.usuario_logado = None
        st.session_state.perfil_logado = None
        st.session_state.pagina_atual = "home"
        st.rerun()

    # Roteamento de Páginas
    if st.session_state.pagina_atual == "home":
        st.subheader("🏠 Bem-vinda ao Peladinha FC!")
        st.write("Confira abaixo o regulamento oficial e as principais informações do grupo.")
        
        for reg in st.session_state.regulamento:
            st.markdown(f"""
            <div class='card-team'>
                <h4>{reg['topico']}</h4>
                <p>{reg['regrinha']}</p>
            </div>
            """, unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "presenca":
        st.subheader("🙋‍♀️ Lista de Presença & Confirmação")
        
        limite = st.session_state.avisos.get("limite_vagas", 15)
        lista_atual = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        confirmadas = lista_atual[:limite]
        espera = lista_atual[limite:]
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"### ✅ Lista Principal ({len(confirmadas)}/{limite})")
            for idx, p in enumerate(confirmadas):
                nome_p = obter_nome_p(p)
                tipo_p = obter_tipo_p(p)
                st.markdown(f"- **{idx+1}º** — {nome_p} (`{tipo_p}`)")
        with col_p2:
            st.markdown(f"### ⏳ Fila de Espera ({len(espera)})")
            for idx, p in enumerate(espera):
                nome_p = obter_nome_p(p)
                tipo_p = obter_tipo_p(p)
                st.markdown(f"- **{idx+1}º** — {nome_p} (`{tipo_p}`)")

        st.markdown("---")
        
        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            st.write("### 👑 Painel Administrativo de Presenças")
            with st.form("form_add_manual"):
                st.write("<b>Adicionar Atleta Cadastrada</b>", unsafe_allow_html=True)
                nomes_cadastradas = [j["nome"] for j in st.session_state.jogadoras if j.get("status") == "Ativo" and not any(obter_nome_p(p) == j["nome"] for p in st.session_state.presencas)]
                atleta_escolhida = st.selectbox("Selecione a Atleta", nomes_cadastradas if nomes_cadastradas else ["Nenhuma disponível"])
                if st.form_submit_button("Incluir na Lista"):
                    if nomes_cadastradas and atleta_escolhida != "Nenhuma disponível":
                        j_dados = next((j for j in st.session_state.jogadoras if j["nome"] == atleta_escolhida), None)
                        tipo_j = j_dados.get("tipo", "Avulso") if j_dados else "Avulso"
                        st.session_state.presencas.append({
                            "nome": atleta_escolhida,
                            "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j,
                            "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success(f"{atleta_escolhida} incluída com sucesso!")
                        st.rerun()

            with st.form("form_add_externa"):
                st.write("<b>Adicionar Convidada / Avulsa (Sem Cadastro)</b>", unsafe_allow_html=True)
                nome_externa = st.text_input("Nome da Convidada")
                tipo_externa = st.selectbox("Tipo da Convidada", ["Avulso", "Mensalista"], key="tipo_ext")
                if st.form_submit_button("Incluir Convidada"):
                    if nome_externa.strip():
                        if not any(obter_nome_p(p) == nome_externa.strip() for p in st.session_state.presencas):
                            st.session_state.presencas.append({
                                "nome": nome_externa.strip(), "hora": hoje_dt.strftime("%H:%M"),
                                "tipo": tipo_externa, "dt_confirmacao": hoje_dt.isoformat()
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            st.success(f"Convidada {nome_externa.strip()} incluída!")
                            st.rerun()
                        else:
                            st.error("Esta atleta já está na lista.")
                    else:
                        st.error("Informe o nome da convidada.")

            st.write("### Remover da Lista:")
            for p in st.session_state.presencas:
                c_nome = obter_nome_p(p)
                if st.button(f"Remover {c_nome}", key=f"rem_l_{c_nome}"):
                    st.session_state.presencas = [item for item in st.session_state.presencas if obter_nome_p(item) != c_nome]
                    salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                    st.rerun()
        else:
            st.write("### ✍️ Gerenciar Minha Presença")
            if st.session_state.perfil_logado == "Jogadora":
                j_nome = st.session_state.usuario_logado
                dados_j = next((j for j in st.session_state.jogadoras if j["nome"] == j_nome), None)
                tipo_j = dados_j.get("tipo", "Avulso") if dados_j else "Avulso"
                
                pos_conf = next((idx + 1 for idx, p in enumerate(confirmadas) if obter_nome_p(p) == j_nome), None)
                pos_esp = next((idx + 1 for idx, p in enumerate(espera) if obter_nome_p(p) == j_nome), None)
                
                if pos_conf:
                    st.success(f"🎉 Você está na **Lista Principal** na posição **{pos_conf}**!")
                elif pos_esp:
                    st.warning(f"⏳ Você está na **Fila de Espera** na posição **{pos_esp}º**.")
                else:
                    st.info("ℹ️ Você não está confirmada.")

                with st.form("form_pres"):
                    c_ok = st.form_submit_button("👍 Confirmar Presença", use_container_width=True)
                    c_canc = st.form_submit_button("❌ Cancelar Presença", use_container_width=True)

                ja_na_lista = (pos_conf is not None or pos_esp is not None)

                if c_ok:
                    if ja_na_lista:
                        st.warning("⚠️ Você já está confirmada na lista! Sua posição e horário foram preservados.")
                    else:
                        st.session_state.presencas.append({
                            "nome": j_nome, "hora": hoje_dt.strftime("%H:%M"),
                            "tipo": tipo_j, "dt_confirmacao": hoje_dt.isoformat()
                        })
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.success("Presença confirmada com sucesso!")
                        st.rerun()

                if c_canc:
                    if ja_na_lista:
                        st.session_state.presencas = [item for item in st.session_state.presencas if obter_nome_p(item) != j_nome]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.info("Presença cancelada com sucesso!")
                        st.rerun()
                    else:
                        st.error("Seu nome não está na lista.")

    elif st.session_state.pagina_atual == "sorteio":
        st.subheader("🔀 Sorteio de Times (Oficial & Paralelo)")
        sorteio_salvo = st.session_state.sorteio_oficial
        
        if sorteio_salvo and "times" in sorteio_salvo:
            st.write("#### 🏆 Sorteio Oficial")
            for nome_time, membros in sorteio_salvo["times"].items():
                st.markdown(f"<div class='card-team'><h3>⚽ {nome_time}</h3>", unsafe_allow_html=True)
                for item in membros:
                    st.markdown(f"• **{item}**")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Nenhum sorteio oficial gerado ainda.")

        st.markdown("#### ⚡ Sorteio Paralelo (Baseado em Presença no Local)")
        if st.button("Gerar Sorteio Paralelo Agora", use_container_width=True):
            confirmadas_nomes = [obter_nome_p(p) for p in st.session_state.presencas]
            if len(confirmadas_nomes) >= 2:
                random.shuffle(confirmadas_nomes)
                res_paralelo = {"Time A": confirmadas_nomes[::2], "Time B": confirmadas_nomes[1::2]}
                st.success("Sorteio Paralelo Gerado com Sucesso!")
                for nome_t, membros_t in res_paralelo.items():
                    st.markdown(f"<div class='card-team'><b>{nome_t}:</b> {', '.join(membros_t)}</div>", unsafe_allow_html=True)
            else:
                st.error("Atletas insuficientes para gerar o sorteio paralelo.")

    elif st.session_state.pagina_atual == "elenco":
        st.subheader("📋 Elenco de Atletas Cadastradas")
        for j in st.session_state.jogadoras:
            if j.get("status") == "Ativo":
                st.markdown(f"<div class='card-team'><b>⚽ {j['nome']}</b><br><small>Tipo: `{j.get('tipo', 'Avulso')}` | Quitado: `{j.get('quitado', 'Não')}` | Nasc: {j.get('nascimento')}</small></div>", unsafe_allow_html=True)

    elif st.session_state.pagina_atual == "pagamento":
        st.subheader("💸 Pagamentos e Chave Pix")
        v_mensal = st.session_state.avisos.get('valor_mensalidade', 50.00)
        v_avulso = st.session_state.avisos.get('valor_avulso', 15.00)
        
        st.markdown(f"""
        <div class='card-team'>
            📌 <b>Chave Pix Oficial:</b> <code>{st.session_state.avisos.get('pix', 'peladinhafc@email.com')}</code><br><br>
            📅 Vencimento: <b>{st.session_state.avisos.get('vencimento', 'Todo dia 10')}</b><br>
            💵 <b>Valores:</b> Mensalidade: <b>R$ {v_mensal:.2f}</b> | Avulsa: <b>R$ {v_avulso:.2f}</b>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.perfil_logado == "Jogadora":
            st.write("### Enviar Comprovante de Pagamento")
            with st.form("form_comprovante_envio", clear_on_submit=True):
                arquivo_submetido = st.file_uploader("Selecione a imagem do comprovante", type=["png", "jpg", "jpeg"])
                if st.form_submit_button("Enviar Comprovante"):
                    if arquivo_submetido:
                        caminho_arquivo = os.path.join(UPLOAD_DIR, f"{st.session_state.usuario_logado}_{int(datetime.now().timestamp())}.png")
                        with open(caminho_arquivo, "wb") as f:
                            f.write(arquivo_submetido.getbuffer())
                        
                        st.session_state.comprovantes.append({
                            "nome": st.session_state.usuario_logado,
                            "arquivo": caminho_arquivo,
                            "data": hoje_dt.strftime("%d/%m/%Y"),
                            "conferido": False
                        })
                        salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                        st.success("Comprovante enviado com sucesso para validação do Administrador!")
                    else:
                        st.error("Selecione um arquivo de imagem.")

        if st.session_state.perfil_logado in ["Admin", "Dev"]:
            st.write("### 👑 Conferência de Comprovantes Pendentes")
            comprovantes = st.session_state.comprovantes
            pendentes_comp = [c for c in comprovantes if not c.get("conferido", False)]
            if not pendentes_comp:
                st.info("Nenhum comprovante pendente para conferência.")
            for idx, comp in enumerate(comprovantes):
                if not comp.get("conferido", False):
                    st.markdown(f"<div class='card-team'><b>Atleta:</b> {comp['nome']} | <b>Data:</b> {comp['data']}</div>", unsafe_allow_html=True)
                    if os.path.exists(comp['arquivo']):
                        st.image(comp['arquivo'], width=300)
                    if st.button(f"Validar Pagamento de {comp['nome']}", key=f"val_comp_{idx}"):
                        comp["conferido"] = True
                        
                        j_cad = next((j for j in st.session_state.jogadoras if j["nome"] == comp["nome"]), None)
                        tipo_j_cad = j_cad.get("tipo", "Avulso") if j_cad else "Avulso"
                        
                        v_recebido = st.session_state.avisos.get('valor_mensalidade', 50.00) if tipo_j_cad == "Mensalista" else st.session_state.avisos.get('valor_avulso', 15.00)
                        
                        for j in st.session_state.jogadoras:
                            if j["nome"] == comp["nome"]:
                                j["quitado"] = "Sim"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        
                        st.session_state.financeiro.append({
                            "mes": hoje_dt.strftime("%B/%Y"), "tipo": "Receita", "descricao": f"Pagamento ({tipo_j_cad}) - {comp['nome']}", "valor": float(v_recebido)
                        })
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        salvar_dados(COMPROVANTES_FILE, comprovantes)
                        st.success("Pagamento validado e adicionado automaticamente como receita no fluxo de caixa!")
                        st.rerun()

    elif st.session_state.pagina_atual == "caixa":
        st.subheader("📊 Fluxo de Caixa Completo")
        
        with st.form("form_lanca_caixa", clear_on_submit=True):
            st.write("<b>Lançar Nova Receita ou Despesa Manualmente</b>", unsafe_allow_html=True)
            c_mes = st.text_input("Mês / Ano (Ex: Janeiro/2026)", value=hoje_dt.strftime("%B/%Y"))
            c_tipo_fin = st.selectbox("Tipo", ["Receita", "Despesa"])
            c_desc = st.text_input("Descrição (Ex: Compra de Coletes, Aluguel)")
            c_valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
            if st.form_submit_button("Adicionar Lançamento"):
                if c_desc.strip() and c_valor > 0:
                    st.session_state.financeiro.append({
                        "mes": c_mes.strip(), "tipo": c_tipo_fin, "descricao": c_desc.strip(), "valor": float(c_valor)
                    })
                    salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                    st.success("Lançamento adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("Preencha a descrição e informe um valor válido.")

        st.markdown("---")
        
        registros_caixa = st.session_state.financeiro
        if not registros_caixa:
            st.info("Nenhum registro financeiro encontrado.")
        else:
            total_geral_rec = sum(item["valor"] for item in registros_caixa if item["tipo"] == "Receita")
            total_geral_desp = sum(item["valor"] for item in registros_caixa if item["tipo"] == "Despesa")
            saldo_total = total_geral_rec - total_geral_desp

            st.markdown(f"""
            <div class='card-team'>
                <h3>💰 Saldo Total em Caixa: R$ {saldo_total:.2f}</h3>
                <p>🟢 Total de Receitas: R$ {total_geral_rec:.2f} | 🔴 Total de Despesas: R$ {total_geral_desp:.2f}</p>
            </div>
            """, unsafe_allow_html=True)

            st.write("### Histórico de Movimentações & Exclusão")
            for idx, item in enumerate(registros_caixa):
                col_c1, col_c2 = st.columns([4, 1])
                with col_c1:
                    st.markdown(f"""
                    <div class='card-team' style='margin-bottom: 5px;'>
                        <b>Mês:</b> {item.get('mes', 'Geral')} | <b>Tipo:</b> <code>{item['tipo']}</code> | <b>Descrição:</b> {item['descricao']} | <b>Valor:</b> R$ {item['valor']:.2f}
                    </div>
                    """, unsafe_allow_html=True)
                with col_c2:
                    if st.button("🗑️ Excluir", key=f"del_fin_{idx}"):
                        st.session_state.financeiro.pop(idx)
                        salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                        st.success("Lançamento excluído com sucesso!")
                        st.rerun()

    elif st.session_state.pagina_atual == "gerenciamento":
        st.subheader("🛠️ Painel de Gerenciamento Geral & Aprovações")
        
        tab_ger1, tab_ger2, tab_ger3 = st.tabs(["📝 Aprovar Cadastros", "⚙️ Configurações Gerais", "🔒 Gestão de Contas (Dev)"])

        with tab_ger1:
            st.write("### Aprovação de Novas Atletas")
            pendentes = [j for j in st.session_state.jogadoras if j.get("status") == "Pendente"]
            if not pendentes:
                st.info("Nenhum cadastro pendente no momento.")
            for idx, j in enumerate(pendentes):
                col_p1, col_p2, col_p3 = st.columns([2, 1, 1])
                with col_p1:
                    st.write(f"**{j['nome']}** (`{j.get('tipo', 'Avulso')}`) - Nasc: {j.get('nascimento')}")
                with col_p2:
                    if st.button("✅ Aprovar", key=f"aprov_{idx}"):
                        j["status"] = "Ativo"
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.success(f"✔️ Confirmação: A atleta {j['nome']} foi aprovada e ativada com sucesso!")
                        st.rerun()
                with col_p3:
                    if st.button("❌ Recusar", key=f"rec_{idx}"):
                        st.session_state.jogadoras.remove(j)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.warning(f"⚠️ O cadastro de {j['nome']} foi recusado/removido.")
                        st.rerun()

        with tab_ger2:
            with st.form("form_cfg_geral_painel"):
                st.write("<b>Configurações Gerais e Valores</b>", unsafe_allow_html=True)
                limite_v = st.number_input("Limite de Vagas", value=int(st.session_state.avisos.get("limite_vagas", 15)))
                pix_val = st.text_input("Chave Pix", value=st.session_state.avisos.get("pix", ""))
                venc_val = st.text_input("Dia/Regra de Vencimento", value=st.session_state.avisos.get("vencimento", "Todo dia 10"))
                val_mensal = st.number_input("Valor da Mensalidade (R$)", min_value=0.0, step=5.0, value=float(st.session_state.avisos.get("valor_mensalidade", 50.00)))
                val_avulso = st.number_input("Valor da Diária Avulsa (R$)", min_value=0.0, step=5.0, value=float(st.session_state.avisos.get("valor_avulso", 15.00)))
                
                if st.form_submit_button("Salvar Ajustes"):
                    st.session_state.avisos["limite_vagas"] = limite_v
                    st.session_state.avisos["pix"] = pix_val
                    st.session_state.avisos["vencimento"] = venc_val
                    st.session_state.avisos["valor_mensalidade"] = val_mensal
                    st.session_state.avisos["valor_avulso"] = val_avulso
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações e valores atualizados com sucesso!")

        with tab_ger3:
            if st.session_state.perfil_logado == "Dev":
                st.write("### 🔒 Gestão Completa de Contas e Credenciais (Dev)")
                st.info("Aqui você pode cadastrar o número do celular dos administradores, redefinir senhas e gerenciar contas.")

                sub_tab_adm, sub_tab_jog = st.tabs(["👑 Administradores", "⚽ Atletas / Jogadoras"])

                with sub_tab_adm:
                    st.write("#### Gerenciar Contas de Administradores & Celular WhatsApp")
                    for idx, adm in enumerate(st.session_state.administradores):
                        st.markdown(f"""
                        <div class='card-team'>
                            <b>Nome:</b> {adm['nome']} | <b>Login:</b> <code>{adm['login']}</code> | <b>Celular:</b> <code>{adm.get('celular', 'Não cadastrado')}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.form(f"form_alt_adm_{idx}"):
                            nova_cel_adm = st.text_input("Atualizar número do Celular/WhatsApp (Ex: 5531999999999)", value=adm.get("celular", ""), key=f"cel_adm_{idx}")
                            nova_s_adm = st.text_input("Redefinir nova senha (opcional)", type="password", key=f"nova_s_adm_{idx}")
                            if st.form_submit_button("Salvar Dados do Admin"):
                                adm["celular"] = nova_cel_adm.strip()
                                if nova_s_adm.strip():
                                    adm["senha"] = nova_s_adm.strip()
                                salvar_dados(ADMINS_FILE, st.session_state.administradores)
                                st.success(f"Dados do admin {adm['nome']} atualizados com sucesso!")
                                st.rerun()

                        if st.button(f"Excluir Admin {adm['nome']}", key=f"del_adm_{idx}"):
                            if len(st.session_state.administradores) > 1:
                                st.session_state.administradores.pop(idx)
                                salvar_dados(ADMINS_FILE, st.session_state.administradores)
                                st.success("Administrador removido!")
                                st.rerun()
                            else:
                                st.error("Você não pode excluir o único administrador do sistema.")

                with sub_tab_jog:
                    st.write("#### Gerenciar Contas de Atletas / Jogadoras")
                    if not st.session_state.jogadoras:
                        st.info("Nenhuma atleta cadastrada.")
                    for idx_j, jog in enumerate(st.session_state.jogadoras):
                        st.markdown(f"""
                        <div class='card-team'>
                            <b>Atleta:</b> {jog['nome']} | <b>Login:</b> <code>{jog.get('login', 'N/D')}</code><br>
                            <small>Status: `{jog.get('status')}` | Tipo: `{jog.get('tipo')}`</small>
                        </div>
                        """, unsafe_allow_html=True)

                        with st.form(f"form_alt_senha_jog_{idx_j}"):
                            nova_s_jog = st.text_input("Redefinir nova senha para esta atleta", type="password", key=f"nova_s_jog_{idx_j}")
                            if st.form_submit_button("Atualizar Senha da Atleta"):
                                if nova_s_jog.strip():
                                    jog["senha"] = nova_s_jog.strip()
                                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                                    st.success(f"Senha da atleta {jog['nome']} alterada com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Digite uma nova senha válida.")

                        if st.button(f"Excluir Conta de {jog['nome']}", key=f"del_jog_{idx_j}"):
                            st.session_state.jogadoras.pop(idx_j)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            st.warning(f"A atleta {jog['nome']} foi removida do sistema.")
                            st.rerun()
            else:
                st.warning("⚠️ Esta área é restrita apenas ao perfil de Desenvolvedor.")
