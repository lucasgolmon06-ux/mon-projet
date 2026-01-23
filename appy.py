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
    
    # ID mis à jour : Xbox Series (169) et ajout Xbox One (49) si besoin
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": "169,49", "Switch": 130}
    p_id = platforms.get(platform_name)
    
    # Requête élargie pour être sûr d'avoir 12 jeux même sans notes
    query = f"fields name, cover.url; where platforms = ({p_id}) & cover != null; sort hypes desc; limit 12;"
    
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend Ultra", layout="wide")

# On garde ton intro incroyable (Ne pas toucher au script d'affichage)
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    #ultra-launch {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d;
        display: flex; justify-content: center; align-items: center;
        z-index: 10000;
        animation: fadeOut 5s forwards;
    }
    .logo-anim { font-family: 'Arial Black', sans-serif; font-size: 50px; font-weight: 900; text-align: center; text-transform: uppercase; }
    .logo-ps { color: #0072ce; text-shadow: 0 0 20px #0072ce; animation: show1 1s forwards; opacity: 0; }
    .logo-xbox { color: #107c10; text-shadow: 0 0 20px #107c10; animation: show2 2s forwards; opacity: 0; }
    .logo-switch { color: #e60012; text-shadow: 0 0 20px #e60012; animation: show3 3s forwards; opacity: 0; }
    .logo-final { color: white; text-shadow: 0 0 30px #ffffff; animation: show4 4s forwards; opacity: 0; }
    @keyframes show1 { 0% { opacity: 0; transform: scale(0.5); } 100% { opacity: 1; transform: scale(1.2); } }
    @keyframes show2 { 0% { opacity: 0; } 50% { opacity: 0; } 100% { opacity: 1; } }
    @keyframes show3 { 0% { opacity: 0; } 66% { opacity: 0; } 100% { opacity: 1; } }
    @keyframes show4 { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
    @keyframes fadeOut { 0%, 90% { opacity: 1; visibility: visible; } 100% { opacity: 0; visibility: hidden; } }
    .cat-title { font-size: 28px; font-weight: bold; color: #0072ce; margin: 20px 0; border-bottom: 2px solid #0072ce; }
    </style>
    <div id="ultra-launch">
        <div class="logo-anim">
            <div class="logo-ps">Sony PlayStation</div>
            <div class="logo-xbox">Microsoft Xbox</div>
            <div class="logo-switch">Nintendo Switch</div>
            <div class="logo-final">GAMETREND UNLOCKED</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if 'started' not in st.session_state:
    time.sleep(4.5)
    st.session_state['started'] = True

st.title("🎮 PlayStation™ Store")

# --- BOUCLE D'AFFICHAGE ---
for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.markdown(f'<div class="cat-title">{plateforme}</div>', unsafe_allow_html=True)
    jeux = fetch_games(plateforme)
    
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"<p style='font-size:12px;'><b>{g['name'][:15]}</b></p>", unsafe_allow_html=True)
    st.divider()
