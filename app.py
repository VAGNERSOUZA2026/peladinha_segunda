with col_B:
        st.write("### 📋 Status da Lista")
        
        # Ordena todas as confirmações pela ordem de chegada (cronológica)
        lista_ordenada = sorted(st.session_state.presencas, key=lambda x: x.get("dt_confirmacao", x.get("hora", "")))
        
        mensalistas_confirmadas = []
        avulsas_confirmadas = []
        
        for p in lista_ordenada:
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            
            # Validação rigorosa do prazo limite (Segunda-feira até às 17:30)
            atrasada = False
            dt_conf_str = p.get("dt_confirmacao", "")
            if dt_conf_str:
                try:
                    dt_obj = datetime.fromisoformat(dt_conf_str)
                    # Se confirmou na segunda-feira (weekday == 0) após as 17h30
                    if dt_obj.weekday() == 0 and (dt_obj.hour > 17 or (dt_obj.hour == 17 and dt_obj.minute > 30)):
                        atrasada = True
                    # Se confirmou em qualquer outro dia após segunda-feira
                    elif dt_obj.weekday() > 0:
                        atrasada = True
                except:
                    pass

            # Mensalista no prazo fica na lista principal; Avulsa ou mensalista atrasada vai para o grupo de avulsas/espera
            if tipo == "Mensalista" and not atrasada:
                mensalistas_confirmadas.append(p)
            else:
                avulsas_confirmadas.append(p)

        # Junta as mensalistas no prazo primeiro, seguidas pelas avulsas/atrasadas na ordem de chegada
        combinada = mensalistas_confirmadas + avulsas_confirmadas
        principal = combinada[:limite]
        espera = combinada[limite:]

        st.write(f"**🟢 Lista Principal ({len(principal)}/{limite})**")
        for idx, p in enumerate(principal, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            hora_conf = p.get("hora", "")
            
            if st.session_state.cargo_logado in ["Administrador", "Desenvolvedor"]:
                col_p_nome, col_p_del = st.columns([4, 1])
                with col_p_nome:
                    st.markdown(f"<b>{idx}.</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i>", unsafe_allow_html=True)
                with col_p_del:
                    if st.button("❌", key=f"del_prin_{p['nome']}"):
                        st.session_state.presencas = [item for item in st.session_state.presencas if item["nome"] != p["nome"]]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                st.markdown(f"<div class='card-team'><b>{idx}.</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i></div>", unsafe_allow_html=True)

        st.write(f"**⏳ Fila de Espera ({len(espera)})**")
        for idx, p in enumerate(espera, 1):
            j_info = next((j for j in st.session_state.jogadoras if j["nome"] == p["nome"]), None)
            tipo = j_info.get("tipo", "Avulsa") if j_info else "Avulsa"
            hora_conf = p.get("hora", "")
            
            if st.session_state.cargo_logado in ["Administrador", "Desenvolvedor"]:
                col_e_nome, col_e_del = st.columns([4, 1])
                with col_e_nome:
                    st.markdown(f"<b>{idx}º esp:</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i>", unsafe_allow_html=True)
                with col_e_del:
                    if st.button("❌", key=f"del_esp_{p['nome']}"):
                        st.session_state.presencas = [item for item in st.session_state.presencas if item["nome"] != p["nome"]]
                        salvar_dados(PRESENCAS_FILE, st.session_state.presencas)
                        st.rerun()
            else:
                st.markdown(f"<div class='card-team'><b>{idx}º espera:</b> {p['nome']} `[{tipo}]` — <i>Conf: {hora_conf}</i></div>", unsafe_allow_html=True)
