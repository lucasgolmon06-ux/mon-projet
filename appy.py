import streamlit as st
import requests
import json
import os

# --- CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "commentaires_sauvegardés.json"

# --- SYSTÈME DE SAUVEGARDE ---
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
st.set_page_config(page_title="GameTrend Admin", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .msg-user { background: #001a3d; padding: 10px; border-radius: 8px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .msg-admin { background: #002b5c; padding: 10px; border-radius: 8px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; }
    </style>
""", unsafe_allow_html=True)

# --- BARRE DE GAUCHE : LES COMMENTAIRES ---
with st.sidebar:
    st.title("💬 Salon de discussion")
    
    # Formulaire pour les utilisateurs
    with st.form("publier", clear_on_submit=True):
        pseudo = st.text_input("Ton Pseudo")
        message = st.text_area("Ton message")
        if st.form_submit_button("Poster l'avis"):
            if pseudo and message:
                st.session_state.comments.append({"user": pseudo, "msg": message, "reply": None})
                sauver_comms(st.session_state.comments)
                st.rerun()

    st.divider()
    
    # TON ESPACE RÉPONSE (Facile)
    st.subheader("🛠 Espace Admin")
    code = st.text_input("Entre ton code pour répondre", type="password")
    # Remplace '1234' par le code que tu veux utiliser pour te connecter
    je_suis_lauteur = (code == "1234") 

    if je_suis_lauteur:
        st.success("Mode réponse activé !")

    st.divider()

    # Affichage des messages et bouton de réponse
    for i, c in enumerate(reversed(st.session_state.comments)):
        real_idx = len(st.session_state.comments) - 1 - i
        
        # Le message de l'utilisateur
        st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> :<br>{c["msg"]}</div>', unsafe_allow_html=True)
        
        # Ta réponse si elle existe déjà
        if c['reply']:
            st.markdown(f'<div class="msg-admin"><b>Réponse de l\'auteur</b> :<br>{c["reply"]}</div>', unsafe_allow_html=True)
        
        # Le champ pour répondre direct si tu es connecté
        elif je_suis_lauteur:
            reponse_directe = st.text_input(f"Ta réponse à {c['user']}", key=f"input_{real_idx}")
            if st.button("Répondre maintenant", key=f"btn_{real_idx}"):
                st.session_state.comments[real_idx]['reply'] = reponse_directe
                sauver_comms(st.session_state.comments)
                st.rerun()

# --- RESTE DU SITE (TES JEUX) ---
st.title("GameTrend Pro")
# ... (Tes catégories de jeux s'affichent ici comme d'habitude)

