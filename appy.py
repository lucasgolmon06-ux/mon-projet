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
    try:
        res = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials")
        return res.json().get('access_token')
    except: return None

def fetch(query):
    token = get_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- 3. STYLE CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0b0f19; color: white; }
    .msg-box { background: rgba(255,255,255,0.07); padding: 12px; border-radius: 10px; margin-bottom: 5px; border-left: 4px solid #00d4ff; }
    .reply-box { background: rgba(255,165,0,0.1); padding: 10px; border-radius: 10px; margin-bottom: 5px; margin-left: 35px; border-left: 4px solid #ffa500; }
    .stButton>button { border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None
if 'reply_to' not in st.session_state: st.session_state.reply_to = None

# --- 5. BARRE LATÉRALE ---
with st.sidebar:
    st.title("🕹️ GameTrend")
    admin_input = st.text_input("🔑 Mode Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Retour Accueil"):
        st.session_state.game = None
        st.rerun()
    if is_admin: st.success("Admin Connecté")

# --- 6. VUE DÉTAILLÉE ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")
    if res:
        g = res[0]
        if st.button("⬅️ Quitter"): st.session_state.game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in g else "")
        with c2:
            st.title(g['name'])
            st.write(g.get('summary', "Pas de description."))
    st.stop()

# --- 7. RECHERCHE ET NEWS ---
st.title("🚀 GameTrend 2026")
s = st.text_input("🔍 Rechercher un jeu ou un style...")

if s:
    st.subheader("🔎 Résultats")
    res = fetch(f'search "{s}"; fields name, cover.url; where cover != null; limit 12;')
    if res:
        cols = st.columns(6)
        for i, g in enumerate(res):
            with cols[i%6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
                if st.button(g['name'][:15], key=f"s_{g['id']}"):
                    st.session_state.game = g['id']; st.rerun()

st.divider()
st.subheader("📰 News Gaming 2026")
n1, n2 = st.columns(2)
with n1: st.info("**GTA VI** : Le mode online disponible dès le premier jour.")
with n2: st.warning("**PS6** : Sony confirme une sortie pour fin 2027.")

# --- 8. FORUM AVEC RÉPONSES ---
st.divider()
st.subheader("💬 Forum")

for i, c in enumerate(st.session_state.comments):
    box = "reply-box" if c.get('reply_to') else "msg-box"
    prefix = f"↳ Réponse à {c['reply_to']}" if c.get('reply_to') else ""
    st.markdown(f"<div class='{box}'><small>{prefix}</small><br><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Répondre", key=f"rep_{i}"):
            st.session_state.reply_to = c['user']; st.rerun()
    with col2:
        if is_admin:
            if st.button("Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_comms(st.session_state.comments); st.rerun()

if st.session_state.user:
    with st.form("f_msg", clear_on_submit=True):
        label = f"Répondre à {st.session_state.reply_to}" if st.session_state.reply_to else "Ton message"
        m = st.text_input(label)
        if st.form_submit_button("Envoyer"):
            if m:
                st.session_state.comments.append({"user": st.session_state.user, "msg": m, "reply_to": st.session_state.reply_to})
                sauver_comms(st.session_state.comments); st.session_state.reply_to = None; st.rerun()
    if st.session_state.reply_to:
        if st.button("Annuler réponse"): st.session_state.reply_to = None; st.rerun()
else:
    u = st.text_input("Pseudo")
    if st.button("Rejoindre le chat"):
        if u: st.session_state.user = u; st.rerun()

# --- 9. TOP 12 ---
st.divider()
st.subheader("🔥 Top 12 des Jeux mieux notés")
tops = fetch("fields name, cover.url; where total_rating > 80 & cover != null; sort total_rating desc; limit 12;")
if tops:
    cols = st.columns(6)
    for i, g in enumerate(tops):
        with cols[i%6]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
            if st.button(g['name'][:15], key=f"t_{g['id']}"):
                st.session_state.game = g['id']; st.rerun()
