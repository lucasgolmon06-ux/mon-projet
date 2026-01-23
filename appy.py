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
    except:
        return None

def fetch_games(search_query=None, platform_name=None):
    token = get_access_token()
    if not token: return []
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": 169, "Switch": 130}
    
    if search_query:
        query = f'fields name, cover.url; search "{search_query}"; limit 12;'
    elif platform_name:
        p_id = platforms.get(platform_name)
        query = f'fields name, cover.url; where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;'
    else:
        query = 'fields name, cover.url; where rating > 80 & cover != null; sort rating desc; limit 12;'
    
    try:
        response = requests.post(url, headers=headers, data=query)
        return response.json()
    except:
        return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

st.title("🎮 Tendances Jeux Vidéo")
search = st.text_input("🔍 Rechercher un jeu...")

if search:
    data = fetch_games(search_query=search)
    # 6 colonnes pour que les résultats de recherche soient petits aussi
    cols = st.columns(6)
    for i, game in enumerate(data):
        with cols[i % 6]:
            if 'cover' in game:
                img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
            st.caption(game['name'])
else:
    for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
        st.subheader(f"🔥 {plateforme}")
        jeux = fetch_games(platform_name=plateforme)
        if jeux:
            # ICI ON MET 6 COLONNES POUR RÉDUIRE LA TAILLE
            cols = st.columns(6)
            for i, game in enumerate(jeux[:6]):
                with cols[i]:
                    if 'cover' in game:
                        # On utilise l'image format cover_big mais dans une colonne étroite
                        img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big')
                        st.image(img, use_container_width=True)
                    st.caption(game['name'])
        st.divider()
