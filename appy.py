import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

def charger_data(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return default
    return default

def sauver_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(auth_url)
    return res.json().get('access_token')

def fetch_data(query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
    return res.json()

# --- 2. INITIALISATION ---
if 'view' not in st.session_state: st.session_state.view = "accueil"
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-header { border: 3px solid white; padding: 20px; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .msg-user { background: #001a3d; padding: 15px; border-radius: 10px; border-left: 5px solid #0072ce; margin-bottom: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. BARRE DE NAVIGATION (Ton schéma) ---
st.markdown('<div class="news-header">NEW</div>', unsafe_allow_html=True)

nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("🏠 ACCUEIL", use_container_width=True): st.session_state.view = "accueil"
with nav_col2:
    if st.button("🔥 DUEL", use_container_width=True): st.session_state.view = "duel"
with nav_col3:
    if st.button("💬 COMMU", use_container_width=True): st.session_state.view = "commu"
with nav_col4:
    if st.button("🛡️ ADMIN", use_container_width=True): st.session_state.view = "admin"

st.divider()

# --- 5. LOGIQUE D'AFFICHAGE ---

# --- VUE : DUEL (S'affiche en grand) ---
if st.session_state.view == "duel":
    st.title("🔥 LE CHOC DES TITRES")
    v1, vs_txt, v2 = st.columns([2, 1, 2])
    with v1: 
        st.subheader("GTA VI")
        if st.button("VOTER GTA"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
    with v2:
        st.subheader("CYBERPUNK 2")
        if st.button("VOTER CP2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    st.progress(st.session_state.vs['j1'] / (st.session_state.vs['j1'] + st.session_state.vs['j2'] + 0.1))

# --- VUE : COMMU (S'affiche en grand) ---
elif st.session_state.view == "commu":
    st.title("💬 ESPACE COMMUNAUTÉ")
    if not st.session_state.get('user_pseudo'):
        p = st.text_input("Pseudo :")
        if st.button("Se connecter"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat"):
            m = st.text_input("Ton message...")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        for c in st.session_state.comments[::-1]:
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'): st.markdown(f"<div class='admin-reply'>🛡️ {c['reply']}</div>", unsafe_allow_html=True)

# --- VUE : ADMIN (S'affiche en grand - Zone Vide si pas de code) ---
elif st.session_state.view == "admin":
    st.title("🛡️ PANEL ADMINISTRATION")
    pwd = st.text_input("Code Secret :", type="password")
    if pwd == "628316":
        st.metric("Total Messages", len(st.session_state.comments))
        st.subheader("Répondre aux messages")
        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            if not c.get('reply'):
                with st.expander(f"Message de {c['user']}"):
                    r = st.text_input("Réponse :", key=f"ans_{idx}")
                    if st.button("Envoyer", key=f"btn_{idx}"):
                        st.session_state.comments[idx]['reply'] = r
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    elif pwd != "":
        st.error("Accès refusé.")

# --- VUE : ACCUEIL (OUVERT PAR DÉFAUT) ---
else:
    st.title("🎮 TOP JEUX 2026")
    # Ici on met le catalogue qui est toujours visible à l'ouverture
    res = fetch_data("fields name, cover.url; sort total_rating desc; limit 18;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(g['name'])
