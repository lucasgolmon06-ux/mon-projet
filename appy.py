import streamlit as st
import requests
import json
import os

# --- CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "commentaires_sauvegardes.json"

# --- SAUVEGARDE ---
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comms, f, indent=4)

if 'comments' not in st.session_state:
    st.session_state.comments = charger_comms()

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .msg-admin { background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; font-size: 0.9em; }
    
    /* Style pour le bouton en haut à droite */
    .comm-button-container {
        display: flex;
        justify-content: flex-end;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER AVEC BOUTON EN HAUT À DROITE ---
header_col1, header_col2 = st.columns([3, 1])

with header_col1:
    st.title("GameTrend Pro")

with header_col2:
    # C'est ici que se trouve ton bouton pour ouvrir l'espace
    ouvrir_comm = st.toggle("💬 Espace Communauté")

# --- L'ESPACE COMMUNAUTÉ (S'affiche seulement si activé) ---
if ouvrir_comm:
    st.markdown("### 👥 Discussion")
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        st.write("**Poster un avis**")
        with st.form("form_avis", clear_on_submit=True):
            pseudo = st.text_input("Pseudo")
            message = st.text_area("Message")
            if st.form_submit_button("Envoyer"):
                if pseudo and message:
                    st.session_state.comments.append({"user": pseudo, "msg": message, "reply": None})
                    sauver_comms(st.session_state.comments)
                    st.rerun()
        
        st.divider()
        code_admin = st.text_input("🔑 Code Admin (pour répondre)", type="password")
        is_admin = (code_admin == "1234") # Code par défaut : 1234

    with col_c2:
        st.write("**Messages récents**")
        for i, c in enumerate(reversed(st.session_state.comments)):
            real_idx = len(st.session_state.comments) - 1 - i
            st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> : {c["msg"]}</div>', unsafe_allow_html=True)
            
            if c['reply']:
                st.markdown(f'<div class="msg-admin"><b>Auteur</b> : {c["reply"]}</div>', unsafe_allow_html=True)
            elif is_admin:
                rep_text = st.text_input(f"Répondre à {c['user']}", key=f"ans_{real_idx}")
                if st.button("Répondre", key=f"btn_{real_idx}"):
                    st.session_state.comments[real_idx]['reply'] = rep_text
                    sauver_comms(st.session_state.comments)
                    st.rerun()
    st.divider()

# --- RESTE DU SITE (CONSEILLER ET TOP 12) ---
# Ton champ de recherche de style
style_in = st.text_input("💡 Propose-moi des jeux dans le style de...")
# ... (Code IGDB habituel pour afficher les jeux)
