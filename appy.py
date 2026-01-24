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
    auth_url = "https://id.twitch.tv/oauth2/token"
    params = {'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET, 'grant_type': 'client_credentials'}
    res = requests.post(auth_url, params=params)
    return res.json().get('access_token')

def fetch_data(endpoint, query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}', 'Content-Type': 'text/plain'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})

# --- 3. STYLE CSS (DISCRET PREMIUM) ---
st.set_page_config(page_title="GameTrend", layout="wide")
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top, #000d26 0%, #00050d 100%); color: #e0e0e0; }
    h1, h2 { font-weight: 300; color: #ffffff; letter-spacing: -0.5px; }
    .stButton>button { 
        background: linear-gradient(to bottom right, #003366, #000000); 
        color: white; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; 
    }
    .stButton>button:hover { border-color: #00d4ff; color: #00d4ff; }
    .news-bar { font-size: 0.8rem; color: #666; text-align: center; border-bottom: 1px solid #111; padding: 10px; margin-bottom: 20px; }
    .chat-card { background: rgba(255,255,255,0.03); padding: 10px; border-radius: 5px; margin-bottom: 5px; border-left: 3px solid #003366; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("← Retour"):
        st.session_state.page = "home"; st.rerun()
    st.title(g['name'])
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), width=250)
        st.write(f"**Score:** {int(g.get('total_rating', 0))}/100")
        st.caption(g.get('summary', ''))
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.markdown('<div class="news-bar">GT 2026 // BASE DE DONNÉES TEMPS RÉEL // VOTEZ POUR LE CHOC DES TITANS</div>', unsafe_allow_html=True)

# SECTION DUEL
st.subheader("Duel : GTA VI vs CYBERPUNK 2")
cv1, cv2 = st.columns(2)
with cv1:
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with cv2:
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
t = st.session_state.vs['j1'] + st.session_state.vs['j2']
p = (st.session_state.vs['j1']/t*100) if t>0 else 50
st.progress(p/100)

# SECTION CATALOGUE
st.divider()
user_search = st.text_input("🔍 Rechercher un jeu...", placeholder="Entrez un titre...")

def display_grid(query):
    jeux = fetch_data("games", query)
    if jeux:
        cols = st.columns(6)
        for idx, j in enumerate(jeux):
            with cols[idx%6]:
                if 'cover' in j: st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.write(f"<p style='font-size:0.8rem;'>{j['name']}</p>", unsafe_allow_html=True)
                if st.button("Détails", key=f"d_{j['id']}"):
                    st.session_state.selected_game = j; st.session_state.page = "details"; st.rerun()

if user_search:
    display_grid(f'search "{user_search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12;')
else:
    tabs = st.tabs(["🔥 Tendances", "🆕 Prochainement", "🕹️ Classiques"])
    with tabs[0]: display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; sort popularity desc; limit 12; where cover != null;")
    with tabs[1]: display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date > 1735689600; sort popularity desc; limit 12; where cover != null;")
    with tabs[2]: display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where total_rating > 85; sort popularity desc; limit 12; where cover != null;")

# SECTION FORUM
st.divider()
with st.expander("💬 Forum & Discussions"):
    msg = st.text_input("Votre message :")
    if st.button("Envoyer") and msg:
        st.session_state.comments.append({"user": "Joueur", "msg": msg, "reply": None})
        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    for c in st.session_state.comments[::-1]:
        st.markdown(f"<div class='chat-card'><b>{c['user']}</b>: {c['msg']}</div>", unsafe_allow_html=True)
        if c.get('reply'):
            st.info(f"Admin: {c['reply']}")

# SECTION ADMIN (CACHÉE)
with st.expander("🛠️"):
    if st.text_input("Code", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            st.write(f"{c['msg']}")
            rep = st.text_input("Réponse", key=f"r_{i}")
            if st.button("Valider", key=f"b_{i}"):
                st.session_state.comments[i]['reply'] = rep; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
