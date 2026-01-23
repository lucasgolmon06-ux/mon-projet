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

# --- 4. DESIGN ---
st.set_page_config(page_title="GameTrend Ultimate", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    #intro-screen { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #00051d; display: flex; justify-content: center; align-items: center; z-index: 10000; animation: fadeOut 7.5s forwards; }
    .logo-img { position: absolute; width: 300px; opacity: 0; transform: scale(0.8); }
    .ps { animation: seq 2s 0.5s forwards; z-index: 10001; }
    .xb { animation: seq 2s 2.7s forwards; z-index: 10002; }
    .nt { animation: seq 2s 4.9s forwards; z-index: 10003; }
    @keyframes seq { 0% { opacity:0; transform:scale(0.8); } 20%, 80% { opacity:1; transform:scale(1); } 100% { opacity:0; transform:scale(1.1); } }
    @keyframes fadeOut { 0%, 96% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }
    .badge { background: #ffcc00; color: black; padding: 2px 8px; border-radius: 5px; font-size: 0.75em; font-weight: bold; }
    .wish-card { border: 1px solid #0072ce; padding: 10px; border-radius: 8px; margin-bottom: 8px; background: #001a3d; }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

if not st.session_state.loaded:
    st.markdown('<div id="intro-screen"><img class="logo-img ps" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png"><img class="logo-img xb" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png"><img class="logo-img nt" src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Nintendo_Switch_logo_logotype.png/800px-Nintendo_Switch_logo_logotype.png"></div>', unsafe_allow_html=True)
    time.sleep(7.2)
    st.session_state.loaded = True

# --- 5. PAGE DÉTAILS DU JEU ---
if st.session_state.selected_game:
    g_id = st.session_state.selected_game
    details = fetch_data(f"fields name, cover.url, summary, storyline, total_rating, first_release_date, genres.name; where id = {g_id};")[0]
    
    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.selected_game = None
        st.rerun()
    
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        img = "https:" + details['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in details else ""
        st.image(img, use_container_width=True)
    with col_d2:
        st.title(details['name'])
        if 'total_rating' in details:
            st.subheader(f"Note : ⭐ {round(details['total_rating'])}/100")
        
        st.write("### Résumé")
        st.write(details.get('summary', "Pas de résumé disponible."))
        
        if 'genres' in details:
            st.write(f"**Genres :** {', '.join([gn['name'] for gn in details['genres']])}")
        
        yt_link = f"https://www.youtube.com/results?search_query={details['name'].replace(' ', '+')}+official+trailer"
        st.link_button("🎬 Voir le Trailer sur YouTube", yt_link)
        
        if st.button("⭐ Ajouter à ma Wishlist"):
            if details['name'] not in st.session_state.wishlist:
                st.session_state.wishlist.append(details['name'])
                st.success("Ajouté !")
    st.stop() # Arrête le reste du script pour n'afficher que les détails

# --- 6. PAGE ACCUEIL (Si aucun jeu sélectionné) ---
with st.sidebar:
    st.title("⭐ Ma Wishlist")
    for game in st.session_state.wishlist:
        st.markdown(f'<div class="wish-card">🎮 {game}</div>', unsafe_allow_html=True)
    if st.session_state.wishlist and st.button("Vider"):
        st.session_state.wishlist = []; st.rerun()

h_col1, h_col2 = st.columns([3, 1])
with h_col1: st.title("🎮 GameTrend Ultimate")
with h_col2: ouvrir_comm = st.toggle("💬 Communauté")

if ouvrir_comm:
    # (Bloc communauté identique au précédent...)
    st.info("Espace de discussion actif")
    st.divider()

# --- 7. TOPS PAR CONSOLE ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    st.header(f"Top 12 {name}")
    jeux = fetch_data(f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;")
    
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                # ICI : Le titre devient le bouton pour ouvrir la page
                if st.button(f"{g['name'][:18]}", key=f"sel_{g['id']}_{name}"):
                    st.session_state.selected_game = g['id']
                    st.rerun()
                st.caption(f"⭐ {round(g.get('total_rating', 0))}/100")
