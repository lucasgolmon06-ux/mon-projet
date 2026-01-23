import streamlit as st
import requests
import json
import os
import time

# --- CONFIGURATION API IGDB ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# --- SYSTÈME DE SAUVEGARDE ---
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comms, f, indent=4)

# INITIALISATION DES SESSIONS
if 'comments' not in st.session_state:
    st.session_state.comments = charger_comms()
if 'user_pseudo' not in st.session_state:
    st.session_state.user_pseudo = None
if 'loaded' not in st.session_state:
    st.session_state.loaded = False

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    try:
        res = requests.post(auth_url)
        return res.json().get('access_token')
    except: return None

def fetch_data(query):
    token = get_access_token()
    if not token: return []
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- DESIGN & ANIMATIONS ---
st.set_page_config(page_title="GameTrend Ultra", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    
    /* Animation Intro 3 Logos */
    #intro-screen {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d; display: flex; justify-content: center; align-items: center;
        z-index: 10000; animation: fadeOut 6.5s forwards;
    }
    .logo-img { position: absolute; width: 250px; opacity: 0; transform: scale(0.8); }
    .ps { animation: seq 1.8s 0.5s forwards; }
    .xb { animation: seq 1.8s 2.3s forwards; }
    .nt { animation: seq 1.8s 4.1s forwards; }
    @keyframes seq { 0% { opacity:0; } 50% { opacity:1; transform:scale(1); } 100% { opacity:0; transform:scale(1.1); } }
    @keyframes fadeOut { 0%, 95% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }

    /* Bulles de commentaires */
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .msg-admin { background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; font-size: 0.9em; }
    </style>

    <div id="intro-screen">
        <img class="logo-img ps" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png">
        <img class="logo-img xb" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png">
        <img class="logo-img nt" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Nintendo_Switch_logo_and_wordmark.svg/1280px-Nintendo_Switch_logo_and_wordmark.svg.png">
    </div>
""", unsafe_allow_html=True)

# GESTION DU CHARGEMENT (Animation une seule fois)
if not st.session_state.loaded:
    time.sleep(6.2)
    st.session_state.loaded = True

# --- HEADER ---
head_col1, head_col2 = st.columns([3, 1])
with head_col1:
    st.title("🎮 GameTrend Pro")
with head_col2:
    # C'est ce bouton qui déclenche l'ouverture
    ouvrir_comm = st.toggle("💬 Espace Communauté", key="main_toggle_comm")

# --- ESPACE COMMUNAUTÉ (S'OUVRE ICI) ---
if ouvrir_comm:
    st.markdown("### 👥 Forum de la Communauté")
    # On crée deux colonnes : Gauche pour poster, Droite pour lire
    col_comm_form, col_comm_list = st.columns([1, 2])
    
    with col_comm_form:
        st.write("---")
        # Étape 1 : Choisir son pseudo unique
        if st.session_state.user_pseudo is None:
            st.info("Choisissez un pseudo pour participer.")
            with st.form("set_pseudo_form"):
                p_input = st.text_input("Votre Pseudo")
                if st.form_submit_button("Valider"):
                    if p_input:
                        st.session_state.user_pseudo = p_input
                        st.rerun()
        else:
            # Étape 2 : Poster un message
            st.success(f"Connecté : **{st.session_state.user_pseudo}**")
            with st.form("post_message_form", clear_on_submit=True):
                m_text = st.text_area("Votre message...")
                if st.form_submit_button("Poster"):
                    if m_text:
                        st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m_text, "reply": None})
                        sauver_comms(st.session_state.comments)
                        st.rerun()
            if st.button("Modifier mon pseudo"):
                st.session_state.user_pseudo = None
                st.rerun()

        st.divider()
        # Zone Secrète pour toi
        admin_pass = st.text_input("🔑 Mode Admin (Code)", type="password")
        je_suis_auteur = (admin_pass == "1234")

    with col_comm_list:
        st.write("---")
        # Affichage des messages
        if not st.session_state.comments:
            st.write("Soyez le premier à laisser un avis !")
        else:
            for i, c in enumerate(reversed(st.session_state.comments)):
                real_idx = len(st.session_state.comments) - 1 - i
                st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> : {c["msg"]}</div>', unsafe_allow_html=True)
                
                # Affichage de ta réponse si elle existe
                if c.get('reply'):
                    st.markdown(f'<div class="msg-admin"><b>Réponse de l\'auteur</b> : {c["reply"]}</div>', unsafe_allow_html=True)
                # Champ pour répondre si tu es en mode admin
                elif je_suis_auteur:
                    rep = st.text_input(f"Répondre à {c['user']}", key=f"rep_{real_idx}")
                    if st.button("Publier Réponse", key=f"btn_rep_{real_idx}"):
                        st.session_state.comments[real_idx]['reply'] = rep
                        sauver_comms(st.session_state.comments)
                        st.rerun()
    st.markdown("---")

# --- LE RESTE DU SITE (Toujours visible en dessous) ---
col_search1, col_search2 = st.columns(2)
with col_search1:
    search_q = st.text_input("🔍 Rechercher un jeu...")
with col_search2:
    style_q = st.text_input("💡 Style de jeu (alternatives)...")

# (La logique IGDB pour la recherche et les Top 12 par console suit ici...)
# ... (Code identique à la version précédente pour les requêtes)
