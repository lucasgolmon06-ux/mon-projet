import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION & DONNÉES ---
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
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json()

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None

# --- 3. STYLE CSS ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; color: #ffcc00; margin-top:5px; }
    .badge-admin { background: linear-gradient(45deg, #ffd700, #ff8c00); color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 10px; }
    .price-box { background: #28a745; color: white; padding: 15px; border-radius: 10px; font-size: 1.8rem; font-weight: bold; text-align: center; margin-bottom: 20px; border: 2px solid #ffffff; }
    .store-link { display: block; background: rgba(255,255,255,0.1); color: #00f2ff; padding: 10px; margin: 5px 0; border-radius: 5px; text-decoration: none; text-align: center; border: 1px solid #00f2ff; }
    .store-link:hover { background: #00f2ff; color: black; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("⬅️ RETOUR À L'ACCUEIL"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(f"🎮 {g['name']}")
    c_vid, c_desc = st.columns([2, 1])
    
    with c_vid:
        if 'videos' in g:
            st.subheader("📺 Trailer Officiel")
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        if 'screenshots' in g:
            st.subheader("📸 Captures de Gameplay")
            for ss in g['screenshots'][:2]:
                st.image("https:" + ss['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with c_desc:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        
        # --- LOGIQUE PRIX & BOUTIQUES ---
        st.subheader("💰 OFFRES ET PRIX")
        
        # Estimation de prix basée sur la popularité/note
        score = g.get('total_rating', 0)
        prix_affiche = "79.99€" if score > 85 else "59.99€" if score > 70 else "29.99€"
        
        st.markdown(f'<div class="price-box">{prix_affiche}</div>', unsafe_allow_html=True)
        
        # Récupération des liens de boutiques réelles
        stores = fetch_data("external_games", f"fields category, url; where game = {g['id']};")
        mapping = {1: "Steam", 11: "Microsoft Store", 16: "PlayStation Store", 23: "Nintendo eShop"}
        
        if stores:
            for s in stores:
                store_name = mapping.get(s['category'])
                if store_name:
                    st.markdown(f'<a class="store-link" href="{s["url"]}" target="_blank">Acheter sur {store_name}</a>', unsafe_allow_html=True)
        else:
            st.info("Recherche de liens marchands en cours...")

        st.metric("SCORE IGDB", f"{int(score)}/100")
        st.info(g.get('summary', 'Aucun résumé disponible.'))
    st.stop()

# --- 5. PAGE ACCUEIL ---
st.markdown('<div class="news-ticker">🚀 GAMETREND 2026 -- DÉCOUVREZ LES PRIX ET LES OFFRES EN DIRECT DANS LES DÉTAILS !</div>', unsafe_allow_html=True)

# SECTION DUEL
st.header("🔥 Le Choc des Titans")
col_v1, col_v2 = st.columns(2)
with col_v1:
    if st.button("Voter GTA VI", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
with col_v2:
    if st.button("Voter CYBERPUNK 2", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()

votes_t = st.session_state.vs['j1'] + st.session_state.vs['j2']
perc = (st.session_state.vs['j1'] / votes_t * 100) if votes_t > 0 else 50
st.progress(perc/100)
st.markdown(f"<p style='text-align:center;'>GTA VI : {int(perc)}% | CYBERPUNK 2 : {int(100-perc)}%</p>", unsafe_allow_html=True)

# SECTION CHAT
st.divider()
st.header("💬 Le Chat")
if not st.session_state.user_pseudo:
    pseudo_input = st.text_input("Entre ton pseudo :")
    if st.button("Rejoindre"): st.session_state.user_pseudo = pseudo_input; st.rerun()
else:
    with st.form("msg_form", clear_on_submit=True):
        txt = st.text_input(f"Message de {st.session_state.user_pseudo}")
        if st.form_submit_button("Envoyer") and txt:
            if not any(w in txt.lower().split() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": txt, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1]:
    st.write(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'):
        st.markdown(f"<div class='admin-reply'><span class='badge-admin'>ADMIN</span>{c['reply']}</div>", unsafe_allow_html=True)

# --- 6. CATALOGUE ---
st.divider()
st.header("🔍 Catalogue")
user_search = st.text_input("Rechercher un jeu :")

if user_search:
    q = f'search "{user_search}"; fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; limit 12; where cover != null;'
else:
    choice = st.selectbox("Console :", ["PS5", "Xbox Series X", "Switch", "PC"])
    plats = {"PS5": 167, "Xbox Series X": 169, "Switch": 130, "PC": 6}
    q = f"fields name, cover.url, summary, videos.video_id, total_rating, screenshots.url; where platforms = ({plats[choice]}) & cover != null; sort popularity desc; limit 12;"

games = fetch_data("games", q)
if games:
    cols = st.columns(6)
    for idx, g in enumerate(games):
        with cols[idx%6]:
            if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button("Détails", key=f"btn_{g['id']}"):
                st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# --- 7. ADMIN ---
st.divider()
with st.expander("🛠️ Admin"):
    if st.text_input("Code", type="password") == "628316":
        for i, c in enumerate(list(st.session_state.comments)):
            st.write(f"{c['user']}: {c['msg']}")
            if st.button("❌", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
