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

# --- 2. GESTION DES MESSAGES (Correction du bug de disparition) ---
def charger_comms():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return []
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(comms, f, indent=4)

# --- 3. CONNEXION IGDB ---
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

# --- 4. STYLE ---
st.markdown("""
    <style>
    .stApp { background-color: #060d23; color: white; }
    .msg { background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #0072ce; }
    .reply { background: rgba(255,165,0,0.1); padding: 10px; border-radius: 10px; margin-left: 30px; border-left: 5px solid #ffa500; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 5. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None
if 'reply_to' not in st.session_state: st.session_state.reply_to = None

# --- 6. BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎮 GameTrend")
    admin_input = st.text_input("🔑 Mode Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Accueil"):
        st.session_state.game = None
        st.rerun()

# --- 7. RECHERCHE & JEUX ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")
    if res:
        g = res[0]
        st.button("⬅️ Retour", on_click=lambda: setattr(st.session_state, 'game', None))
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in g else "")
        with c2:
            st.title(g['name'])
            st.write(g.get('summary', "Pas de résumé."))
    st.stop()

st.title("🚀 Découvrez votre prochain jeu")
search = st.text_input("🔍 Rechercher un jeu ou un style...")
if search:
    res = fetch(f'search "{search}"; fields name, cover.url; where cover != null; limit 12;')
    cols = st.columns(6)
    for i, g in enumerate(res):
        with cols[i%6]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
            if st.button(g['name'][:15], key=f"s_{g['id']}"):
                st.session_state.game = g['id']; st.rerun()

# --- 8. FORUM (AVEC RÉPONSES) ---
st.divider()
st.subheader("💬 Forum")

for i, c in enumerate(st.session_state.comments):
    div_class = "reply" if c.get('reply_to') else "msg"
    mention = f"<small>↳ Réponse à {c['reply_to']}</small><br>" if c.get('reply_to') else ""
    st.markdown(f"<div class='{div_class}'>{mention}<b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    
    col_r, col_d = st.columns([1, 5])
    with col_r:
        if st.button("💬", key=f"r_{i}"):
            st.session_state.reply_to = c['user']; st.rerun()
    with col_d:
        if is_admin and st.button("🗑️", key=f"d_{i}"):
            st.session_state.comments.pop(i)
            sauver_comms(st.session_state.comments)
            st.rerun()

if st.session_state.user:
    with st.form("forum", clear_on_submit=True):
        txt = f"Répondre à {st.session_state.reply_to}" if st.session_state.reply_to else "Message"
        m = st.text_input(txt)
        if st.form_submit_button("Envoyer"):
            if m:
                st.session_state.comments.append({"user": st.session_state.user, "msg": m, "reply_to": st.session_state.reply_to})
                sauver_comms(st.session_state.comments)
                st.session_state.reply_to = None
                st.rerun()
else:
    u = st.text_input("Pseudo")
    if st.button("Se connecter"): st.session_state.user = u; st.rerun()

# --- 9. TOP 12 ---
st.divider()
st.subheader("🔥 Top 12")
tops = fetch("fields name, cover.url; where total_rating > 80 & cover != null; sort total_rating desc; limit 12;")
cols = st.columns(6)
for i, g in enumerate(tops):
    with cols[i%6]:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        if st.button(g['name'][:15], key=f"t_{g['id']}"):
            st.session_state.game = g['id']; st.rerun()
