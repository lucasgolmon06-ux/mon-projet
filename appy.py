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
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
    .top-card { background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; border-radius: 10px; padding: 15px; text-align: center; }
    .price-box { background: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 1.2rem; text-align: center; margin-bottom: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; color: #ffcc00; margin-top:5px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR À L'ACCUEIL"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(f"🎮 {g['name']}")
    c_vid, c_desc = st.columns([2, 1])
    
    with c_vid:
        if 'videos' in g:
            st.subheader("📺 Trailer")
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g:
            st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with c_desc:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        
        # PRIX DYNAMIQUE
        score = g.get('total_rating', 0)
        prix = "79.99€" if score > 85 else "59.99€" if score > 70 else "29.99€"
        st.markdown(f'<div class="price-box">PRIX : {prix}</div>', unsafe_allow_html=True)
        
        st.metric("SCORE IGDB", f"{int(score)}/100")
        st.info(g.get('summary', 'Aucun résumé disponible.'))
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.markdown('<div class="news-ticker">🚀 GAMETREND 2026 -- LE TOP 3 PS5 ET LES FILTRES SONT EN LIGNE !</div>', unsafe_allow_html=True)

# SECTION DUEL (GTA VI vs CYBERPUNK 2)
st.header("🔥 Le Choc des Titans")
col_v1, col_v2 = st.columns(2)
with col_v1:
    if st.button(f"Voter GTA VI ({st.session_state.vs['j1']})", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with col_v2:
    if st.button(f"Voter CYBERPUNK 2 ({st.session_state.vs['j2']})", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

total_votes = st.session_state.vs['j1'] + st.session_state.vs['j2']
st.write(f"📊 **Total des participants : {total_votes}**")
perc = (st.session_state.vs['j1'] / total_votes * 100) if total_votes > 0 else 50
st.progress(perc/100)

# SECTION VRAI TOP 3 PS5
st.divider()
st.header("🏆 Top 3 des Meilleurs Jeux PS5")
top_ps5_q = "fields name, cover.url, total_rating; where platforms = (167) & total_rating_count > 50 & cover != null; sort total_rating desc; limit 3;"
top_games = fetch_data("games", top_ps5_q)
if top_games:
    cols_top = st.columns(3)
    for i, tg in enumerate(top_games):
        with cols_top[i]:
            st.markdown(f'<div class="top-card"><h2 style="color:#ffd700;">#{i+1}</h2><h4>{tg["name"]}</h4></div>', unsafe_allow_html=True)
            st.image("https:" + tg['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            st.metric("Score", f"{int(tg.get('total_rating', 0))}/100")

# SECTION CATALOGUE AVEC FILTRES
st.divider()
st.header("🔍 Catalogue & Recherche")
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1: user_search = st.text_input("Rechercher un jeu :")
with f_col2: platform_choice = st.selectbox("Console :", ["Toutes", "PS5", "Xbox Series X", "Switch", "PC"])
with f_col3: genre_choice = st.selectbox("Genre :", ["Tous", "Action", "RPG", "Sport", "Aventure", "Shooter"])

# Mapping IDs IGDB
plats_map = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
genres_map = {"Action": 31, "RPG": 12, "Sport": 14, "Aventure": 31, "Shooter": 5}

q = "fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null"
if user_search:
    q = f'search "{user_search}"; ' + q
else:
    if platform_choice != "Toutes": q += f" & platforms = ({plats_map[platform_choice]})"
    if genre_choice != "Tous": q += f" & genres = ({genres_map[genre_choice]})"
    q += "; sort popularity desc;"

games = fetch_data("games", q)
if games:
    grid = st.columns(6)
    for idx, g in enumerate(games):
        with grid[idx%6]:
            if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button("Détails", key=f"btn_{g['id']}"):
                st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# SECTION CHAT
st.divider()
st.header("💬 Le Chat")
if not st.session_state.user_pseudo:
    pseudo_in = st.text_input("Ton pseudo pour tchatter :")
    if st.button("Rejoindre"): st.session_state.user_pseudo = pseudo_in; st.rerun()
else:
    with st.form("chat_msg", clear_on_submit=True):
        txt = st.text_input(f"Message de {st.session_state.user_pseudo}")
        if st.form_submit_button("Envoyer") and txt:
            if not any(w in txt.lower() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": txt, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1][:10]:
    st.write(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'):
        st.markdown(f"<div class='admin-reply'><b>ADMIN :</b> {c['reply']}</div>", unsafe_allow_html=True)

# SECTION ADMIN
st.divider()
with st.expander("🛠️ Administration"):
    if st.text_input("Code secret", type="password") == "628316":
        for i, c in enumerate(list(st.session_state.comments)):
            col_a1, col_a2 = st.columns([3, 1])
            with col_a1: st.write(f"**{c['user']}**: {c['msg']}")
            with col_a2:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            rep = st.text_input("Répondre", key=f"rep_{i}")
            if st.button("🚀", key=f"btn_rep_{i}"):
                st.session_state.comments[i]['reply'] = rep; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
