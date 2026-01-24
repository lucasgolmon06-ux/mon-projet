import streamlit as st
import requests
import json
import os
import time

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

def charger_data(file, default=[]):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return default
    return default

def sauver_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(auth_url)
    return res.json().get('access_token')

def fetch_data(endpoint, query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json()

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("<style>.stApp { background-color: #00051d; color: white; }</style>", unsafe_allow_html=True)

# --- 4. PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR"): st.session_state.page = "home"; st.rerun()
    st.title(g['name'])
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g:
            for ss in g['screenshots'][:2]: st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.write(f"⭐ Score: {int(g.get('total_rating', 0))}/100")
        st.write(g.get('summary', 'Pas de résumé.'))
    st.stop()

# --- 5. ACCUEIL ---
st.title("🚀 GameTrend Ultimate 2026")

# --- 6. CATALOGUE & RECHERCHE (LA CORRECTION EST ICI) ---
st.divider()
st.header("🎮 Catalogue des jeux")

# Barre de recherche globale
search_input = st.text_input("🔍 Chercher un jeu précis :", placeholder="Ex: Elden Ring, Zelda, FIFA...")

def afficher_jeux(query):
    data = fetch_data("games", query)
    if data:
        cols = st.columns(6)
        for i, game in enumerate(data):
            with cols[i % 6]:
                if 'cover' in game:
                    st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                    if st.button("Détails", key=f"btn_{game['id']}"):
                        st.session_state.selected_game = game
                        st.session_state.page = "details"
                        st.rerun()
    else:
        st.warning("Aucun jeu trouvé pour cette catégorie.")

# Logique d'affichage
if search_input:
    # Si on cherche, on ignore les onglets
    q_search = f'search "{search_input}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
    afficher_jeux(q_search)
else:
    # Sinon, on utilise les onglets avec des requêtes uniques
    t1, t2, t3, t4 = st.tabs(["🏆 Meilleurs AAA", "✨ Pépites Indés", "🆕 Sorties 2026", "🕹️ Légendes Rétro"])
    
    with t1:
        # AAA récents et bien notés (category 0 = main game)
        afficher_jeux("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where total_rating > 80 & category = 0; sort popularity desc; limit 12;")
    
    with t2:
        # INDÉS (genre 32)
        afficher_jeux("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where genres = (32) & total_rating > 60; sort popularity desc; limit 12;")
        
    with t3:
        # ATTENDUS (dates en 2026 : timestamp > 1767225600)
        afficher_jeux("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date >= 1735689600; sort popularity desc; limit 12;")
        
    with t4:
        # RÉTRO (avant l'an 2000)
        afficher_jeux("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date < 946684800 & total_rating > 75; sort popularity desc; limit 12;")

# --- 7. FORUM ---
st.divider()
st.subheader("💬 Forum")
# ... (ton code forum habituel ici)
