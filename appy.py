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

# --- 3. DESIGN, AUDIO & STYLE ---
st.set_page_config(page_title="GameTrend 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    .news-ticker { background: #0072ce; color: white; padding: 12px; font-weight: bold; border-radius: 5px; margin-bottom: 20px;}
    .top-card { background: rgba(255, 215, 0, 0.1); border: 1px solid #ffd700; border-radius: 10px; padding: 15px; text-align: center; }
    .price-box { background: #28a745; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 1.2rem; text-align: center; margin-bottom: 10px; }
    .buy-button { 
        display: block; width: 100%; text-align: center; background-color: #ff9900; color: black !important; 
        padding: 15px; font-weight: bold; text-decoration: none; border-radius: 5px; margin-top: 10px;
    }
    .vote-perc { font-size: 1.5rem; font-weight: bold; color: #ffd700; text-align: center; }
    .admin-reply { background: rgba(255, 204, 0, 0.1); border-left: 5px solid #ffcc00; padding: 10px; margin-left: 20px; border-radius: 5px; color: #ffcc00; margin-top: 5px; }
    </style>

    <iframe src="https://www.youtube.com/embed/5qap5aO4i9A?autoplay=1&loop=1&playlist=5qap5aO4i9A" 
            width="0" height="0" frameborder="0" allow="autoplay"></iframe>
    
    <audio id="clickSound" src="https://www.soundjay.com/buttons/button-16.mp3" preload="auto"></audio>

    <script>
    window.parent.document.addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON' || e.target.closest('button')) {
            const audio = window.parent.document.getElementById('clickSound');
            if(audio) { audio.currentTime = 0; audio.play(); }
        }
    });
    </script>
""", unsafe_allow_html=True)

# --- 4. LOGIQUE API IGDB ---
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

# --- 5. NAVIGATION : PAGE DÉTAILS ---
if st.session_state.page == "details" and st.session_state.selected_game:
    g = st.session_state.selected_game
    if st.button("RETOUR A L'ACCUEIL"):
        st.session_state.page = "home"; st.rerun()
    
    st.title(g['name'])
    c_vid, c_desc = st.columns([2, 1])
    
    with c_vid:
        if 'videos' in g:
            st.subheader("Trailer Officiel")
            st.video(f"https://www.youtube.com/watch?v={g['videos'][0]['video_id']}")
        elif 'screenshots' in g:
            st.image("https:" + g['screenshots'][0]['url'].replace('t_thumb', 't_720p'), use_container_width=True)
    
    with c_desc:
        if 'cover' in g: st.image("https:" + g['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
        score = g.get('total_rating', 0)
        prix = "79.99€" if score > 85 else "59.99€" if score > 70 else "29.99€"
        st.markdown(f'<div class="price-box">PRIX ESTIMÉ : {prix}</div>', unsafe_allow_html=True)
        
        search_query = urllib.parse.quote(f"{g['name']} jeu vidéo")
        url_amazon = f"https://www.amazon.fr/s?k={search_query}"
        st.markdown(f'<a href="{url_amazon}" target="_blank" class="buy-button">ACHETER SUR AMAZON</a>', unsafe_allow_html=True)
        
        st.divider()
        st.metric("SCORE CRITIQUE", f"{int(score)}/100")
        st.subheader("Résumé (FR)")
        st.info(traduire_en_fr(g.get('summary', 'Aucun résumé disponible.')))
    st.stop()

# --- 6. PAGE ACCUEIL ---
st.markdown('<div class="news-ticker">GAMETREND 2026 -- TOUTES OPTIONS ACTIVÉES</div>', unsafe_allow_html=True)

# SECTION DUEL
st.header("Duel de Légendes")
total_votes = st.session_state.vs['j1'] + st.session_state.vs['j2']
p1 = int((st.session_state.vs['j1'] / total_votes) * 100) if total_votes > 0 else 50
p2 = 100 - p1 if total_votes > 0 else 50

col_v1, col_v2 = st.columns(2)
if not st.session_state.already_voted:
    with col_v1:
        if st.button(f"GTA VI ({st.session_state.vs['j1']})", use_container_width=True):
            st.session_state.vs['j1']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.session_state.already_voted=True; st.snow(); st.rerun()
    with col_v2:
        if st.button(f"CYBERPUNK 2 ({st.session_state.vs['j2']})", use_container_width=True):
            st.session_state.vs['j2']+=1; sauver_data(VERSUS_FILE, st.session_state.vs); st.session_state.already_voted=True; st.balloons(); st.rerun()
else: st.success("Merci pour votre vote unique !")

c_p1, c_p2 = st.columns(2)
c_p1.markdown(f'<div class="vote-perc">GTA VI : {p1}%</div>', unsafe_allow_html=True)
c_p2.markdown(f'<div class="vote-perc">CYBERPUNK 2 : {p2}%</div>', unsafe_allow_html=True)
st.progress(p1 / 100)

# CATALOGUE
st.divider()
st.header("Top Jeux PS5")
top_ps5_q = "fields name, cover.url, total_rating, summary, videos.video_id, screenshots.url; where platforms = (167) & cover != null; sort total_rating desc; limit 6;"
top_games = fetch_data("games", top_ps5_q)
if top_games:
    cols_cat = st.columns(6)
    for i, tg in enumerate(top_games):
        with cols_cat[i]:
            st.image("https:" + tg['cover']['url'].replace('t_thumb', 't_cover_big'), use_container_width=True)
            if st.button("Détails", key=f"cat_{tg['id']}"):
                st.session_state.selected_game = tg; st.session_state.page = "details"; st.rerun()

# CHAT
st.divider()
st.header("Chat")
if not st.session_state.user_pseudo:
    pseudo_in = st.text_input("Ton Pseudo")
    if st.button("Rejoindre le chat"): st.session_state.user_pseudo = pseudo_in; st.rerun()
else:
    with st.form("chat_form", clear_on_submit=True):
        txt = st.text_input(f"Message de {st.session_state.user_pseudo}")
        if st.form_submit_button("Envoyer") and txt:
            if not any(w in txt.lower() for w in BAD_WORDS):
                st.session_state.comments.append({"user": st.session_state.user_pseudo, "msg": txt, "reply": None})
                sauver_data(DB_FILE, st.session_state.comments); st.rerun()

for c in st.session_state.comments[::-1][:10]:
    st.write(f"**{c['user']}** : {c['msg']}")
    if c.get('reply'): st.markdown(f"<div class='admin-reply'><b>ADMIN :</b> {c['reply']}</div>", unsafe_allow_html=True)

# ADMIN ZONE (RÉPONSES + SUPPRESSION + RESET)
with st.expander("Admin Zone"):
    if st.text_input("Code Secret", type="password") == "628316":
        if st.button("🔴 RESET TOUS LES VOTES"):
            st.session_state.vs = {"j1": 0, "j2": 0}
            sauver_data(VERSUS_FILE, st.session_state.vs); st.rerun()
        
        st.write("--- Gestion des Messages ---")
        for i, com in enumerate(st.session_state.comments):
            col_msg, col_act = st.columns([3, 1])
            col_msg.write(f"**{com['user']}** : {com['msg']}")
            if col_act.button("Supprimer", key=f"del_{i}"):
                st.session_state.comments.pop(i); sauver_data(DB_FILE, st.session_state.comments); st.rerun()
            
            with st.form(key=f"rep_{i}"):
                rep_text = st.text_input("Répondre à ce message :", value=com.get('reply') or "")
                if st.form_submit_button("Publier Réponse"):
                    st.session_state.comments[i]['reply'] = rep_text
                    sauver_data(DB_FILE, st.session_state.comments); st.success("Réponse publiée !"); st.rerun()
