import streamlit as st

def render_sidebar():
    with st.sidebar:
        st.markdown("<div class='sidebar-title'>🌍 AI Travel Planner</div>", unsafe_allow_html=True)
        st.markdown("---")
        thread_id = st.text_input("👤 User ID", value="User-Sagar", help="Your session ID")

        st.markdown("<div class='sidebar-title'>Powered by</div>", unsafe_allow_html=True)
        for tech in ["🔗 LangGraph", "🧠 Groq · LLaMA 3.3 70B", "🐘 PostgreSQL", "🔍 Tavily Search", "✈️ AviationStack"]:
            st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

        st.markdown("<div class='sidebar-title'>Agent Pipeline</div>", unsafe_allow_html=True)
        for step in ["① Flight Agent", "② Hotel Agent", "③ Itinerary Agent", "④ Final Agent"]:
            st.markdown(f"<div class='sidebar-chip'>{step}</div>", unsafe_allow_html=True)
            
    return thread_id

def render_hero():
    st.markdown("""
    <div class="hero-wrapper">
        <img class="hero-bg" src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1400&q=80" alt="airplane above clouds"/>
        <div class="hero-content">
            <div class="hero-badge">✦ Multi-Agent AI System</div>
            <div class="hero-title">✈️ AI Travel Booking System</div>
            <div class="hero-sub">Four specialized agents work together...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_destinations():
    DESTINATIONS = [
        ("🇯🇵 Tokyo",     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
        ("🇫🇷 Paris",     "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
        ("🇹🇭 Bangkok",   "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
        ("🇮🇹 Rome",      "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
        ("🇦🇪 Dubai",     "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
    ]
    cols = st.columns(5)
    for col, (name, img_url) in zip(cols, DESTINATIONS):
        with col:
            st.markdown(f"""
            <div style="border-radius:10px;overflow:hidden;position:relative;height:90px;cursor:pointer;">
                <img src="{img_url}" style="width:100%;height:100%;object-fit:cover;filter:brightness(0.55);" />
                <div style="position:absolute;bottom:8px;left:0;right:0;text-align:center; color:#fff;font-size:0.8rem;font-weight:600;">{name}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

def render_metrics(llm_calls):
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Agents Run</div></div>
        <div class="metric-box"><div class="metric-val">{llm_calls}</div><div class="metric-lbl">LLM Calls</div></div>
        <div class="metric-box"><div class="metric-val">✅</div><div class="metric-lbl">Status</div></div>
    </div>
    """, unsafe_allow_html=True)