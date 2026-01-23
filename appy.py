import streamlit as st
import requests
import time

# --- CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'

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
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    
    /* Intro logos */
    #intro-screen {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d; display: flex; justify-content: center; align-items: center;
        z-index: 10000; animation: fadeOutContainer 5s forwards;
    }
    .logo-container { position: relative; width: 250px; height: 250px; display: flex; justify-content: center; align-items: center; }
    .logo-img { position: absolute; width: 100%; height: auto; opacity: 0; transform: scale(0.8); }
    .ps-logo { animation: logoSequence 1.5s 0.5s forwards; }
    .xb-logo { animation: logoSequence 1.5s 2s forwards; }
    .nt-logo { animation: logoSequence 1.5s 3.5s forwards; }

    @keyframes logoSequence {
        0% { opacity: 0; transform: scale(0.8); }
        50% { opacity: 1; transform: scale(1); }
        100% { opacity: 0; transform: scale(1.1); }
    }
    @keyframes fadeOutContainer {
        0%, 90% { opacity: 1; visibility: visible; }
        100% { opacity: 0; visibility: hidden; }
    }

    /* Style Suggestion */
    .suggest-box {
        background: rgba(0, 114, 206, 0.1);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #0072ce;
        margin-bottom: 20px;
    }
    </style>

    <div id="intro-screen">
        <div class="logo-container">
            <img class="logo-img ps-logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png">
            <img class="logo-img xb-logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png">
            <img class="logo-img nt-logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Nintendo_Switch_logo_and_wordmark.svg/1280px-Nintendo_Switch_logo_and_wordmark.svg.png">
        </div>
    </div>
    """, unsafe_allow_html=True)

if 'loaded' not in st.session_state:
    time.sleep(5.0)
    st.session_state['loaded'] = True

# --- HEADER AVEC CONSEILLER ---
head_col1, head_col2 = st.columns([2, 1.5])

with head_col1:
    st.title("GameTrend Pro")

with head_col2:
    style_input = st.text_input("💡 Propose-moi des jeux dans le style de...", placeholder="Ex: Claire Obscur, Souls, Cyberpunk...", key="style_search")

# --- AFFICHAGE DES SUGGESTIONS DE STYLE ---
if style_input:
    st.markdown(f"### ✨ Inspirés par '{style_input}'")
    # On cherche des jeux qui correspondent à la description ou au nom
    q_style = f'search "{style_input}"; fields name, cover.url, total_rating; where cover != null; limit 4;'
    suggestions = fetch_data(q_style)
    
    if suggestions:
        s_cols = st.columns(4)
        for idx, s in enumerate(suggestions):
            with s_cols[idx]:
                s_img = "https:" + s['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(s_img, use_container_width=True)
                st.caption(s['name'])
    st.divider()

# --- RECHERCHE CLASSIQUE ---
search_query = st.text_input("🔍 Recherche rapide par nom...")
if search_query:
    q = f'search "{search_query}"; fields name, cover.url, total_rating, summary; where cover != null; limit 6;'
    results = fetch_data(q)
    if results:
        cols = st.columns(6)
        for i, g in enumerate(results):
            with cols[i]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.write(f"**{g['name'][:15]}**")
    st.divider()

# --- TOP 12 PAR CONSOLE ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    st.header(f"Top 12 {name}")
    query = f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null & total_rating != null; sort total_rating desc; limit 12;"
    jeux = fetch_data(query)
    
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                note = round(g.get('total_rating', 0))
                st.markdown(f"<p style='color:#ffcc00;'>⭐ {note}/100</p>", unsafe_allow_html=True)
    st.divider()

