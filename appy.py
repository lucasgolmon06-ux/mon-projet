import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & DONNÉES ---
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
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}', 'Content-Type': 'text/plain'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS AVANCÉ ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    /* Fond d'écran dégradé */
    .stApp {
        background: linear-gradient(135deg, #00051d 0%, #020205 100%);
        color: white;
    }
    
    /* Titres Néons */
    h1, h2 {
        color: #00f2ff;
        text-shadow: 0 0 10px #00f2ff, 0 0 20px #00f2ff;
        text-align: center;
    }

    /* Bandeau de news dégradé */
    .news-ticker {
        background: linear-gradient(90deg, #ff00cc, #3333ff);
        color: white;
        padding: 15px;
        font-weight: bold;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 0, 204, 0.4);
        margin-bottom: 30px;
    }

    /* Boutons personnalisés */
    .stButton>button {
        background: linear-gradient(45deg, #00c6ff, #0072ff);
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        font-weight: bold;
        transition: 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #ff00cc, #ff0066);
        transform: scale(1.05);
        box-shadow: 0 0 15px #ff00cc;
    }

    /* Style du chat (Glassmorphism) */
    .chat-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 10px;
    }

    .admin-reply {
        background: linear-gradient(90deg, #1a1a00, #332200);
        border-left: 5px solid #ffcc00;
        padding: 12px;
        margin-left: 20px;
        border-radius: 10px;
        color: #ffcc00;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR À L'ACCUEIL"):
        st.session_state.page = "home"; st.rerun()
    
    st.markdown(f"<h1>{g['name']}</h1>", unsafe_allow_html=True)
    c_vid, c_desc = st.columns([2, 1])
    
    with c_vid:
        if 'videos' in g:
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g:
            st.subheader("📸 Captures")
            for ss in g['screenshots'][:3]:
                st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with c_desc:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.metric("⭐ SCORE", f"{int(g.get('total_rating', 0))}/100")
        st.markdown(f"<div style='background:rgba(255,255,255,0.05); padding:15px; border-radius:10px;'>{g.get('summary', 'Aucun résumé.')}</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.markdown('<div class="news-ticker"><div class="news-text">🔥 BIENVENUE SUR GAMETREND 2026 : LA RÉFÉRENCE DU JEU VIDÉO 🔥</div></div>', unsafe_allow_html=True)

# SECTION DUEL (COULEURS)
st.markdown("<h2>🔥 Duel de la Semaine</h2>", unsafe_allow_html=True)
col_v1, col_v2 = st.columns(2)
with col_v1:
    if st.button("Voter GTA VI"):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with col_v2:
    if st.button("Voter CYBERPUNK 2"):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

votes_t = st.session_state.vs['j1'] + st.session_state.vs['j2']
perc = (st.session_state.vs['j1'] / votes_t * 100) if votes_t > 0 else 50
st.progress(perc/100)
st.markdown(f"<p style='text-align:center; color:#00f2ff; font-weight:bold;'>GTA VI : {int(perc)}% | CYBERPUNK 2 : {int(100-perc)}%</p>", unsafe_allow_html=True)

# SECTION CHAT
st.divider()
st.markdown("<h2>💬 Chat Communautaire</h2>", unsafe_allow_html=True)
if not st.session_state.user_pseudo:
    pseudo_input = st.text_input("Choisis un pseudo :")
    if st.button("Rejoindre le chat"): st.session_state.user_pseudo = pseudo_input; st.rerun()
else:
    with st.form("msg_form", clear_on_submit=True):
        txt = st.text_input(f"Message de {st.session_state.user_pseudo}")
        if st.form_submit_button("Envoyer") and txt:
            if not any(w in txt.lower().split() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": txt, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1]:
    st.markdown(f"<div class='chat-box'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    if c.get('reply'):
        st.markdown(f"<div class='admin-reply'><b>⭐ ADMIN</b> : {c['reply']}</div>", unsafe_allow_html=True)

# --- 6. CATALOGUE & RECHERCHE ---
st.divider()
st.markdown("<h2>🔍 Catalogue & Exploration</h2>", unsafe_allow_html=True)

user_search = st.text_input("Rechercher un jeu :", placeholder="Ex: Elden Ring, Mario, FIFA...")

if user_search:
    q = f'search "{user_search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    plats = {"PlayStation 5": 167, "Xbox Series X": 169, "Nintendo Switch": 130, "PC (Windows)": 6}
    choice = st.selectbox("Choisir une plateforme :", list(plats.keys()))
    q = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where platforms = ({plats[choice]}) & cover != null; sort popularity desc; limit 12;"

games = fetch_data("games", q)
if games:
    cols = st.columns(4)
    for idx, g in enumerate(games):
        with cols[idx%4]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            st.write(f"**{g['name']}**")
            if st.button("🔎 Voir Détails", key=f"btn_{g['id']}"):
                st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# --- 7. ADMIN ---
st.divider()
with st.expander("🛠️ Panneau Admin"):
    if st.text_input("Code confidentiel", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            st.write(f"{c['user']}: {c['msg']}")
            if st.button("❌ Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            rep = st.text_input("Répondre", key=f"rep_{i}")
            if st.button("✔ Envoyer Réponse", key=f"b_{i}"):
                st.session_state.comments[i]['reply'] = rep; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
