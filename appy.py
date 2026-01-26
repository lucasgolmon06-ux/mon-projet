import streamlit as st
import requests
import json
import os
import urllib.parse

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

def traduire_en_fr(texte):
    if not texte or texte == 'Aucun résumé disponible.': return texte
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(texte[:500])}&langpair=en|fr"
        res = requests.get(url).json()
        return res['responseData']['translatedText']
    except: return texte

# --- 2. INITIALISATION ---
if 'comments' not in st.session_state: st.session_state.comments = charger_data(DB_FILE)
if 'vs' not in st.session_state: st.session_state.vs = charger_data(VERSUS_FILE, {"j1": 0, "j2": 0})
if 'user_pseudo' not in st.session_state: st.session_state.user_pseudo = None
if 'page' not in st.session_state: st.session_state.page = "home"
if 'selected_game' not in st.session_state: st.session_state.selected_game = None
if 'already_voted' not in st.session_state: st.session_state.already_voted = False

# --- 3. DESIGN ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
    .price-box { background: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; }
    .buy-button { display: block; width: 100%; text-align: center; background-color: #ff9900; color: black !important; padding: 15px; font-weight: bold; text-decoration: none; border-radius: 5px; margin-top: 10px; }
    .admin-reply { background: rgba(255, 204, 0, 0.1); border-left: 5px solid #ffcc00; padding: 10px; margin-left: 20px; border-radius: 5px; color: #ffcc00; margin-top: 5px; }
    </style>
    <iframe src="https://www.youtube.com/embed/5qap5aO4i9A?autoplay=1&loop=1&playlist=5qap5aO4i9A" width="0" height="0" frameborder="0" allow="autoplay"></iframe>
""", unsafe_allow_html=True)

# --- 4. LOGIQUE API ---
@st.cache_data(ttl=3600)
def get_access_token():
    auth_url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(auth_url)
    return res.json().get('access_token')

def fetch_data(endpoint, query):
    token = get_access_token()
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    res = requests.post(f"https://api.igdb.com/v4/{endpoint}", headers=headers, data=query)
    return res.json() if res.status_code == 200 else []

# --- PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("RETOUR"): st.session_state.page = "home"; st.rerun()
    st.title(g['name'])
    c1, c2 = st.columns([2, 1])
    with c1:
        if 'videos' in g: st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g: st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'))
    with c2:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'))
        st.markdown('<div class="price-box">EN STOCK</div>', unsafe_allow_html=True)
        url_amz = f"https://www.amazon.fr/s?k={urllib.parse.quote(g['name'] + ' jeu vidéo')}"
        st.markdown(f'<a href="{url_amz}" target="_blank" class="buy-button">ACHETER SUR AMAZON</a>', unsafe_allow_html=True)
        st.info(traduire_en_fr(g.get('summary', 'Pas de résumé.')))
    st.stop()

# --- PAGE ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND 2026 -- MODE ADMIN OPÉRATIONNEL</div>', unsafe_allow_html=True)

# DUEL
st.header("Duel de Légendes")
total_votes = st.session_state.vs['j1'] + st.session_state.vs['j2']
p1 = int((st.session_state.vs['j1'] / total_votes) * 100) if total_votes > 0 else 50
col_v1, col_v2 = st.columns(2)
if not st.session_state.already_voted:
    if col_v1.button(f"GTA VI ({st.session_state.vs['j1']})", use_container_width=True):
        st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.session_state.already_voted=True; st.snow(); st.rerun()
    if col_v2.button(f"CYBERPUNK 2 ({st.session_state.vs['j2']})", use_container_width=True):
        st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.session_state.already_voted=True; st.balloons(); st.rerun()
else: st.success(f"GTA VI: {p1}% | Cyberpunk: {100-p1}%")

# CATALOGUE
st.divider()
games = fetch_data("games", "fields name, cover.url, summary, videos.video_id, screenshots.url; limit 6; where cover != null; sort popularity desc;")
if games:
    cols = st.columns(6)
    for i, g in enumerate(games):
        with cols[i]:
            st.image("https:" + g['cover']['url'])
            if st.button("Détails", key=f"btn_h_{g['id']}"):
                st.session_state.selected_game = g; st.session_state.page = "details"; st.rerun()

# --- CHAT ---
st.divider()
st.header("Chat")
if not st.session_state.user_pseudo:
    p = st.text_input("Pseudo")
    if st.button("Rejoindre"): st.session_state.user_pseudo = p; st.rerun()
else:
    with st.form("new_msg", clear_on_submit=True):
        m = st.text_input(f"{st.session_state.user_pseudo} :")
        if st.form_submit_button("Envoyer") and m:
            st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": m, "reply": None})
            sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1][:10]:
    st.write(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'): st.markdown(f'<div class="admin-reply"><b>ADMIN :</b> {c["reply"]}</div>', unsafe_allow_html=True)

# --- ZONE ADMIN ---
with st.expander("Zone Admin"):
    if st.text_input("Code", type="password") == "628316":
        for i, com in enumerate(st.session_state.comments):
            st.write(f"--- Message de {com['user']} ---")
            st.write(f"Texte : {com['msg']}")
            
            # Formulaire de réponse UNIQUE par message
            with st.form(key=f"admin_form_{i}"):
                rep = st.text_input("Ta réponse", value=com.get('reply') or "")
                c_del, c_rep = st.columns(2)
                if c_rep.form_submit_button("Publier Réponse"):
                    st.session_state.comments[i]['reply'] = rep
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()
                if c_del.form_submit_button("Supprimer Message"):
                    st.session_state.comments.pop(i)
                    sauver_data(DB_FILE, st.session_state.comments); st.rerun()
        
        if st.button("RESET TOUS LES VOTES"):
            st.session_state.vs = {"j1": 0, "j2": 0}; sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
