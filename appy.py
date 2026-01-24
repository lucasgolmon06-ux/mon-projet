Import streamlit as st
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

# --- 2. INITIALISATION SESSION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px;}
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; color: #ffcc00; margin-top:5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. PAGE DE DÉTAILS (PLEIN ÉCRAN) ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR À L'ACCUEIL"):
        st.session_state.page = "home"; st.rerun()
    
    st.markdown(f"<h1 style='text-align:center;'>{g['name']}</h1>", unsafe_allow_html=True)
    col_main, col_side = st.columns([2, 1])
    
    with col_main:
        if 'videos' in g:
            st.subheader("📺 Bande-annonce")
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g:
            st.subheader("📸 Gameplay")
            for ss in g['screenshots'][:3]:
                st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with col_side:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.metric("⭐ NOTE", f"{int(g.get('total_rating', 0))}/100")
        st.write(f"**Résumé :** {g.get('summary', 'Pas de résumé disponible.')}")
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 -- RECHERCHEZ VOS JEUX EN DIRECT -- GTA VI vs CYBERPUNK 2 -- </div></div>', unsafe_allow_html=True)

# --- DUEL ---
st.header("🔥 Duel de la semaine")
c1, c2 = st.columns(2)
with c1: 
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with c2: 
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
t = st.session_state.vs['j1'] + st.session_state.vs['j2']
p = (st.session_state.vs['j1']/t*100) if t>0 else 50
st.progress(p/100)
st.markdown(f"<p style='text-align:center;'>GTA VI: **{int(p)}%** | CP2: **{int(100-p)}%**</p>", unsafe_allow_html=True)

# --- FORUM ---
st.divider()
st.header("💬 Forum Communautaire")
if not st.session_state.user_pseudo:
    st.session_state.user_pseudo = st.text_input("Choisis un pseudo pour discuter :")
else:
    with st.form("chat", clear_on_submit=True):
        m = st.text_input(f"Message ({st.session_state.user_pseudo}) :")
        if st.form_submit_button("Envoyer") and m:
            if not any(word in m.lower().split() for word in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            else: st.error("Message bloqué (insultes).")

for comm in st.session_state.comments[::-1]:
    st.markdown(f"**{comm['user']}** : {comm['msg']}")
    if comm.get('reply'):
        st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span>{comm['reply']}</div>", unsafe_allow_html=True)

# --- RECHERCHE ET CATALOGUE ---
st.divider()
st.header("🎮 Catalogue & Recherche")

# BARRE DE RECHERCHE (Ultra simple)
search = st.text_input("🔍 Rechercher un jeu (ex: FIFA, Elden Ring, Mario...) :")

if search:
    q = f'search "{search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    platforms = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
    p_sel = st.selectbox("Ou voir par plateforme :", list(platforms.keys()))
    q = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where platforms = ({platforms[p_sel]}) & cover != null; sort popularity desc; limit 12;"

jeux = fetch_data("games", q)
if jeux:
    cols = st.columns(6)
    for i, j in enumerate(jeux):
        with cols[i%6]:
            st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button("🔎 Détails", key=f"d_{j['id']}"):
                st.session_state.selected_game = j; st.session_state.page = "details"; st.rerun()

# --- ADMIN ---
st.divider()
with st.expander("🛠️ Admin Panel"):
    if st.text_input("Code Secret", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            st.write(f"{c['user']}: {c['msg']}")
            if st.button("Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            rep = st.text_input("Répondre", key=f"r_{i}")
            if st.button("OK", key=f"b_{i}"):
                st.session_state.comments[i]['reply'] = rep; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
Avec se script je veut pas de couleur est on enleve par console edt on met a la place Les 12 mailleurs jeux AAA les 12 indépendants les 12 meilleurs je rétro
