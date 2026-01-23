import streamlit as st
import requests

# --- CONFIGURATION ---
CLIENT_ID = '21ely20t5zzbxzby557r34oi16j4hh'
CLIENT_SECRET = 'n0i3u05gs9gmknoho2sed9q3vfn1y3'

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
    url = "https://api.igdb.com/v4/games"
    headers = {'Client-ID': CLIENT_ID, 'Authorization': f'Bearer {token}'}
    try:
        res = requests.post(url, headers=headers, data=query)
        return res.json()
    except: return []

# --- INTERFACE ---
st.set_page_config(page_title="GameTrend Pro", layout="wide")

# CSS : Option C (Effets de survol et design propre)
st.markdown("""
    <style>
    .stApp { background-color: #00051d; color: white; }
    h2 { color: #0072ce !important; border-bottom: 2px solid #0072ce; padding-bottom: 5px; }
    
    /* Effet Zoom sur les images */
    .stImage:hover {
        transform: scale(1.05);
        transition: 0.3s;
        cursor: pointer;
    }
    
    .rating-badge { color: #ffcc00; font-weight: bold; font-size: 14px; }
    .search-box { background: rgba(255,255,255,0.1); border-radius: 20px; padding: 20px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎮 GameTrend : L'Elite du Jeu Vidéo")

# --- OPTION A : BARRE DE RECHERCHE ---
with st.container():
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    search_query = st.text_input("🔍 Rechercher un jeu (Appuie sur Entrée)...", "")
    st.markdown('</div>', unsafe_allow_html=True)

if search_query:
    st.header(f"Résultats pour : {search_query}")
    q = f'search "{search_query}"; fields name, cover.url, total_rating, summary, first_release_date; where cover != null; limit 6;'
    results = fetch_data(q)
    if results:
        cols = st.columns(6)
        for i, g in enumerate(results):
            with cols[i]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.write(f"**{g['name'][:20]}**")
                # OPTION B : MODALE DE DÉTAILS
                if st.button("Détails", key=f"search_{i}"):
                    st.info(f"**Résumé :** {g.get('summary', 'Pas de description.')}")
    else:
        st.warning("Aucun jeu trouvé.")
    st.divider()

# --- CLASSEMENT TOP 12 ---
platforms = {"PS5": 167, "Xbox Series": "169,49", "Switch": 130, "PC": 6}

for name, p_id in platforms.items():
    st.header(f"🏆 Top 12 {name}")
    query = f"fields name, cover.url, total_rating, summary; where platforms = ({p_id}) & cover != null & total_rating != null; sort total_rating desc; limit 12;"
    jeux = fetch_data(query)
    
    if jeux:
        cols = st.columns(6)
        for i, g in enumerate(jeux):
            with cols[i % 6]:
                img = "https:" + g['cover']['url'].replace('t_thumb', 't_cover_big')
                st.image(img, use_container_width=True)
                st.markdown(f"**{g['name'][:15]}**")
                note = round(g.get('total_rating', 0))
                st.markdown(f"<p class='rating-badge'>⭐ {note}/100</p>", unsafe_allow_html=True)
                
                # OPTION B : DÉTAILS POUR LE TOP 12
                with st.expander("En savoir plus"):
                    st.write(g.get('summary', 'Aucune description disponible.'))
    st.divider()
