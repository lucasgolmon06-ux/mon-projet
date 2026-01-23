import streamlit as st
import requests
import time

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

def fetch_data(query):
    token = get_access_token()
    if not token: return []
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend", layout="wide")

# (L'intro reste la même, je la raccourcis ici pour la lisibilité)
st.markdown("""<style>.stApp { background-color: #00051d; color: white; }</style>""", unsafe_allow_html=True)

# --- HEADER AVEC CONSEILLER ---
head_col1, head_col2 = st.columns([2, 1.5])

with head_col1:
    st.title("GameTrend Pro")

with head_col2:
    style_input = st.text_input("💡 Style de jeu recherché...", placeholder="Ex: Cyberpunk, Dark Souls...", key="style_search")

# --- SUGGESTIONS INTELLIGENTES (SANS LE JEU CITÉ) ---
if style_input:
    st.markdown(f"### ✨ Si tu aimes '{style_input}', essaie ceux-là :")
    
    # On cherche des jeux par mots-clés mais on EXCLUT le nom exact pour éviter les doublons/éditions
    # On filtre aussi par note > 75 pour la qualité
    q_style = f'search "{style_input}"; fields name, cover.url, total_rating; where cover != null & total_rating > 75 & name != "{style_input}" & name !~ *"{style_input}"*; limit 4;'
    suggestions = fetch_data(q_style)
    
    if suggestions:
        s_cols = st.columns(4)
        for idx, s in enumerate(suggestions):
            with s_cols[idx]:
                s_img = "https:" + s['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(s_img, use_container_width=True)
                st.caption(f"{s['name']} (⭐ {round(s['total_rating'])}/100)")
    else:
        # Si la recherche par nom exclut tout, on tente une recherche plus large
        st.write("On cherche des pépites similaires...")
    st.divider()

# --- RECHERCHE CLASSIQUE ---
search_query = st.text_input("🔍 Recherche par nom...")
if search_query:
    q = f'search "{search_query}"; fields name, cover.url, total_rating; where cover != null; limit 6;'
    results = fetch_data(q)
    if results:
        cols = st.columns(6)
        for i, g in enumerate(results):
            with cols[i]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.write(f"**{g['name'][:15]}**")
    st.divider()

# --- TOP 12 PAR CONSOLE ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    st.header(f"Top 12 {name}")
    query = f"fields name, cover.url, total_rating; where platforms = ({p_id}) & cover != null & total_rating != null; sort total_rating desc; limit 12;"
    jeux = fetch_data(query)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                st.markdown(f"<p style='color:#ffcc00;'>⭐ {round(g['total_rating'])}/100</p>", unsafe_allow_html=True)
    st.divider()

