import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & SECRETS ---
st.set_page_config(page_title="GameTrend 2026", page_icon="🎮", layout="wide")

# Récupération sécurisée depuis le carré noir (Secrets)
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

# --- 3. STYLE CSS (Le look "Incroyable") ---
st.markdown("""
    <style>
    .stApp { background-color: #0b1120; color: white; }
    .msg-box { background: rgba(30, 41, 59, 0.7); padding: 15px; border-radius: 12px; margin-bottom: 8px; border-left: 5px solid #38bdf8; }
    .reply-box { background: rgba(51, 65, 85, 0.7); padding: 12px; border-radius: 12px; margin-bottom: 8px; margin-left: 40px; border-left: 5px solid #fbbf24; }
    .stButton>button { border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { background-color: #38bdf8; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- 4. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user' not in st.session_state: st.session_state.user = None
if 'game' not in st.session_state: st.session_state.game = None
if 'reply_to' not in st.session_state: st.session_state.reply_to = None

# --- 5. BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎮 Menu Principal")
    admin_input = st.text_input("🔑 Code Admin", type="password")
    is_admin = (admin_input == ADMIN_PASS)
    if st.button("🏠 Accueil"):
        st.session_state.game = None
        st.rerun()
    if is_admin: st.success("Mode Admin Activé")

# --- 6. VUE DÉTAILLÉE DU JEU ---
if st.session_state.game:
    res = fetch(f"fields name, cover.url, summary, total_rating; where id = {st.session_state.game};")
    if res:
        g = res[0]
        if st.button("⬅️ Retour au catalogue"): st.session_state.game = None; st.rerun()
        col_img, col_txt = st.columns([1, 2])
        with col_img:
            img = "https:" + g['cover']['url'].replace('t_thumb', 't_720p') if 'cover' in g else ""
            st.image(img, use_container_width=True)
        with col_txt:
            st.title(g['name'])
            st.subheader(f"⭐ Score : {round(g.get('total_rating', 0))}/100")
            st.write(g.get('summary', "Aucun résumé disponible pour ce titre."))
    st.stop()

# --- 7. RECHERCHE ET ACTUALITÉS ---
st.title("🚀 GameTrend 2026")
search_query = st.text_input("🔍 Recherche rapide (Jeux, Styles, Studios...)")

if search_query:
    st.subheader(f"🔎 Résultats pour : {search_query}")
    res = fetch(f'search "{search_query}"; fields name, cover.url; where cover != null; limit 12;')
    if res:
        cols = st.columns(6)
        for i, g in enumerate(res):
            with cols[i%6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                if st.button(g['name'][:15], key=f"s_{g['id']}"):
                    st.session_state.game = g['id']; st.rerun()

st.divider()
st.subheader("📰 Flash News 2026")
n1, n2 = st.columns(2)
with n1: st.info("**GTA VI** : Le record de précommandes est officiellement battu.")
with n2: st.warning("**Switch 2** : Nintendo annonce une compatibilité totale avec les anciens jeux.")

# --- 8. FORUM AVEC SYSTÈME DE RÉPONSES ---
st.divider()
st.subheader("💬 Espace Discussion")

for i, c in enumerate(st.session_state.comments):
    # Différencier visuellement les messages et les réponses
    is_rep = c.get('reply_to')
    box_type = "reply-box" if is_rep else "msg-box"
    
    st.markdown(f"""
        <div class='{box_type}'>
            {f"<small style='color: #fbbf24;'>↳ Réponse à {is_rep}</small><br>" if is_rep else ""}
            <b>{c['user']}</b> : {c['msg']}
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 6])
    with c1:
        if st.button("Répondre", key=f"btn_rep_{i}"):
            st.session_state.reply_to = c['user']; st.rerun()
    with c2:
        if is_admin:
            if st.button("Supprimer", key=f"btn_del_{i}"):
                st.session_state.comments.pop(i); sauver_comms(st.session_state.comments); st.rerun()

# Formulaire d'envoi
if st.session_state.user:
    with st.form("form_message", clear_on_submit=True):
        txt_label = f"Répondre à {st.session_state.reply_to}" if st.session_state.reply_to else "Écris ton message..."
        msg_input = st.text_input(txt_label)
        if st.form_submit_button("Envoyer"):
            if msg_input:
                st.session_state.comments.append({
                    "user": st.session_state.user, 
                    "msg": msg_input, 
                    "reply_to": st.session_state.reply_to
                })
                sauver_comms(st.session_state.comments)
                st.session_state.reply_to = None
                st.rerun()
    if st.session_state.reply_to:
        if st.button("Annuler la réponse"): st.session_state.reply_to = None; st.rerun()
else:
    user_name = st.text_input("Choisis un pseudo pour participer")
    if st.button("Entrer dans le forum"):
        if user_name: st.session_state.user = user_name; st.rerun()

# --- 9. LE TOP 12 ---
st.divider()
st.subheader("🔥 Les Incontournables de 2026")
tops = fetch("fields name, cover.url; where total_rating > 85 & cover != null; sort total_rating desc; limit 12;")
if tops:
    cols = st.columns(6)
    for i, g in enumerate(tops):
        with cols[i%6]:
            st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button(g['name'][:15], key=f"t_{g['id']}"):
                st.session_state.game = g['id']; st.rerun()
