import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
# Vérifie bien que ces deux clés sont exactement celles de ton dashboard Twitch Dev
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token"
    params = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    res = requests.post(auth_url, params=params)
    if res.status_code != 200:
        st.error(f"Erreur d'authentification : {res.json()}")
        return None
    return res.json().get('access_token')

def fetch_data(endpoint, query):
    token = get_access_token()
    if not token:
        return []
    
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {token}',
        'Content-Type': 'text/plain'
    }
    
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    
    if res.status_code != 200:
        st.error(f"Erreur API IGDB ({res.status_code}) : {res.text}")
        return []
    
    return res.json()

# --- 2. STYLE & INTERFACE ---
st.set_page_config(page_title="GameTrend Fix", layout="wide")
st.title("🎮 GameTrend - Debug Mode")

# Barre de recherche
user_search = st.text_input("🔍 Rechercher un jeu :")

def display_grid(query):
    with st.spinner('Chargement des jeux...'):
        games = fetch_data("games", query)
        if not games:
            st.warning("Aucun résultat renvoyé par l'API.")
            return
        
        cols = st.columns(6)
        for idx, g in enumerate(games):
            with cols[idx % 6]:
                if 'cover' in g:
                    st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(g['name'])
                if st.button("Voir", key=f"btn_{g['id']}"):
                    st.write(g.get('summary', 'Pas de résumé.'))

# --- 3. LOGIQUE D'AFFICHAGE ---
if user_search:
    q = f'search "{user_search}"; fields name, cover.url, summary; limit 12;'
    display_grid(q)
else:
    tab1, tab2 = st.tabs(["🔥 Tendances", "✨ Indés"])
    with tab1:
        display_grid("fields name, cover.url, summary; sort popularity desc; limit 12; where cover != null;")
    with tab2:
        display_grid("fields name, cover.url, summary; where genres = (32); sort popularity desc; limit 12; where cover != null;")
