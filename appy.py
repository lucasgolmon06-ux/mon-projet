import streamlit as st
import requests
import time

# --- CONFIGURATION (Tes clés IGDB) ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    try:
        res = requests.post(auth_url)
        return res.json().get('access_token')
    except: return None

def fetch_games(platform_name):
    token = get_access_token()
    if not token: return []
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": 169, "Switch": 130}
    p_id = platforms.get(platform_name)
    query = f"fields name, cover.url; where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;"
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

# CSS pour l'animation de lancement (Défilement des consoles)
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    
    /* Splash Screen avec défilement */
    #intro-layer {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d;
        display: flex; justify-content: center; align-items: center;
        z-index: 9999;
        animation: fadeOut 4s forwards;
    }

    .rolling-text {
        font-family: 'Segoe UI', sans-serif;
        font-size: 40px;
        font-weight: bold;
        color: #0072ce;
        height: 50px;
        overflow: hidden;
    }

    .rolling-text ul {
        list-style: none;
        padding: 0;
        margin: 0;
        animation: roll 3s steps(4) forwards;
    }

    .rolling-text li {
        height: 50px;
        display: flex;
        justify-content: center;
        align-items: center;
    }

    @keyframes roll {
        0% { transform: translateY(0); }
        100% { transform: translateY(-200px); } /* Fait défiler les 4 noms */
    }

    @keyframes fadeOut {
        0%, 80% { opacity: 1; visibility: visible; }
        100% { opacity: 0; visibility: hidden; }
    }

    h2 { color: #0072ce !important; border-left: 5px solid #0072ce; padding-left: 15px; }
    </style>

    <div id="intro-layer">
        <div class="rolling-text">
            <ul>
                <li>PLAYSTATION</li>
                <li>XBOX</li>
                <li>NINTENDO</li>
                <li>PC MASTER RACE</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Pause pour laisser l'intro finir proprement
if 'init' not in st.session_state:
    time.sleep(3.5)
    st.session_state['init'] = True

st.title("🎮 PlayStation™ Store")

# --- AFFICHAGE DES JEUX ---
for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.header(plateforme)
    jeux = fetch_games(plateforme)
    
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                if 'cover' in g:
                    img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                    st.image(img, use_container_width=True)
                st.write(f"**{g['name'][:15]}**")
    st.divider()
