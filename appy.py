import streamlit as st
import requests

# --- CONFIGURATION API ---
# REMPLACE LES DEUX LIGNES CI-DESSOUS PAR TES CODES TWITCH
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = '9xvwv4o9mc03ko535ouklmq3abcsi'

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(auth_url)
    return res.json().get('access_token')

def fetch_games(search_query=None):
    token = get_access_token()
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    
    # On exclut les mobiles (34, 39) et on prend PC, PS5, Xbox, Switch...
    platform_whitelist = "6, 167, 169, 130, 48, 49, 137"
    
    if search_query:
        query = f'fields name, cover.url, rating, summary, platforms.name; search "{search_query}"; where platforms = ({platform_whitelist});'
    else:
        query = f'fields name, cover.url, rating, summary, platforms.name; where platforms = ({platform_whitelist}) & rating != null; sort rating desc; limit 20;'
    
    response = requests.post(url, headers=headers, data=query)
    return response.json()

st.set_page_config(page_title="Mon Index Jeux Vidéo", layout="wide")
st.title("🎮 Mon Répertoire de Jeux Vidéo")

search = st.text_input("Rechercher un jeu (PC, Consoles)...")
data = fetch_games(search if search else None)

if data and isinstance(data, list):
    cols = st.columns(4)
    for i, game in enumerate(data):
        with cols[i % 4]:
            if 'cover' in game:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'))
            st.subheader(game['name'])
            if 'rating' in game:
                st.write(f"Note : {int(game['rating'])}/100")

