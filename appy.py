import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

# Liste noire de mots (à compléter si besoin)
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
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; }
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; margin-top: 5px; color: #ffcc00; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. BANDEAU ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 -- CLIQUEZ SUR UN JEU POUR VOIR LE TRAILER -- CHAT MODÉRÉ -- GTA VI vs CYBERPUNK 2 -- </div></div>', unsafe_allow_html=True)
st.title("GameTrend Ultimate")

# --- 5. SECTION DUEL ---
st.header("🔥 Le Duel de la Semaine")
v1, vs_txt, v2 = st.columns([2, 1, 2])
with v1:
    st.subheader("GTA VI")
    if st.button("Voter GTA VI"):
        st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
with v2:
    st.subheader("CYBERPUNK 2")
    if st.button("Voter CYBERPUNK 2"):
        st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

total = st.session_state.vs['j1'] + st.session_state.vs['j2']
p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
st.progress(p1 / 100)

# --- 6. SECTION COMMUNAUTÉ (FILTRE CORRIGÉ) ---
st.divider()
st.header("💬 Communauté")
if not st.session_state.user_pseudo:
    pseudo = st.text_input("Ton pseudo :")
    if st.button("Rejoindre le chat"): st.session_state.user_pseudo = pseudo; st.rerun()
else:
    with st.form("chat_form", clear_on_submit=True):
        message = st.text_input(f"Message ({st.session_state.user_pseudo}) :")
        if st.form_submit_button("Envoyer"):
            if message:
                # Vérification intelligente : on regarde chaque mot
                words_in_msg = message.lower().split()
                has_insult = any(bad in words_in_msg for bad in BAD_WORDS)
                
                if has_insult:
                    st.error("⚠️ Ton message contient un mot interdit.")
                else:
                    st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": message, "reply": None})
                    sauver_data(DB_FILE, st.session_state.comments)
                    st.rerun()

for c in st.session_state.comments[::-1]:
    st.markdown(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'):
        st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span>{c['reply']}</div>", unsafe_allow_html=True)

# --- 7. CATALOGUES ---
st.divider()
st.header("🎮 Catalogues Jeux")
platforms = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
p_choice = st.selectbox("Console :", list(platforms.keys()))

query = f"fields name, cover.url, summary, videos.video_id, total_rating; where platforms = ({platforms[p_choice]}) & cover != null; sort total_rating desc; limit 12;"
jeux = fetch_data("games", query)

if jeux:
    cols = st.columns(6)
    for i, j in enumerate(jeux):
        with cols[i % 6]:
            st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(f"Voir : {j['name'][:15]}", key=f"btn_{j['id']}"):
                st.session_state.selected_game = j; st.rerun()

if st.session_state.selected_game:
    g = st.session_state.selected_game
    st.markdown(f"### ℹ️ {g['name']}")
    c1, c2 = st.columns([1, 2])
    with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
    with c2:
        st.write(f"**Note :** {int(g.get('total_rating', 0))}/100")
        st.write(f"**Résumé :** {g.get('summary', 'Pas de résumé.')}")
        if 'videos' in g:
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
    if st.button("Fermer"): st.session_state.selected_game = None; st.rerun()

# --- 8. ADMIN ---
st.divider()
with st.expander("🛠️ Admin"):
    if st.text_input("Code :", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            col_m, col_d = st.columns([0.8, 0.2])
            with col_m: st.write(f"**{c['user']}** : {c['msg']}")
            with col_d:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            if not c.get('reply'):
                ans = st.text_input("Réponse :", key=f"ans_{i}")
                if st.button("Répondre", key=f"btn_{i}"):
                    st.session_state.comments[i]['reply'] = ans
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()
