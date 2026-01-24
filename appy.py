import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
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

# --- 3. STYLE CSS (SOBRE) ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14; color: #ffffff; }
    .news-ticker { border-bottom: 1px solid #333; padding: 10px; font-size: 0.9em; color: #aaa; text-align: center; margin-bottom: 20px;}
    .admin-reply { background: #1a1a1a; border-left: 3px solid #666; padding: 10px; margin-left: 20px; border-radius: 4px; color: #ccc; margin-top:5px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. PAGE DE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("← RETOUR"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'])
    col_main, col_side = st.columns([2, 1])
    with col_main:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g:
            for ss in g['screenshots'][:2]:
                st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    with col_side:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        st.write(f"**Note IGDB:** {int(g.get('total_rating', 0))}/100")
        st.write(g.get('summary', 'Pas de résumé.'))
    st.stop()

# --- 5. ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND 2026 // ANALYSE DU MARCHÉ // GTA VI vs CYBERPUNK 2</div>', unsafe_allow_html=True)

# DUEL
st.subheader("Duel de la semaine")
c1, c2 = st.columns(2)
with c1: 
    if st.button("GTA VI", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with c2: 
    if st.button("CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
t = st.session_state.vs['j1'] + st.session_state.vs['j2']
p = (st.session_state.vs['j1']/t*100) if t>0 else 50
st.progress(p/100)

# FORUM
st.divider()
st.subheader("Discussions")
if not st.session_state.user_pseudo:
    st.session_state.user_pseudo = st.text_input("Pseudo :")
else:
    with st.form("chat", clear_on_submit=True):
        m = st.text_input(f"Message ({st.session_state.user_pseudo}) :")
        if st.form_submit_button("Envoyer") and m:
            if not any(word in m.lower().split() for word in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for comm in st.session_state.comments[::-1][:10]:
    st.markdown(f"**{comm['user']}** : {comm['msg']}")
    if comm.get('reply'):
        st.markdown(f"<div class='admin-reply'><b>Réponse Admin</b> : {comm['reply']}</div>", unsafe_allow_html=True)

# --- 6. CATALOGUE (AAA, INDÉ, RÉTRO) ---
st.divider()
st.subheader("Catalogue")

def afficher_grille(query):
    jeux = fetch_data("games", query)
    if jeux:
        cols = st.columns(6)
        for i, j in enumerate(jeux):
            with cols[i%6]:
                if 'cover' in j:
                    st.image("https:" + j['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.write(f"**{j['name']}**")
                if st.button("Détails", key=f"d_{j['id']}"):
                    st.session_state.selected_game = j; st.session_state.page = "details"; st.rerun()

search = st.text_input("🔍 Rechercher un jeu :")

if search:
    q = f'search "{search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
    afficher_grille(q)
else:
    t1, t2, t3 = st.tabs(["🏆 Meilleurs AAA", "✨ Indépendants", "🕹️ Rétro"])
    with t1:
        # AAA : Gros budget (category 0) + Note élevée
        afficher_grille("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where total_rating > 80 & category = 0; sort popularity desc; limit 12; where cover != null;")
    with t2:
        # Indé : Thème Indie (32)
        afficher_grille("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where themes = (32); sort popularity desc; limit 12; where cover != null;")
    with t3:
        # Rétro : Avant l'an 2000
        afficher_grille("fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where first_release_date < 946684800 & total_rating > 75; sort popularity desc; limit 12; where cover != null;")

# --- 7. ADMIN ---
st.divider()
with st.expander("🛠️ Admin"):
    if st.text_input("Code", type="password") == "628316":
        for i, c in enumerate(st.session_state.comments):
            st.write(f"{c['user']}: {c['msg']}")
            if st.button("Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            rep = st.text_input("Répondre", key=f"r_{i}")
            if st.button("OK", key=f"b_{i}"):
                st.session_state.comments[i]['reply'] = rep; sauver_data(DB_FILE, st.session_state.comments); st.rerun()
