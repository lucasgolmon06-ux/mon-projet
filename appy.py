import streamlit as st
import requests
import json
import os
import time
from datetime import datetime

# --- 1. CONFIGURATION API IGDB ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# --- 2. FONCTIONS SYSTÈME ---
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(comms, f, indent=4)

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
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'loaded' not in st.session_state: st.session_state.loaded = False
if 'wishlist' not in st.session_state: st.session_state.wishlist = []
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'theme' not in st.session_state: st.session_state.theme = "#0072ce"

# --- 4. DESIGN & ANIMATIONS ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #00051d; color: white; }}
    #intro-screen {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #00051d; display: flex; justify-content: center; align-items: center; z-index: 10000; animation: fadeOut 7s forwards; }}
    .logo-img {{ position: absolute; width: 300px; opacity: 0; transform: scale(0.8); }}
    .ps {{ animation: seq 2s 0.5s forwards; z-index: 10001; }}
    .xb {{ animation: seq 2s 2.7s forwards; z-index: 10002; }}
    .nt {{ animation: seq 2s 4.9s forwards; z-index: 10003; }}
    @keyframes seq {{ 0% {{ opacity:0; }} 20%, 80% {{ opacity:1; }} 100% {{ opacity:0; }} }}
    @keyframes fadeOut {{ 0%, 96% {{ opacity:1; visibility:visible; }} 100% {{ opacity:0; visibility:hidden; }} }}
    .badge {{ background: {st.session_state.theme}; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.75em; font-weight: bold; }}
    .msg-user {{ background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid {st.session_state.theme}; margin-top: 10px; }}
    .msg-admin {{ background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; font-size: 0.9em; }}
    .news-ticker {{ background: {st.session_state.theme}; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px; }}
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
    time.sleep(7.2)
    st.session_state.loaded = True

st.markdown("""<div class="news-ticker"><div class="news-text">🚀 BIENVENUE EN 2026 SUR GAMETREND ULTIMATE -- GTA VI BAT TOUS LES RECORDS -- NINTENDO SWITCH 2 : RÉVÉLATION IMMINENTE -- </div></div>""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    color_choice = st.selectbox("Couleur Thème", ["Néon Blue", "Cyber Red", "Emerald Green"])
    if color_choice == "Néon Blue": st.session_state.theme = "#0072ce"
    elif color_choice == "Cyber Red": st.session_state.theme = "#ff003c"
    else: st.session_state.theme = "#00ff88"
    
    st.divider()
    admin_code = st.text_input("🔑 Code Admin", type="password")
    is_admin = (admin_code == "1234")
    
    st.divider()
    st.title("⭐ Wishlist")
    for g in st.session_state.wishlist:
        st.markdown(f"🎮 {g}")
    if st.button("Vider"): st.session_state.wishlist = []; st.rerun()

# --- 6. NAVIGATION DÉTAILS ---
if st.session_state.selected_game:
    g_id = st.session_state.selected_game
    res = fetch_data(f"fields name, cover.url, summary, total_rating; where id = {g_id};")
    if res:
        game = res[0]
        if st.button("⬅️ Retour"): st.session_state.selected_game = None; st.rerun()
        st.title(game['name'])
        st.image("https:" + game['cover']['url'].replace('t_thumb', 't_720p'), width=300)
        st.write(game.get('summary', ''))
        st.stop()

# --- 7. HEADER & COMMUNAUTÉ ---
h1, h2 = st.columns([3, 1])
with h1: st.title("🎮 GameTrend Ultimate")
with h2: ouvrir_comm = st.toggle("💬 Communauté")

if ouvrir_comm:
    st.subheader("💬 Forum de discussion")
    
    # Affichage des messages (Ancien -> Nouveau)
    for i, c in enumerate(st.session_state.comments):
        col_msg, col_del = st.columns([5, 1])
        with col_msg:
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b>: {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f"<div class='msg-admin'><b>Réponse</b>: {c['reply']}</div>", unsafe_allow_html=True)
        
        with col_del:
            if is_admin:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.comments.pop(i)
                    sauver_comms(st.session_state.comments)
                    st.rerun()
                if not c.get('reply'):
                    if st.button("💬", key=f"rep_btn_{i}"):
                        st.session_state[f"show_rep_{i}"] = True
        
        # Champ de réponse admin
        if is_admin and st.session_state.get(f"show_rep_{i}", False):
            with st.container():
                rep_txt = st.text_input("Ta réponse", key=f"txt_{i}")
                if st.button("Envoyer", key=f"send_{i}"):
                    st.session_state.comments[i]['reply'] = rep_txt
                    sauver_comms(st.session_state.comments)
                    st.rerun()

    st.divider()
    if st.session_state.user_pseudo is None:
        p_in = st.text_input("Entre un pseudo pour parler")
        if st.button("Rejoindre"): st.session_state.user_pseudo = p_in; st.rerun()
    else:
        with st.form("new_message", clear_on_submit=True):
            m_in = st.text_area(f"Message de {st.session_state.user_pseudo}")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m_in, "reply": None})
                sauver_comms(st.session_state.comments); st.rerun()

# --- 8. TOPS PAR CONSOLE ---
st.divider()
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    st.header(f"Top 12 {name}")
    jeux = fetch_data(f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;")
    if jeux:
        cols = st.columns(6)
        for j, g in enumerate(jeux):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:18]}", key=f"g_{g['id']}_{name}"):
                    st.session_state.selected_game = g['id']; st.rerun()

