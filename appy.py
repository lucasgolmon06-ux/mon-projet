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

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    # CORRECTION : On ajoute verify=False pour éviter l'erreur SSLError
    res = requests.post(auth_url, verify=False)
    return res.json().get('access_token')

def fetch_data(endpoint, query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}', 'Content-Type': 'text/plain'}
    # CORRECTION : verify=False ici aussi
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query, verify=False)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'page' not in st.session_state: st.session_state.page = "home"

# --- 3. STYLE VISUEL ---
st.set_page_config(page_title="GAMETREND", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at center, #001233 0%, #000000 100%); color: #ffffff; }
    h1, h2, h3 { letter-spacing: 3px; font-weight: 300; text-transform: uppercase; }
    .section-box { border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 4px; background: rgba(255, 255, 255, 0.02); margin-bottom: 20px; }
    .news-card { border-left: 3px solid #00f2ff; padding: 15px; margin-bottom: 15px; background: rgba(0, 242, 255, 0.05); }
    </style>
""", unsafe_allow_html=True)

# --- 4. ACCUEIL ---
st.title("GAMETREND // 2026")

# --- SECTION NEWS (MAJ 1H) ---
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("📰 LIVE GAMING NEWS")
# On cherche les actus sur les jeux populaires
news_data = fetch_data("website_previews", "fields title, summary, url; limit 3;") 
if news_data:
    cols_news = st.columns(3)
    for idx, news in enumerate(news_data):
        with cols_news[idx]:
            st.markdown(f"""
            <div class="news-card">
                <div style="color:#00f2ff; font-weight:bold; font-size:1rem; margin-bottom:5px;">{news.get('title', 'ACTU')}</div>
                <div style="font-size:0.8rem; opacity:0.7;">{news.get('summary', '')[:150]}...</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("Actualisation des flux d'informations...")
st.markdown('</div>', unsafe_allow_html=True)

# --- STRUCTURE PRINCIPALE ---
col_jeux, col_new = st.columns([3, 1])

with col_jeux:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("🎮 JEUX ÉLITE")
    
    selected_genre = st.selectbox("GENRE", ["Tous", "Action", "RPG", "Shooter", "Horreur"])
    GENRES_MAP = {"Action": 31, "RPG": 12, "Shooter": 5, "Horreur": 19}
    
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
                st.caption(f"{g['name']} ({int(g.get('total_rating', 0))}/100)")
    st.markdown('</div>', unsafe_allow_html=True)

with col_new:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("✨ NEW")
    new_games = fetch_data("games", "fields name, cover.url; where first_release_date > 1737742000 & cover != null; sort popularity desc; limit 3;")
    for ng in new_games:
        st.image("https:" + ng['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

# --- BAS DE PAGE ---
c_comm, c_admin = st.columns([3, 1])
with c_comm:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("💬 CHAT")
    msg = st.text_input("Message :", key="msg_input")
    if st.button("PUBLIER") and msg:
        st.session_state.comments.append({"msg": msg})
        sauver_data(DB_FILE, st.session_state.comments)
        st.rerun()
    for c in st.session_state.comments[::-1][:3]:
        st.markdown(f"<div style='color:#00f2ff; font-size:0.8rem;'>• {c['msg']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_admin:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("🛠️")
    if st.text_input("Code", type="password") == "628316":
        if st.button("RAZ"):
            st.session_state.comments = []; sauver_data(DB_FILE, []); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
