import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
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
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE VISUEL CINÉMA ---
st.set_page_config(page_title="GAMETREND", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at center, #001233 0%, #000000 100%);
        color: #ffffff;
    }
    h1, h2, h3 { letter-spacing: 5px; font-weight: 300; text-transform: uppercase; }
    .news-ticker {
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: #d1d1d1;
        padding: 10px;
        font-size: 0.8rem;
        text-align: center;
        letter-spacing: 3px;
        margin-bottom: 30px;
    }
    .vs-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        padding: 40px;
        border-radius: 4px;
        text-align: center;
        margin-bottom: 40px;
    }
    .stButton>button {
        background: transparent;
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
        border-radius: 0px;
        transition: 0.3s;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        border-color: #00f2ff;
        color: #00f2ff;
    }
    .badge-gold {
        color: #ffd700;
        border: 1px solid #ffd700;
        padding: 2px 6px;
        font-size: 0.7rem;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("← RETOUR"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'])
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: 
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: 
            st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'))
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        if g.get('total_rating'): 
            st.metric("SCORE", f"{int(g['total_rating'])}/100")
        
        st.markdown("### TARIFS")
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:15px; border:1px solid rgba(255,255,255,0.1);">
                Console : 79.99€<br>PC Digital : 69.99€
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.write(g.get('summary', ''))
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND // AAA & MASTERPIECES // 2026 EDITION</div>', unsafe_allow_html=True)

# --- DUEL (CLASH) ---
st.markdown('<div class="vs-card">', unsafe_allow_html=True)
st.markdown("<h1>THE CLASH</h1>", unsafe_allow_html=True)
cv1, cv_mid, cv2 = st.columns([2, 1, 2])
with cv1:
    st.markdown("### GTA VI")
    if st.button("VOTE GTA VI", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with cv_mid:
    st.markdown("<h2 style='text-align:center; color:#00f2ff; margin-top:35px;'>VS</h2>", unsafe_allow_html=True)
with cv2:
    st.markdown("### CYBERPUNK 2")
    if st.button("VOTE CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

v_total = st.session_state.vs['j1'] + st.session_state.vs['j2']
p = (st.session_state.vs['j1'] / v_total * 100) if v_total > 0 else 50
st.progress(p/100)
st.markdown(f"<div style='display:flex; justify-content:space-between; font-size:0.8rem; color:#888;'><span>{int(p)}% ROCKSTAR</span><span>{100-int(p)}% CDPR</span></div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 6. CATALOGUE ÉLITE (NO RÉTRO / SCORE > 85) ---
st.header("SÉLECTION PAR GENRE")
GENRES_MAP = {"Action/Aventure": 31, "RPG": 12, "Simulation": 13, "Sport": 14, "Shooter": 5, "Combat": 4}

c_f1, c_f2 = st.columns(2)
with c_f1: s_query = st.text_input("RECHERCHE", placeholder="Nom du jeu...")
with c_f2: s_genres = st.multiselect("GENRES", list(GENRES_MAP.keys()))

if s_query:
    q = f'search "{s_query}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    # Filtre drastique : Score >= 85 + Date > 2010
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
                sc = int(g.get('total_rating', 0))
                if sc >= 90: st.markdown('<span class="badge-gold">GOLD</span>', unsafe_allow_html=True)
                if st.button("DETAILS", key=f"btn_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# --- 7. SORTIES FUTURES ---
st.divider()
st.header("PROCHAINEMENT")
f_query = "fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date > 1737742000 & cover != null; sort popularity desc; limit 6;"
futures = fetch_data("games", f_query)

if futures:
    cols_f = st.columns(6)
    for i, g in enumerate(futures):
        with cols_f[i]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button("VOIR", key=f"fut_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()
