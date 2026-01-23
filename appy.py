import streamlit as st
import requests

# --- CONFIGURATION TWITCH ---
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
    
    fields = "fields name, cover.url, genres.name;"
    if search_query:
        query = f'{fields} search "{search_query}"; limit 12;'
    else:
        p_id = platforms.get(platform_name)
        # On récupère 12 jeux pour faire les 2 lignes
        query = f'{fields} where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;'
    
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="PlayStation Store", layout="wide")

# CSS pour réduire la taille et supprimer les scripts visibles
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    /* Titres des catégories */
    h2 { font-size: 20px !important; color: #0072ce !important; margin-top: 30px !important; }
    /* Réduction de l'espace entre les colonnes */
    div[data-testid="column"] { padding: 2px !important; }
    /* Style des noms de jeux */
    .game-name { font-size: 12px !important; font-weight: bold; margin-bottom: 0px; }
    .game-genre { font-size: 10px !important; color: #b0b0b0; }
    /* Arrondir les affiches */
    .stImage img { border-radius: 6px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 PlayStation™ Store")
search = st.text_input("", placeholder="🔍 Rechercher un jeu...")

if search:
    jeux = fetch_games(search_query=search)
    cols = st.columns(6)
    for i, game in enumerate(jeux):
        with cols[i % 6]:
            if 'cover' in game:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'))
            st.caption(game['name'])
else:
    # Pour chaque console : 2 lignes de 6
    for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
        st.header(f"✨ {plateforme}")
        jeux = fetch_games(platform_name=plateforme)
        
        if jeux:
            # LIGNE 1
            c1 = st.columns(6)
            for i in range(min(6, len(jeux))):
                with c1[i]:
                    g = jeux[i]
                    img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in g else ""
                    st.image(img, use_container_width=True)
                    st.markdown(f"<p class='game-name'>{g['name'][:15]}</p>", unsafe_allow_html=True)
                    if 'genres' in g: 
                        st.markdown(f"<p class='game-genre'>{g['genres'][0]['name']}</p>", unsafe_allow_html=True)
            
            # LIGNE 2
            if len(jeux) > 6:
                c2 = st.columns(6)
                for i in range(6, min(12, len(jeux))):
                    with c2[i-6]:
                        g = jeux[i]
                        img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in g else ""
                        st.image(img, use_container_width=True)
                        st.markdown(f"<p class='game-name'>{g['name'][:15]}</p>", unsafe_allow_html=True)
                        if 'genres' in g: 
                            st.markdown(f"<p class='game-genre'>{g['genres'][0]['name']}</p>", unsafe_allow_html=True)
        st.divider()

