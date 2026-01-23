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
    .msg-user { background: #001a3d; padding: 15px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .msg-admin { background: #002b5c; padding: 15px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 40px; margin-top: 5px; color: #ffcc00; }
    .titre-com { font-size: 24px; font-weight: bold; color: #0072ce; border-bottom: 2px solid #0072ce; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("GameTrend Pro")

# --- NOUVEL ONGLET COMMENTAIRES (BIEN VISIBLE) ---
st.markdown('<div class="titre-com">💬 Espace Communauté</div>', unsafe_allow_html=True)

col_com1, col_com2 = st.columns([1, 2])

with col_com1:
    st.subheader("Poste ton avis")
    with st.form("publier_avis", clear_on_submit=True):
        pseudo = st.text_input("Pseudo")
        message = st.text_area("Message")
        if st.form_submit_button("Envoyer"):
            if pseudo and message:
                st.session_state.comments.append({"user": pseudo, "msg": message, "reply": None})
                sauver_comms(st.session_state.comments)
                st.rerun()
    
    st.divider()
    # Zone Admin pour toi
    code_admin = st.text_input("Code auteur (pour répondre)", type="password")
    is_admin = (code_admin == "1234") # TON CODE ICI

with col_com2:
    st.subheader("Derniers messages")
    if not st.session_state.comments:
        st.write("Aucun commentaire pour le moment.")
    
    # On affiche les messages du plus récent au plus ancien
    for i, c in enumerate(reversed(st.session_state.comments)):
        real_idx = len(st.session_state.comments) - 1 - i
        
        st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> :<br>{c["msg"]}</div>', unsafe_allow_html=True)
        
        if c['reply']:
            st.markdown(f'<div class="msg-admin"><b>Réponse de l\'auteur</b> :<br>{c["reply"]}</div>', unsafe_allow_html=True)
        elif is_admin:
            # Champ de réponse direct sur le site
            rep_text = st.text_input(f"Répondre à {c['user']}", key=f"ans_{real_idx}")
            if st.button("Publier la réponse", key=f"btn_{real_idx}"):
                st.session_state.comments[real_idx]['reply'] = rep_text
                sauver_comms(st.session_state.comments)
                st.rerun()

st.divider()

# --- LE RESTE DU SITE (CONSEILLER ET TOP 12) ---
# ... (Tes requêtes IGDB et l'affichage des consoles ici)
