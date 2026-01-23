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

st.markdown(f"""<div class="news-ticker"><div class="news-text">🚀 BIENVENUE EN 2026 SUR GAMETREND ULTIMATE -- GTA VI BAT TOUS LES RECORDS -- NINTENDO SWITCH 2 : RÉVÉLATION IMMINENTE -- </div></div>""", unsafe_allow_html=True)

# --- 5. SIDEBAR ---
with st.sidebar:
    st.title("⚙️ Paramètres")
    color_choice = st.selectbox("Style", ["Néon Blue", "Cyber Red", "Emerald Green"])
    st.session_state.theme = {"Néon Blue": "#0072ce", "Cyber Red": "#ff003c", "Emerald Green": "#00ff88"}[color_choice]
    
    st.divider()
    admin_code = st.text_input("🔑 Code Admin", type="password")
    is_admin = (admin_code == "1234")
    
    st.divider()
    st.title("⭐ Wishlist")
    for g in st.session_state.wishlist: st.markdown(f"🎮 {g}")
    if st.button("Vider la Wishlist"): st.session_state.wishlist = []; st.rerun()

# --- 6. NAVIGATION DÉTAILS ---
if st.session_state.selected_game:
    res = fetch_data(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.selected_game};")
    if res:
        game = res[0]
        if st.button("⬅️ Retour"): st.session_state.selected_game = None; st.rerun()
        col1, col2 = st.columns([1, 2])
        with col1: st.image("https:" + game['cover']['url'].replace('t_thumb', 't_720p'), use_container_width=True)
        with col2:
            st.title(game['name'])
            st.subheader(f"Note : ⭐ {round(game.get('total_rating', 0))}/100")
            st.write(game.get('summary', ''))
            st.link_button("🎬 Voir le Trailer", f"https://www.youtube.com/results?search_query={game['name'].replace(' ', '+')}+official+trailer")
            if st.button("⭐ Ajouter à la Wishlist"):
                if game['name'] not in st.session_state.wishlist: st.session_state.wishlist.append(game['name']); st.rerun()
        st.stop()

# --- 7. HEADER & COMMUNAUTÉ ---
h1, h2 = st.columns([3, 1])
with h1: st.title("🎮 GameTrend Ultimate")
with h2: ouvrir_comm = st.toggle("💬 Communauté")

if ouvrir_comm:
    for i, c in enumerate(st.session_state.comments):
        cm, cd = st.columns([5, 1])
        with cm:
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b>: {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'): st.markdown(f"<div style='margin-left:30px; color:#ffcc00;'>↳ <b>Auteur</b>: {c['reply']}</div>", unsafe_allow_html=True)
        with cd:
            if is_admin:
                if st.button("❌", key=f"del_{i}"): st.session_state.comments.pop(i); sauver_comms(st.session_state.comments); st.rerun()
                if not c.get('reply'):
                    if st.button("💬", key=f"rep_{i}"): st.session_state[f"op_{i}"] = True
        if st.session_state.get(f"op_{i}"):
            r_txt = st.text_input("Ta réponse", key=f"in_{i}")
            if st.button("Répondre", key=f"go_{i}"):
                st.session_state.comments[i]['reply'] = r_txt; sauver_comms(st.session_state.comments); st.rerun()
    if st.session_state.user_pseudo:
        with st.form("msg"):
            m = st.text_area(f"Message ({st.session_state.user_pseudo})")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_comms(st.session_state.comments); st.rerun()
    else:
        p = st.text_input("Choisis un pseudo")
        if st.button("Rejoindre le forum"): st.session_state.user_pseudo = p; st.rerun()
    st.divider()

# --- 8. RECHERCHE & STYLE (LE RETOUR) ---
st.subheader("🔎 Trouver un jeu")
sc1, sc2 = st.columns(2)
with sc1: q_search = st.text_input("Nom du jeu...")
with sc2: q_style = st.text_input("Style (ex: Action, Horreur, Zelda...)")

if q_search:
    res = fetch_data(f'search "{q_search}"; fields name, cover.url; where cover != null; limit 6;')
    if res:
        cols = st.columns(6)
        for i, g in enumerate(res):
            with cols[i]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:15]}", key=f"sh_{g['id']}"): st.session_state.selected_game = g['id']; st.rerun()

if q_style:
    res = fetch_data(f'search "{q_style}"; fields name, cover.url, total_rating; where cover != null & total_rating > 70; limit 6;')
    if res:
        st.write(f"### Recommandations pour : {q_style}")
        cols = st.columns(6)
        for i, g in enumerate(res):
            with cols[i]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:15]}", key=f"st_{g['id']}"): st.session_state.selected_game = g['id']; st.rerun()

# --- 9. CATALOGUE ---
st.divider()
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    st.header(f"Top 12 {name}")
    jeux = fetch_data(f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;")
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:18]}", key=f"cat_{g['id']}_{name}"): st.session_state.selected_game = g['id']; st.rerun()
