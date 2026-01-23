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

st.markdown(f"""<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 : GTA VI, SWITCH 2, ET VOS JEUX PRÉFÉRÉS EN DIRECT -- </div></div>""", unsafe_allow_html=True)

# --- 5. VUE DÉTAILLÉE ---
if st.session_state.selected_game:
    res = fetch_data(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.selected_game};")
    if res:
        game = res[0]
        if st.button("⬅️ Retour"): st.session_state.selected_game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + game['cover']['url'].replace('t_thumb', 't_720p'), use_container_width=True)
        with c2:
            st.title(game['name'])
            st.write(game.get('summary', ''))
            if st.button("❤️ Voter"):
                st.session_state.global_w.append(game['name'])
                sauver_data(WISHLIST_FILE, st.session_state.global_w); st.success("Voté !")
    st.stop()

# --- 6. CATALOGUE ---
st.title("🎮 GameTrend Ultimate")

# Section Communauté (Toujours visible car c'est ton Top 12 spécial)
if st.session_state.global_w:
    st.header("❤️ Top 12 - Communauté")
    voted = Counter(st.session_state.global_w).most_common(12)
    names = '("' + '","'.join([v[0] for v in voted]) + '")'
    jeux_comm = fetch_data(f"fields name, cover.url; where name = {names} & cover != null; limit 12;")
    if jeux_comm:
        cols = st.columns(6)
        for i, g in enumerate(jeux_comm):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(g['name'][:18], key=f"comm_{g['id']}"): st.session_state.selected_game = g['id']; st.rerun()
st.divider()

# Sections par Plateforme avec Tri Intelligent
platforms = {"PS5": 167, "Xbox": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1: st.header(f"🎮 {name}")
    with col_t2: 
        tri = st.selectbox("Type de Top 12 :", ["Mieux notés", "Gros Blockbusters (AAA)", "Pépites Indépendantes"], key=f"tri_{name}")
    
    if tri == "Mieux notés":
        query = f"fields name, cover.url; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;"
    elif tri == "Gros Blockbusters (AAA)":
        query = f"fields name, cover.url; where platforms = ({p_id}) & genres != (32) & total_rating > 80 & cover != null; sort total_rating desc; limit 12;"
    else: # Indépendants
        query = f"fields name, cover.url; where platforms = ({p_id}) & genres = (32) & cover != null; sort total_rating desc; limit 12;"
    
    jeux = fetch_data(query)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(g['name'][:18], key=f"p_{p_id}_{g['id']}"): st.session_state.selected_game = g['id']; st.rerun()
    st.divider()

# --- 7. FORUM ---
st.subheader("💬 Communauté")
if st.session_state.user_pseudo:
    with st.form("chat"):
        m = st.text_input(f"Message de {st.session_state.user_pseudo}")
        if st.form_submit_button("Envoyer"):
            st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()
else:
    p = st.text_input("Pseudo")
    if st.button("Rejoindre"): st.session_state.user_pseudo = p; st.rerun()

for c in st.session_state.comments[::-1]:
    st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
