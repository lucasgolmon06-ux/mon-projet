import streamlit as st
import requests
import json
import os

# --- 1. CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'
DB_FILE = "data_comms.json"
VERSUS_FILE = "versus_stats.json"

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

def fetch_data(query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
    return res.json()

# --- 2. INITIALISATION ---
if 'section' not in st.session_state: st.session_state.section = "ACCUEIL"
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None

# --- 3. STYLE CSS (TON SCHÉMA) ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-header { border: 3px solid white; padding: 20px; text-align: center; font-size: 40px; font-weight: bold; margin-bottom: 20px; }
    .msg-user { background: #001a3d; padding: 15px; border-radius: 10px; border-left: 5px solid #0072ce; margin-bottom: 10px; }
    .admin-reply { background: #1a1a00; border-left: 5px solid #ffcc00; padding: 10px; margin-left: 30px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- 4. NAVIGATION HAUTE ---
st.markdown('<div class="news-header">NEW</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("DUEL", use_container_width=True): st.session_state.section = "ACCUEIL"
with c2:
    if st.button("COMMU", use_container_width=True): st.session_state.section = "COMMU"
with c3:
    if st.button("TOP", use_container_width=True): st.session_state.section = "TOP"
with c4:
    if st.button("ADMIN", use_container_width=True): st.session_state.section = "ADMIN"

st.divider()

# --- 5. LOGIQUE D'AFFICHAGE ---

# --- SECTION ACCUEIL (DUEL + JEUX OUVERT IMMÉDIATEMENT) ---
if st.session_state.section == "ACCUEIL":
    # Le Duel
    st.subheader("🔥 DUEL EN COURS")
    v1, vs_txt, v2 = st.columns([2, 1, 2])
    with v1:
        st.write("### GTA VI")
        if st.button("Voter GTA"): st.session_state.vs['j1'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    with vs_txt: st.markdown("<h2 style='text-align:center;'>VS</h2>", unsafe_allow_html=True)
    with v2:
        st.write("### CYBERPUNK 2")
        if st.button("Voter CP2"): st.session_state.vs['j2'] += 1; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
    
    total = st.session_state.vs['j1'] + st.session_state.vs['j2']
    st.progress(st.session_state.vs['j1'] / (total if total > 0 else 1))
    
    st.divider()
    
    # Les Jeux
    st.subheader("🎮 DERNIÈRES SORTIES")
    res = fetch_data("fields name, cover.url; sort first_release_date desc; limit 12; where cover != null;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(g['name'])

# --- SECTION COMMUNAUTÉ (S'AFFICHE EN GRAND) ---
elif st.session_state.section == "COMMU":
    st.title("💬 FORUM COMMUNAUTÉ")
    if not st.session_state.user_pseudo:
        p = st.text_input("Choisis ton pseudo :")
        if st.button("Entrer"): st.session_state.user_pseudo = p; st.rerun()
    else:
        with st.form("chat"):
            m = st.text_input("Message...")
            if st.form_submit_button("Envoyer"):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        
        for c in st.session_state.comments[::-1]:
            st.markdown(f"<div class='msg-user'><b>{c['user']}</b> : {c['msg']}</div>", unsafe_allow_html=True)
            if c.get('reply'):
                st.markdown(f"<div class='admin-reply'>🛡️ {c['reply']}</div>", unsafe_allow_html=True)

# --- SECTION ADMIN (VIDE SANS CODE) ---
elif st.session_state.section == "ADMIN":
    st.title("🛡️ ZONE ADMIN")
    code = st.text_input("Code secret :", type="password")
    
    if code == "628316":
        st.success("Accès Maître autorisé")
        st.write(f"📊 Votes GTA: {st.session_state.vs['j1']} | Votes CP2: {st.session_state.vs['j2']}")
        
        st.subheader("Répondre aux messages")
        for i, c in enumerate(st.session_state.comments[::-1]):
            idx = len(st.session_state.comments) - 1 - i
            if not c.get('reply'):
                with st.expander(f"De: {c['user']} - {c['msg']}"):
                    ans = st.text_input("Ta réponse :", key=f"ans_{idx}")
                    if st.button("Envoyer", key=f"btn_{idx}"):
                        st.session_state.comments[idx]['reply'] = ans
                        sauver_data(DB_FILE, st.session_state.comments); st.rerun()
    elif code != "":
        st.error("Code erroné.")

# --- SECTION TOP ---
elif st.session_state.section == "TOP":
    st.title("🏆 MEILLEURES NOTES")
    res = fetch_data("fields name, cover.url; sort total_rating desc; limit 18; where cover != null;")
    if res:
        cols = st.columns(6)
        for j, g in enumerate(res):
            with cols[j % 6]:
                st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
                st.caption(g['name'])
