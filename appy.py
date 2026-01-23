import streamlit as st
import requests
import json
import os
import time

# --- CONFIGURATION API ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# (Fonctions de base inchangées)
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(comms, f, indent=4)

if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None

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
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend Ultra", layout="wide")
st.markdown("""<style>.stApp { background-color: #00051d; color: white; }</style>""", unsafe_allow_html=True)

# (Intro Logos ici...)

# --- HEADER & COMMUNAUTÉ ---
h_col1, h_col2 = st.columns([3, 1])
with h_col1: st.title("GameTrend Pro")
with h_col2: ouvrir_comm = st.toggle("💬 Communauté")

# (Espace Communauté ici...)

# --- RECHERCHE ---
search_query = st.text_input("🔍 Recherche précise...")
style_in = st.text_input("💡 Style de jeu...")

# --- FILTRES DYNAMIQUES PAR CONSOLE ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    st.divider()
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.header(f"Top 12 {name}")
    with col_t2:
        choix = st.selectbox(f"Filtrer {name} par :", 
                              ["Meilleures notes", "Coup de ❤️ Communauté", "Gros Budgets (AAA)", "Jeux Indépendants"],
                              key=f"filter_{name}")

    base_where = f"platforms = ({p_id}) & cover != null"
    
    if choix == "Meilleures notes":
        # Note globale (Critiques + Joueurs)
        q = f"fields name, cover.url, total_rating; where {base_where} & total_rating != null; sort total_rating desc; limit 12;"
    
    elif choix == "Coup de ❤️ Communauté":
        # On utilise 'rating' (note des joueurs uniquement) et on trie par ceux qui ont le plus d'avis
        q = f"fields name, cover.url, rating; where {base_where} & rating != null & rating_count > 50; sort rating desc; limit 12;"
    
    elif choix == "Gros Budgets (AAA)":
        # Exclure le thème Indie (31)
        q = f"fields name, cover.url, total_rating; where {base_where} & themes != (31) & total_rating > 70; sort total_rating desc; limit 12;"
    
    else: # Indépendants
        # Thème Indie (31) uniquement
        q = f"fields name, cover.url, total_rating; where {base_where} & themes = (31); sort total_rating desc; limit 12;"

    jeux = fetch_data(q)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                # Affichage de la note selon le filtre
                note_val = g.get('rating') if choix == "Coup de ❤️ Communauté" else g.get('total_rating')
                note_final = round(note_val) if note_val else "N/A"
                st.markdown(f"<p style='color:#ffcc00;'>⭐ {note_final}/100</p>", unsafe_allow_html=True)

