import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

BAD_WORDS = ["merde", "connard", "fdp", "salope", "pute", "encule", "con"]

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

def fetch_data(endpoint, query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}', 'Content-Type': 'text/plain'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE "CINÉMA" (RETOUR AU STYLE INITIAL) ---
st.set_page_config(page_title="GameTrend", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top, #000a1f 0%, #00050d 100%);
        color: #d1d1d1;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 300;
        letter-spacing: 1px;
    }
    .news-ticker {
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: #888;
        padding: 8px;
        font-size: 0.8rem;
        text-align: center;
        margin-bottom: 30px;
        text-transform: uppercase;
    }
    .stButton>button {
        background: linear-gradient(to right, #004e92, #000428);
        color: white;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 4px;
        transition: 0.4s;
    }
    .stButton>button:hover {
        border-color: #00f2ff;
        color: #00f2ff;
        background: transparent;
    }
    .price-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 4px;
    }
    .badge-gold {
        color: #ffd700;
        font-weight: bold;
        font-size: 0.8rem;
        border: 1px solid #ffd700;
        padding: 2px 6px;
        border-radius: 3px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("← RETOUR"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'])
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'))
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        if g.get('total_rating'):
            st.metric("SCORE", f"{int(g['total_rating'])}/100")
        
        st.markdown("### 💰 Tarifs")
        st.markdown(f"""
            <div class="price-card">
                <div style="display:flex; justify-content:space-between"><span>AAA Edition</span><b>79.99€</b></div>
                <div style="display:flex; justify-content:space-between; margin-top:5px"><span>PC Digital</span><b>69.99€</b></div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.caption(g.get('summary', ''))
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND // EXCELLENCE GAMING // SCORE > 85 // VERSION 2026</div>', unsafe_allow_html=True)

# DUEL
st.subheader("Duel : GTA VI vs CYBERPUNK 2")
v1, v2 = st.columns(2)
with v1: 
    if st.button("Voter GTA VI", use_container_width=True): 
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with v2: 
    if st.button("Voter CYBERPUNK 2", use_container_width=True): 
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

# CATALOGUE "VRAIS JEUX"
st.divider()
GENRES_MAP = {"Action/Aventure": 31, "RPG": 12, "Simulation": 13, "Sport": 14, "Shooter": 5, "Horreur": 19, "Combat": 4}

col_s1, col_s2 = st.columns([2, 2])
with col_s1: search_query = st.text_input("🔍 Rechercher un hit :", placeholder="Nom du jeu...")
with col_s2: selected_genres = st.multiselect("🎯 Genres Élite :", list(GENRES_MAP.keys()))

if search_query:
    q = f'search "{search_query}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    # FILTRE ÉLITE : Score > 85 + Date > 2010
    filters = ["cover != null", "total_rating >= 85", "first_release_date > 1262304000"]
    if selected_genres:
        genre_ids = [str(GENRES_MAP[g]) for g in selected_genres]
        filters.append(f"genres = ({','.join(genre_ids)})")
    q = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where {' & '.join(filters)}; sort popularity desc; limit 12;"

games = fetch_data("games", q)

if games:
    cols = st.columns(6)
    for idx, g in enumerate(games):
        with cols[idx%6]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                score = int(g.get('total_rating', 0))
                if score >= 90: st.markdown('<span class="badge-gold">GOLD</span>', unsafe_allow_html=True)
                if st.button("Détails", key=f"b_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# SORTIES FUTURES
st.divider()
st.subheader("🚀 Très Attendus")
futures = fetch_data("games", "fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date > 1735689600 & cover != null; sort popularity desc; limit 6;")
if futures:
    cols_f = st.columns(6)
    for idx, g in enumerate(futures):
        with cols_f[idx]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button("Détails", key=f"f_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# CHAT DISCRET
st.divider()
with st.expander("💬 Salon Communautaire"):
    msg = st.text_input("Message :")
    if st.button("Envoyer") and msg:
        if not any(w in msg.lower() for w in BAD_WORDS):
            st.session_state.comments.append({"user": "Player", "msg": msg})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    for c in st.session_state.comments[::-1]:
        st.markdown(f"<div style='border-left: 2px solid rgba(255,255,255,0.1); padding-left:10px; margin-bottom:10px; font-size:0.9rem;'>{c['msg']}</div>", unsafe_allow_html=True)
