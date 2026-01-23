import streamlit as st
import requests
import json
import os
from collections import Counter

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")

CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
WISHLIST_FILE = "global_wishlists.json"

# --- 2. FONCTIONS ---
def charger_data(file):
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def sauver_data(file, data):
    with open(file, "w", encoding="utf-8") as f: json.dump(data, f, indent=4)

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(auth_url)
    return res.json().get('access_token')

def fetch(query):
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {get_access_token()}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- 3. INITIALISATION ---
if 'global_w' not in st.session_state: st.session_state.global_w = charger_data(WISHLIST_FILE)
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 4. STYLE (La bande bleue et look sombre) ---
st.markdown("""
    <style>
    .stApp { background-color: #060d23; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 5px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 2px; }
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .stButton>button { border-radius: 5px; background-color: rgba(255,255,255,0.1); color: white; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 5. BANDE DE NEWS ---
st.markdown('<div class="news-ticker"><div class="news-text">🔥 REAL NEWS 2026 : GTA VI CONFIRMÉ POUR L\'AUTOMNE -- SONY RÉVÈLE LA PS5 PRO+ -- LE PROCHAIN ZELDA SERA UN OPEN-WORLD COOP -- </div></div>', unsafe_allow_html=True)

# --- 6. VUE JEU DÉTAILLÉE ---
if st.session_state.selected_game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.selected_game};")
    if res:
        g = res[0]
        if st.button("⬅️ Retour"): st.session_state.selected_game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_720p'), use_container_width=True)
        with c2:
            st.title(g['name'])
            st.write(g.get('summary', "Pas de résumé."))
            if st.button("❤️ Voter"):
                st.session_state.global_w.append(g['name'])
                sauver_data(WISHLIST_FILE, st.session_state.global_w); st.success("Vote enregistré !")
    st.stop()

st.title("🚀 GameTrend Ultimate")

# --- 7. LES 12 TYPES DE JEUX (LES SECTIONS) ---

def afficher_12(titre, query, key_pref):
    st.header(titre)
    jeux = fetch(query)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big') if 'cover' in g else ""
                st.image(img, use_container_width=True)
                if st.button(g['name'][:18], key=f"{key_pref}_{g['id']}"):
                    st.session_state.selected_game = g['id']; st.rerun()
    st.divider()

# 1. TOP 12 AAA (Gros Budgets)
afficher_12("💎 Top 12 - Blockbusters AAA", 
            "fields name, cover.url; where genres != (32) & total_rating > 85 & cover != null; sort total_rating desc; limit 12;", "aaa")

# 2. TOP 12 INDÉPENDANTS
afficher_12("🎨 Top 12 - Pépites Indépendantes", 
            "fields name, cover.url; where genres = (32) & total_rating > 75 & cover != null; sort total_rating desc; limit 12;", "indie")

# 3. TOP 12 COMMUNAUTÉ (Les plus aimés)
if st.session_state.global_w:
    voted = Counter(st.session_state.global_w).most_common(12)
    names = '("' + '","'.join([v[0] for v in voted]) + '")'
    afficher_12("❤️ Top 12 - Aimés par la Communauté", 
                f"fields name, cover.url; where name = {names} & cover != null; limit 12;", "comm")

# 4. TOP 12 PLAYSTATION 5
afficher_12("🎮 Top 12 - PlayStation 5", 
            "fields name, cover.url; where platforms = (167) & cover != null; sort total_rating desc; limit 12;", "ps5")

# 5. TOP 12 XBOX SERIES
afficher_12("🎮 Top 12 - Xbox Series X|S", 
            "fields name, cover.url; where platforms = (169,49) & cover != null; sort total_rating desc; limit 12;", "xbox")

# 6. TOP 12 NINTENDO SWITCH
afficher_12("🎮 Top 12 - Nintendo Switch", 
            "fields name, cover.url; where platforms = (130) & cover != null; sort total_rating desc; limit 12;", "switch")

# 7. TOP 12 PC
afficher_12("🎮 Top 12 - PC Gaming", 
            "fields name, cover.url; where platforms = (6) & cover != null; sort total_rating desc; limit 12;", "pc")
