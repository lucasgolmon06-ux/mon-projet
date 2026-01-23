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
st.set_page_config(page_title="GameTrend", layout="wide")

# CSS simple pour le fond et les titres
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h2 { color: #0072ce !important; font-size: 24px !important; }
    .stCaption { color: #b0b0b0 !important; font-size: 10px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 PlayStation™ Store")

# On boucle sur les consoles
for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.header(plateforme)
    jeux = fetch_games(plateforme)
    
    if jeux:
        # On crée une grille de 6 colonnes (pour PC)
        # Sur mobile, Streamlit va essayer de les réduire
        cols = st.columns(6)
        
        for i, g in enumerate(jeux):
            # On utilise le modulo % 6 pour remplir les 2 lignes (6 + 6 = 12)
            with cols[i % 6]:
                if 'cover' in g:
                    img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                    st.image(img, use_container_width=True)
                
                # Nom du jeu en gras et petit
                st.write(f"**{g['name'][:15]}**")
                
                # Genre en petit
                if 'genres' in g:
                    st.caption(g['genres'][0]['name'])
    st.divider()

