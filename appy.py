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
if 'page' not in st.session_state: st.session_state.page = "Accueil"
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend Ultimate", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .menu-card { 
        background: linear-gradient(145deg, #001a3d, #000a2d);
        border: 2px solid #0072ce;
        border-radius: 15px;
        padding: 40px;
        text-align: center;
        transition: 0.3s;
        cursor: pointer;
        margin-bottom: 20px;
    }
    .menu-card:hover { transform: scale(1.05); border-color: #ffcc00; box-shadow: 0 0 20px #0072ce; }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; }
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION & ADMIN ---
with st.sidebar:
    st.title("🛡️ Admin")
    mon_code = st.text_input("Code Secret", type="password")
    c_est_moi = (mon_code == "628316")
    if st.button("🏠 Retour Accueil"): st.session_state.page = "Accueil"; st.rerun()

# BANDEAU NEWS
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 : CLIQUE SUR UNE CASE POUR EXPLORER -- GTA VI vs CYBERPUNK 2 -- FORUM DISPO -- </div></div>', unsafe_allow_html=True)
st.title("🎮 GameTrend Ultimate")

# --- 5. LOGIQUE DES PAGES ---

# --- PAGE ACCUEIL (LES CASES) ---
if st.session_state.page == "Accueil":
    st.subheader("Choisissez votre destination :")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="menu-card"><h2>💬</h2><h3>FORUM</h3><p>Discute avec la communauté</p></div>', unsafe_allow_html=True)
        if st.button("Ouvrir le Forum", use_container_width=True):
            st.session_state.page = "Forum"; st.rerun()
            
    with col2:
        st.markdown('<div class="menu-card"><h2>🔥</h2><h3>MODE DUEL</h3><p>Vote pour ton jeu préféré</p></div>', unsafe_allow_html=True)
        if st.button("Lancer le Duel", use_container_width=True):
            st.session_state.page = "Duel"; st.rerun()
            
    with col3:
        st.markdown('<div class="menu-card"><h2>🎮</h2><h3>CATALOGUES</h3><p>Découvre les tops jeux</p></div>', unsafe_allow_html=True)
        if st.button("Voir les Catalogues", use_container_width=True):
            st.session_state.page = "Catalogues"; st.rerun()

# --- PAGE FORUM ---
elif st.session_state.page == "Forum":
    st.header("💬 Forum Communauté")
    if st.button("⬅️"): st.session_state.page = "Accueil"; st.rerun()
    
    if not st.session_state.user_pseudo:
        p = st.text_input("Pseudo :")
        if st.button("Entrer"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat"):
            m = st.text_input(f"Message ({st.session_state.user_pseudo})")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        
        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            st.markdown(f"**{c['user']}** : {c['msg']}")
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN 🛡️</span> {c['reply']}</div>", unsafe_allow_html=True)
            if c_est_moi and not c.get('reply'):
                if st.button(f"Répondre à {c['user']}", key=f"r_{idx}"):
                    st.session_state[f"active_{idx}"] = True
                if st.session_state.get(f"active_{idx}"):
                    r = st.text_input("Ta réponse VIP :", key=f"in_{idx}")
                    if st.button("Poster", key=f"ok_{idx}"):
                        st.session_state.comments[idx]['reply'] = r
                        sauver_data(DB_FILE, st.session_state.comments)
                        del st.session_state[f"active_{idx}"]; st.rerun()

# --- PAGE DUEL (LA CASE QUE TU VOULAIS) ---
elif st.session_state.page == "Duel":
    st.header("🔥 Duel de la Semaine")
    if st.button("⬅️"): st.session_state.page = "Accueil"; st.rerun()
    
    v1, vs_txt, v2 = st.columns([2, 1, 2])
    with v1: 
        st.subheader("GTA VI")
        if st.button("Voter GTA VI"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs)
    with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
    with v2:
        st.subheader("CYBERPUNK 2")
        if st.button("Voter CYBERPUNK 2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs)
    
    total = st.session_state.vs['j1'] + st.session_state.vs['j2']
    p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
    st.progress(p1 / 100)
    st.write(f"📊 Score : GTA {int(p1)}% | CP2 {int(100-p1)}%")

# --- PAGE CATALOGUES ---
elif st.session_state.page == "Catalogues":
    st.header("🎮 Les Catalogues")
    if st.button("⬅️"): st.session_state.page = "Accueil"; st.rerun()
    
    con = st.selectbox("Console :", ["PS5", "Xbox Series X", "Switch", "PC"])
    p_ids = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
    
    res = fetch_data("games", f"fields name, cover.url; where platforms = ({p_ids[con]}) & cover != null; sort total_rating desc; limit 12;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.write(g['name'][:20])

