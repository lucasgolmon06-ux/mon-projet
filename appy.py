import streamlit as st
import requests

# --- CONFIGURATION PRIVÉE ---
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

# --- STYLE PS STORE ---
st.set_page_config(page_title="GameTrend", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    /* Masquer le menu Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    .category-title {
        font-size: 24px;
        font-weight: bold;
        color: #0072ce;
        margin: 30px 0 10px 10px;
        font-family: 'Segoe UI', sans-serif;
    }

    /* GRILLE : 3 colonnes sur mobile, 6 colonnes sur PC */
    .game-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        padding: 10px;
    }
    @media (min-width: 1024px) {
        .game-grid { grid-template-columns: repeat(6, 1fr); }
    }

    .card {
        background: rgba(255,255,255,0.05);
        padding: 5px;
        border-radius: 10px;
        text-align: center;
        transition: 0.3s;
    }
    .card:hover { border: 1px solid #0072ce; transform: scale(1.02); }
    .card img { width: 100%; border-radius: 8px; }
    .card p {
        font-size: 11px;
        margin-top: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 GameTrend Store")

for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.markdown(f'<div class="category-title">{plateforme}</div>', unsafe_allow_html=True)
    jeux = fetch_games(plateforme)
    
    if jeux:
        html_content = '<div class="game-grid">'
        for g in jeux:
            img_url = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
            html_content += f'''
                <div class="card">
                    <img src="{img_url}">
                    <p>{g['name']}</p>
                </div>
            '''
        html_content += '</div>'
        st.markdown(html_content, unsafe_allow_html=True)


