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
    return res.json() if res.status_code == 200 else []

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
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
    .top-card { background: rgba(255, 255, 255, 0.05); border: 1px solid #ffd700; border-radius: 10px; padding: 10px; text-align: center; }
    .price-box { background: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR"): st.session_state.page = "home"; st.rerun()
    st.title(f"🎮 {g['name']}")
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'))
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        st.markdown(f'<div class="price-box">Prix Estimé : {"79.99€" if g.get("total_rating", 0) > 80 else "59.99€"}</div>', unsafe_allow_html=True)
        st.metric("SCORE", f"{int(g.get('total_rating', 0))}/100")
        st.write(g.get('summary', 'Pas de résumé.'))
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker">🚀 GAMETREND 2026 -- LES FILTRES ET LE TOP 3 SONT ARRIVÉS !</div>', unsafe_allow_html=True)

# SECTION VOTE AMÉLIORÉE
st.header("🔥 Le Duel : GTA VI vs CYBERPUNK 2")
cv1, cv2 = st.columns(2)
with cv1: 
    if st.button(f"Voter GTA VI ({st.session_state.vs['j1']})", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with cv2: 
    if st.button(f"Voter CYBERPUNK 2 ({st.session_state.vs['j2']})", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

total_votes = st.session_state.vs['j1'] + st.session_state.vs['j2']
st.write(f"📊 **Total des participants : {total_votes}**")
prog = (st.session_state.vs['j1'] / total_votes) if total_votes > 0 else 0.5
st.progress(prog)

# SECTION TOP 3
st.divider()
st.header("🏆 Top 3 des Jeux du Moment")
top_games = fetch_data("games", "fields name, cover.url, total_rating; sort popularity desc; limit 3; where cover != null;")
if top_games:
    ctop = st.columns(3)
    for i, tg in enumerate(top_games):
        with ctop[i]:
            st.markdown(f'<div class="top-card"><h3>#{i+1} {tg["name"]}</h3></div>', unsafe_allow_html=True)
            st.image("https:" + tg['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)

# SECTION CATALOGUE AVEC FILTRES
st.divider()
st.header("🔍 Catalogue")
c_f1, c_f2, c_f3 = st.columns([2, 1, 1])
with c_f1: search = st.text_input("Rechercher un titre...")
with c_f2: console = st.selectbox("Console :", ["Toutes", "PS5", "Xbox Series X", "Switch", "PC"])
with c_f3: genre = st.selectbox("Genre :", ["Tous", "Action", "RPG", "Sport", "Adventure", "Shooter"])

# Construction de la requête
plats = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
genres_ids = {"Action": 31, "RPG": 12, "Sport": 14, "Adventure": 31, "Shooter": 5}

q = "fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null"
if search: q = f'search "{search}"; ' + q
else:
    if console != "Toutes": q += f" & platforms = ({plats[console]})"
    if genre != "Tous": q += f" & genres = ({genres_ids[genre]})"
    q += "; sort popularity desc;"

games = fetch_data("games", q)
if games:
    cols = st.columns(6)
    for idx, g in enumerate(games):
        with cols[idx%6]:
            if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button("Détails", key=f"g_{g['id']}"):
                st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# --- 6. CHAT & ADMIN ---
st.divider()
st.header("💬 Chat")
if not st.session_state.user_pseudo:
    p_in = st.text_input("Pseudo :")
    if st.button("Ok"): st.session_state.user_pseudo = p_in; st.rerun()
else:
    with st.form("chat", clear_on_submit=True):
        m = st.text_input(f"{st.session_state.user_pseudo} :")
        if st.form_submit_button("Envoyer") and m:
            if not any(w in m.lower() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1][:10]:
    st.write(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'): st.info(f"ADMIN : {c['reply']}")
