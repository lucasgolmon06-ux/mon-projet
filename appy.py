import streamlit as st
import requests
import json
import os
from datetime import datetime

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

def charger_data(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return default
    return default

def sauver_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

@st.cache_data(ttl=3600) # Mise à jour toutes les 1h
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(auth_url)
    return res.json().get('access_token')

def fetch_data(endpoint, query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}', 'Content-Type': 'text/plain'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'page' not in st.session_state: st.session_state.page = "home"

# --- 3. STYLE VISUEL CINÉMA ---
st.set_page_config(page_title="GAMETREND", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #001233 0%, #000000 100%); color: #ffffff; }
    h1, h2, h3 { letter-spacing: 3px; font-weight: 300; text-transform: uppercase; }
    .section-box { border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 4px; background: rgba(255, 255, 255, 0.02); margin-bottom: 20px; }
    .news-card { border-left: 3px solid #00f2ff; padding-left: 15px; margin-bottom: 20px; background: rgba(0, 242, 255, 0.05); padding: 10px; }
    .stButton>button { background: transparent; color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 0px; width: 100%; }
    .stButton>button:hover { border-color: #00f2ff; color: #00f2ff; }
    </style>
""", unsafe_allow_html=True)

# --- 4. ACCUEIL ---
st.title("GAMETREND // 2026")

# --- SECTION NEWS (MISE À JOUR 1H) ---
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("📰 DERNIÈRES INFOS (MAJ 1H)")
# On récupère les actus via les blogs IGDB/Web
news_data = fetch_data("website_previews", "fields title, summary, url; limit 3;") 
if news_data:
    for news in news_data:
        st.markdown(f"""
        <div class="news-card">
            <div style="color:#00f2ff; font-weight:bold; font-size:1.1rem;">{news.get('title', 'Info Gaming')}</div>
            <div style="font-size:0.85rem; opacity:0.8;">{news.get('summary', 'Cliquez pour voir les détails de cette info...')}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Recherche de nouvelles actualités en cours...")
st.markdown('</div>', unsafe_allow_html=True)

# --- LAYOUT PRINCIPAL ---
col_jeux, col_new = st.columns([3, 1])

with col_jeux:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("🎮 JEUX ÉLITE")
    
    GENRES_MAP = {"Action": 31, "RPG": 12, "Shooter": 5, "Horreur": 19}
    selected_genre = st.selectbox("GENRE", ["Tous"] + list(GENRES_MAP.keys()))
    
    # Filtre Élite (>85 score + pas de vieux jeux)
    filters = ["cover != null", "total_rating >= 85", "first_release_date > 1262304000"]
    if selected_genre != "Tous":
        filters.append(f"genres = ({GENRES_MAP[selected_genre]})")
    
    q_jeux = f"fields name, cover.url, total_rating; where {' & '.join(filters)}; sort popularity desc; limit 9;"
    games = fetch_data("games", q_jeux)
    
    if games:
        grid = st.columns(3)
        for i, g in enumerate(games):
            with grid[i%3]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(f"{g['name']} - {int(g.get('total_rating', 0))}/100")
    st.markdown('</div>', unsafe_allow_html=True)

with col_new:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("✨ NEW")
    # Sorties très proches ou futures
    new_games = fetch_data("games", "fields name, cover.url; where first_release_date > 1737742000 & cover != null; sort popularity desc; limit 4;")
    for ng in new_games:
        st.image("https:" + ng['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION BASSE (COMM & ADMIN) ---
c_comm, c_admin = st.columns([3, 1])
with c_comm:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("💬 COMMENTAIRES")
    msg = st.text_input("Message :", key="msg_input")
    if st.button("PUBLIER"):
        if msg:
            st.session_state.comments.append({"msg": msg})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    for c in st.session_state.comments[::-1][:3]:
        st.markdown(f"<div style='color:#00f2ff; font-size:0.8rem;'>• {c['msg']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_admin:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("🛠️ ADMIN")
    if st.text_input("Code", type="password") == "628316":
        if st.button("Vider"):
            st.session_state.comments = []; sauver_data(DB_FILE, []); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
