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

def fetch_games(platform_name):
    token = get_access_token()
    if not token: return []
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    
    # IDs précis : PS5(167), Xbox Series(169), Switch(130), PC(6)
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": 169, "Switch": 130}
    p_id = platforms.get(platform_name)
    
    # LA REQUÊTE : On trie par total_rating (note moyenne) décroissant
    query = f"fields name, cover.url, total_rating; where platforms = {p_id} & cover != null & total_rating != null; sort total_rating desc; limit 12;"
    
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except:
        return []

# --- DESIGN ---
st.set_page_config(page_title="Top 12 Games", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h2 { color: #0072ce !important; border-bottom: 2px solid #0072ce; padding-bottom: 5px; margin-top: 40px; }
    .game-card { text-align: center; margin-bottom: 20px; }
    .rating { color: #ffcc00; font-weight: bold; font-size: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 Classement des 12 Meilleurs Jeux")

# --- AFFICHAGE ---
for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.header(plateforme)
    jeux = fetch_games(plateforme)
    
    if jeux:
        # Création de 6 colonnes pour avoir 2 lignes parfaites de 6 jeux
        cols = st.columns(6)
        
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                # On récupère l'image en grande taille
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                
                # Nom du jeu (limité à 15 caractères pour rester propre)
                st.markdown(f"**{g['name'][:18]}**")
                
                # La Note
                score = round(g.get('total_rating', 0))
                st.markdown(f"<p class='rating'>⭐ {score}/100</p>", unsafe_allow_html=True)
    else:
        st.write("Aucun jeu trouvé pour cette catégorie.")

    st.divider()

