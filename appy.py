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
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS XXL ---
st.set_page_config(page_title="GameTrend Ultimate 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h1 { font-size: 70px !important; text-align: center; font-weight: 900; color: #0072ce; }
    h2 { border-left: 10px solid #0072ce; padding-left: 15px; margin-top: 40px; font-size: 40px !important; }
    .news-ticker { background: #0072ce; color: white; padding: 15px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; }
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .msg-user { background: #001a3d; padding: 15px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 BIENVENUE SUR GAMETREND 2026 -- RECHERCHEZ VOS JEUX -- REGARDEZ LES TRAILERS -- VOTEZ AU DUEL -- NOUVELLES SECTIONS DISPONIBLES --</div></div>', unsafe_allow_html=True)
st.markdown("<h1>GAMETREND ULTIMATE</h1>", unsafe_allow_html=True)

# --- 5. LE DUEL ---
st.markdown("## 🔥 LE CHOC DES TITRES")
v1, vs_txt, v2 = st.columns([2, 1, 2])
with v1:
    st.markdown("<h3 style='text-align:center;'>GTA VI</h3>", unsafe_allow_html=True)
    if st.button("Voter GTA", use_container_width=True):
        st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
with v2:
    st.markdown("<h3 style='text-align:center;'>CYBERPUNK 2</h3>", unsafe_allow_html=True)
    if st.button("Voter CP2", use_container_width=True):
        st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

total = st.session_state.vs['j1'] + st.session_state.vs['j2']
st.progress(st.session_state.vs['j1'] / (total if total > 0 else 1))

# --- 6. RECHERCHE INTERACTIVE ---
st.divider()
st.markdown("## 🔎 RECHERCHER UN JEU")
search = st.text_input("Tapez un nom...", placeholder="Ex: Elden Ring...")
if search:
    res_search = fetch_data(f'search "{search}"; fields name, cover.url, summary, videos.video_id, total_rating; limit 8; where cover != null;')
    if res_search:
        cols = st.columns(4)
        for i, g in enumerate(res_search):
            with cols[i%4]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"Infos : {g['name'][:15]}", key=f"search_{g['id']}"):
                    st.session_state.selected_game = g; st.rerun()

# --- 7. ZONE D'INFOS (SYSTÈME DE CLIC + TRAILERS) ---
if st.session_state.selected_game:
    sel = st.session_state.selected_game
    st.markdown(f"### 📽️ Focus sur : {sel['name']}")
    ci, ct = st.columns([1, 2])
    with ci: st.image("https:" + sel['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
    with ct:
        st.write(f"**Note :** {int(sel.get('total_rating', 0))}/100")
        st.write(sel.get('summary', 'Pas de résumé.'))
        if 'videos' in sel: st.video(f"https://www.youtube.com/watch?v={sel['videos'][0]['video_id']}")
    if st.button("Fermer"): st.session_state.selected_game = None; st.rerun()

# --- 8. LES SECTIONS DE 12 ---
def afficher_section(titre, query):
    st.markdown(f"## {titre}")
    data = fetch_data(query)
    if data:
        cols = st.columns(6)
        for i, g in enumerate(data):
            with cols[i%6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(f"Voir : {g['name'][:10]}", key=f"{titre}_{g['id']}"):
                    st.session_state.selected_game = g; st.rerun()

afficher_section("💎 12 MEILLEURS INDÉPENDANTS", "fields name, cover.url, summary, videos.video_id, total_rating; where themes = (32) & cover != null; sort total_rating desc; limit 12;")
afficher_section("💰 12 LES PLUS ACHETÉS (POPULAIRES)", "fields name, cover.url, summary, videos.video_id, total_rating; where cover != null; sort popularity desc; limit 12;")
afficher_section("❤️ 12 COUPS DE CŒUR COMMU", "fields name, cover.url, summary, videos.video_id, total_rating; where cover != null & total_rating > 85; sort hypes desc; limit 12;")

# --- 9. LE FORUM ---
st.divider()
st.markdown("## 💬 FORUM COMMUNAUTÉ")
if not st.session_state.user_pseudo:
    p = st.text_input("Pseudo :")
    if st.button("Se connecter"): st.session_state.user_pseudo = p; st.rerun()
else:
    with st.form("chat"):
        m = st.text_input(f"Message ({st.session_state.user_pseudo})")
        if st.form_submit_button("Envoyer"):
            st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1]:
    st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    if c.get('reply'): st.markdown(f"<div class='admin-reply'>🛡️ {c['reply']}</div>", unsafe_allow_html=True)

# --- 10. ADMIN ---
st.divider()
with st.expander("🛠️ ADMIN"):
    if st.text_input("Code :", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            if not c.get('reply'):
                with st.expander(f"Répondre à {c['user']}"):
                    ans = st.text_input("Réponse", key=f"ans_{i}")
                    if st.button("Poster", key=f"btn_{i}"):
                        st.session_state.comments[i]['reply'] = ans
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
