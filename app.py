
import streamlit as st
from reporting import render_reporting_form
from dashboard import render_dashboard, render_admin_panel

# ==========================================
# BIN2CHAIN - CITYFIX BUILDATHON 2026
# ==========================================

st.set_page_config(
    page_title="Bin2Chain | Your City. Your Voice. Your Impact.",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# BILINGUAL CONTENT
# ==========================================

CONTENT = {
    "English": {
        "nav": ["Home", "About", "How It Works", "Features", "Community"],
        "tagline": "Your City. Your Voice. Your Impact.",
        "subtitle": "A better city begins with you.",
        "description": "Together, we can make our neighbourhoods cleaner, safer and better places to live.",
        "report": "Report an Issue",
        "explore": "Explore Our Platform",
        "problem_title": "Every neighbourhood deserves better.",
        "problem_desc": "Potholes, overflowing garbage, waterlogging and broken streetlights affect our everyday lives.",
        "solution_title": "Small actions. Meaningful change.",
        "solution_desc": "Bin2Chain connects citizens, AI technology and community participation to turn urban challenges into meaningful civic action.",
        "how_title": "How Bin2Chain Works",
        "steps": [
            ("01", "Speak Up", "Report neighbourhood problems with a photo and location."),
            ("02", "Understand", "AI helps identify and prioritize civic issues."),
            ("03", "Connect", "Discover nearby issues and connect with your community."),
            ("04", "Make an Impact", "Track progress and participate in community action.")
        ],
        "features_title": "Technology with a human purpose.",
        "features": [
            ("📸", "AI Civic Vision", "Identify civic issues from photographs."),
            ("📍", "Smart Location", "Detect and map the location of urban problems."),
            ("🗺️", "Community Intelligence", "Discover recurring problems and local hotspots."),
            ("🤝", "Citizen Rewards", "Encourage meaningful community participation."),
            ("🌱", "Civic Impact", "Understand reported issues and verified progress.")
        ],
        "join_title": "Your neighbourhood matters.",
        "join_desc": "A better city doesn't happen by itself. It happens when we work together.",
        "join_button": "Be Part of the Change",
        "footer": "People. Community. Change.",
        "location": "Starting in Delhi. Growing through communities.",
        "notice": "Bin2Chain is an independent civic technology initiative. It is not affiliated with any government authority.",
        "community_message": "Community participation is coming soon.",
        "gallery_title": "Real Issues. Real Impact.",
        "gallery_subtitle": "Together, let's build cleaner, safer and greener neighbourhoods."
    },

    "Hindi": {
        "nav": ["होम", "परिचय", "कैसे काम करता है", "फीचर्स", "समुदाय"],
        "tagline": "एक बेहतर शहर की शुरुआत आपसे होती है।",
        "subtitle": "आपकी आवाज़। आपका मोहल्ला। आपका योगदान।",
        "description": "आइए, मिलकर अपने मोहल्लों को स्वच्छ, सुरक्षित और रहने के लिए बेहतर बनाएं।",
        "report": "समस्या दर्ज करें",
        "explore": "हमारे प्लेटफॉर्म को जानें",
        "problem_title": "हर मोहल्ला बेहतर सुविधाओं का हकदार है।",
        "problem_desc": "सड़कों के गड्ढे, कूड़े के ढेर, जलभराव और खराब स्ट्रीट लाइट हमारी रोजमर्रा की जिंदगी को प्रभावित करते हैं।",
        "solution_title": "छोटे कदम। बड़ा बदलाव।",
        "solution_desc": "Bin2Chain नागरिकों, AI तकनीक और सामुदायिक भागीदारी को जोड़कर शहरी समस्याओं के समाधान की दिशा में काम करता है।",
        "how_title": "Bin2Chain कैसे काम करता है?",
        "steps": [
            ("01", "अपनी बात रखें", "फोटो और लोकेशन के साथ मोहल्ले की समस्या बताएं।"),
            ("02", "समस्या समझें", "AI समस्याओं की पहचान और प्राथमिकता तय करने में मदद करता है।"),
            ("03", "समुदाय से जुड़ें", "आसपास की समस्याएं जानें और लोगों से जुड़ें।"),
            ("04", "बदलाव लाएं", "प्रगति देखें और सामुदायिक गतिविधियों में भाग लें।")
        ],
        "features_title": "तकनीक, लोगों की भलाई के लिए।",
        "features": [
            ("📸", "AI नागरिक पहचान", "तस्वीरों से शहरी समस्याओं की पहचान।"),
            ("📍", "स्मार्ट लोकेशन", "समस्याओं की लोकेशन पहचानें और मैप पर देखें।"),
            ("🗺️", "सामुदायिक जानकारी", "बार-बार होने वाली समस्याओं और संवेदनशील क्षेत्रों को पहचानें।"),
            ("🤝", "नागरिक पुरस्कार", "समुदाय में सकारात्मक भागीदारी को प्रोत्साहित करें।"),
            ("🌱", "शहर की प्रगति", "समस्याओं और सत्यापित सुधारों की जानकारी पाएं।")
        ],
        "join_title": "आपका मोहल्ला महत्वपूर्ण है।",
        "join_desc": "एक बेहतर शहर अपने आप नहीं बनता। यह हम सबके साथ मिलकर प्रयास करने से बनता है।",
        "join_button": "बदलाव का हिस्सा बनें",
        "footer": "लोग। समुदाय। बदलाव।",
        "location": "शुरुआत दिल्ली से। विस्तार हर समुदाय तक।",
        "notice": "Bin2Chain एक स्वतंत्र नागरिक तकनीकी पहल है। इसका किसी सरकारी प्राधिकरण से संबंध नहीं है।",
        "community_message": "सामुदायिक भागीदारी जल्द शुरू होगी।",
        "gallery_title": "असली समस्याएं। वास्तविक बदलाव।",
        "gallery_subtitle": "आइए, मिलकर स्वच्छ, सुरक्षित और हरित मोहल्ले बनाएं।"
    }
}

# ==========================================
# SESSION STATE
# ==========================================

if "language" not in st.session_state:
    st.session_state.language = "English"

for key in [
    "show_report",
    "show_explore",
    "show_dashboard",
    "show_admin_panel"
]:
    if key not in st.session_state:
        st.session_state[key] = False

# ==========================================
# DESIGN CSS
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap');

html {
    scroll-behavior: smooth;
    scroll-padding-top: 24px;
}

header[data-testid="stHeader"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    display: none !important;
}

.stApp {
    background: #F7F5EF;
    color: #123C35;
    font-family: 'Inter', sans-serif;
}

.stAppViewContainer .main .block-container,
.block-container {
    max-width: 1200px;
    padding-top: 1.25rem !important;
    padding-bottom: 2rem;
}

.brand {
    font-family: 'Poppins', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #123C35;
    letter-spacing: 1px;
    white-space: nowrap;
    padding-top: 4px;
}

.nav-container {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    padding-top: 12px;
}

.nav-container a {
    text-decoration: none;
    color: #123C35;
    font-size: 14px;
    font-weight: 600;
}

.nav-container a:hover {
    color: #248B65;
}

.hero {
    background: linear-gradient(135deg, #123C35, #20594B);
    padding: 75px 35px;
    border-radius: 22px;
    color: white;
    text-align: center;
    margin: 25px 0 35px 0;
}

.hero h1 {
    font-family: 'Poppins', sans-serif;
    font-size: clamp(32px, 5vw, 55px);
    line-height: 1.25;
    color: white;
}

.hero p {
    color: #D9EEE3;
    font-size: 18px;
    line-height: 1.8;
}

.section-title {
    font-family: 'Poppins', sans-serif;
    color: #123C35;
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    margin-top: 55px;
    margin-bottom: 15px;
}

.section-desc {
    text-align: center;
    color: #587267;
    font-size: 16px;
    line-height: 1.8;
    margin-bottom: 25px;
}

.feature-card,
.photo-card,
.work-card {
    background: white;
    border-radius: 16px;
    padding: 14px;
    border: 1px solid #E1E9E2;
    margin-bottom: 18px;
    overflow: hidden;
}

.feature-card {
    min-height: 165px;
    padding: 25px;
}

.feature-card h3,
.work-card h3 {
    color: #123C35;
    font-family: 'Poppins', sans-serif;
    font-size: 18px;
}

.feature-card p,
.work-card p {
    color: #64766D;
    font-size: 14px;
    line-height: 1.7;
}

.work-number {
    color: #248B65;
    font-size: 25px;
    font-weight: 800;
    margin-top: 12px;
}

.gallery-heading {
    text-align: center;
    color: #123C35;
    font-family: 'Poppins', sans-serif;
    font-size: 30px;
    font-weight: 800;
    margin-top: 35px;
    margin-bottom: 8px;
}

.gallery-subtitle {
    text-align: center;
    color: #64766D;
    font-size: 16px;
    margin-bottom: 25px;
}

.photo-title {
    color: #123C35;
    font-size: 18px;
    font-weight: 700;
    padding: 10px 4px 2px;
}

.photo-description {
    color: #64766D;
    font-size: 14px;
    padding: 0 4px 8px;
}

.join-box {
    background: #E4F4E9;
    border-radius: 22px;
    padding: 45px 25px;
    text-align: center;
    margin-top: 45px;
}

.footer {
    text-align: center;
    padding: 35px 10px;
    color: #587267;
    font-size: 13px;
}

.stButton > button {
    background: #248B65;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: 600;
    min-height: 45px;
}

.stButton > button:hover {
    background: #123C35;
    color: white;
}

div[data-testid="stSelectbox"] {
    min-width: 100px;
}

@media (max-width: 900px) {
    .brand {
        font-size: 25px;
    }

    .nav-container {
        gap: 10px;
        justify-content: flex-start;
    }

    .nav-container a {
        font-size: 12px;
    }

    .hero {
        padding: 45px 18px;
    }

    .section-title {
        font-size: 25px;
    }
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER AND NAVIGATION
# ==========================================

col_brand, col_nav, col_language = st.columns([2, 4, 1.3])

with col_brand:
    st.markdown(
        '<div class="brand">🌱 Bin2Chain</div>',
        unsafe_allow_html=True
    )

with col_nav:
    st.markdown("""
    <div class="nav-container">
        <a href="#top">Home</a>
        <a href="#about">About</a>
        <a href="#how-it-works">How It Works</a>
        <a href="#features">Features</a>
        <a href="#community">Community</a>
    </div>
    """, unsafe_allow_html=True)

with col_language:
    selected_language = st.selectbox(
        "Language",
        ["English", "Hindi"],
        index=["English", "Hindi"].index(st.session_state.language),
        label_visibility="collapsed"
    )

st.session_state.language = selected_language
data = CONTENT[selected_language]

# ==========================================
# HERO SECTION
# ==========================================

st.markdown('<div id="top"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
    <h1>{data['tagline']}</h1>
    <p><b>{data['subtitle']}</b></p>
    <p>{data['description']}</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# MAIN ACTION BUTTONS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button(data["report"], use_container_width=True):
        st.session_state.show_report = True
        st.session_state.show_explore = False
        st.session_state.show_dashboard = False
        st.session_state.show_admin_panel = False

with col2:
    if st.button(data["explore"], use_container_width=True):
        st.session_state.show_explore = True
        st.session_state.show_report = False
        st.session_state.show_dashboard = False
        st.session_state.show_admin_panel = False

with col3:
    if st.button("📊 Citizen Dashboard", use_container_width=True):
        st.session_state.show_dashboard = True
        st.session_state.show_report = False
        st.session_state.show_explore = False
        st.session_state.show_admin_panel = False

with col4:
    if st.button("🔐 Admin Panel", use_container_width=True):
        st.session_state.show_admin_panel = True
        st.session_state.show_report = False
        st.session_state.show_explore = False
        st.session_state.show_dashboard = False

# ==========================================
# SELECTED MODULES
# ==========================================

if st.session_state.show_report:
    st.markdown("---")
    render_reporting_form(selected_language)

if st.session_state.show_explore:
    st.success(data["solution_desc"])

if st.session_state.show_dashboard:
    st.markdown("---")
    render_dashboard(selected_language)

if st.session_state.show_admin_panel:
    st.markdown("---")
    render_admin_panel()

# ==========================================
# ABOUT SECTION
# ==========================================

st.markdown('<div id="about"></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="section-title">{data["problem_title"]}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="section-desc">{data["problem_desc"]}</div>',
    unsafe_allow_html=True
)

# ==========================================
# CENTERED BIN2CHAIN CIVIC SOLUTIONS BANNER
# ==========================================

left_space, banner_col, right_space = st.columns([1, 3, 1])

with banner_col:
    st.image(
        "assets/bin2chain_civic_solutions.png",
        use_container_width=True
    )

st.markdown(
    f'<div class="section-title">{data["solution_title"]}</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="section-desc">{data["solution_desc"]}</div>',
    unsafe_allow_html=True
)



# ==========================================
# BIN2CHAIN - FINAL CIVIC IMPACT GALLERY
# ==========================================

st.markdown("""
<style>
div[data-testid="stImage"] img {
    width: 100% !important;
    height: 220px !important;
    object-fit: cover !important;
    border-radius: 12px !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
}

.impact-heading {
    color: #123C35;
    font-family: 'Poppins', sans-serif;
    font-size: 20px;
    font-weight: 700;
    margin-top: 10px;
}

.impact-description {
    color: #64766D;
    font-size: 14px;
    line-height: 1.6;
    min-height: 48px;
}
</style>
""", unsafe_allow_html=True)

impact_cards = [
    {
        "image": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=900",
        "en_title": "Cleaner Streets",
        "hi_title": "स्वच्छ सड़कें",
        "en_desc": "Better waste management and clean public spaces.",
        "hi_desc": "बेहतर कचरा प्रबंधन और स्वच्छ सार्वजनिक स्थान।"
    },
    {
        "image": "https://images.unsplash.com/photo-1518005020951-eccb494ad742?w=900",
        "en_title": "Safer Roads",
        "hi_title": "सुरक्षित सड़कें",
        "en_desc": "Improved roads, safer footpaths and infrastructure.",
        "hi_desc": "बेहतर सड़कें, सुरक्षित फुटपाथ और बुनियादी सुविधाएं।"
    },
    {
        "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=900",
        "en_title": "Greener Cities",
        "hi_title": "हरित शहर",
        "en_desc": "More trees and healthier neighbourhoods.",
        "hi_desc": "अधिक पेड़ और स्वस्थ हरे-भरे मोहल्ले।"
    }
]

columns = st.columns(3, gap="medium")

for column, card in zip(columns, impact_cards):
    with column:
        with st.container(border=True):
            st.image(card["image"], use_container_width=True)

            title = card["en_title"] if selected_language == "English" else card["hi_title"]
            description = card["en_desc"] if selected_language == "English" else card["hi_desc"]

            st.markdown(
                f'<div class="impact-heading">{title}</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                f'<div class="impact-description">{description}</div>',
                unsafe_allow_html=True
            )



# ==========================================
# HOW BIN2CHAIN WORKS - PHOTO CARDS
# ==========================================

st.markdown('<div id="how-it-works"></div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="section-title">{data["how_title"]}</div>',
    unsafe_allow_html=True
)

step_images = [
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800",
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800",
    "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=800",
    "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800"
]

step_columns = st.columns(4)

for index, (col, step) in enumerate(zip(step_columns, data["steps"])):
    with col:
        st.markdown('<div class="work-card">', unsafe_allow_html=True)

        st.image(
            step_images[index],
            use_container_width=True
        )

        st.markdown(f"""
            <div class="work-number">{step[0]}</div>
            <h3>{step[1]}</h3>
            <p>{step[2]}</p>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

feature_images = [
    # AI Civic Vision
    "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=900",

    # Smart Location - Map and GPS
    "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=900",

    # Community Intelligence
    "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=900",

    # Citizen Rewards
    "https://images.unsplash.com/photo-1559027615-cd4628902d4a?w=900",

    # Civic Impact
    "https://images.unsplash.com/photo-1518005020951-eccb494ad742?w=900"
]


# ==========================================
# COMMUNITY
# ==========================================

st.markdown('<div id="community"></div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="join-box">
    <h1 style="color:#123C35;font-family:Poppins">
        {data['join_title']}
    </h1>
    <p style="color:#45635A;font-size:17px">
        {data['join_desc']}
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

if st.button(data["join_button"], use_container_width=True):
    st.info(data["community_message"])

# ==========================================
# FOOTER
# ==========================================

st.markdown(f"""
<div class="footer">
    <h2 style="color:#123C35;font-family:Poppins">🌱 Bin2Chain</h2>
    <p>{data['footer']}</p>
    <p>{data['location']}</p>
    <hr>
    <p>{data['notice']}</p>
    <p>© 2026 Bin2Chain | CityFix Buildathon</p>
</div>
""", unsafe_allow_html=True)
