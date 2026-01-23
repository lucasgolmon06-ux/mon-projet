import streamlit as st
import requests
import json
import os
import time
from collections import Counter

# --- 1. CONFIGURATION API IGDB ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
WISHLIST_FILE = "global_wishlists.json"

# --- 2. FONCTIONS SYSTÈME ---
def charger_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

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

# --- 3. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'global_w' not in st.session_state: st.session_state.global_w = charger_data(WISHLIST_FILE)
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'loaded' not in st.session_state: st.session_state.loaded = False
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 4. DESIGN & INTRO ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #00051d; color: white; }}
    #intro-screen {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #00051d; display: flex; justify-content: center; align-items: center; z-index: 10000; animation: fadeOut 6s forwards; }}
    .logo-img {{ position: absolute; width: 300px; opacity: 0; transform: scale(0.8); }}
    .ps {{ animation: seq 1.8s 0.5s forwards; z-index: 10001; }}
    .xb {{ animation: seq 1.8s 2.3s forwards; z-index: 10002; }}
    .nt {{ animation: seq 1.8s 4.1s forwards; z-index: 10003; }}
    @keyframes seq {{ 0% {{ opacity:0; }} 20%, 80% {{ opacity:1; }} 100% {{ opacity:0; }} }}
    @keyframes fadeOut {{ 0%, 96% {{ opacity:1; visibility:visible; }} 100% {{ opacity:0; visibility:hidden; }} }}
    .msg-user {{ background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }}
    .reply-text {{ margin-left: 30px; border-left: 3px solid #ffcc00; padding-left: 15px; margin-top: 5px; color: #ffcc00; font-size: 0.9em; }}
    .news-ticker {{ background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px; }}
    .news-text {{ display: inline-block; padding-left: 100%; animation: ticker 30s linear infinite; }}
    @keyframes ticker {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
""", unsafe_allow_html=True)

if not st.session_state.loaded:
    st.markdown("""<div id="intro-screen">
        <img class="logo-img ps" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png">
        <img class="logo-img xb" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png">
        <img class="logo-img nt" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Nintendo_Switch_logo_logotype.png/800px-Nintendo_Switch_logo_logotype.png">
    </div>""", unsafe_allow_html=True)
    time.sleep(6.2); st.session_state.loaded = True

# --- 5. SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🛡️ Panel Admin")
    # MISE À JOUR DU CODE ICI
    mon_code = st.text_input("Entrer le code secret", type="password")
    c_est_moi = (mon_code == "628316")
    if c_est_moi:
        st.success("Mode Réponse Activé")

# --- 6. FORUM (EN HAUT) ---
st.title("🎮 GameTrend Ultimate")
st.markdown(f"""<div class="news-ticker"><div class="news-text">🚀 BIENVENUE EN 2026 -- SEUL L'ADMIN PEUT RÉPONDRE AUX MESSAGES -- GTA VI, SWITCH 2 -- </div></div>""", unsafe_allow_html=True)

st.subheader("💬 Communauté")
if not st.session_state.user_pseudo:
    cp1, cp2 = st.columns([3, 1])
    with cp1: p = st.text_input("Ton pseudo")
    with cp2: 
        if st.button("Rejoindre"):
            if p: st.session_state.user_pseudo = p; st.rerun()
else:
    with st.form("main_chat", clear_on_submit=True):
        m = st.text_input(f"Message ({st.session_state.user_pseudo})")
        if st.form_submit_button("Envoyer"):
            if m:
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

# Affichage des messages
for i, c in enumerate(st.session_state.comments[::-1]):
    idx = len(st.session_state.comments) - 1 - i
    col_msg, col_btn = st.columns([5, 1])
    
    with col_msg:
        st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
        if c.get('reply'):
            st.markdown(f"<div class='reply-text'>↳ <b>Admin</b> : {c['reply']}</div>", unsafe_allow_html=True)
    
    with col_btn:
        # Seul toi avec le code 628316 peut voir ce bouton
        if c_est_moi and not c.get('reply'):
            if st.button("💬", key=f"rep_{idx}"):
                st.session_state[f"show_rep_{idx}"] = True

    if st.session_state.get(f"show_rep_{idx}"):
        r_txt = st.text_input("Ta réponse exclusive...", key=f"input_{idx}")
        if st.button("Envoyer la réponse", key=f"send_{idx}"):
            st.session_state.comments[idx]['reply'] = r_txt
            sauver_data(DB_FILE, st.session_state.comments)
            del st.session_state[f"show_rep_{idx}"]
            st.rerun()

st.divider()

# --- 7. CATALOGUES ---
platforms = {"PS5": 167, "Xbox": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    st.header(f"🎮 {name}")
    tri = st.selectbox("Trier par :", ["Mieux notés", "AAA", "Indés"], key=f"tri_{name}")
    
    q = f"fields name, cover.url; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;"
    if tri == "AAA": q = f"fields name, cover.url; where platforms = ({p_id}) & genres != (32) & total_rating > 80 & cover != null; sort total_rating desc; limit 12;"
    elif tri == "Indés": q = f"fields name, cover.url; where platforms = ({p_id}) & genres = (32) & cover != null; sort total_rating desc; limit 12;"
    
    res_games = fetch_data(q)
    if res_games:
        cols = st.columns(6)
        for j, g in enumerate(res_games):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(g['name'][:18], key=f"btn_{p_id}_{g['id']}"):
                    st.session_state.selected_game = g['id']; st.rerun()
