import streamlit as st
import requests

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

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend Mobile", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    
    /* LE SECRET : Conteneur qui défile horizontalement */
    .scroll-container {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        gap: 12px;
        padding: 10px 5px;
        scrollbar-width: none; /* Cache la barre sur Firefox */
    }
    .scroll-container::-webkit-scrollbar { display: none; } /* Cache la barre sur Chrome/Safari */

    .game-card {
        flex: 0 0 140px; /* Force chaque jeu à faire 140px de large */
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 8px;
        text-align: center;
    }

    .game-card img {
        width: 100%;
        border-radius: 6px;
        border: 1px solid #0072ce;
    }

    .game-title {
        font-size: 11px;
        font-weight: bold;
        margin-top: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: #efefef;
    }
    
    h2 { color: #0072ce !important; font-size: 22px !important; margin-left: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 PlayStation™ Store")

for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.markdown(f"<h2>{plateforme}</h2>", unsafe_allow_html=True)
    jeux = fetch_games(plateforme)
    
    if jeux:
        # On crée le bandeau défilant
        html_content = '<div class="scroll-container">'
        for g in jeux:
            img_url = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in g else ""
            html_content += f'''
                <div class="game-card">
                    <img src="{img_url}">
                    <div class="game-title">{g['name']}</div>
                </div>
            '''
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)
