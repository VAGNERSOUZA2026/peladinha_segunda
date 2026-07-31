# -----------------------------------------------------------------------------
# PÁGINA 5: REGULAMENTO DO GRUPO
# -----------------------------------------------------------------------------
elif menu == "📜 Regulamento":
    st.subheader("📜 Regulamento Oficial & Estatuto do Peladinha FC")
    
    st.markdown("""
    <div style='background-color: #F8FAFC; border-left: 6px solid #0284C7; padding: 15px; border-radius: 8px; margin-bottom: 25px;'>
        📌 <b>Objetivo do Grupo:</b> Promover a prática do futebol feminino com espírito esportivo, integração, respeito mútuo e organização. Todas as participantes concordam com as regras descritas abaixo ao ingressarem na pelada.
    </div>
    """, unsafe_allow_html=True)

    tab_r1, tab_r2, tab_r3, tab_r4 = st.tabs([
        "🤝 Conduta & Convivência", 
        "⏰ Presença & Fila de Espera", 
        "💸 Mensalidade & Avulsas", 
        "⚽ Regras de Jogo & Fair Play"
    ])

    with tab_r1:
        st.markdown("""
        ### 🤝 1. Respeito e Boa Convivência
        * **Respeito Mútuo:** Não serão toleradas ofensas verbais, discussões acaloradas, xingamentos ou agressões físicas entre jogadoras ou com a organização.
        * **Inclusão:** O grupo apoia jogadoras de todos os níveis técnicos. Incentive e ajude suas companheiras de time.
        * **Comunicação no Grupo:** O grupo de WhatsApp é voltado exclusivamente para assuntos da pelada (confirmações, avisos, pagamentos e resenha saudável).
        * **Penalidades:** Atitudes antidesportivas sujeitarão a jogadora a advertência ou remoção definitiva do grupo, a critério da administração.
        """)

    with tab_r2:
        st.markdown("""
        ### ⏰ 2. Horários, Confirmação e Lista de Espera
        * **Pontualidade:** Chegar com pelo menos **10 minutos de antecedência** ao local para organização do material e início pontual.
        * **Confirmação de Presença:** A lista de presença é aberta no aplicativo/grupo semanalmente. As vagas principais são preenchidas por ordem de confirmação.
        * **Desistências e Cancelamento:** 
          * Caso não possa comparecer, **cancele sua presença no aplicativo com antecedência mínima de 4 horas**.
          * Cancelamentos em cima da hora prejudicam o fechamento dos times e podem gerar cobrança da taxa avulsa caso a vaga não seja preenchida.
        * **Fila de Espera:** Quando o limite de vagas for atingido, novas confirmações entram automaticamente na fila de espera. Havendo desistência, a primeira da fila é promovida para a lista principal.
        """)

    with tab_r3:
        st.markdown("""
        ### 💸 3. Pagamentos e Taxas
        * **Mensalistas:**
          * O pagamento da mensalidade deve ser efetuado até a **data de vencimento estipulada no painel (dia 10 de cada mês)**.
          * O não pagamento até o prazo sujeita a perda da prioridade de vaga no mês seguinte.
        * **Jogadoras Avulsas:**
          * O valor avulso deve ser quitado **via Pix antes do início da partida** ou enviado no grupo/app como comprovante.
        * **Uso da Arrecadação:** Todos os valores arrecadados são destinados exclusivamente ao aluguel da quadra/campo, aquisição e manutenção de materiais (bolas, coletes, apitos) e eventos do grupo. A prestação de contas fica disponível na aba *Fluxo de Caixa*.
        """)

    with tab_r4:
        st.markdown("""
        ### ⚽ 4. Regras de Jogo & Segurança
        * **Calçado e Equipamentos:** É obrigatório o uso de calçado adequado para a modalidade da quadra/campo (society/futsal). Recomendado o uso de caneleiras.
        * **Jogo Limpo (Fair Play):**
          * **Entradas Violentas:** Proibido carrinho ou divididas com força excessiva/risco de lesão.
          * **Auto-arbitragem:** Prevalece a honestidade! Se a bola saiu ou houve falta, a própria jogadora deve admitir e paralisar a jogada.
        * **Rodízio e Substituições:**
          * Todos os times jogam o mesmo tempo estipulado pela organização.
          * Caso o time possua jogadoras reservas, o rodízio de substituições deve ser feito de forma igualitária para que todas joguem o mesmo tempo.
        """)
