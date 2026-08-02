tabs_objetos = st.tabs(tabs_titulos)
        idx_tab = 0

        # TAB 1: LABORATÓRIO DE TESTES (DEV)
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
                            st.success(f"Comprovante de teste gerado para {j_teste}!")
                            st.rerun()
            idx_tab += 1

        # TAB 2: APROVAR COMPROVANTES
        with tabs_objetos[idx_tab]:
            st.markdown("### 💳 Análise de Comprovantes Recebidos")
            pendentes = [c for c in st.session_state.comprovantes if c.get("status") == "Em Análise"]

            if not pendentes:
                st.info("Nenhum comprovante pendente de análise no momento.")
            else:
                for comp in pendentes:
                    with st.expander(f"📄 Comprovante de {comp['jogadora']} — R$ {comp['valor']:.2f} ({comp['data_envio']} às {comp['hora_envio']})"):
                        if "imagem_b64" in comp:
                            st.image(base64.b64decode(comp["imagem_b64"]), caption=f"Comprovante {comp['id']}", width=350)
                        
                        col_ap1, col_ap2 = st.columns(2)
                        if col_ap1.button(f"✅ Aprovar Pagamento ({comp['id']})", use_container_width=True):
                            comp["status"] = "Aprovado"
                            for j in st.session_state.jogadoras:
                                if j["nome"] == comp["jogadora"]:
                                    j["status_pagamento"] = "Pago"
                            
                            st.session_state.financeiro.append({
                                "data": hoje_str,
                                "tipo": "Entrada (Receita)",
                                "descricao": f"Mensalidade/Pix: {comp['jogadora']}",
                                "valor": comp['valor']
                            })
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            salvar_dados(DATA_FILE, st.session_state.jogadoras)
                            salvar_dados(FINANCE_FILE, st.session_state.financeiro)
                            st.success(f"Pagamento de {comp['jogadora']} APROVADO!")
                            st.rerun()

                        if col_ap2.button(f"❌ Recusar Comprovante ({comp['id']})", use_container_width=True):
                            comp["status"] = "Recusado"
                            salvar_dados(COMPROVANTES_FILE, st.session_state.comprovantes)
                            st.error(f"Comprovante de {comp['jogadora']} RECUSADO!")
                            st.rerun()
        idx_tab += 1

        # TAB 3: CONTRATO DE SERVIÇO
        with tabs_objetos[idx_tab]:
            st.markdown("### 📜 Gerador de Contrato de Licenciamento")
            st.caption("Gere o termo de aceite em HTML para formalização do serviço.")
            with st.form("form_contrato"):
                c_nome = st.text_input("Nome da Responsável / Clube:", value="Peladinha FC")
                c_doc = st.text_input("CPF ou CNPJ:")
                c_whats = st.text_input("WhatsApp de Contato:")
                c_cidade = st.text_input("Cidade/UF:", value="Contagem/MG")
                c_valor = st.number_input("Valor Mensal do App (R$):", value=50.0, step=10.0)
                c_ass = st.text_input("Assinatura Digital (Nome Completo):")
                btn_doc = st.form_submit_button("📄 Gerar Documento do Contrato")

                if btn_doc and c_nome and c_ass:
                    html_bytes = gerar_documento_contrato(c_nome, c_doc, c_whats, c_cidade, c_valor, hoje_str, c_ass)
                    st.download_button(
                        label="⬇️ Baixar Contrato em HTML",
                        data=html_bytes,
                        file_name=f"Contrato_PeladinhaFC_{c_nome.replace(' ', '_')}.html",
                        mime="text/html"
                    )
        idx_tab += 1

        # TAB 4: CONFIGURAÇÕES GERAIS
        with tabs_objetos[idx_tab]:
            st.markdown("### ⚙️ Ajustes do App e Avisos")
            with st.form("form_cfg_avisos"):
                n_pix = st.text_input("Chave Pix:", value=st.session_state.avisos.get("pix", ""))
                n_venc = st.text_input("Vencimento:", value=st.session_state.avisos.get("vencimento", ""))
                n_recado = st.text_area("Recado no Mural:", value=st.session_state.avisos.get("recado", ""))
                n_vagas = st.number_input("Limite Máximo de Vagas por Jogo:", value=st.session_state.avisos.get("limite_vagas", 15), min_value=4, max_value=30)
                btn_salvar_cfg = st.form_submit_button("💾 Salvar Configurações")

                if btn_salvar_cfg:
                    st.session_state.avisos["pix"] = n_pix
                    st.session_state.avisos["vencimento"] = n_venc
                    st.session_state.avisos["recado"] = n_recado
                    st.session_state.avisos["limite_vagas"] = n_vagas
                    salvar_dados(AVISOS_FILE, st.session_state.avisos)
                    st.success("Configurações atualizadas!")
                    st.rerun()

            st.markdown("---")
            st.markdown("### 🗑️ Limpeza de Presenças")
            if st.button("🗑️ Zerar Lista de Presenças do Jogo"):
                st.session_state.presencas = []
                salvar_dados(PRESENCAS_FILE, [])
                st.success("Lista de presença zerada com sucesso!")
                st.rerun()
        idx_tab += 1

        # TAB 5: CADASTRAR JOGADORA
        with tabs_objetos[idx_tab]:
            st.markdown("### ➕ Cadastrar Nova Jogadora (Admin)")
            with st.form("form_cad_adm", clear_on_submit=True):
                adm_nome = st.text_input("Nome Completo *")
                adm_nasc = st.text_input("Nascimento (DD/MM)")
                adm_tipo = st.selectbox("Categoria", ["Mensalista", "Avulso"])
                adm_user = st.text_input("Login do App *")
                adm_pass = st.text_input("Senha Inicial *", value="1234")
                btn_cad_adm = st.form_submit_button("➕ Cadastrar no Elenco")

                if btn_cad_adm and adm_nome and adm_user:
                    nome_f = formatar_nome_proprio(adm_nome)
                    st.session_state.jogadoras.append({
                        "nome": nome_f,
                        "nascimento": adm_nasc.strip(),
                        "login": adm_user.strip(),
                        "senha": adm_pass.strip(),
                        "tipo": adm_tipo,
                        "mes_vigente": mes_vigente_str,
                        "contato": "",
                        "status": "Ativo",
                        "status_pagamento": "Pendente"
                    })
                    salvar_dados(DATA_FILE, st.session_state.jogadoras)
                    st.success(f"Jogadora **{nome_f}** cadastrada com sucesso!")
                    st.rerun()
        idx_tab += 1

        # TAB 6: GERENCIAR ELENCO
        with tabs_objetos[idx_tab]:
            st.markdown("### 📋 Gerenciamento do Elenco Cadastrado")
            if not st.session_state.jogadoras:
                st.info("Nenhuma jogadora cadastrada no momento.")
            else:
                for idx_j, jog in enumerate(st.session_state.jogadoras):
                    col_j1, col_j2, col_j3, col_j4 = st.columns([2, 1.2, 1.2, 1])
                    col_j1.write(f"**{jog['nome']}** (`{jog.get('login', 'sem login')}`)")
                    
                    novo_tipo = col_j2.selectbox("Tipo", ["Mensalista", "Avulso"], index=0 if jog.get("tipo") == "Mensalista" else 1, key=f"tp_{idx_j}")
                    novo_pag = col_j3.selectbox("Pagamento", ["Pendente", "Pago"], index=0 if jog.get("status_pagamento") == "Pendente" else 1, key=f"pag_{idx_j}")
                    
                    if col_j4.button("🗑️ Excluir", key=f"del_{idx_j}"):
                        st.session_state.jogadoras.pop(idx_j)
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.rerun()

                    if novo_tipo != jog.get("tipo") or novo_pag != jog.get("status_pagamento"):
                        jog["tipo"] = novo_tipo
                        jog["status_pagamento"] = novo_pag
                        salvar_dados(DATA_FILE, st.session_state.jogadoras)
                        st.rerun()

# -----------------------------------------------------------------------------
# RODAPÉ DO DESENVOLVEDOR
# -----------------------------------------------------------------------------
st.markdown("""
<div class='developer-footer'>
    Desenvolvido com ❤️ por <b>Vagner Souza</b> | Ciência da Computação<br>
    <i>Sistema Inteligente de Gestão de Pelada Feminina</i>
</div>
""", unsafe_allow_html=True)
