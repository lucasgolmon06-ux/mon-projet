import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & MOTEUR ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

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
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. DESIGN "PREMIUM DARK" ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #001233 0%, #000000 100%);
        color: #ffffff;
    }
    .news-ticker {
        border-bottom: 1px solid rgba(0, 242, 255, 0.2);
        color: #00f2ff;
        padding: 10px;
        font-size: 0.8rem;
        text-align: center;
        letter-spacing: 4px;
        margin-bottom: 30px;
    }
    .vs-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
    }
    .stButton>button {
        background: transparent;
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        padding: 15px 30px;
        transition: 0.4s;
    }
    .stButton>button:hover {
        border-color: #00f2ff;
        box-shadow: 0 0 20px rgba(0, 242, 255, 0.4);
        color: #00f2ff;
    }
    .badge-masterpiece {
        color: #ffd700;
        border: 1px solid #ffd700;
        padding: 1px 6px;
        font-size: 0.65rem;
        text-transform: uppercase;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DETAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("← RETOUR AU CATALOGUE"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'].upper())
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'))
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        if g.get('total_rating'): st.metric("SCORE ÉLITE", f"{int(g['total_rating'])}/100")
        st.markdown("### 💰 TARIFS 2026")
        st.markdown("<div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:5px;'>Édition AAA : 79.99€<br>Version Steam : 69.99€</div>", unsafe_allow_html=True)
        st.write("")
        st.caption(g.get('summary', ''))
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND // SELECTION HAUTE PRODUCTION // AAA ONLY // 2026</div>', unsafe_allow_html=True)

# --- LE DUEL ULTIME ---
st.markdown('<div class="vs-card">', unsafe_allow_html=True)
st.markdown("<h1 style='letter-spacing:10px; font-weight:100;'>THE CLASH</h1>", unsafe_allow_html=True)
cv1, cv_mid, cv2 = st.columns([2, 1, 2])
with cv1:
    st.markdown("### GTA VI")
    if st.button("VOTER ROCKSTAR", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with cv_mid:
    st.markdown("<h2 style='text-align:center; color:#00f2ff; margin-top:35px;'>VS</h2>", unsafe_allow_html=True)
with cv2:
    st.markdown("### CYBERPUNK 2")
    if st.button("VOTER CD PROJEKT", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

votes_t = st.session_state.vs['j1'] + st.session_state.vs['j2']
perc = (st.session_state.vs['j1'] / votes_t * 100) if votes_t > 0 else 50
st.progress(perc/100)
st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#00f2ff;'><span>{int(perc)}% Rockstar</span><span>{100-int(perc)}% CDPR</span></div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CATALOGUE ÉLITE (VRAIS JEUX SEULEMENT) ---
st.header("SELECTION PAR GENRE")
GENRES_MAP = {"Action/Aventure": 31, "RPG": 12, "Simulation": 13, "Sport": 14, "Shooter": 5, "Horreur": 19, "Combat": 4}

c_f1, c_f2 = st.columns(2)
with c_f1: s_query = st.text_input("RECHERCHER UN HIT", placeholder="Nom du jeu...")
with c_f2: s_genres = st.multiselect("GENRES ÉLITE (AAA)", list(GENRES_MAP.keys()))

# Requête IGDB : Score > 85 + Date > 2010
if s_query:
    q = f'search "{s_query}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    # Filtre drastique pour ne garder que les chefs-d'œuvre
    filters = ["cover != null", "total_rating >= 85", "first_release_date > 1262304000"]
    if s_genres:
        g_ids = [str(GENRES_MAP[g]) for g in s_genres]
        filters.append(f"genres = ({','.join(g_ids)})")
    q = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where {' & '.join(filters)}; sort popularity desc; limit 12;"

games = fetch_data("games", q)

if games:
    cols = st.columns(6)
    for i, g in enumerate(games):
        with cols[i%6]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                score = int(g.get('total_rating', 0))
                if score >= 90: st.markdown('<span class="badge-masterpiece">Masterpiece</span>', unsafe_allow_html=True)
                if st.button("VOIR", key=f"btn_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# --- 7. FUTURES SORTIES ---
st.divider()
st.header("🚀 PROCHAINEMENT")
futures = fetch_data("games", "fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date > 1735689600 & cover != null; sort popularity desc; limit 6;")
if futures:
    cols_f = st.columns(6)
    for i, g in enumerate(futures):
        with cols_f[i]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button("VOIR", key=f"f_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()
