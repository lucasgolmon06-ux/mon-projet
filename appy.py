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
    
    fields = "fields name, cover.url, genres.name;"
    if search_query:
        query = f'{fields} search "{search_query}"; limit 12;'
    else:
        p_id = platforms.get(platform_name)
        query = f'{fields} where platforms = {p_id} & rating != null & cover != null; sort rating desc; limit 12;'
    
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend PS", layout="wide")

# CSS pour le look PS Store sans bug d'affichage
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h3 { color: #0072ce !important; font-family: 'Segoe UI', sans-serif; }
    .stImage img { border-radius: 10px; border: 2px solid transparent; transition: 0.3s; }
    .stImage img:hover { border-color: #0072ce; transform: scale(1.05); }
    div[data-testid="column"] { padding: 5px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 PlayStation™ Store")
search = st.text_input("🔍 Rechercher un jeu...")

if search:
    jeux = fetch_games(search_query=search)
    cols = st.columns(6)
    for i, game in enumerate(jeux):
        with cols[i % 6]:
            if 'cover' in game:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'))
            st.caption(game['name'])
else:
    # On utilise des colonnes Streamlit natives pour éviter l'affichage de texte bizarre
    for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
        st.subheader(f"✨ {plateforme}")
        jeux = fetch_games(platform_name=plateforme)
        
        if jeux:
            # On crée 2 lignes de 6 pour que ce soit bien rangé
            # Ligne 1
            cols1 = st.columns(6)
            for i in range(min(6, len(jeux))):
                with cols1[i]:
                    game = jeux[i]
                    img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in game else ""
                    st.image(img, use_container_width=True)
                    st.write(f"**{game['name'][:15]}**")
                    if 'genres' in game: st.caption(game['genres'][0]['name'])
            
            # Ligne 2
            if len(jeux) > 6:
                cols2 = st.columns(6)
                for i in range(6, min(12, len(jeux))):
                    with cols2[i-6]:
                        game = jeux[i]
                        img = "https:" + game['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in game else ""
                        st.image(img, use_container_width=True)
                        st.write(f"**{game['name'][:15]}**")
                        if 'genres' in game: st.caption(game['genres'][0]['name'])
        st.divider()

