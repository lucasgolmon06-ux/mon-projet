import streamlit as st
import requests
import json
import os
import time

# --- 1. CONFIGURATION API IGDB ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# --- 2. FONCTIONS DE SAUVEGARDE ET API ---
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comms, f, indent=4)

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    try:
        res = requests.post(auth_url)
        return res.json().get('access_token')
    except: return None

def fetch_data(query):
    token = get_access_token()
    if not token: return []
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- 3. INITIALISATION DES SESSIONS ---
if 'comments' not in st.session_state:
    st.session_state.comments = charger_comms()
if 'user_pseudo' not in st.session_state:
    st.session_state.user_pseudo = None
if 'loaded' not in st.session_state:
    st.session_state.loaded = False

# --- 4. DESIGN & ANIMATIONS (CSS) ---
st.set_page_config(page_title="GameTrend Ultra", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    
    /* Animation Intro 3 Logos */
    #intro-screen {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-color: #00051d; display: flex; justify-content: center; align-items: center;
        z-index: 10000; animation: fadeOut 6.5s forwards;
    }
    .logo-img { position: absolute; width: 250px; opacity: 0; transform: scale(0.8); }
    .ps { animation: seq 1.8s 0.5s forwards; }
    .xb { animation: seq 1.8s 2.3s forwards; }
    .nt { animation: seq 1.8s 4.1s forwards; }
    @keyframes seq { 0% { opacity:0; } 50% { opacity:1; transform:scale(1); } 100% { opacity:0; transform:scale(1.1); } }
    @keyframes fadeOut { 0%, 95% { opacity:1; visibility:visible; } 100% { opacity:0; visibility:hidden; } }

    /* Bulles de commentaires */
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .msg-admin { background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; font-size: 0.9em; }
    </style>

    <div id="intro-screen">
        <img class="logo-img ps" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/00/PlayStation_logo.svg/1280px-PlayStation_logo.svg.png">
        <img class="logo-img xb" src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/f9/Xbox_one_logo.svg/1024px-Xbox_one_logo.svg.png">
        <img class="logo-img nt" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/04/Nintendo_Switch_logo_and_wordmark.svg/1280px-Nintendo_Switch_logo_and_wordmark.svg.png">
    </div>
""", unsafe_allow_html=True)

if not st.session_state.loaded:
    time.sleep(6.2)
    st.session_state.loaded = True

# --- 5. HEADER & BOUTON COMMUNAUTÉ ---
h_col1, h_col2 = st.columns([3, 1])
with h_col1:
    st.title("🎮 GameTrend Pro")
with h_col2:
    ouvrir_comm = st.toggle("💬 Espace Communauté")

# --- 6. BLOC COMMUNAUTÉ (S'OUVRE SI COCHÉ) ---
if ouvrir_comm:
    st.markdown("### 👥 Forum de la Communauté")
    col_c1, col_c2 = st.columns([1, 2])
    
    with col_c1:
        if st.session_state.user_pseudo is None:
            with st.form("pseudo_form"):
                p_in = st.text_input("Pseudo unique")
                if st.form_submit_button("Valider"):
                    if p_in:
                        st.session_state.user_pseudo = p_in
                        st.rerun()
        else:
            st.success(f"Connecté : **{st.session_state.user_pseudo}**")
            with st.form("msg_form", clear_on_submit=True):
                m_in = st.text_area("Ton message")
                if st.form_submit_button("Poster"):
                    if m_in:
                        st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m_in, "reply": None})
                        sauver_comms(st.session_state.comments)
                        st.rerun()
        st.divider()
        admin_pass = st.text_input("🔑 Mode Admin", type="password")
        is_admin = (admin_pass == "1234")

    with col_c2:
        for i, c in enumerate(reversed(st.session_state.comments)):
            idx = len(st.session_state.comments) - 1 - i
            st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> : {c["msg"]}</div>', unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f'<div class="msg-admin"><b>Auteur</b> : {c["reply"]}</div>', unsafe_allow_html=True)
            elif is_admin:
                rep = st.text_input(f"Répondre à {c['user']}", key=f"ans_{idx}")
                if st.button("Répondre", key=f"btn_{idx}"):
                    st.session_state.comments[idx]['reply'] = rep
                    sauver_comms(st.session_state.comments)
                    st.rerun()
    st.markdown("---")

# --- 7. BARRE DE RECHERCHE ET STYLE ---
col_s1, col_s2 = st.columns(2)
with col_s1:
    search_q = st.text_input("🔍 Rechercher un jeu précis...")
with col_s2:
    style_q = st.text_input("💡 Style de jeu recherché...")

if search_q:
    res = fetch_data(f'search "{search_q}"; fields name, cover.url; where cover != null; limit 6;')
    if res:
        cols = st.columns(6)
        for i, g in enumerate(res):
            with cols[i]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(g['name'])

if style_q:
    res = fetch_data(f'search "{style_q}"; fields name, cover.url, total_rating; where cover != null & total_rating > 75 & name !~ *"{style_q}"*; limit 4;')
    if res:
        st.subheader(f"Si tu aimes {style_q}...")
        cols = st.columns(4)
        for i, g in enumerate(res):
            with cols[i]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(f"{g['name']} ({round(g['total_rating'])}/100)")

# --- 8. TOP 12 PAR CONSOLE AVEC FILTRES ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    st.divider()
    t_col1, t_col2 = st.columns([2, 1])
    with t_col1:
        st.header(f"Top 12 {name}")
    with t_col2:
        filtre = st.selectbox(f"Filtrer {name}", 
                             ["Meilleures notes", "Coup de ❤️ Communauté", "Gros Budgets (AAA)", "Jeux Indépendants"],
                             key=f"f_{name}")

    base = f"platforms = ({p_id}) & cover != null"
    if filtre == "Meilleures notes":
        q = f"fields name, cover.url, total_rating; where {base} & total_rating != null; sort total_rating desc; limit 12;"
    elif filtre == "Coup de ❤️ Communauté":
        q = f"fields name, cover.url, rating; where {base} & rating != null & rating_count > 50; sort rating desc; limit 12;"
    elif filtre == "Gros Budgets (AAA)":
        q = f"fields name, cover.url, total_rating; where {base} & themes != (31) & total_rating > 70; sort total_rating desc; limit 12;"
    else: # Indés
        q = f"fields name, cover.url, total_rating; where {base} & themes = (31); sort total_rating desc; limit 12;"

    jeux = fetch_data(q)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                n_val = g.get('rating') if filtre == "Coup de ❤️ Communauté" else g.get('total_rating')
                st.markdown(f"<p style='color:#ffcc00;'>⭐ {round(n_val) if n_val else 'N/A'}/100</p>", unsafe_allow_html=True)
