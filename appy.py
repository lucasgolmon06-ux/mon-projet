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
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'admin_active' not in st.session_state: st.session_state.admin_active = False

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .section-container { 
        background: rgba(0, 26, 61, 0.5);
        border: 1px solid #0072ce;
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 25px;
    }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px;}
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; margin-top: 5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 4. EN-TÊTE & NEWS ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 : TOUT LE GAMING EN DIRECT -- GTA VI vs CYBERPUNK 2 -- SEUL L\'ADMIN RÉPOND -- </div></div>', unsafe_allow_html=True)

col_title, col_admin = st.columns([5, 1])
with col_title:
    st.title("🎮 GameTrend Ultimate")
with col_admin:
    # LE BOUTON ADMIN DISCRET (POUR RÉPONDRE)
    with st.popover("🛠️ Admin"):
        pwd = st.text_input("Code :", type="password")
        if pwd == "628316":
            st.session_state.admin_active = True
            st.success("Mode Admin Activé")
        else:
            st.session_state.admin_active = False

# --- 5. SECTION DUEL (OUVERTURE IMMÉDIATE) ---
with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🔥 LE DUEL DU MOMENT")
    c1, cvs, c2 = st.columns([2, 1, 2])
    with c1:
        st.write("### GTA VI")
        if st.button("Voter GTA"): 
            st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    with cvs: st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)
    with c2:
        st.write("### CYBERPUNK 2")
        if st.button("Voter CP2"): 
            st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    
    total = st.session_state.vs['j1'] + st.session_state.vs['j2']
    p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
    st.progress(p1 / 100)
    st.write(f"📊 Score : GTA {int(p1)}% | CP2 {int(100-p1)}%")
    st.markdown('</div>', unsafe_allow_html=True)

# --- 6. SECTION COMMUNAUTÉ ---
with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("💬 Forum de la Communauté")
    
    if not st.session_state.user_pseudo:
        p = st.text_input("Choisis ton pseudo pour participer :")
        if st.button("Rejoindre le Chat"): 
            st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat_form", clear_on_submit=True):
            m = st.text_input(f"Message ({st.session_state.user_pseudo})")
            if st.form_submit_button("Envoyer"):
                if m:
                    st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()

        # Affichage des derniers messages
        for i, c in enumerate(st.session_state.comments[::-1][:10]): # 10 derniers
            idx = len(st.session_state.comments) - 1 - i
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN 🛡️</span> {c['reply']}</div>", unsafe_allow_html=True)
            
            # Si Admin actif via le bouton discret
            if st.session_state.admin_active and not c.get('reply'):
                with st.expander("Répondre"):
                    r_txt = st.text_input("Réponse :", key=f"r_{idx}")
                    if st.button("Poster", key=f"b_{idx}"):
                        st.session_state.comments[idx]['reply'] = r_txt
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 7. SECTION CATALOGUES ---
with st.container():
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🎮 Catalogues de Jeux")
    con = st.selectbox("Choisir une plateforme :", ["PS5", "Xbox Series X", "Switch", "PC"])
    p_ids = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
    
    res = fetch_data("games", f"fields name, cover.url; where platforms = ({p_ids[con]}) & cover != null; sort total_rating desc; limit 12;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.write(g['name'][:20])
    st.markdown('</div>', unsafe_allow_html=True)
