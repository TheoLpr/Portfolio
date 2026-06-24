import pandas as pd
import streamlit as st
import json

st.set_page_config(page_title="MoMA Tinder", layout="centered")

# --- Chargement des données ---
@st.cache_data
def load_artworks():
    df = pd.read_csv("./Donnees/Artworks.csv")
    df = df[~df.ImageURL.isna()].reset_index(drop=True)
    return df

artworks = load_artworks()

# --- Session state ---
if "index" not in st.session_state:
    st.session_state.index = 0
if "likes" not in st.session_state:
    st.session_state.likes = []
if "dislikes" not in st.session_state:
    st.session_state.dislikes = []
if "superlike" not in st.session_state:
    st.session_state.superlike = []
if "action" not in st.session_state:
    st.session_state.action = None  # "like" | "dislike" | "superlike"

# --- Gestion des actions via query params (astuce Streamlit) ---
# On utilise des boutons cachés pour déclencher les actions JS->Python
def next_artwork(action):
    i = st.session_state.index
    if action == "like":
        st.session_state.likes.append(i)
    elif action == "dislike":
        st.session_state.dislikes.append(i)
    elif action == "superlike":
        st.session_state.superlike.append(i)
    st.session_state.index += 1
    st.session_state.action = None

# --- Œuvre courante ---
i = st.session_state.index
total = len(artworks)
finished = i >= total

# --- CSS global ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(145deg, #008CD6 0%, #001F33 100%);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding-top: 2rem; max-width: 480px; }

