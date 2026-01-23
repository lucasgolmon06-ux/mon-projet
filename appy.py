import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="GameTrend 2026", page_icon="🎮", layout="wide")

CLIENT_ID = st.secrets["ID"]
CLIENT_SECRET = st.secrets["SECRET"]
ADMIN_PASS = st.secrets["ADMIN"]
DB_FILE = "data_comms.json"

# --- 2. FONCTIONS TECHNIQUES ---
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
    except: return []

# --- 3. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None
if 'reply_to' not in st.session_state: st.session_state.reply_to = None

# --- 4. STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #060d23; color: white; }
    .msg-box { background: rgba(255,255,255,0.07); padding: 12px; border-radius: 10px; margin-bottom: 5px; border-left: 4px solid #00d4ff; }
    .reply-box { background: rgba(0,212,255,0.05); padding: 10px; border-radius: 10px; margin-bottom: 5px; margin-left: 30px; border-left: 4px solid #ffcc00; }
    </style>
""", unsafe_allow_html=True)

# --- 5. BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎮 GameTrend")
    admin_input = st.text_input("🔑 Mode Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Retour Accueil"):
        st.session_state.game = None
        st.rerun()
    if is_admin: st.success("Mode Admin Activé")

# --- 6. VUE DÉTAILLÉE DU JEU ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")
    if res:
        g = res[0]
        if st.button("⬅️ Quitter la fiche"): st.session_state.game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1:
            img = "https:" + g['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in g else ""
            st.image(img, use_container_width=True)
        with c2:
            st.title(g['name'])
            st.write(g.get('summary', "Pas de description."))
    st.stop()

# --- 7. ACCUEIL ET RECHERCHE ---
st.title("🚀 Découvrez votre prochain jeu")
search = st.text_input("🔍 Rechercher un jeu (Zelda, Mario, Action...)")

if search:
    st.subheader("🔎 Résultats de recherche")
    res = fetch(f'search "{search}"; fields name, cover.url; where cover != null; limit 12;')
else:
    st.subheader("🔥 Top 12 des Jeux 2026")
    res = fetch("fields name, cover.url; where total_rating > 80 & cover != null; sort total_rating desc; limit 12;")

if res:
    cols = st.columns(6)
    for i, g in enumerate(res):
        with cols[i % 6]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(g['name'][:15], key=f"g_{g['id']}"):
                st.session_state.game = g['id']; st.rerun()

# --- 8. FORUM AVEC RÉPONSES ---
st.divider()
st.subheader("💬 Forum des Joueurs")

for i, c in enumerate(st.session_state.comments):
    div_class = "reply-box" if c.get('reply_to') else "msg-box"
    prefix = f"↳ En réponse à {c['reply_to']}" if c.get('reply_to') else ""
    st.markdown(f"<div class='{div_class}'><small>{prefix}</small><br><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button(f"Répondre", key=f"rep_{i}"):
            st.session_state.reply_to = c['user']; st.rerun()
    with col2:
        if is_admin:
            if st.button(f"Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i)
                sauver_comms(st.session_state.comments)
                st.rerun()

if st.session_state.user:
    with st.form("msg_form", clear_on_submit=True):
        txt = f"Répondre à {st.session_state.reply_to}" if st.session_state.reply_to else "Votre message"
        m = st.text_input(txt)
        if st.form_submit_button("Envoyer"):
            if m:
                new_msg = {"user": st.session_state.user, "msg": m, "reply_to": st.session_state.reply_to}
                st.session_state.comments.append
