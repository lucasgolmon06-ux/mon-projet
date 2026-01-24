import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

BAD_WORDS = ["merde", "connard", "fdp", "salope", "pute", "encule", "con"]

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
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home" # Gestion des pages
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px;}
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .game-card { background: #001a3d; padding: 10px; border-radius: 10px; text-align: center; margin-bottom: 20px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; color: #ffcc00; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- PAGE DE DÉTAILS DU JEU ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()
    
    st.title(f"🎮 {g['name']}")
    col_img, col_info = st.columns([1, 2])
    
    with col_img:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
    
    with col_info:
        st.subheader("Informations")
        st.write(f"⭐ **Note :** {int(g.get('total_rating', 0))}/100")
        st.write(f"📝 **Résumé :** {g.get('summary', 'Aucun résumé disponible pour ce titre.')}")
        
        if 'videos' in g:
            st.subheader("📺 Bande-annonce")
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
    st.stop() # Arrête le reste de l'exécution pour ne pas afficher l'accueil en bas

# --- PAGE D'ACCUEIL ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 -- CLIQUEZ SUR LES MINI-BOUTONS POUR EXPLORER -- CHAT MODÉRÉ -- GTA VI vs CYBERPUNK 2 -- </div></div>', unsafe_allow_html=True)
st.title("GameTrend Ultimate")

# --- SECTION DUEL ---
st.header("🔥 Le Duel de la Semaine")
v1, vs_txt, v2 = st.columns([2, 1, 2])
with v1:
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
with v2:
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

total = st.session_state.vs['j1'] + st.session_state.vs['j2']
st.progress((st.session_state.vs['j1'] / total) if total > 0 else 0.5)

# --- SECTION COMMUNAUTÉ ---
st.divider()
st.header("💬 Communauté")
if not st.session_state.user_pseudo:
    pseudo = st.text_input("Ton pseudo :")
    if st.button("Rejoindre"): st.session_state.user_pseudo = pseudo; st.rerun()
else:
    with st.form("chat_form", clear_on_submit=True):
        message = st.text_input(f"Message ({st.session_state.user_pseudo}) :")
        if st.form_submit_button("Envoyer"):
            if message:
                words = message.lower().split()
                if any(bad in words for bad in BAD_WORDS):
                    st.error("Mot interdit !")
                else:
                    st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": message, "reply": None})
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1]:
    st.markdown(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'):
        st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span>{c['reply']}</div>", unsafe_allow_html=True)

# --- CATALOGUE ---
st.divider()
st.header("🎮 Catalogues Jeux")
platforms = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
p_choice = st.selectbox("Plateforme :", list(platforms.keys()))

query = f"fields name, cover.url, summary, videos.video_id, total_rating; where platforms = ({platforms[p_choice]}) & cover != null; sort total_rating desc; limit 12;"
jeux = fetch_data("games", query)

if jeux:
    cols = st.columns(6)
    for i, j in enumerate(jeux):
        with cols[i % 6]:
            st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            # MINI BOUTON POUR LA PAGE
            if st.button("🔎 Détails", key=f"details_{j['id']}"):
                st.session_state.selected_game = j
                st.session_state.page = "details"
                st.rerun()

# --- ADMIN ---
st.divider()
with st.expander("🛠️ ACCÈS ADMIN"):
    code = st.text_input("Code :", type="password", key="admin_key")
    if code == "628316":
        if st.button("🗑️ Vider le chat"):
            st.session_state.comments = []; sauver_data(DB_FILE, []); st.rerun()
        for i, c in enumerate(st.session_state.comments):
            st.write(f"**{c['user']}** : {c['msg']}")
            if st.button("❌", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            if not c.get('reply'):
                r = st.text_input("Réponse", key=f"r_{i}")
                if st.button("Envoyer", key=f"b_{i}"):
                    st.session_state.comments[i]['reply'] = r; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
