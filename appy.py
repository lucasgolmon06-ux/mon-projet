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
    
    # IDs : PS5(167), Xbox(169,49), Switch(130), PC(6)
    platforms = {"PC": 6, "PS5": 167, "Xbox Series": "169,49", "Switch": 130}
    p_id = platforms.get(platform_name)
    
    # Requête pour les 12 mieux notés (Rating)
    query = f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null & total_rating != null; sort total_rating desc; limit 12;"
    
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except:
        return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

# Style PS Store classique (sans animations de logos)
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h2 { color: #0072ce !important; border-bottom: 2px solid #0072ce; padding-bottom: 5px; }
    .rating-badge { color: #ffcc00; font-weight: bold; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 Top 12 des Meilleurs Jeux")

# --- BOUCLE D'AFFICHAGE ---
for plateforme in ["PS5", "Xbox Series", "Switch", "PC"]:
    st.header(plateforme)
    jeux = fetch_games(plateforme)
    
    if jeux:
        # Grille de 6 colonnes pour avoir 2 lignes de 6 (total 12)
        cols = st.columns(6)
        
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                # Image de couverture
                if 'cover' in g:
                    img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                    st.image(img, use_container_width=True)
                
                # Titre du jeu
                st.markdown(f"**{g['name'][:15]}**")
                
                # Note avec étoile
                note = round(g.get('total_rating', 0))
                st.markdown(f"<p class='rating-badge'>⭐ {note}/100</p>", unsafe_allow_html=True)
    st.divider()