/* Cacher les boutons Streamlit natifs utilisés comme triggers */
.action-buttons { display: none; }
</style>
""", unsafe_allow_html=True)

if finished:
    # --- Écran de fin ---
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 16px;
        padding: 40px 32px;
        text-align: center;
        margin-top: 40px;
    ">
        <div style="font-size: 48px; margin-bottom: 16px;">🎨</div>
        <h2 style="font-family: Georgia, serif; color: #001F33; margin-bottom: 8px;">
            Visite personnalisée prête !
        </h2>
        <p style="color: #666; font-size: 14px; margin-bottom: 24px;">
            Vous avez aimé <strong>{len(st.session_state.likes)}</strong> œuvres,
            dont <strong>{len(st.session_state.superlike)}</strong> coups de cœur.
        </p>
        <div style="
            background: #f5f5f5;
            border-radius: 10px;
            padding: 16px;
            font-size: 13px;
            color: #444;
            text-align: left;
        ">
            Vos préférences ont été enregistrées.<br>
            Votre parcours MoMA sera généré ici.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Recommencer", use_container_width=True):
        st.session_state.index = 0
        st.session_state.likes = []
        st.session_state.dislikes = []
        st.session_state.superlike = []
        st.rerun()

else:
    row = artworks.iloc[i]
    image_url = row["ImageURL"]
    title = row.get("Title", "Sans titre")
    artist = row.get("Artist", "Artiste inconnu")
    date = row.get("Date", "")
    medium = row.get("Medium", "")

    # Troncature propre
    if isinstance(title, str) and len(title) > 50:
        title = title[:48] + "…"
    if isinstance(artist, str) and len(artist) > 40:
        artist = artist[:38] + "…"

    progress_dots = ""
    dot_count = min(total, 12)
    for d in range(dot_count):
        active = "active" if d < i else ""
        current = "current" if d == i else ""
        progress_dots += f'<div class="dot {active} {current}"></div>'

    # On sérialise les infos pour le JS
    card_data = json.dumps({
        "title": str(title),
        "artist": str(artist),
        "date": str(date),
        "medium": str(medium),
    })

    st.markdown(f"""
    <style>
    @keyframes slideInRight {{
        from {{ opacity: 0; transform: translateX(60px) rotate(3deg); }}
        to   {{ opacity: 1; transform: translateX(0) rotate(0deg); }}
    }}
    @keyframes flyRight {{
        from {{ opacity: 1; transform: translateX(0) rotate(0deg); }}
        to   {{ opacity: 0; transform: translateX(120%) rotate(12deg); }}
    }}
    @keyframes flyLeft {{
        from {{ opacity: 1; transform: translateX(0) rotate(0deg); }}
        to   {{ opacity: 0; transform: translateX(-120%) rotate(-12deg); }}
    }}
    @keyframes flyUp {{
        from {{ opacity: 1; transform: translateX(0) rotate(0deg); }}
        to   {{ opacity: 0; transform: translateY(-80%) scale(0.85); }}
    }}
    .moma-app {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 0 0 24px;
    }}
    .moma-title {{
        font-family: Georgia, serif;
        font-size: 20px;
        font-weight: normal;
        color: rgba(255,255,255,0.92);
        letter-spacing: 0.04em;
        margin-bottom: 4px;
    }}
    .moma-subtitle {{
        font-size: 11px;
        color: rgba(255,255,255,0.4);
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 20px;
    }}
    .progress-row {{
        display: flex;
        gap: 5px;
        margin-bottom: 20px;
        align-items: center;
    }}
    .dot {{
        width: 5px; height: 5px;
        border-radius: 50%;
        background: rgba(255,255,255,0.18);
        transition: background 0.3s;
    }}
    .dot.active {{ background: rgba(255,255,255,0.6); }}
    .dot.current {{ background: white; width: 7px; height: 7px; }}

    .card-stack {{
        position: relative;
        width: 320px;
        height: 410px;
        margin-bottom: 28px;
        cursor: grab;
    }}
    .card-ghost {{
        position: absolute;
        border-radius: 16px;
        background: rgba(255,255,255,0.15);
    }}
    .card-ghost-2 {{
        inset: 18px 12px -18px 12px;
        transform: rotate(3.5deg);
        z-index: 1;
    }}
    .card-ghost-1 {{
        inset: 9px 6px -9px 6px;
        transform: rotate(-1.8deg);
        z-index: 2;
    }}
    .card {{
        position: absolute;
        inset: 0;
        background: white;
        border-radius: 16px;
        padding: 14px 14px 0;
        display: flex;
        flex-direction: column;
        z-index: 3;
        animation: slideInRight 0.35s cubic-bezier(0.22, 1, 0.36, 1);
        user-select: none;
    }}
    .card.fly-right {{ animation: flyRight 0.38s ease-in forwards; }}
    .card.fly-left  {{ animation: flyLeft  0.38s ease-in forwards; }}
    .card.fly-up    {{ animation: flyUp    0.38s ease-in forwards; }}

    .artwork-frame {{
        flex: 1;
        background: #f0ede8;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden;
        position: relative;
    }}
    .artwork-frame img {{
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        display: block;
    }}
    .badge {{
        position: absolute;
        top: 14px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.1em;
        padding: 4px 10px;
        border-radius: 6px;
        border: 2.5px solid;
        opacity: 0;
        transition: opacity 0.1s;
        pointer-events: none;
    }}
    .badge-like   {{ left: 12px;  color: #1a7a4a; border-color: #1a7a4a; background: rgba(255,255,255,0.85); }}
    .badge-nope   {{ right: 12px; color: #b83030; border-color: #b83030; background: rgba(255,255,255,0.85); }}
    .badge-super  {{ left: 50%; transform: translateX(-50%); bottom: 14px; color: #185FA5; border-color: #185FA5; background: rgba(255,255,255,0.85); }}

    .card-info {{
        padding: 10px 2px 16px;
    }}
    .card-title {{
        font-family: Georgia, serif;
        font-size: 15px;
        color: #1a1a1a;
        margin-bottom: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .card-meta {{
        font-size: 11px;
        color: #888;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .actions {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
    }}
    .btn-action {{
        border: none;
        border-radius: 50%;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: transform 0.12s;
        background: white;
        font-size: 0;
        line-height: 0;
    }}
    .btn-action:hover  {{ transform: scale(1.1); }}
    .btn-action:active {{ transform: scale(0.94); }}
    .btn-dislike {{
        width: 62px; height: 62px;
        border: 2px solid #f5b0b0;
    }}
    .btn-superlike {{
        width: 48px; height: 48px;
        border: 2px solid #b5d4f4;
    }}
    .btn-like {{
        width: 62px; height: 62px;
        border: 2px solid #aed89a;
    }}
    .counter-text {{
        font-size: 11px;
        color: rgba(255,255,255,0.35);
        margin-top: 16px;
        letter-spacing: 0.05em;
    }}
    </style>

    <div class="moma-app">
        <p class="moma-title">MoMA Tinder</p>
        <p class="moma-subtitle">Collection permanente</p>

        <div class="progress-row">{progress_dots}</div>

        <div class="card-stack" id="stack">
            <div class="card-ghost card-ghost-2"></div>
            <div class="card-ghost card-ghost-1"></div>
            <div class="card" id="card">
                <div class="artwork-frame">
                    <span class="badge badge-like"  id="badge-like">LIKE</span>
                    <span class="badge badge-nope"  id="badge-nope">NOPE</span>
                    <span class="badge badge-super" id="badge-super">SUPER</span>
                    <img src="{image_url}" alt="{title}" onerror="this.style.display='none'">
                </div>
                <div class="card-info">
                    <div class="card-title">{title}</div>
                    <div class="card-meta">{artist}{' · ' + str(date) if date else ''}</div>
                </div>
            </div>
        </div>

        <div class="actions">
            <button class="btn-action btn-dislike" onclick="doAction('dislike')" title="Passer">
                <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <line x1="7" y1="7" x2="19" y2="19" stroke="#c94040" stroke-width="2.5" stroke-linecap="round"/>
                    <line x1="19" y1="7" x2="7" y2="19" stroke="#c94040" stroke-width="2.5" stroke-linecap="round"/>
                </svg>
            </button>
            <button class="btn-action btn-superlike" onclick="doAction('superlike')" title="Super like">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 2L12.09 7.26L17.8 7.27L13.35 10.74L14.99 16.18L10 13L5.01 16.18L6.65 10.74L2.2 7.27L7.91 7.26L10 2Z"
                          fill="#378ADD"/>
                </svg>
            </button>
            <button class="btn-action btn-like" onclick="doAction('like')" title="J'aime">
                <svg width="26" height="26" viewBox="0 0 26 26" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M13 22C13 22 3 16 3 9.5C3 6.46 5.46 4 8.5 4C10.24 4 11.8 4.85 13 6.08C14.2 4.85 15.76 4 17.5 4C20.54 4 23 6.46 23 9.5C23 16 13 22 13 22Z"
                          fill="#27a060"/>
                </svg>
            </button>
        </div>

        <p class="counter-text">{i + 1} / {min(total, 100)} œuvres</p>
    </div>

    <script>
    const ACTIONS = {{}};

    function showBadge(id) {{
        const b = document.getElementById(id);
        if (b) {{ b.style.opacity = '1'; }}
    }}
    function hideBadges() {{
        ['badge-like','badge-nope','badge-super'].forEach(id => {{
            const b = document.getElementById(id);
            if (b) b.style.opacity = '0';
        }});
    }}

    function doAction(type) {{
        const card = document.getElementById('card');
        if (!card) return;

        const badgeMap = {{
            like: {{ badge: 'badge-like', cls: 'fly-right' }},
            dislike: {{ badge: 'badge-nope', cls: 'fly-left' }},
            superlike: {{ badge: 'badge-super', cls: 'fly-up' }},
        }};
        const m = badgeMap[type];
        showBadge(m.badge);

        setTimeout(() => {{
            card.classList.add(m.cls);
            setTimeout(() => {{
                // Soumettre via le bouton Streamlit caché
                const btn = document.getElementById('trigger-' + type);
                if (btn) btn.click();
            }}, 350);
        }}, 120);
    }}

    // Drag-to-swipe
    let startX = 0, dragging = false;
    const card = document.getElementById('card');
    if (card) {{
        card.addEventListener('mousedown', e => {{ startX = e.clientX; dragging = true; }});
        window.addEventListener('mouseup', e => {{
            if (!dragging) return;
            dragging = false;
            const dx = e.clientX - startX;
            if (Math.abs(dx) > 80) doAction(dx > 0 ? 'like' : 'dislike');
        }});
        card.addEventListener('touchstart', e => {{ startX = e.touches[0].clientX; }}, {{passive: true}});
        card.addEventListener('touchend', e => {{
            const dx = e.changedTouches[0].clientX - startX;
            if (Math.abs(dx) > 60) doAction(dx > 0 ? 'like' : 'dislike');
        }});
    }}
    </script>
    """, unsafe_allow_html=True)

    # Boutons Streamlit cachés qui servent de triggers
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("like", key="trigger-like"):
            next_artwork("like")
            st.rerun()
    with col2:
        if st.button("superlike", key="trigger-superlike"):
            next_artwork("superlike")
            st.rerun()
    with col3:
        if st.button("dislike", key="trigger-dislike"):
            next_artwork("dislike")
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Fallback clavier : flèches gauche/droite
    st.markdown("""
    <script>
    document.addEventListener('keydown', e => {
        if (e.key === 'ArrowRight') doAction('like');
        if (e.key === 'ArrowLeft')  doAction('dislike');
        if (e.key === 'ArrowUp')    doAction('superlike');
    });
    </script>
    """, unsafe_allow_html=True)
