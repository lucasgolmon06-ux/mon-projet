import streamlit as st
import requests

# --- CONFIGURATION (Tes codes Twitch) ---
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
    # Requête propre : on ne demande que le nécessaire
    query = f"fields name, cover.url; where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;"
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- DESIGN DU SITE ---
st.set_page_config(page_title="GameStore", layout="wide")

# CSS pour forcer l'affichage en grille même sur mobile
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    /* Cache les éléments inutiles */
    #MainMenu, footer, header {visibility: hidden;}
    
    .category-title {
        font-size: 22px;
        font-weight: bold;
        color: #0072ce;
        margin: 20px 0px 10px 10px;
        border-left: 4px solid #0072ce;
        padding-left: 10px;
    }
    
    /* Conteneur Grille : 3 colonnes sur mobile, 6 sur PC */
    .main-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr); 
        gap: 10px;
        padding: 10px;
    }
    @media (min-width: 800px) {
        .main-grid { grid-template-columns: repeat(6, 1fr); }
    }
    
    .game-card {
        text-align: center;
    }
    .game-card img {
        width: 100%;
        border-radius: 8px;
        border: 1px solid #1a1f3d;
    }
    .game-card p {
        font-size: 11px;
        margin-top: 5px;
        color: white;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 PlayStation™ Store")

for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.markdown(f'<div class="category-title">{plateforme}</div>', unsafe_allow_html=True)
    jeux = fetch_games(plateforme)
    
    if jeux:
        # Construction de la grille sans passer par les colonnes Streamlit (qui buggent sur mobile)
        html_grid = '<div class="main-grid">'
        for g in jeux:
            # On nettoie l'URL de l'image
            img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in g else ""
            
            html_grid += f'''
            <div class="game-card">
                <img src="{img}">
                <p>{g['name'][:15]}</p>
            </div>
            '''
        html_grid += '</div>'
        st.markdown(html_grid, unsafe_allow_html=True)

