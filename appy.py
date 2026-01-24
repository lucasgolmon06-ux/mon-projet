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

# --- 3. STYLE CSS (GRANDE TAILLE) ---
st.set_page_config(page_title="GameTrend Ultimate", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h1 { font-size: 60px !important; text-align: center; font-weight: 900; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; overflow: hidden; white-space: nowrap; border-radius: 5px; margin-bottom: 20px;}
    .news-text { display: inline-block; padding-left: 100%; animation: ticker 25s linear infinite; }
    @keyframes ticker { 0% { transform: translate(0, 0); } 100% { transform: translate(-100%, 0); } }
    .msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. BANDEAU & TITRE ---
st.markdown('<div class="news-ticker"><div class="news-text">🚀 GAMETREND 2026 : RECHERCHEZ VOS JEUX, REGARDEZ LES TRAILERS ET VOTEZ AU DUEL -- GTA VI vs CYBERPUNK 2 -- </div></div>', unsafe_allow_html=True)
st.markdown("<h1>GAMETREND ULTIMATE</h1>", unsafe_allow_html=True)

# --- 5. SECTION DUEL ---
st.header("🔥 Le Duel du Moment")
v1, vs_txt, v2 = st.columns([2, 1, 2])
with v1:
    st.subheader("GTA VI")
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1'] += 1
        sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with vs_txt: st.markdown("<h1 style='text-align:center;'>VS</h1>", unsafe_allow_html=True)
with v2:
    st.subheader("CYBERPUNK 2")
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2'] += 1
        sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

p1 = (st.session_state.vs['j1'] / (st.session_state.vs['j1'] + st.session_state.vs['j2'] or 1)) * 100
st.progress(p1 / 100)

# --- 6. RECHERCHE ET CATALOGUE ---
st.divider()
st.header("🎮 Rechercher un Jeu")
search_query = st.text_input("Tapez le nom d'un jeu (ex: Elden Ring, Zelda...)", placeholder="Rechercher...")

if search_query:
    q = f'search "{search_query}"; fields name, cover.url, summary, videos.video_id, total_rating; limit 8; where cover != null;'
else:
    q = 'fields name, cover.url, summary, videos.video_id, total_rating; sort popularity desc; limit 8; where cover != null;'

jeux = fetch_data("games", q)

if jeux:
    cols = st.columns(4)
    for i, j in enumerate(jeux):
        with cols[i % 4]:
            st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(f"Infos : {j['name']}", key=f"btn_{j['id']}"):
                st.session_state.selected_game = j
                st.rerun()

# AFFICHAGE DES INFOS DU JEU SÉLECTIONNÉ
if st.session_state.selected_game:
    g = st.session_state.selected_game
    st.markdown(f"## ℹ️ {g['name']}")
    col_img, col_txt = st.columns([1, 2])
    with col_img:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
    with col_txt:
        st.write(f"**Note :** {int(g.get('total_rating', 0))}/100")
        st.write(f"**Résumé :** {g.get('summary', 'Pas de résumé disponible.')}")
        
        if 'videos' in g:
            st.write("**Bande-annonce :**")
            vid_id = g['videos'][0]['video_id']
            st.video(f"https://www.youtube.com/watch?v={vid_id}")
    
    if st.button("Fermer les détails"):
        st.session_state.selected_game = None
        st.rerun()

# --- 7. SECTION COMMUNAUTÉ ---
st.divider()
st.header("💬 Communauté")
if not st.session_state.user_pseudo:
    pseudo = st.text_input("Pseudo :")
    if st.button("Se connecter"): st.session_state.user_pseudo = pseudo; st.rerun()
else:
    with st.form("chat_form", clear_on_submit=True):
        message = st.text_input(f"Message ({st.session_state.user_pseudo})")
        if st.form_submit_button("Envoyer"):
            st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": message, "reply": None})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1]:
    st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    if c.get('reply'):
        st.markdown(f"<div class='admin-reply'>🛡️ {c['reply']}</div>", unsafe_allow_html=True)

# --- 8. ZONE ADMIN ---
st.divider()
with st.expander("🛠️ Admin"):
    if st.text_input("Code :", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            if not c.get('reply'):
                with st.expander(f"Répondre à {c['user']}"):
                    ans = st.text_input("Réponse :", key=f"ans_{i}")
                    if st.button("Poster", key=f"btn_ans_{i}"):
                        st.session_state.comments[i]['reply'] = ans
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
