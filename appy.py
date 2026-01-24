# --- PAGE FORUM ---
elif st.session_state.page == "Forum":
    # Header avec bouton retour et bouton admin discret
    head_col1, head_col2 = st.columns([5, 1])
    with head_col1:
        st.header("💬 Forum Communauté")
        if st.button("⬅️ Retour Accueil"): st.session_state.page = "Accueil"; st.rerun()
    
    with head_col2:
        # Petit bouton discret pour activer les droits
        if st.button("🛠️ Admin"):
            st.session_state.show_admin_login = not st.session_state.get('show_admin_login', False)
        
    # Zone de connexion Admin (s'affiche seulement si on a cliqué sur le bouton)
    c_est_moi = False
    if st.session_state.get('show_admin_login'):
        admin_code = st.text_input("Code secret :", type="password", key="admin_pwd")
        if admin_code == "628316":
            st.success("Mode Maître activé 🛡️")
            c_est_moi = True
        elif admin_code != "":
            st.error("Code incorrect")

    st.divider()
    
    # Système de Chat habituel
    if not st.session_state.user_pseudo:
        p = st.text_input("Choisis ton pseudo :")
        if st.button("Entrer dans la discussion"): 
            st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat_global", clear_on_submit=True):
            m = st.text_input(f"Message ({st.session_state.user_pseudo}) :")
            if st.form_submit_button("Publier"):
                if m:
                    st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        
        # Affichage des messages
        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            
            # Design du message
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            
            # Affichage de la réponse si elle existe
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN 🛡️</span> {c['reply']}</div>", unsafe_allow_html=True)
            
            # Si tu es connecté en tant qu'admin, le bouton "Répondre" apparaît sous chaque message sans réponse
            if c_est_moi and not c.get('reply'):
                with st.expander(f"Répondre à {c['user']}"):
                    r_txt = st.text_area("Ta réponse :", key=f"area_{idx}")
                    if st.button("Envoyer la réponse officielle", key=f"btn_admin_{idx}"):
                        st.session_state.comments[idx]['reply'] = r_txt
                        sauver_data(DB_FILE, st.session_state.comments)
                        st.rerun()
