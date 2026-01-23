import streamlit as st
import requests

# --- CONFIGURATION TWITCH / IGDB ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    try:
        res = requests.post(auth_url)
        return res.json().get('access_token')
    except:
        return None

def fetch_games(search_query=None, platform_name=None):
    token = get_access_token()
    if not token: return []
    
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    
    # IDs des plateformes : PC (6), PS5 (167), Xbox Series (169), Switch (130)
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": 169, "Switch": 130}
    
    if search_query:
        query = f'fields name, cover.url, rating; search "{search_query}"; limit 12;'
    elif platform_name:
        p_id = platforms.get(platform_name)
        query = f'fields name, cover.url, rating; where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 8;'
    else:
        query = 'fields name, cover.url, rating; where rating > 80 & cover != null; sort rating desc; limit 12;'
    
    try:
        response = requests.post(url, headers=headers, data=query)
        return response.json()
    except:
        return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

st.title("🎮 Tendances Jeux Vidéo")

# Barre de recherche en haut
search = st.text_input("🔍 Rechercher un jeu spécifique...")

if search:
    data = fetch_games(search_query=search)
    st.subheader(f"Résultats pour : {search}")
    cols = st.columns(4)
    for i, game in enumerate(data):
        with cols[i % 4]:
            if 'cover' in game:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'))
            st.caption(game['name'])
else:
    # --- AFFICHAGE DES TENDANCES PAR PLATEFORME ---
    for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
        st.header(f"🔥 Tendances {plateforme}")
        jeux = fetch_games(platform_name=plateforme)
        
        if jeux:
            cols = st.columns(4)
            for i, game in enumerate(jeux[:4]): # On affiche les 4 premiers
                with cols[i]:
                    if 'cover' in game:
                        st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'))
                    st.subheader(game['name'])
                    if 'rating' in game:
                        st.write(f"⭐ {int(game['rating'])}/100")
        st.divider()

