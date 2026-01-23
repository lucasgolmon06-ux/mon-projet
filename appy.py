import streamlit as st
import requests
import json
import os
import time

# --- CONFIGURATION API ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"

# (Fonctions charger_comms, sauver_comms et get_access_token identiques...)
def charger_comms():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    return []
def sauver_comms(comms):
    with open(DB_FILE, "w", encoding="utf-8") as f: json.dump(comms, f, indent=4)

if 'comments' not in st.session_state: st.session_state.comments = charger_comms()
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None

@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    try:
        res = requests.post(auth_url)
        return res.json().get('access_token')
    except: return None

def fetch_data(query):
    token = get_access_token()
    if not token: return []
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE & DESIGN ---
st.set_page_config(page_title="GameTrend Ultra", layout="wide")
st.markdown("""<style>.stApp { background-color: #00051d; color: white; }
.msg-user { background: #001a3d; padding: 12px; border-radius: 10px; border-left: 5px solid #0072ce; margin-top: 10px; }
.msg-admin { background: #002b5c; padding: 12px; border-radius: 10px; border-left: 5px solid #ffcc00; margin-left: 30px; margin-top: 5px; color: #ffcc00; }
</style>""", unsafe_allow_html=True)

# (L'intro des logos reste ici...)
if 'loaded' not in st.session_state:
    time.sleep(1.0) # Réduit pour test, remets 6.2 pour la version finale
    st.session_state['loaded'] = True

# --- HEADER & COMMUNAUTÉ ---
h_col1, h_col2 = st.columns([3, 1])
with h_col1: st.title("GameTrend Pro")
with h_col2: ouvrir_comm = st.toggle("💬 Communauté")

if ouvrir_comm:
    c1, c2 = st.columns([1, 2])
    with c1:
        if st.session_state.user_pseudo is None:
            p_in = st.text_input("Choisis ton pseudo unique")
            if st.button("Valider"): st.session_state.user_pseudo = p_in; st.rerun()
        else:
            st.write(f"Connecté : **{st.session_state.user_pseudo}**")
            m = st.text_area("Message")
            if st.button("Poster"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_comms(st.session_state.comments); st.rerun()
    with c2:
        for i, c in enumerate(reversed(st.session_state.comments)):
            st.markdown(f'<div class="msg-user"><b>{c["user"]}</b> : {c["msg"]}</div>', unsafe_allow_html=True)
            if c.get('reply'): st.markdown(f'<div class="msg-admin"><b>Auteur</b> : {c["reply"]}</div>', unsafe_allow_html=True)
    st.divider()

# --- RECHERCHE & STYLE ---
search_query = st.text_input("🔍 Recherche précise...")
style_in = st.text_input("💡 Style de jeu...")

# --- FILTRES DYNAMIQUES PAR CONSOLE ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    st.divider()
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        st.header(f"Top 12 {name}")
    with col_t2:
        # LE PETIT TRUC POUR CHOISIR L'OPTION
        choix = st.selectbox(f"Filtrer {name} par :", 
                              ["Meilleures notes", "Les plus appréciés", "Gros Budgets (AAA)", "Jeux Indépendants"],
                              key=f"filter_{name}")

    # Logique des requêtes IGDB selon le choix
    base_where = f"platforms = ({p_id}) & cover != null"
    
    if choix == "Meilleures notes":
        q = f"fields name, cover.url, total_rating; where {base_where} & total_rating != null; sort total_rating desc; limit 12;"
    elif choix == "Les plus appréciés":
        q = f"fields name, cover.url, total_rating, follows; where {base_where}; sort follows desc; limit 12;"
    elif choix == "Gros Budgets (AAA)":
        # On filtre par thèmes ou on exclut le tag Indie (IGDB n'a pas de filtre 'budget' direct, on utilise le rating/popularity)
        q = f"fields name, cover.url, total_rating; where {base_where} & themes != (31); sort total_rating desc; limit 12;"
    else: # Indépendants
        q = f"fields name, cover.url, total_rating; where {base_where} & themes = (31); sort total_rating desc; limit 12;"

    jeux = fetch_data(q)
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                note = round(g.get('total_rating', 0))
                st.markdown(f"<p style='color:#ffcc00;'>⭐ {note}/100</p>", unsafe_allow_html=True)
