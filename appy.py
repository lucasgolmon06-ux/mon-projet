import streamlit as st
import requests
import json
import os
import urllib.parse

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

# --- INITIALISATION DES FICHIERS ---
if not os.path.exists(DB_FILE): sauver_data(DB_FILE, [])
# Pour forcer le reset à 0 maintenant, tu peux changer momentanément la ligne suivante par : 
# st.session_state.vs = {"j1": 0, "j2": 0} puis relancer une fois.
if not os.path.exists(VERSUS_FILE): sauver_data(VERSUS_FILE, {"j1": 0, "j2": 0})

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

# --- 2. INITIALISATION SESSION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE)
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'already_voted' not in st.session_state: st.session_state.already_voted = False

# --- 3. DESIGN & AUDIO ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
    .top-card { background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; border-radius: 10px; padding: 15px; text-align: center; }
    .price-box { background: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 1.2rem; text-align: center; margin-bottom: 10px; }
    .buy-button { 
        display: block; width: 100%; text-align: center; background-color: #ff9900; color: black !important; 
        padding: 15px; font-weight: bold; text-decoration: none; border-radius: 5px; margin-top: 10px;
    }
    </style>

    <iframe src="https://www.youtube.com/embed/5qap5aO4i9A?autoplay=1&loop=1&playlist=5qap5aO4i9A" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>

    <script>
    window.parent.document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            const audio = window.parent.document.getElementById('clickSound');
            if(audio) { audio.currentTime = 0; audio.play(); }
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("RETOUR A L'ACCUEIL"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'])
    c_vid, c_desc = st.columns([2, 1])
    
    with c_vid:
        if 'videos' in g:
            st.subheader("Trailer Officiel")
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g:
            st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with c_desc:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        score = g.get('total_rating', 0)
        prix = "79.99€" if score > 85 else "59.99€" if score > 70 else "29.99€"
        st.markdown(f'<div class="price-box">PRIX ESTIME : {prix}</div>', unsafe_allow_html=True)
        
        search_query = urllib.parse.quote(f"{g['name']} jeu vidéo")
        url_amazon = f"https://www.amazon.fr/s?k={search_query}"
        st.markdown(f'<a href="{url_amazon}" target="_blank" class="buy-button">ACHETER SUR AMAZON</a>', unsafe_allow_html=True)
        
        st.divider()
        st.metric("SCORE CRITIQUE", f"{int(score)}/100")
        st.info(g.get('summary', 'Aucun résumé disponible.'))
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND 2026 -- SYSTEME DE VOTE UNIQUE ACTIVE</div>', unsafe_allow_html=True)

# SECTION DUEL (REMISE A ZERO)
st.header("Duel de Legendes")

col_v1, col_v2 = st.columns(2)

if not st.session_state.already_voted:
    with col_v1:
        if st.button(f"Voter GTA VI ({st.session_state.vs['j1']})", key="v_gta", use_container_width=True):
            st.session_state.vs['j1']+=1
            sauver_data(VERSUS_FILE, st.session_state.vs)
            st.session_state.already_voted = True
            st.rerun()
    with col_v2:
        if st.button(f"Voter CYBERPUNK 2 ({st.session_state.vs['j2']})", key="v_cp", use_container_width=True):
            st.session_state.vs['j2']+=1
            sauver_data(VERSUS_FILE, st.session_state.vs)
            st.session_state.already_voted = True
            st.rerun()
else:
    st.success("Votre vote a bien été pris en compte !")

total_votes = st.session_state.vs['j1'] + st.session_state.vs['j2']
st.write(f"Votes totaux : {total_votes}")
perc = (st.session_state.vs['j1'] / total_votes) if total_votes > 0 else 0.5
st.progress(perc)

# [SECTION CATALOGUE...]
st.divider()
st.header("Top 3 des Meilleurs Jeux PS5")
top_ps5_q = "fields name, cover.url, total_rating, summary, videos.video_id, screenshots.url; where platforms = (167) & total_rating_count > 50 & cover != null; sort total_rating desc; limit 3;"
top_games = fetch_data("games", top_ps5_q)
if top_games:
    cols_top = st.columns(3)
    for i, tg in enumerate(top_games):
        with cols_top[i]:
            st.markdown(f'<div class="top-card"><h2>#{i+1}</h2><h4>{tg["name"]}</h4></div>', unsafe_allow_html=True)
            st.image("https:" + tg['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            st.metric("Score", f"{int(tg.get('total_rating', 0))}/100")
            if st.button("Voir la fiche", key=f"top_btn_{tg['id']}"):
                st.session_state.selected_game = tg; st.session_state.page = "details"; st.rerun()

st.divider()
st.header("Catalogue et Filtres")
f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
with f_col1: user_search = st.text_input("Chercher un jeu")
with f_col2: platform_choice = st.selectbox("Console", ["Toutes", "PS5", "Xbox Series X", "Switch", "PC"])
with f_col3: genre_choice = st.selectbox("Genre", ["Tous", "Action", "RPG", "Sport", "Aventure", "Shooter"])

plats_map = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
genres_map = {"Action": 31, "RPG": 12, "Sport": 14, "Aventure": 31, "Shooter": 5}

if user_search:
    q = f'search "{user_search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    q = "fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null"
    if platform_choice != "Toutes": q += f" & platforms = ({plats_map[platform_choice]})"
    if genre_choice != "Tous": q += f" & genres = ({genres_map[genre_choice]})"
    q += "; sort popularity desc;"

games = fetch_data("games", q)
if games:
    grid = st.columns(6)
    for idx, g in enumerate(games):
        with grid[idx%6]:
            if 'cover' in g:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button("Details", key=f"cat_btn_{g['id']}"):
                    st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

st.divider()
st.header("Chat")
if not st.session_state.user_pseudo:
    pseudo_in = st.text_input("Pseudo")
    if st.button("Rejoindre"): st.session_state.user_pseudo = pseudo_in; st.rerun()
else:
    with st.form("chat_form", clear_on_submit=True):
        txt = st.text_input(f"Message de {st.session_state.user_pseudo}")
        if st.form_submit_button("Envoyer") and txt:
            if not any(w in txt.lower() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": txt, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1][:10]:
    st.write(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'): st.markdown(f"<div class='admin-reply'><b>ADMIN :</b> {c['reply']}</div>", unsafe_allow_html=True)

# --- SECTION ADMIN AMÉLIORÉE ---
with st.expander("Admin"):
    pwd = st.text_input("Code Secret", type="password")
    if pwd == "628316":
        st.warning("Zone de gestion critique")
        if st.button("🔴 RESET TOUS LES VOTES (REMISE A ZERO)"):
            st.session_state.vs = {"j1": 0, "j2": 0}
            sauver_data(VERSUS_FILE, st.session_state.vs)
            st.success("Les compteurs sont revenus à zéro !")
            st.rerun()
        
        for i, c in enumerate(list(st.session_state.comments)):
            if st.button(f"Supprimer message {i}", key=f"del_{i}"):
                st.session_state.comments.pop(i)
                sauver_data(DB_FILE, st.session_state.comments)
                st.rerun()
