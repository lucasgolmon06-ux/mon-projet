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

def fetch_data(query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
    return res.json()

# --- 2. INITIALISATION ---
if 'section' not in st.session_state: st.session_state.section = None
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None

# --- 3. STYLE CSS (Basé sur ton schéma) ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .nav-box { border: 2px solid white; padding: 10px; text-align: center; border-radius: 5px; cursor: pointer; }
    .news-header { border: 3px solid white; padding: 20px; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; margin-top: 5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LE SCHÉMA DU HAUT (NEW, DUEL, COMMU, ADMIN, TOP) ---
st.markdown('<div class="news-header">NEW</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("DUEL", use_container_width=True): st.session_state.section = "duel"
with col2:
    if st.button("COMMU", use_container_width=True): st.session_state.section = "commu"
with col3:
    if st.button("TOP", use_container_width=True): st.session_state.section = "top"
with col4:
    if st.button("ADMIN", use_container_width=True): st.session_state.section = "admin"

st.divider()

# --- 5. LOGIQUE DE LA ZONE DE CONTENU (VIDE PAR DÉFAUT) ---

# SECTION : DUEL
if st.session_state.section == "duel":
    st.subheader("🔥 Duel de la Semaine")
    c1, cvs, c2 = st.columns([2, 1, 2])
    with c1:
        st.write("### GTA VI")
        if st.button("Voter GTA"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    with cvs: st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)
    with c2:
        st.write("### CYBERPUNK 2")
        if st.button("Voter CP2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    
    total = st.session_state.vs['j1'] + st.session_state.vs['j2']
    p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
    st.progress(p1 / 100)

# SECTION : COMMU
elif st.session_state.section == "commu":
    st.subheader("💬 Forum")
    if not st.session_state.user_pseudo:
        p = st.text_input("Pseudo :")
        if st.button("Valider"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat"):
            m = st.text_input(f"Message de {st.session_state.user_pseudo}")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        for c in st.session_state.comments[::-1]:
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span> {c['reply']}</div>", unsafe_allow_html=True)

# SECTION : TOP (CATALOGUES)
elif st.session_state.section == "top":
    st.subheader("🎮 Top Jeux")
    con = st.selectbox("Console :", ["PS5", "Xbox", "Switch", "PC"])
    p_ids = {"PS5": 167, "Xbox": 169, "Switch": 130, "PC": 6}
    res = fetch_data(f"fields name, cover.url; where platforms = ({p_ids[con]}) & cover != null; sort total_rating desc; limit 12;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))

# SECTION : ADMIN (VIDE AU DÉBUT)
elif st.session_state.section == "admin":
    st.subheader("🛡️ Espace Administrateur")
    code = st.text_input("Entrez le code secret pour débloquer les outils :", type="password")
    
    if code == "628316":
        st.success("Accès autorisé. Outils et Statistiques débloqués.")
        
        # STATS DU SITE
        st.markdown("### 📊 Statistiques du site")
        col_s1, col_s2 = st.columns(2)
        col_s1.metric("Messages total", len(st.session_state.comments))
        col_s2.metric("Votes total", st.session_state.vs['j1'] + st.session_state.vs['j2'])
        
        # RÉPONDRE AUX MESSAGES
        st.markdown("### 💬 Répondre aux utilisateurs")
        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            if not c.get('reply'):
                with st.expander(f"Répondre à {c['user']}"):
                    r_text = st.text_area("Ta réponse :", key=f"admin_in_{idx}")
                    if st.button("Poster la réponse", key=f"admin_btn_{idx}"):
                        st.session_state.comments[idx]['reply'] = r_text
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    elif code != "":
        st.error("Code incorrect. La zone reste vide.")

# ZONE VIDE SI RIEN N'EST CLIQUÉ
else:
    st.info("Cliquez sur un bouton en haut pour afficher le contenu.")
