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
if 'theme' not in st.session_state: st.session_state.theme = "#0072ce"

# --- 4. DESIGN ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")
st.markdown(f"""
    <style>
    .stApp {{ background-color: #00051d; color: white; }}
    #intro-screen {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #00051d; display: flex; justify-content: center; align-items: center; z-index: 10000; animation: fadeOut 5s forwards; }}
    .logo-img {{ position: absolute; width: 300px; opacity: 0; transform: scale(0.8); }}
    .ps {{ animation: seq 1.5s 0.5s forwards; }}
    .xb {{ animation: seq 1.5s 2.0s forwards; }}
    .nt {{ animation: seq 1.5s 3.5s forwards; }}
    @keyframes seq {{ 0% {{ opacity:0; }} 20%, 80% {{ opacity:1; }} 100% {{ opacity:0; }} }}
    @keyframes fadeOut {{ 0%, 96% {{ opacity:1; visibility:visible; }} 100% {{ opacity:0; visibility:hidden; }} }}
    .news-ticker {{ background: {st.session_state.theme}; color: white; padding: 10px; font-weight: bold; overflow: hidden; border-radius: 5px; }}
    .news-text {{ display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }}
    @keyframes ticker {{ 0% {{ transform: translate(0, 0); }} 100% {{ transform: translate(-100%, 0); }} }}
    </style>
""", unsafe_allow_html=True)

if not st.session_state.loaded:
    st.markdown("""<div id="intro-screen">
        <img class="logo-img ps" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png">
        <img class="logo-img xb" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png">
        <img class="logo-img nt" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Nintendo_Switch_logo_logotype.png/800px-Nintendo_Switch_logo_logotype.png">
    </div>""", unsafe_allow_html=True)
    time.sleep(5.2); st.session_state.loaded = True

st.markdown(f"""<div class="news-ticker"><div class="news-text">🚀 TOP AAA & INDÉPENDANTS DISPONIBLES -- GTA VI EN TÊTE DES VOTES -- NOUVELLES PÉPITES INDÉES DÉCOUVERTES -- </div></div>""", unsafe_allow_html=True)

# --- 5. NAVIGATION DÉTAILS ---
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
            if st.button("❤️ Voter pour ce jeu"):
                st.session_state.global_w.append(game['name'])
                sauver_data(WISHLIST_FILE, st.session_state.global_w); st.rerun()
    st.stop()

# --- 6. SECTIONS SPÉCIALES (AAA & INDÉ) ---
st.title("🏆 Sélections Spéciales 2026")

col_aaa, col_indie = st.tabs(["💎 TOP 12 - JEUX AAA", "🎨 TOP 12 - JEUX INDÉPENDANTS"])

with col_aaa:
    # On filtre sur les gros budgets (excluant le tag indie) et score élevé
    aaa_jeux = fetch_data("fields name, cover.url, total_rating; where genres != (32) & total_rating > 85 & cover != null; sort total_rating desc; limit 12;")
    if aaa_jeux:
        cols = st.columns(6)
        for i, g in enumerate(aaa_jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:18]}", key=f"aaa_{g['id']}"): st.session_state.selected_game = g['id']; st.rerun()

with col_indie:
    # On filtre spécifiquement sur le tag Indie (ID: 32)
    indie_jeux = fetch_data("fields name, cover.url, total_rating; where genres = (32) & total_rating > 80 & cover != null; sort total_rating desc; limit 12;")
    if indie_jeux:
        cols = st.columns(6)
        for i, g in enumerate(indie_jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:18]}", key=f"ind_{g['id']}"): st.session_state.selected_game = g['id']; st.rerun()

# --- 7. CATALOGUES PAR PLATEFORME ---
st.divider()
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1: st.header(f"🎮 {name}")
    with col_t2: 
        tri = st.selectbox("Trier par :", ["Mieux notés", "Plus récents", "Plus aimés (Communauté)"], key=f"tri_{name}")
    
    jeux = []
    if tri == "Plus aimés (Communauté)":
        voted_games = Counter(st.session_state.global_w).most_common(50)
        names = [v[0] for v in voted_games]
        if names:
            formatted_names = '("' + '","'.join(names) + '")'
            jeux = fetch_data(f'fields name, cover.url; where name = {formatted_names} & platforms = ({p_id}) & cover != null; limit 12;')
    elif tri == "Mieux notés":
        jeux = fetch_data(f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;")
    else:
        jeux = fetch_data(f"fields name, cover.url, first_release_date; where platforms = ({p_id}) & cover != null; sort first_release_date desc; limit 12;")

    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:18]}", key=f"cat_{g['id']}_{name}"): st.session_state.selected_game = g['id']; st.rerun()
    st.divider()
