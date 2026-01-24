import streamlit as st
import requests
import json
import os
import time
from collections import Counter

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
WISHLIST_FILE = "global_wishlists.json"
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
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE & MENU ---
st.set_page_config(page_title="GameTrend Ultimate", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; }
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR : ADMIN + NAVIGATION
with st.sidebar:
    st.title("🕹️ MENU")
    menu = st.radio("Aller vers :", ["🏠 Accueil", "💬 Communauté", "🔥 Duel de la Semaine", "🎮 Catalogues Jeux"])
    st.divider()
    st.title("🛡️ Admin")
    mon_code = st.text_input("Code Secret", type="password")
    c_est_moi = (mon_code == "628316")

# --- 4. BANDEAU NEWS (TOUJOURS VISIBLE) ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 BIENVENUE SUR GAMETREND 2026 -- UTILISE LE MENU À GAUCHE POUR NAVIGUER -- GTA VI ARRIVE -- </div></div>', unsafe_allow_html=True)
st.title("GameTrend Ultimate")

# --- 5. LOGIQUE DES ONGLETS ---

# --- ONGLET : ACCUEIL ---
if menu == "🏠 Accueil":
    st.header("Bienvenue dans le futur du Gaming")
    st.write("Sélectionnez une catégorie dans le menu de gauche pour commencer l'expérience.")
    st.image("https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=1200", use_container_width=True)

# --- ONGLET : COMMUNAUTÉ ---
elif menu == "💬 Communauté":
    st.header("💬 Espace Discussion")
    if not st.session_state.user_pseudo:
        p = st.text_input("Ton pseudo :")
        if st.button("Rejoindre"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat"):
            m = st.text_input("Message :")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        
        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            st.markdown(f"**{c['user']}** : {c['msg']}")
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span> {c['reply']}</div>", unsafe_allow_html=True)
            if c_est_moi and not c.get('reply'):
                if st.button("Répondre", key=f"r_{idx}"):
                    rep = st.text_input("Ta réponse :", key=f"in_{idx}")
                    if st.button("Valider", key=f"ok_{idx}"):
                        st.session_state.comments[idx]['reply'] = rep
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()

# --- ONGLET : DUEL (LA CASE QUE TU VOULAIS) ---
elif menu == "🔥 Duel de la Semaine":
    st.header("🔥 LE CHOC DES TITRES")
    v1, vs_txt, v2 = st.columns([2, 1, 2])
    with v1: 
        st.subheader("GTA VI")
        if st.button("Voter GTA"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs)
    with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
    with v2:
        st.subheader("CYBERPUNK 2")
        if st.button("Voter CP2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs)
    
    total = st.session_state.vs['j1'] + st.session_state.vs['j2']
    p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
    st.progress(p1 / 100)
    st.write(f"📊 Score actuel : {int(p1)}% vs {int(100-p1)}%")

# --- ONGLET : CATALOGUES ---
elif menu == "🎮 Catalogues Jeux":
    platforms = {"PS5": 167, "Xbox": "169,49", "Switch": 130, "PC": 6}
    platform_choice = st.selectbox("Choisir une console :", list(platforms.keys()))
    
    q = f"fields name, cover.url; where platforms = ({platforms[platform_choice]}) & cover != null; sort total_rating desc; limit 18;"
    jeux = fetch_data("games", q)
    if jeux:
        cols = st.columns(6)
        for j, g in enumerate(jeux):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.write(g['name'][:20])
