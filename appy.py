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

def fetch_games(platform_name):
    token = get_access_token()
    if not token: return []
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": 169, "Switch": 130}
    p_id = platforms.get(platform_name)
    query = f"fields name, cover.url, genres.name; where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;"
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE & ANIMATION ---
st.set_page_config(page_title="GameTrend Pro", layout="wide")

# CSS : Le Splash Screen et le style Store
st.markdown("""
    <style>
    /* Fond noir profond */
    .stApp { background-color: #00051d; color: white; }
    
    /* Animation de chargement */
    #splash-screen {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d;
        display: flex; justify-content: center; align-items: center;
        z-index: 9999;
        animation: fadeOut 3s forwards;
    }
    
    @keyframes fadeOut {
        0% { opacity: 1; visibility: visible; }
        80% { opacity: 1; }
        100% { opacity: 0; visibility: hidden; }
    }

    .loader-text {
        font-family: 'Segoe UI', sans-serif;
        font-size: 30px;
        font-weight: bold;
        color: #0072ce;
        letter-spacing: 5px;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 1; }
        100% { transform: scale(1); opacity: 0.5; }
    }
    
    h2 { color: #0072ce !important; border-bottom: 2px solid #0072ce; padding-bottom: 5px; }
    </style>
    
    <div id="splash-screen">
        <div class="loader-text">GAMETREND...</div>
    </div>
    """, unsafe_allow_html=True)

# Petite attente pour laisser l'animation respirer au premier lancement
if 'loaded' not in st.session_state:
    time.sleep(2.5)
    st.session_state['loaded'] = True

st.title("🎮 PlayStation™ Store")

# --- LE CATALOGUE ---
for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.header(plateforme)
    jeux = fetch_games(plateforme)
    
    if jeux:
        # Grille de 6 colonnes
        cols = st.columns(6)
        for i, game in enumerate(jeux):
            with cols[i % 6]:
                if 'cover' in game:
                    img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big')
                    st.image(img, use_container_width=True)
                st.write(f"**{game['name'][:15]}**")
                if 'genres' in game:
                    st.caption(game['genres'][0]['name'])
    st.divider()
