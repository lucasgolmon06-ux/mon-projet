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
    
    # On demande maintenant les genres aussi
    fields = "fields name, cover.url, genres.name;"
    
    if search_query:
        query = f'{fields} search "{search_query}"; limit 12;'
    elif platform_name:
        p_id = platforms.get(platform_name)
        # On demande 12 jeux pour faire 2 lignes de 6
        query = f'{fields} where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;'
    else:
        query = f'{fields} where rating > 80 & cover != null; sort rating desc; limit 12;'
    
    try:
        response = requests.post(url, headers=headers, data=query)
        return response.json()
    except:
        return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend Pro", layout="wide")

# CSS pour réduire les marges et la taille du texte
st.markdown("""
    <style>
    .stImage { border-radius: 10px; }
    p { font-size: 12px !important; margin-bottom: 0px !important; }
    h3 { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 GameTrend : Les Tops")

search = st.text_input("🔍 Rechercher un jeu...")

if search:
    data = fetch_games(search_query=search)
    cols = st.columns(6)
    for i, game in enumerate(data):
        with cols[i % 6]:
            if 'cover' in game:
                img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
            st.write(f"**{game['name'][:20]}**")
else:
    for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
        st.subheader(f"🔥 Top {plateforme}")
        jeux = fetch_games(platform_name=plateforme)
        
        if jeux:
            # Affichage en grille de 6 colonnes
            cols = st.columns(6)
            for i, game in enumerate(jeux):
                with cols[i % 6]: # Le modulo %6 permet de passer à la ligne suivante après 6 jeux
                    if 'cover' in game:
                        img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big')
                        st.image(img, use_container_width=True)
                    
                    # Affichage du nom (court) et du genre
                    st.write(f"**{game['name'][:18]}...**")
                    if 'genres' in game:
                        genre_name = game['genres'][0]['name'] # On prend le premier genre
                        st.caption(f"🏷️ {genre_name}")
        st.divider()
