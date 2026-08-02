# -----------------------------------------------------------------------------
# PÁGINA 1: PRESENÇA NO JOGO
# -----------------------------------------------------------------------------
if pagina == "📌 Presença no Jogo":
    col_esq, col_dir = st.columns([1.2, 1])

    with col_esq:
        st.subheader("📋 Status da Lista de Presença")
        
        if passou_das_1830_segunda:
            st.success("🎲 **Sorteio das 18:30 REALIZADO!** Acesse a aba 'Sorteio de Times'.")
        elif passou_das_17_segunda:
            st.info("🟢 **Vagas de Avulsas Liberadas (17:00)!**")
        else:
            st.warning("⏳ **Aguardando Segunda-feira 17:00:** Avulsas na Fila de Espera.")

        st.markdown(f"### ⭐ Lista Principal com Vaga Garantida ({len(jogadoras_confirmadas_jogo)}/12)")
        
        # MENSALISTAS
        if mensalistas_confirmadas:
            for idx, p in enumerate(mensalistas_confirmadas, start=1):
                st.write(f"**{idx}. {p['nome']}** [Mensalista] — *(às {p.get('hora', '')})* ✅")
        
        # AVULSAS PROMOVIDAS
        if avulsas_com_vaga:
            offset = len(mensalistas_confirmadas) + 1
            for idx, p in enumerate(avulsas_com_vaga, start=offset):
                st.write(f"**{idx}. {p['nome']}** [⚽ Avulsa Promovida] — *(às {p.get('hora', '')})* 🟢")

        if not jogadoras_confirmadas_jogo:
            st.caption("Nenhuma jogadora confirmada na lista principal ainda.")

        st.markdown("---")

        st.markdown(f"### ⏳ Fila de Espera ({len(avulsas_na_fila)})")
        if avulsas_na_fila:
            for idx, p in enumerate(avulsas_na_fila, start=1):
                st.write(f"**{idx}. {p['nome']}** [Avulsa] — *(às {p.get('hora', '')})* 🟡")
        else:
            st.caption("Fila de espera vazia.")

    with col_dir:
        st.subheader("✍️ Marcar / Cancelar Presença")
        with st.container(border=True):
            if not st.session_state.usuario_logado and not st.session_state.e_admin:
                st.warning("🔒 **Acesso Negado!** Faça login no menu lateral para acessar.")
            
            # -----------------------------------------------------------------
            # PAINEL EXCLUSIVO DO ADMIN (AUTONOMIA TOTAL)
            # -----------------------------------------------------------------
            elif st.session_state.e_admin:
                st.info("👑 **Modo Administrador:** Gestão Direta de Presenças")
                
                # Lista de jogadoras cadastradas no elenco
                nomes_elenco = [j["nome"] for j in st.session_state.jogadoras]
                
                # Opção de escolha
                st.markdown("#### 1. Selecionar do Elenco Cadastrado")
                nome_admin_sel = st.selectbox("Escolha a jogadora:", nomes_elenco, key="select_admin_jogadora")
                
                col_adm1, col_adm2 = st.columns(2)
                
                with col_adm1:
                    if st.button("👍 Confirmar Selecionada", use_container_width=True):
                        user_obj = next((j for j in st.session_state.jogadoras if j["nome"] == nome_admin_sel), None)
                        tipo_e = "Avulsa" if user_obj and user_obj['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                        
                        nomes_atuais = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        if nome_admin_sel.strip().lower() in nomes_atuais:
                            st.warning(f"**{nome_admin_sel}** já está na lista!")
                        else:
                            st.session_state.presencas.append({
                                "nome": nome_admin_sel,
                                "tipo": tipo_e,
                                "hora": datetime.now().strftime("%H:%M")
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.success(f"✅ {nome_admin_sel} confirmada com sucesso!")
                            st.rerun()

                with col_adm2:
                    if st.button("❌ Remover Selecionada", use_container_width=True):
                        st.session_state.presencas = [
                            p for p in st.session_state.presencas 
                            if p["nome"].strip().lower() != nome_admin_sel.strip().lower()
                        ]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        if "times_sorteados" in st.session_state:
                            del st.session_state["times_sorteados"]
                        st.info(f"🗑️ {nome_admin_sel} removida da lista.")
                        st.rerun()

                st.markdown("---")
                
                # Opção de inclusão de nome avulso / convidada extra
                st.markdown("#### 2. Confirmar Convidada Extra (Fora do Elenco)")
                nome_extra = st.text_input("Nome da Convidada:", key="input_nome_extra")
                tipo_extra = st.radio("Tipo:", ["Avulsa", "Mensalista"], horizontal=True, key="radio_tipo_extra")
                
                if st.button("➕ Adicionar Convidada Manualmente", use_container_width=True):
                    if not nome_extra.strip():
                        st.error("Digite o nome da jogadora antes de adicionar!")
                    else:
                        nomes_atuais = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        if nome_extra.strip().lower() in nomes_atuais:
                            st.warning(f"**{nome_extra}** já está na lista!")
                        else:
                            st.session_state.presencas.append({
                                "nome": nome_extra.strip(),
                                "tipo": tipo_extra,
                                "hora": datetime.now().strftime("%H:%M")
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.success(f"✅ {nome_extra} adicionada com sucesso!")
                            st.rerun()

            # -----------------------------------------------------------------
            # PAINEL DA JOGADORA (SÓ AFETA A PRÓPRIA CONTA)
            # -----------------------------------------------------------------
            else:
                user = st.session_state.usuario_logado
                st.success(f"Conectada como: **{user['nome']}** ({user['tipo']})")

                cb1, cb2 = st.columns(2)
                with cb1:
                    if st.button("👍 Confirmar Minha Presença", use_container_width=True):
                        tipo_e = "Avulsa" if user['tipo'].lower() in ["avulsa", "diarista"] else "Mensalista"
                        nomes_atuais = [p["nome"].strip().lower() for p in st.session_state.presencas]
                        
                        if user["nome"].strip().lower() in nomes_atuais:
                            st.warning("Seu nome já está na lista!")
                        else:
                            st.session_state.presencas.append({
                                "nome": user["nome"],
                                "tipo": tipo_e,
                                "hora": datetime.now().strftime("%H:%M")
                            })
                            salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                            if "times_sorteados" in st.session_state:
                                del st.session_state["times_sorteados"]
                            st.rerun()

                with cb2:
                    if st.button("❌ Cancelar Minha Presença", use_container_width=True):
                        nome_alvo = user["nome"].strip().lower()
                        st.session_state.presencas = [
                            p for p in st.session_state.presencas 
                            if p["nome"].strip().lower() != nome_alvo
                        ]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        if "times_sorteados" in st.session_state:
                            del st.session_state["times_sorteados"]
                        st.rerun()
