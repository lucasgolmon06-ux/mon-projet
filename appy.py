import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="GameTrend 2026", page_icon="🎮", layout="wide")

# Récupération sécurisée
CLIENT_ID = st.secrets["ID"]
CLIENT_SECRET = st.secrets["SECRET"]
ADMIN_PASS = st.secrets["ADMIN"]
DB_FILE = "data_comms.json"

# --- 2. FONCTIONS ---
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
    res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
    return res.json()

# --- 3. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None
if 'reply_to' not in st.session_state: st.session_state.reply_to = None

# --- 4. BARRE LATÉRALE (ADMIN & RETOUR) ---
with st.sidebar:
    st.title("🕹️ GameTrend")
    admin_input = st.text_input("🔑 Mode Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Retour à l'accueil"):
        st.session_state.game = None
        st.rerun()

# --- 5. VUE DÉTAILLÉE DU JEU ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")
    if res:
        g = res[0]
        st.button("⬅️ Retour", on_click=lambda: setattr(st.session_state, 'game', None))
        c1, c2 = st.columns([1, 2])
        with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_720p'))
        with c2:
            st.title(g['name'])
            st.write(g.get('summary', "Aucune description."))
    st.stop()

# --- 6. SECTION RECHERCHE ---
st.title("🚀 GameTrend 2026")
search = st.text_input("🔍 Rechercher un jeu, une console ou un style (Action, RPG...)")
if search:
    res = fetch(f'search "{search}"; fields name, cover.url; where cover != null; limit 12;')
    cols = st.columns(6)
    for i, g in enumerate(res):
        with cols[i%6]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
            if st.button(g['name'][:15], key=f"s_{g['id']}"):
                st.session_state.game = g['id']; st.rerun()

# --- 7. TOP 12 DES JEUX (POPULAIRES) ---
st.divider()
st.subheader("🔥 Top 12 des Jeux du moment")
tops = fetch("fields name, cover.url; where total_rating > 80 & cover != null; sort total_rating desc; limit 12;")
cols = st.columns(6)
for i, g in enumerate(tops):
    with cols[i%6]:
        st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        if st.button(g['name'][:15], key=f"t_{g['id']}"):
            st.session_state.game = g['id']; st.rerun()

# --- 8. SECTION NEWS (SIMULÉES 2026) ---
st.divider()
st.subheader("📰 Actualités Gaming 2026")
col_n1, col_n2 = st.columns(2)
with col_n1:
    st.info("**GTA VI :** Nouveau DLC 'Vice City Nights' annoncé pour cet été !")
with col_n2:
    st.warning("**Nintendo :** La 'Switch 2' reçoit sa première mise à jour majeure.")

# --- 9. FORUM AVEC RÉPONSES ---
st.divider()
st.subheader("💬 Forum")
for i, c in enumerate(st.session_state.comments):
    box_style = "margin-left: 30px; border-left: 3px solid orange;" if c.get('reply_to') else "border-left: 3px solid blue;"
    st.markdown(f"<div style='background: #1e2630; padding: 10px; border-radius: 5px; {box_style} margin-bottom: 5px;'>"
                f"<small>{'↳ Réponse à ' + c['reply_to'] if c.get('reply_to') else ''}</small><br>"
                f"<b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns([1, 5])
    with col_f1:
        if st.button("Répondre", key=f"rep_{i}"): st.session_state.reply_to = c['user']; st.rerun()
    with col_f2:
        if is_admin:
            if st.button("Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_comms(st.session_state.comments); st.rerun()

if st.session_state.user:
    with st.form("msg", clear_on_submit=True):
        label = f"Répondre à {st.session_state.reply_to}" if st.session_state.reply_to else "Message"
        m = st.text_input(label)
        if st.form_submit_button("Envoyer"):
            if m:
                st.session_state.comments.append({"user": st.session_state.user, "msg": m, "reply_to": st.session_state.reply_to})
                sauver_comms(st.session_state.comments); st.session_state.reply_to = None; st.rerun()
    if st.session_state.reply_to:
        if st.button("Annuler la réponse"): st.session_state.reply_to = None; st.rerun()
else:
    u = st.text_input("Pseudo")
    if st.button("Se connecter"): st.session_state.user = u; st.rerun()
