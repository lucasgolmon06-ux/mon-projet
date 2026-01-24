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

# --- 2. INITIALISATION SESSION ---
if 'page' not in st.session_state: st.session_state.page = "Accueil"
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'admin_active' not in st.session_state: st.session_state.admin_active = False

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
        margin-bottom: 10px;
    }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px;}
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; margin-top: 5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# BANDEAU NEWS (TOUJOURS EN HAUT)
st.markdown('<div class="news-ticker"><div class="news-text">🚀 BIENVENUE SUR GAMETREND 2026 -- CHOISIS TA CASE -- GTA VI vs CYBERPUNK 2 -- SEUL L\'ADMIN RÉPOND -- </div></div>', unsafe_allow_html=True)

# --- 4. LOGIQUE DES PAGES ---

# --- PAGE ACCUEIL ---
if st.session_state.page == "Accueil":
    st.title("🎮 GameTrend Ultimate")
    st.subheader("Choisissez une section :")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="menu-card"><h2>💬</h2><h3>COMMUNAUTÉ</h3></div>', unsafe_allow_html=True)
        if st.button("Ouvrir le Forum", use_container_width=True):
            st.session_state.page = "Forum"; st.rerun()
    with col2:
        st.markdown('<div class="menu-card"><h2>🔥</h2><h3>DUEL</h3></div>', unsafe_allow_html=True)
        if st.button("Voir le Duel", use_container_width=True):
            st.session_state.page = "Duel"; st.rerun()
    with col3:
        st.markdown('<div class="menu-card"><h2>🎮</h2><h3>JEUX</h3></div>', unsafe_allow_html=True)
        if st.button("Voir les Catalogues", use_container_width=True):
            st.session_state.page = "Catalogues"; st.rerun()

# --- PAGE FORUM ---
elif st.session_state.page == "Forum":
    c1, c2 = st.columns([5, 1])
    with c1: 
        st.header("💬 Forum Communauté")
        if st.button("⬅️ Retour"): st.session_state.page = "Accueil"; st.rerun()
    with c2:
        # LE BOUTON ADMIN DISCRET
        with st.popover("🛠️ Admin"):
            pwd = st.text_input("Code :", type="password")
            if pwd == "628316":
                st.session_state.admin_active = True
                st.success("Mode Admin OK")
            else:
                st.session_state.admin_active = False

    st.divider()

    if not st.session_state.user_pseudo:
        p = st.text_input("Pseudo :")
        if st.button("Valider"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat", clear_on_submit=True):
            m = st.text_input(f"Message ({st.session_state.user_pseudo})")
            if st.form_submit_button("Envoyer"):
                if m:
                    st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()

        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN 🛡️</span> {c['reply']}</div>", unsafe_allow_html=True)
            
            # OPTIONS DE RÉPONSE (SI ADMIN ACTIVÉ)
            if st.session_state.admin_active and not c.get('reply'):
                with st.expander("Répondre"):
                    r_txt = st.text_input("Ta réponse :", key=f"r_{idx}")
                    if st.button("Poster", key=f"b_{idx}"):
                        st.session_state.comments[idx]['reply'] = r_txt
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()

# --- PAGE DUEL ---
elif st.session_state.page == "Duel":
    st.header("🔥 Duel de la Semaine")
    if st.button("⬅️ Retour"): st.session_state.page = "Accueil"; st.rerun()
    
    col1, vs_txt, col2 = st.columns([2, 1, 2])
    with col1:
        st.subheader("GTA VI")
        if st.button("Voter GTA"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
    with col2:
        st.subheader("CYBERPUNK 2")
        if st.button("Voter CP2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    
    total = st.session_state.vs['j1'] + st.session_state.vs['j2']
    p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
    st.progress(p1 / 100)
    st.write(f"📊 Score : GTA {int(p1)}% | CP2 {int(100-p1)}%")

# --- PAGE CATALOGUES ---
elif st.session_state.page == "Catalogues":
    st.header("🎮 Catalogues Jeux")
    if st.button("⬅️ Retour"): st.session_state.page = "Accueil"; st.rerun()
    
    con = st.selectbox("Console :", ["PS5", "Xbox Series X", "Switch", "PC"])
    p_ids = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
    
    res = fetch_data("games", f"fields name, cover.url; where platforms = ({p_ids[con]}) & cover != null; sort total_rating desc; limit 12;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.write(g['name'][:20])
