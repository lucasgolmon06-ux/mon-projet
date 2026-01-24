import streamlit as st
import requests
import json
import os
import time
from collections import Counter

# --- 1. CONFIGURATION & FICHIERS ---
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

# --- 2. INITIALISATION SESSION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'global_w' not in st.session_state: st.session_state.global_w = charger_data(WISHLIST_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'loaded' not in st.session_state: st.session_state.loaded = False
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS & INTERFACE ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; margin-top: 5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em; box-shadow: 0 0 10px #ffd700; }
    .news-ticker { background: #0072ce; color: white; padding: 10px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px; }
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    </style>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR ADMIN ---
with st.sidebar:
    st.title("🛡️ Panel de Contrôle")
    mon_code = st.text_input("Code Secret Admin", type="password")
    c_est_moi = (mon_code == "628316")
    if c_est_moi: st.success("Accès Maître activé")

# --- 5. BANDEAU NEWS ---
st.markdown('<div class="news-ticker"><div class="news-text">🎮 GAMETREND 2026 : BIENVENUE DANS LE FUTUR DU GAMING -- GTA VI, SWITCH 2, ET TOUTE LA COMMUNAUTÉ EN DIRECT -- </div></div>', unsafe_allow_html=True)

# --- 6. VUE JEU (POP-UP DÉTAILS) ---
if st.session_state.selected_game:
    res = fetch_data("games", f"fields name, cover.url, summary, videos.video_id; where id = {st.session_state.selected_game};")
    if res:
        game = res[0]
        if st.button("⬅️ Retour"): st.session_state.selected_game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + game['cover']['url'].replace('t_thumb', 't_720p'), use_container_width=True)
        with c2:
            st.title(game['name'])
            st.write(game.get('summary', ''))
            if 'videos' in game:
                st.video(f"https://www.youtube.com/watch?v={game['videos'][0]['video_id']}")
            if st.button("❤️ Voter pour ce jeu"):
                st.session_state.global_w.append(game['name'])
                sauver_data(WISHLIST_FILE, st.session_state.global_w); st.balloons()
    st.stop()

# --- 7. SECTION COMMUNAUTÉ ---
st.title("🎮 GameTrend Ultimate")
with st.container():
    st.subheader("💬 Le Forum Community")
    if not st.session_state.user_pseudo:
        col_ps, _ = st.columns([1, 2])
        p = col_ps.text_input("Choisis un pseudo pour parler :")
        if st.button("Rejoindre"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat"):
            m = st.text_input(f"Message de {st.session_state.user_pseudo} :")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

    for i, c in enumerate(st.session_state.comments[:-6:-1]): # 5 derniers
        idx = len(st.session_state.comments) - 1 - i
        col_m, col_b = st.columns([5, 1])
        with col_m:
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN 🛡️</span> {c['reply']}</div>", unsafe_allow_html=True)
        with col_b:
            if c_est_moi and not c.get('reply'):
                if st.button("💬", key=f"r_{idx}"): st.session_state[f"act_{idx}"] = True
        if st.session_state.get(f"act_{idx}"):
            r = st.text_input("Réponse VIP...", key=f"in_{idx}")
            if st.button("Poster", key=f"ok_{idx}"):
                st.session_state.comments[idx]['reply'] = r
                sauver_data(DB_FILE, st.session_state.comments)
                del st.session_state[f"act_{idx}"]; st.rerun()

st.divider()

# --- 8. SECTION VERSUS ---
st.subheader("🔥 LE DUEL DE LA SEMAINE")
v1, vs_txt, v2 = st.columns([2, 1, 2])
with v1: 
    st.markdown("### GTA VI")
    if st.button("Voter GTA"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs)
with vs_txt: st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)
with v2:
    st.markdown("### CYBERPUNK 2")
    if st.button("Voter CP2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs)

total = st.session_state.vs['j1'] + st.session_state.vs['j2']
p1 = (st.session_state.vs['j1'] / total * 100) if total > 0 else 50
st.progress(p1 / 100)
st.write(f"📊 GTA VI: {int(p1)}% | CYBERPUNK 2: {int(100-p1)}%")

st.divider()

# --- 9. CATALOGUES JEUX ---
platforms = {"PS5": 167, "Xbox": "169,49", "Switch": 130, "PC": 6}
for name, p_id in platforms.items():
    c_h, c_f = st.columns([3, 1])
    with c_h: st.header(f"🎮 {name}")
    with c_f: tri = st.selectbox("Style :", ["Mieux notés", "AAA", "Indés"], key=f"t_{name}")
    
    q = f"fields name, cover.url; where platforms = ({p_id}) & cover != null; sort total_rating desc; limit 12;"
    if tri == "AAA": q = f"fields name, cover.url; where platforms = ({p_id}) & genres != (32) & total_rating > 80 & cover != null; sort total_rating desc; limit 12;"
    elif tri == "Indés": q = f"fields name, cover.url; where platforms = ({p_id}) & genres = (32) & cover != null; sort total_rating desc; limit 12;"
    
    jeux = fetch_data("games", q)
    if jeux:
        cols = st.columns(6)
        for j, g in enumerate(jeux):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(g['name'][:18], key=f"b_{p_id}_{g['id']}"):
                    st.session_state.selected_game = g['id']; st.rerun()

