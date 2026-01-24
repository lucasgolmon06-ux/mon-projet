import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & DONNÉES ---
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
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json()

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px;}
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; color: #ffcc00; margin-top:5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
    .price-card { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; border: 1px solid #0072ce; }
    .price-line { display: flex; justify-content: space-between; margin-bottom: 5px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(f"🎮 {g['name']}")
    c_vid, c_desc = st.columns([2, 1])
    
    with c_vid:
        if 'videos' in g:
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g:
            st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with c_desc:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.metric("NOTE COMMUNAUTÉ", f"{int(g.get('total_rating', 0))}/100")
        
        st.markdown("### 💰 Prix Estimés")
        st.markdown(f"""
            <div class="price-card">
                <div class="price-line"><span>PS5 / Xbox Series</span><b>79.99€</b></div>
                <div class="price-line"><span>PC Digital</span><b>69.99€</b></div>
                <div class="price-line"><span>Nintendo Switch</span><b>59.99€</b></div>
            </div>
        """, unsafe_allow_html=True)
        st.write("")
        st.info(g.get('summary', 'Pas de description.'))
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 -- LES MEILLEURS JEUX DU MOMENT (NOTES > 80) -- RECHERCHEZ VOS GENRES -- GTA VI vs CYBERPUNK 2 -- </div></div>', unsafe_allow_html=True)

# DUEL
st.header("🔥 Duel de Légendes")
col_v1, col_v2 = st.columns(2)
with col_v1:
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with col_v2:
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

votes_t = st.session_state.vs['j1'] + st.session_state.vs['j2']
perc = (st.session_state.vs['j1'] / votes_t * 100) if votes_t > 0 else 50
st.progress(perc/100)

# --- 6. CATALOGUE AMÉLIORÉ (SÉLECTION DES MEILLEURS) ---
st.divider()
st.header("🏆 Les Meilleurs Jeux par Genre")

GENRES_MAP = {
    "Action": 31, "Aventure": 2, "RPG": 12, "Simulation": 13, 
    "Sport": 14, "Course": 10, "FPS/Shooter": 5, "Combat": 4, 
    "Horreur": 19, "Indépendant": 32, "Stratégie": 15, "Plateforme": 8
}

col_s1, col_s2 = st.columns([2, 2])

with col_s1:
    search_query = st.text_input("Rechercher un titre :", placeholder="Ex: Elden Ring...")

with col_s2:
    selected_genres = st.multiselect("Filtrer par genres :", list(GENRES_MAP.keys()))

# Construction de la requête pour ne prendre que les jeux avec note > 80
if search_query:
    query = f'search "{search_query}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    # On impose le filtre total_rating >= 80 pour n'avoir que "les meilleurs"
    filters = ["cover != null", "total_rating >= 80"]
    if selected_genres:
        genre_ids = [str(GENRES_MAP[g]) for g in selected_genres]
        filters.append(f"genres = ({','.join(genre_ids)})")
        
    where_clause = " & ".join(filters)
    query = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where {where_clause}; sort popularity desc; limit 12;"

games = fetch_data("games", query)

if games:
    cols = st.columns(6)
    for idx, g in enumerate(games):
        with cols[idx%6]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button("Détails", key=f"btn_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()
else:
    st.warning("Aucun 'hit' (note > 80) trouvé avec ces genres.")

# --- 7. CHAT & ADMIN ---
st.divider()
with st.expander("💬 Chat Communautaire"):
    if not st.session_state.user_pseudo:
        pseudo = st.text_input("Pseudo pour le chat :")
        if st.button("Valider"): st.session_state.user_pseudo = pseudo; st.rerun()
    else:
        msg = st.text_input(f"Message ({st.session_state.user_pseudo}) :")
        if st.button("Envoyer") and msg:
            if not any(w in msg.lower() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": msg, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        
        for c in st.session_state.comments[::-1]:
            st.write(f"**{c['user']}** : {c['msg']}")
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span>{c['reply']}</div>", unsafe_allow_html=True)

with st.expander("🛠️ Admin"):
    if st.text_input("Code", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            st.write(f"{c['user']}: {c['msg']}")
            if st.button("Suppr", key=f"d_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
