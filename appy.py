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
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; color: #ffcc00; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
    .percentage-text { font-size: 24px; font-weight: bold; text-align: center; color: #0072ce; }
    </style>
""", unsafe_allow_html=True)

# --- PAGE DE DÉTAILS (PLEIN ÉCRAN) ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR À L'ACCUEIL"):
        st.session_state.page = "home"
        st.rerun()

    st.markdown(f"<h1 style='text-align:center; font-size:60px;'>{g['name']}</h1>", unsafe_allow_html=True)
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        if 'videos' in g:
            vid_id = g['videos'][0]['video_id']
            st.subheader("📺 BANDE-ANNONCE OFFICIELLE")
            st.video(f"https://www.youtube.com/watch?v={vid_id}")
        
        if 'screenshots' in g:
            st.subheader("📸 IMAGES DU GAMEPLAY")
            for ss in g['screenshots'][:3]:
                st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)

    with col_side:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.metric(label="⭐ NOTE", value=f"{int(g.get('total_rating', 0))}/100")
        st.subheader("📝 RÉSUMÉ")
        st.write(g.get('summary', 'Aucun résumé disponible.'))
    st.stop()

# --- PAGE D'ACCUEIL ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 -- RECHERCHEZ VOS JEUX PRÉFÉRÉS -- GTA VI vs CYBERPUNK 2 -- GAMEPLAY & TRAILERS DISPONIBLES --</div></div>', unsafe_allow_html=True)
st.title("GameTrend Ultimate")

# --- SECTION DUEL ---
st.header("🔥 Le Duel du Moment")
v1, vs_txt, v2 = st.columns([2, 1, 2])
with v1:
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with vs_txt: st.markdown("<h1 style='text-align:center; color:red;'>VS</h1>", unsafe_allow_html=True)
with v2:
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

total = st.session_state.vs['j1'] + st.session_state.vs['j2']
p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
st.progress(p1 / 100)
st.markdown(f"<div class='percentage-text'>GTA VI: {int(p1)}% | CYBERPUNK 2: {int(100-p1)}%</div>", unsafe_allow_html=True)

# --- SECTION COMMUNAUTÉ ---
st.divider()
st.header("💬 Communauté")
if not st.session_state.user_pseudo:
    pseudo = st.text_input("Pseudo :")
    if st.button("Rejoindre"): st.session_state.user_pseudo = pseudo; st.rerun()
else:
    with st.form("chat_form", clear_on_submit=True):
        msg = st.text_input(f"Message ({st.session_state.user_pseudo})")
        if st.form_submit_button("Envoyer"):
            if msg and not any(bad in msg.lower().split() for bad in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": msg, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            elif msg: st.error("Langage inapproprié !")

for c in st.session_state.comments[::-1]:
    st.markdown(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'): st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span>{c['reply']}</div>", unsafe_allow_html=True)

# --- CATALOGUE & RECHERCHE (NOUVEAU) ---
st.divider()
st.header("🎮 Catalogue & Recherche")

col_search, col_plat = st.columns([2, 1])
with col_search:
    search_query = st.text_input("🔍 Rechercher un jeu précisément...", placeholder="Ex: Elden Ring, FIFA, Zelda...")
with col_plat:
    platforms = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
    p_choice = st.selectbox("Ou filtrer par console :", list(platforms.keys()))

if search_query:
    q = f'search "{search_query}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    q = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where platforms = ({platforms[p_choice]}) & cover != null; sort popularity desc; limit 12;"

jeux = fetch_data("games", q)

if jeux:
    cols = st.columns(6)
    for i, j in enumerate(jeux):
        with cols[i % 6]:
            st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button("🔎 DÉTAILS", key=f"det_{j['id']}"):
                st.session_state.selected_game = j
                st.session_state.page = "details"
                st.rerun()

# --- ADMIN ---
st.divider()
with st.expander("🛠️ ADMIN"):
    if st.text_input("Code :", type="password", key="adm_final") == "628316":
        if st.button("🗑️ Reset Chat"): st.session_state.comments = []; sauver_data(DB_FILE, []); st.rerun()
        for i, c in enumerate(st.session_state.comments):
            st.write(f"**{c['user']}** : {c['msg']}")
            if st.button("❌", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            if not c.get('reply'):
                rep = st.text_input("Réponse", key=f"rep_{i}")
                if st.button("OK", key=f"b_{i}"):
                    st.session_state.comments[i]['reply'] = rep; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
