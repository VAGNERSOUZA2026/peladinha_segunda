# -----------------------------------------------------------------------------
# AUTOMAÇÃO DE HORÁRIOS (Promover Avulsas às 17:00)
# -----------------------------------------------------------------------------
def processar_promocao_avulsas():
    hoje_agora = datetime.now(FUSO_BRASIL)
    
    # Se já passou das 17:00
    if hoje_agora.hour >= 17:
        limite = st.session_state.avisos.get("limite_vagas", 15)
        lista = st.session_state.presencas
        
        # Separa mensalistas e avulsas
        mensalistas = [p for p in lista if obter_tipo_p(p) == "Mensalista"]
        avulsas = [p for p in lista if obter_tipo_p(p) == "Avulso"]
        
        vagas_restantes = limite - len(mensalistas)
        
        # Se restam vagas e há avulsas na fila de espera
        if vagas_restantes > 0 and len(avulsas) > 0:
            # Pega as avulsas necessárias para completar o limite
            avulsas_promovidas = avulsas[:vagas_restantes]
            avulsas_restantes = avulsas[vagas_restantes:]
            
            # Reorganiza a lista: Mensalistas + Avulsas Promovidas + Avulsas que sobraram na espera
            nova_lista = mensalistas + avulsas_promovidas + avulsas_restantes
            
            # Salva se houver alteração
            if nova_lista != st.session_state.presencas:
                st.session_state.presencas = nova_lista
                salvar_dados(PRESENCAS_FILE, nova_lista)
