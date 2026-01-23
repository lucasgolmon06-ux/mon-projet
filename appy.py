import streamlit as st
import requests
import json
import os

# --- 1. RÉCUPÉRATION DES SECRETS (Sécurité Totale) ---
CLIENT_ID = st.secrets["ID"]
CLIENT_SECRET = st.secrets["SECRET"]
ADMIN_PASS = st.secrets["ADMIN"]
DB_FILE = "data_comms.json"

# --- 2. FONCTIONS TECHNIQUES (IGDB & Sauvegarde) ---
def charger_comms():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: return []
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(comms, f, indent=4)

@st.cache_data(ttl=3600)
def get_token():
    res = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials")
    return res.json().get('access_token')

def fetch(query):
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {get_token()}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except:
        return []

# --- 3. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None

st.set_page_config(page_title="GameTrend 2026", layout="wide")

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #060d23; color: white; }
    .msg { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #0072ce; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 5. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.title("🎮 GameTrend")
    admin_input = st.text_input("🔑 Mode Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.game = None
        st.rerun()
    if is_admin:
        st.success("Mode Admin Activé")

# --- 6. VUE DÉTAILLÉE DU JEU ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating, genres.name; where id = {st.session_state.game};")
    if res:
        g = res[0]
        if st.button("⬅️ Quitter la fiche"): st.session_state.game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1:
            img = "https:" + g['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in g else "https://via.placeholder.com/720"
            st.image(img, use_container_width=True)
        with c2:
            st.title(g['name'])
            st.subheader(f"⭐ Note : {round(g.get('total_rating', 0))}/100")
            st.write(g.get('summary', "Pas de description disponible."))
    st.stop()

# --- 7. RECHERCHE ET FILTRES ---
st.title("🚀 Découvrez votre prochain jeu")
col_s1, col_s2 = st.columns(2)
with col_s1: search_name = st.text_input("🔍 Rechercher un nom (Zelda, Mario...)")
with col_s2: search_style = st.text_input("🎭 Rechercher un style (Action, RPG...)")

if search_name or search_style:
    st.subheader("🔎 Résultats")
    term = search_name if search_name else search_style
    q = f'search "{term}"; fields name, cover.url; where cover != null; limit 12;'
    res = fetch(q)
    if res:
        cols = st.columns(6)
        for i, game in enumerate(res):
            with cols[i % 6]:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(game['name'][:15], key=f"s_{game['id']}"):
                    st.session_state.game = game['id']; st.rerun()

# --- 8. FORUM ---
st.divider()
st.subheader("💬 Forum des Joueurs")

# Affichage des messages
for i, c in enumerate(st.session_state.comments):
    st.markdown(f"<div class='msg'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    if is_admin:
        if st.button(f"Supprimer le message {i}", key=f"del_{i}"):
            st.session_state.comments.pop(i)
            sauver_comms(st.session_state.comments)
            st.rerun()

# Formulaire pour poster
if st.session_state.user:
    with st.form("post_msg", clear_on_submit=True):
        m = st.text_input(f"En tant que {st.session_state.user} :")
        if st.form_submit_button("Envoyer"):
            if m:
                st.session_state.comments.append({"user": st.session_state.user, "msg": m})
                sauver_comms(st.session_state.comments)
                st.rerun()
else:
    u = st.text_input("Choisis un pseudo pour parler")
    if st.button("Rejoindre le chat"):
        if u: st.session_state.user = u; st.rerun()

# --- 9. TOP JEUX (CATALOGUE) ---
st.divider()
st.subheader("🔥 Top 12 des Jeux les mieux notés")
tops = fetch("fields name, cover.url; where total_rating > 80 & cover != null; sort total_rating desc; limit 12;")
if tops:
    cols = st.columns(6)
    for i, game in enumerate(tops):
        with cols[i % 6]:
            st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(game['name'][:15], key=f"t_{game['id']}"):
                st.session_state.game = game['id']; st.rerun()
