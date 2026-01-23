import streamlit as st
import requests
import json
import os
import time

# --- CONFIGURATION (Tes codes sont ici, c'est ton moteur) ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# --- SYSTÈME DE SAUVEGARDE ---
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []

def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(comms, f, indent=4)

@st.cache_data(ttl=3600)
def get_token():
    res = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials")
    return res.json().get('access_token')

def fetch(query):
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {get_token()}'}
    return requests.post("https://api.igdb.com/v4/games", headers=headers, data=query).json()

# --- INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None

st.set_page_config(page_title="GameTrend 2026", layout="wide")

# --- DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #060d23; color: white; }
    .msg { background: rgba(255,255,255,0.05); padding: 10px; border-radius: 10px; margin-bottom: 5px; border-left: 4px solid #0072ce; }
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR (PARAMÈTRES) ---
with st.sidebar:
    st.title("🎮 Menu")
    admin_pass = st.text_input("🔑 Admin", type="password")
    is_admin = (admin_pass == "1234")
    if st.button("🏠 Accueil"): st.session_state.game = None; st.rerun()

# --- VUE DÉTAILLÉE ---
if st.session_state.game:
    g = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")[0]
    if st.button("⬅️ Retour"): st.session_state.game = None; st.rerun()
    c1, c2 = st.columns([1, 2])
    with c1: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    with c2:
        st.title(g['name'])
        st.write(f"⭐ Note: {round(g.get('total_rating', 0))}/100")
        st.write(g.get('summary', 'Pas de description.'))
    st.stop()

# --- RECHERCHE ET STYLE ---
st.title("🚀 GameTrend Ultimate")
col_s1, col_s2 = st.columns(2)
with col_s1: search_name = st.text_input("🔍 Chercher un jeu...")
with col_s2: search_style = st.text_input("🎭 Par style (Action, RPG, Zelda...)")

# Affichage des résultats de recherche
if search_name or search_style:
    st.subheader("🔎 Résultats")
    q = f'search "{search_name if search_name else search_style}"; fields name, cover.url; where cover != null; limit 12;'
    res = fetch(q)
    if res:
        cols = st.columns(6)
        for i, game in enumerate(res):
            with cols[i % 6]:
                st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(game['name'][:15], key=f"s_{game['id']}"):
                    st.session_state.game = game['id']; st.rerun()

# --- FORUM ---
st.divider()
st.subheader("💬 Forum Communauté")
for i, c in enumerate(st.session_state.comments):
    st.markdown(f"<div class='msg'><b>{c['user']}</b>: {c['msg']}</div>", unsafe_allow_html=True)
    if c.get('reply'): st.caption(f"↳ Admin: {c['reply']}")
    if is_admin:
        if st.button(f"Supprimer {i}", key=f"del_{i}"):
            st.session_state.comments.pop(i); sauver_comms(st.session_state.comments); st.rerun()

if st.session_state.user:
    with st.form("post"):
        m = st.text_input("Ton message")
        if st.form_submit_button("Envoyer"):
            st.session_state.comments.append({"user": st.session_state.user, "msg": m, "reply": None})
            sauver_comms(st.session_state.comments); st.rerun()
else:
    u = st.text_input("Ton Pseudo pour parler")
    if st.button("Se connecter"): st.session_state.user = u; st.rerun()

# --- CATALOGUE TOP JEUX ---
st.divider()
st.subheader("🔥 Top Jeux du moment")
tops = fetch("fields name, cover.url; where total_rating > 85 & cover != null; sort total_rating desc; limit 12;")
if tops:
    cols = st.columns(6)
    for i, game in enumerate(tops):
        with cols[i % 6]:
            st.image("https:" + game['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(game['name'][:15], key=f"t_{game['id']}"):
                st.session_state.game = game['id']; st.rerun()
