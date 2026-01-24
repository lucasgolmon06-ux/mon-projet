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
    .stApp { background: radial-gradient(circle at center, #001233 0%, #000000 100%); color: #ffffff; }
    h1, h2, h3 { letter-spacing: 3px; font-weight: 300; text-transform: uppercase; }
    .news-ticker { border-bottom: 1px solid rgba(255, 255, 255, 0.1); color: #d1d1d1; padding: 10px; font-size: 0.8rem; text-align: center; margin-bottom: 20px; }
    .section-box { border: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 4px; background: rgba(255, 255, 255, 0.02); height: 100%; }
    .stButton>button { background: transparent; color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 0px; width: 100%; }
    .stButton>button:hover { border-color: #00f2ff; color: #00f2ff; }
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
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'))
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        st.metric("SCORE", f"{int(g.get('total_rating', 0))}/100")
        st.write(g.get('summary', ''))
    st.stop()

# --- 5. ACCUEIL (STRUCTURE SELON DESSIN) ---
st.markdown('<div class="news-ticker">GAMETREND // SELECTION ELITE // 2026</div>', unsafe_allow_html=True)

# Layout principal : JEUX (Gauche) | NEW (Droite)
col_jeux, col_new = st.columns([3, 1])

with col_jeux:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("🎮 JEUX")
    
    # Filtre Genre intégré en haut de la section Jeux
    GENRES_MAP = {"Action": 31, "RPG": 12, "Shooter": 5, "Horreur": 19, "Combat": 4}
    selected_genre = st.selectbox("FILTRER PAR GENRE", ["Tous"] + list(GENRES_MAP.keys()))
    
    # Requête Élite (>85 score)
    filters = ["cover != null", "total_rating >= 85", "first_release_date > 1262304000"]
    if selected_genre != "Tous":
        filters.append(f"genres = ({GENRES_MAP[selected_genre]})")
    
    q_jeux = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where {' & '.join(filters)}; sort popularity desc; limit 9;"
    games = fetch_data("games", q_jeux)
    
    if games:
        grid = st.columns(3)
        for i, g in enumerate(games):
            with grid[i%3]:
                if 'cover' in g:
                    st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                    if st.button("DETAILS", key=f"btn_{g['id']}"):
                        st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_new:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.header("✨ NEW")
    q_new = "fields name, cover.url, total_rating; where first_release_date > 1737742000 & cover != null; sort popularity desc; limit 5;"
    new_games = fetch_data("games", q_new)
    
    for ng in new_games:
        st.image("https:" + ng['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.caption(ng['name'])
        st.divider()
    st.markdown('</div>', unsafe_allow_html=True)

# --- SECTION BASSE (COMMENTAIRES & ADMIN) ---
st.write("")
col_comm, col_admin = st.columns([3, 1])

with col_comm:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("💬 COMMENTAIRES")
    msg = st.text_input("Ajouter un commentaire :", key="in_comm")
    if st.button("PUBLIER"):
        if msg:
            st.session_state.comments.append({"user": "Player", "msg": msg})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    
    for c in st.session_state.comments[::-1][:3]:
        st.markdown(f"<div style='font-size:0.8rem; color:#00f2ff;'>• {c['msg']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_admin:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("🛠️ ADMIN")
    pwd = st.text_input("Code :", type="password")
    if pwd == "628316":
        if st.button("Vider le chat"):
            st.session_state.comments = []; sauver_data(DB_FILE, []); st.rerun()
        st.success("Accès autorisé")
    st.markdown('</div>', unsafe_allow_html=True)
