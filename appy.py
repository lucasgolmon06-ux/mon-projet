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

def fetch_games(platform_name=None, search_query=None):
    token = get_access_token()
    if not token: return []
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": 169, "Switch": 130}
    
    fields = "fields name, cover.url, genres.name, first_release_date;"
    if search_query:
        query = f'{fields} search "{search_query}"; limit 12;'
    else:
        p_id = platforms.get(platform_name)
        query = f'{fields} where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 15;'
    
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE STYLE PS STORE ---
st.set_page_config(page_title="PS Store Clone", layout="wide")

# CSS pour le look PlayStation (Fond sombre, défilement horizontal, cartes arrondies)
st.markdown("""
    <style>
    /* Fond sombre PS Store */
    .stApp {
        background-color: #00051d;
        color: white;
    }
    /* Conteneur pour le défilement horizontal */
    .row-container {
        display: flex;
        overflow-x: auto;
        white-space: nowrap;
        padding-bottom: 20px;
        gap: 15px;
    }
    /* Style des cartes de jeux */
    .game-card {
        flex: 0 0 auto;
        width: 160px;
        background: #1a1f3d;
        border-radius: 12px;
        padding: 10px;
        transition: transform 0.3s;
    }
    .game-card:hover {
        transform: scale(1.05);
        border: 2px solid #0072ce;
    }
    .game-img {
        width: 100%;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .game-title {
        font-size: 14px;
        font-weight: bold;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .game-genre {
        font-size: 11px;
        color: #b0b0b0;
    }
    /* Cacher la barre de défilement pour un look plus propre */
    .row-container::-webkit-scrollbar {
        height: 6px;
    }
    .row-container::-webkit-scrollbar-thumb {
        background: #0072ce;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 PlayStation™ Store")

search = st.text_input("🔍 Rechercher dans le store...", placeholder="Jeux, extensions...")

if search:
    jeux = fetch_games(search_query=search)
    cols = st.columns(6)
    for i, game in enumerate(jeux):
        with cols[i % 6]:
            if 'cover' in game:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'))
            st.caption(game['name'])
else:
    # On boucle sur les consoles pour créer les rangées
    for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
        st.subheader(f"{plateforme}")
        jeux = fetch_games(platform_name=plateforme)
        
        if jeux:
            # On utilise du HTML pur pour le défilement horizontal type "Store"
            html_content = '<div class="row-container">'
            for game in jeux:
                img_url = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in game else ""
                genre = game['genres'][0]['name'] if 'genres' in game else "Jeu"
                
                html_content += f'''
                <div class="game-card">
                    <img src="{img_url}" class="game-img">
                    <div class="game-title">{game['name'][:18]}</div>
                    <div class="game-genre">{genre}</div>
                </div>
                '''
            html_content += '</div>'
            st.markdown(html_content, unsafe_allow_html=True)
