import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")

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
if 'reply_to' not in st.session_state: st.session_state.reply_to = None # Pour stocker à qui on répond

# --- 4. DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #060d23; color: white; }
    .msg { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 10px; margin-bottom: 5px; border-left: 5px solid #0072ce; }
    .reply { background: rgba(255,165,0,0.1); padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 5px solid #ffa500; margin-left: 40px; }
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

# --- 5. BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎮 GameTrend")
    admin_input = st.text_input("🔑 Mode Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Accueil"):
        st.session_state.game = None
        st.rerun()

# --- 6. VUE JEU ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")
    if res:
        g = res[0]
        if st.button("⬅️ Retour"): st.session_state.game = None; st.rerun()
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in g else "")
        with c2:
            st.title(g['name'])
            st.write(g.get('summary', "Pas de description."))
    st.stop()

# --- 7. RECHERCHE ---
st.title("🚀 GameTrend 2026")
s1, s2 = st.columns(2)
with s1: sn = st.text_input("🔍 Nom du jeu")
with s2: ss = st.text_input("🎭 Style")

if sn or ss:
    term = sn if sn else ss
    res = fetch(f'search "{term}"; fields name, cover.url; where cover != null; limit 12;')
    if res:
        cols = st.columns(6)
        for i, g in enumerate(res):
            with cols[i%6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
                if st.button(g['name'][:15], key=f"s_{g['id']}"):
                    st.session_state.game = g['id']; st.rerun()

# --- 8. FORUM (SYSTÈME DE RÉPONSES) ---
st.divider()
st.subheader("💬 Forum des Joueurs")

for i, c in enumerate(st.session_state.comments):
    # On vérifie si c'est une réponse ou un message normal
    style_class = "reply" if c.get("is_reply") else "msg"
    mention = f"<small style='color: #ffa500;'>↳ En réponse à {c['target']}</small><br>" if c.get("is_reply") else ""
    
    st.markdown(f"<div class='{style_class}'>{mention}<b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    
    # Boutons d'action
    col_a, col_b = st.columns([1, 6])
    with col_a:
        if st.button("💬", key=f"rep_btn_{i}", help="Répondre"):
            st.session_state.reply_to = c['user']
            st.rerun()
    with col_b:
        if is_admin:
            if st.button("🗑️", key=f"del_{i}", help="Supprimer"):
                st.session_state.comments.pop(i)
                sauver_comms(st.session_state.comments)
                st.rerun()

# Formulaire dynamique (Post ou Réponse)
if st.session_state.user:
    with st.form("post_form", clear_on_submit=True):
        label = f"Répondre à {st.session_state.reply_to}" if st.session_state.reply_to else f"Message en tant que {st.session_state.user}"
        m = st.text_input(label)
        c_sub, c_can = st.columns([1, 1])
        with c_sub:
            if st.form_submit_button("Envoyer"):
                if m:
                    new_c = {"user": st.session_state.user, "msg": m}
                    if st.session_state.reply_to:
                        new_c["is_reply"] = True
                        new_c["target"] = st.session_state.reply_to
                    st.session_state.comments.append(new_c)
                    sauver_comms(st.session_state.comments)
                    st.session_state.reply_to = None
                    st.rerun()
        with c_can:
            if st.session_state.reply_to:
                if st.form_submit_button("Annuler"):
                    st.session_state.reply_to = None
                    st.rerun()
else:
    u = st.text_input("Pseudo pour parler")
    if st.button("Se connecter"):
        if u: st.session_state.user = u; st.rerun()

# --- 9. CATALOGUE ---
st.divider()
st.subheader("🔥 Top 12")
tops = fetch("fields name, cover.url; where total_rating > 80 & cover != null; sort total_rating desc; limit 12;")
if tops:
    cols = st.columns(6)
    for i, g in enumerate(tops):
        with cols[i%6]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
            if st.button(g['name'][:15], key=f"t_{g['id']}"):
                st.session_state.game = g['id']; st.rerun()
