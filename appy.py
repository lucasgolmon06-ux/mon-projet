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
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}', 'Content-Type': 'text/plain'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS DISCRET & ÉLÉGANT ---
st.set_page_config(page_title="GameTrend", layout="wide")
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at top, #000a1f 0%, #00050d 100%);
        color: #d1d1d1;
    }
    h1, h2, h3 { color: #ffffff; font-weight: 300; letter-spacing: 1px; }
    .news-ticker {
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: #888; padding: 5px; font-size: 0.8rem; text-align: center; margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(to right, #004e92, #000428);
        color: white; border: 1px solid rgba(255,255,255,0.1); border-radius: 4px;
    }
    /* Style pour la zone des prix */
    .price-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .price-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    .price-row:last-child { border-bottom: none; }
    .platform-name { color: #aaa; font-size: 0.9rem; }
    .platform-price { color: #ffffff; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIQUE PAGES ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("← Retour"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'])
    c1, c2 = st.columns([2, 1])
    
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'), use_container_width=True)
        st.write("### Résumé")
        st.write(g.get('summary', 'Aucune description disponible.'))
        
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        
        # SECTION PRIX PAR PLATEFORME
        st.write("### 💰 Tarifs de sortie")
        st.markdown(f"""
            <div class="price-container">
                <div class="price-row">
                    <span class="platform-name">PlayStation 5</span>
                    <span class="platform-price">79.99€</span>
                </div>
                <div class="price-row">
                    <span class="platform-name">Xbox Series X|S</span>
                    <span class="platform-price">79.99€</span>
                </div>
                <div class="price-row">
                    <span class="platform-name">PC Digital</span>
                    <span class="platform-price">69.99€</span>
                </div>
                <div class="price-row">
                    <span class="platform-name">Nintendo Switch</span>
                    <span class="platform-price">59.99€</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.metric("Score Communauté", f"{int(g.get('total_rating', 0))}/100")
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND // VERSION 2026 // ANALYSE DES PRIX & TENDANCES</div>', unsafe_allow_html=True)

# DUEL
st.subheader("Duel : GTA VI vs CYBERPUNK 2")
v1, v2 = st.columns(2)
with v1: 
    if st.button("Voter GTA VI", use_container_width=True): 
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with v2: 
    if st.button("Voter CYBERPUNK 2", use_container_width=True): 
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

# CATALOGUE
st.divider()
user_search = st.text_input("🔍 Rechercher un jeu...", placeholder="Taper le nom ici...")

def display_grid(query):
    games = fetch_data("games", query)
    if games:
        cols = st.columns(6)
        for idx, g in enumerate(games):
            with cols[idx%6]:
                if 'cover' in g:
                    st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button("Détails & Prix", key=f"b_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

if user_search:
    display_grid(f'search "{user_search}"; fields name, cover.url, summary, videos.video_id, screenshots.url, total_rating; limit 12;')
else:
    t1, t2, t3 = st.tabs(["Populaires", "Attendus 2026", "Rétro"])
    with t1: display_grid("fields name, cover.url, summary, videos.video_id, screenshots.url, total_rating; sort popularity desc; limit 12; where cover != null;")
    with t2: display_grid("fields name, cover.url, summary, videos.video_id, screenshots.url, total_rating; where first_release_date > 1735689600; sort popularity desc; limit 12; where cover != null;")
    with t3: display_grid("fields name, cover.url, summary, videos.video_id, screenshots.url, total_rating; where first_release_date < 946684800; sort popularity desc; limit 12; where cover != null;")

# CHAT DISCRET
st.divider()
with st.expander("💬 Chat Communautaire"):
    user_m = st.text_input("Message :")
    if st.button("Envoyer") and user_m:
        st.session_state.comments.append({"msg": user_m})
        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    for c in st.session_state.comments[::-1]:
        st.markdown(f"<div class='chat-msg'>{c['msg']}</div>", unsafe_allow_html=True)
