import streamlit as st
import requests
import json
import os
import time

# --- CONFIGURATION API ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# --- SYSTÈME DE SAUVEGARDE DES COMMENTAIRES ---
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comms, f, indent=4)

if 'comments' not in st.session_state:
    st.session_state.comments = charger_comms()

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    try:
        res = requests.post(auth_url)
        return res.json().get('access_token')
    except: return None

def fetch_data(query):
    token = get_access_token()
    if not token: return []
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE & DESIGN ---
st.set_page_config(page_title="GameTrend Ultra", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    
    /* Animation Intro Logos */
    #intro-screen {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d; display: flex; justify-content: center; align-items: center;
        z-index: 10000; animation: fadeOut 5s forwards;
    }
    .logo-img { position: absolute; width: 250px; opacity: 0; transform: scale(0.8); }
    .ps { animation: seq 1.5s 0.5s forwards; }
    .xb { animation: seq 1.5s 2s forwards; }
    .nt { animation: seq 1.5s 3.5s forwards; }
    @keyframes seq { 0% { opacity:0; } 50% { opacity:1; transform:scale(1); } 100% { opacity:0; transform:scale(1.1); } }
    @keyframes fadeOut { 0%, 90% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }

    /* Commentaires */
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .msg-admin { background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; }
    
    /* Hover Images */
    .stImage:hover { transform: scale(1.05); transition: 0.3s; cursor: pointer; }
    </style>

    <div id="intro-screen">
        <img class="logo-img ps" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png">
        <img class="logo-img xb" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png">
        <img class="logo-img nt" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Nintendo_Switch_logo_and_wordmark.svg/1280px-Nintendo_Switch_logo_and_wordmark.svg.png">
    </div>
""", unsafe_allow_html=True)

if 'loaded' not in st.session_state:
    time.sleep(5.0)
    st.session_state['loaded'] = True

# --- HEADER & BOUTON COMMUNAUTÉ ---
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.title("GameTrend Pro")
with h_col2:
    ouvrir_comm = st.toggle("💬 Espace Communauté")

# --- ESPACE COMMUNAUTÉ ---
if ouvrir_comm:
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("f_comm", clear_on_submit=True):
            p = st.text_input("Pseudo")
            m = st.text_area("Message")
            if st.form_submit_button("Envoyer"):
                if p and m:
                    st.session_state.comments.append({"user": p, "msg": m, "reply": None})
                    sauver_comms(st.session_state.comments)
                    st.rerun()
        st.divider()
        code_admin = st.text_input("🔑 Code Admin", type="password")
        is_admin = (code_admin == "1234") # TON CODE ICI
    with c2:
        for i, c in enumerate(reversed(st.session_state.comments)):
            idx = len(st.session_state.comments) - 1 - i
            st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> : {c["msg"]}</div>', unsafe_allow_html=True)
            if c['reply']:
                st.markdown(f'<div class="msg-admin"><b>Auteur</b> : {c["reply"]}</div>', unsafe_allow_html=True)
            elif is_admin:
                r = st.text_input(f"Répondre à {c['user']}", key=f"ans_{idx}")
                if st.button("Répondre", key=f"btn_{idx}"):
                    st.session_state.comments[idx]['reply'] = r
                    sauver_comms(st.session_state.comments)
                    st.rerun()
    st.divider()

# --- RECHERCHE DE STYLE ---
style_in = st.text_input("💡 Propose-moi des jeux dans le style de...", placeholder="Ex: Cyberpunk, Elden Ring...")
if style_in:
    st.subheader(f"Inspirés par {style_in}")
    q_style = f'search "{style_in}"; fields name, cover.url, total_rating; where cover != null & total_rating > 75 & name !~ *"{style_in}"*; limit 4;'
    res = fetch_data(q_style)
    if res:
        cols = st.columns(4)
        for i, s in enumerate(res):
            with cols[i]:
                st.image("https:" + s['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(f"{s['name']} (⭐ {round(s['total_rating'])}/100)")
    st.divider()

# --- TOP 12 PAR CONSOLE ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    st.header(f"Top 12 {name}")
    jeux = fetch_data(f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null & total_rating != null; sort total_rating desc; limit 12;")
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                st.markdown(f"<p style='color:#ffcc00;'>⭐ {round(g['total_rating'])}/100</p>", unsafe_allow_html=True)
    st.divider()
