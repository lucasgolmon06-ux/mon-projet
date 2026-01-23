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

# --- 3. INITIALISATION DES SESSIONS ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'loaded' not in st.session_state: st.session_state.loaded = False
if 'wishlist' not in st.session_state: st.session_state.wishlist = []
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'theme' not in st.session_state: st.session_state.theme = "#0072ce"

# --- 4. DESIGN & ANIMATIONS CSS ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")

st.markdown(f"""
    <style>
    .stApp {{ background-color: #00051d; color: white; }}
    #intro-screen {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: #00051d; display: flex; justify-content: center; align-items: center; z-index: 10000; animation: fadeOut 7.5s forwards; }}
    .logo-img {{ position: absolute; width: 300px; opacity: 0; transform: scale(0.8); }}
    .ps {{ animation: seq 2s 0.5s forwards; z-index: 10001; }}
    .xb {{ animation: seq 2s 2.7s forwards; z-index: 10002; }}
    .nt {{ animation: seq 2s 4.9s forwards; z-index: 10003; }}
    @keyframes seq {{ 0% {{ opacity:0; transform:scale(0.8); }} 20%, 80% {{ opacity:1; transform:scale(1); }} 100% {{ opacity:0; transform:scale(1.1); }} }}
    @keyframes fadeOut {{ 0%, 96% {{ opacity:1; visibility:visible; }} 100% {{ opacity:0; visibility:hidden; }} }}
    .badge {{ background: {st.session_state.theme}; color: white; padding: 2px 8px; border-radius: 5px; font-size: 0.75em; font-weight: bold; }}
    .wish-card {{ border: 1px solid {st.session_state.theme}; padding: 10px; border-radius: 8px; margin-bottom: 8px; background: #001a3d; font-size: 0.9em; }}
    .msg-user {{ background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid {st.session_state.theme}; margin-top: 10px; }}
    .msg-admin {{ background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; }}
    
    /* Bandeau News */
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

# --- 5. BANDEAU NEWS ---
st.markdown("""<div class="news-ticker"><div class="news-text">
    🚀 GTA VI EXPLOSE LES PRÉCOMMANDES EN CETTE ANNÉE 2026 -- 🎮 NINTENDO SWITCH 2 : DES IMAGES DU DESIGN ONT FUITÉ -- 🏆 ELDEN RING 2 SERAIT EN DÉVELOPPEMENT -- 🔥 GAME TREND : VOTRE SOURCE N°1 POUR LE GAMING
</div></div>""", unsafe_allow_html=True)

# --- 6. BARRE LATÉRALE (DÉCOR & WISHLIST) ---
with st.sidebar:
    st.title("⚙️ Style du site")
    color_choice = st.selectbox("Choisir une couleur", ["Néon Blue", "Cyber Red", "Emerald Green"])
    if color_choice == "Néon Blue": st.session_state.theme = "#0072ce"
    elif color_choice == "Cyber Red": st.session_state.theme = "#ff003c"
    else: st.session_state.theme = "#00ff88"
    
    st.divider()
    st.title("⭐ Ma Wishlist")
    if not st.session_state.wishlist:
        st.write("Aucun favori.")
    else:
        for game_name in st.session_state.wishlist:
            st.markdown(f'<div class="wish-card">🎮 {game_name}</div>', unsafe_allow_html=True)
        if st.button("Vider ma liste"):
            st.session_state.wishlist = []; st.rerun()

# --- 7. LOGIQUE DE NAVIGATION (PAGE DÉTAILS) ---
if st.session_state.selected_game:
    g_id = st.session_state.selected_game
    res_details = fetch_data(f"fields name, cover.url, summary, storyline, total_rating, first_release_date, genres.name, screenshots.url; where id = {g_id};")
    if res_details:
        game = res_details[0]
        if st.button("⬅️ Retour au catalogue"):
            st.session_state.selected_game = None
            st.rerun()
        col_img, col_info = st.columns([1, 2])
        with col_img:
            st.image("https:" + game['cover']['url'].replace('t_thumb', 't_720p'), use_container_width=True)
        with col_info:
            st.title(game['name'])
            st.subheader(f"Note : ⭐ {round(game.get('total_rating', 0))}/100")
            st.write(f"**Résumé :** {game.get('summary', 'Aucun résumé.')}")
            yt_url = f"https://www.youtube.com/results?search_query={game['name'].replace(' ', '+')}+official+trailer"
            st.link_button("🎬 Regarder le Trailer", yt_url)
            if st.button("⭐ Ajouter aux Favoris"):
                if game['name'] not in st.session_state.wishlist:
                    st.session_state.wishlist.append(game['name']); st.rerun()
        if 'screenshots' in game:
            st.divider()
            cols_ss = st.columns(3)
            for i, ss in enumerate(game['screenshots'][:3]):
                with cols_ss[i]: st.image("https:" + ss['url'].replace('t_thumb', 't_720p'))
        st.stop()

# --- 8. HEADER & COMMUNAUTÉ ---
h1, h2 = st.columns([3, 1])
with h1: st.title("🎮 GameTrend Ultimate")
with h2: ouvrir_comm = st.toggle("💬 Communauté")

if ouvrir_comm:
    st.markdown("### 👥 Forum")
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.session_state.user_pseudo is None:
            with st.form("p_form"):
                p_in = st.text_input("Pseudo")
                if st.form_submit_button("Valider"):
                    st.session_state.user_pseudo = p_in; st.rerun()
        else:
            nb_msg = sum(1 for c in st.session_state.comments if c['user'] == st.session_state.user_pseudo)
            rank = "Nouveau" if nb_msg < 3 else "Expert" if nb_msg < 10 else "Légende"
            st.markdown(f"**{st.session_state.user_pseudo}** <span class='badge'>{rank}</span>", unsafe_allow_html=True)
            with st.form("m_form", clear_on_submit=True):
                m_in = st.text_area("Message")
                if st.form_submit_button("Poster"):
                    st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m_in, "reply": None})
                    sauver_comms(st.session_state.comments); st.rerun()
    with c2:
        for c in reversed(st.session_state.comments):
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b>: {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'): st.markdown(f"<div class='msg-admin'><b>Auteur</b>: {c['reply']}</div>", unsafe_allow_html=True)
    st.divider()

# --- 9. HYPE CHART & TOPS ---
st.subheader("🗓️ Sorties 2026 les plus attendues")
future_games = fetch_data(f"fields name, cover.url, first_release_date; where first_release_date > {int(time.time())} & cover != null; sort popularity desc; limit 6;")
if future_games:
    cf = st.columns(6)
    for i, g in enumerate(future_games):
        with cf[i]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(f"{g['name'][:15]}", key=f"h_{g['id']}"):
                st.session_state.selected_game = g['id']; st.rerun()

platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    st.divider()
    t1, t2 = st.columns([2, 1])
    with t1: st.header(f"Top 12 {name}")
    with t2: filtre = st.selectbox(f"Filtrer {name}", ["Notes", "Coup de Coeur", "Indés"], key=f"f_{name}")
    
    q = f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;"
    jeux = fetch_data(q)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"{g['name'][:18]}", key=f"g_{g['id']}_{name}"):
                    st.session_state.selected_game = g['id']; st.rerun()
                st.caption(f"⭐ {round(g.get('total_rating', 0))}/100")
