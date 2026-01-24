import streamlit as st
import requests
import json
import os

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
    if res.status_code != 200:
        return []
    return res.json()

# --- 2. INITIALISATION ---
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("<style>.stApp { background-color: #00051d; color: white; }</style>", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR"):
        st.session_state.page = "home"
        st.rerun()
    st.title(f"🎮 {g['name']}")
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g:
            for ss in g['screenshots'][:2]: st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.write(f"⭐ Score: {int(g.get('total_rating', 0))}/100")
        st.info(g.get('summary', 'Pas de résumé.'))
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.title("🚀 GameTrend Ultimate 2026")

# --- 6. CATALOGUE (CORRECTIONS AFFICHAGE) ---
st.divider()
st.header("🎮 Exploration")

# Barre de recherche
user_search = st.text_input("🔍 Rechercher un jeu précisément :")

def display_grid(query):
    games = fetch_data("games", query)
    if not games:
        st.write("Aucun jeu trouvé ou problème de connexion API.")
        return
    
    # Création de la grille (6 colonnes)
    cols = st.columns(6)
    for idx, g in enumerate(games):
        with cols[idx % 6]:
            if 'cover' in g:
                img_url = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img_url, use_container_width=True)
            else:
                st.write("🖼️ (Pas d'image)")
            
            st.write(f"**{g['name']}**") # Affiche le nom au cas où
            if st.button("Détails", key=f"btn_{g['id']}"):
                st.session_state.selected_game = g
                st.session_state.page = "details"
                st.rerun()

if user_search:
    q = f'search "{user_search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
    display_grid(q)
else:
    t1, t2, t3, t4 = st.tabs(["🏆 Meilleurs AAA", "✨ Pépites Indés", "🆕 Attendus 2026", "🕹️ Légendes Rétro"])
    
    with t1:
        display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where total_rating > 85 & category = 0; sort popularity desc; limit 12;")
    with t2:
        display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where genres = (32) & total_rating > 70; sort popularity desc; limit 12;")
    with t3:
        display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date >= 1735689600; sort popularity desc; limit 12;")
    with t4:
        display_grid("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date < 946684800 & total_rating > 80; sort popularity desc; limit 12;")
