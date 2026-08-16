import streamlit as st
from src.frontend.user_manager import load_users, add_new_user, create_new_session
from src.frontend.utils import get_session_total_expense
from src.frontend.visuals import get_expense_donut_chart
import os


def render_sidebar():
    st.sidebar.title("👤 User Profile")
    
    users_data = load_users()
    user_list = list(users_data.keys())
    
    # --- CALLBACK 1: Handle User Creation ---
    def handle_new_user():
        name = st.session_state.get("new_user_input", "").strip()
        if name:
            add_new_user(name)
            st.session_state.user_mode = "Existing User" # Safely change mode here
            updated_users = list(load_users().keys())
            st.session_state.selected_user_index = updated_users.index(name)
        else:
            st.session_state.user_error = "Name cannot be empty."

    # --- CALLBACK 2: Handle Session Creation ---
    def handle_new_session(active_user):
        session_name = st.session_state.get("new_session_input", "").strip()
        if session_name:
            create_new_session(active_user, session_name)
            st.session_state.session_mode = "Select Existing Session" # Safely change mode here
            updated_sessions = list(load_users()[active_user].get("sessions", {}).keys())
            st.session_state.selected_session_index = updated_sessions.index(session_name)
        else:
            st.session_state.session_error = "Session name cannot be empty."


    # --- UI Part 1: Users ---
    if "user_mode" not in st.session_state:
        st.session_state.user_mode = "New User" 
               
    user_mode = st.sidebar.radio(
        "Welcome! Please select an option:", 
        ["Existing User", "New User"],
        key="user_mode"
    )
    
    active_user = None
    
    if user_mode == "New User":
        # Bind the text input to a key so the callback can read it
        st.sidebar.text_input("Enter your full name:", key="new_user_input")
        # Use on_click to trigger the callback BEFORE the page reruns
        st.sidebar.button("Create Profile", on_click=handle_new_user)
        
        if "user_error" in st.session_state:
            st.sidebar.error(st.session_state.user_error)
            del st.session_state.user_error
            
    elif user_mode == "Existing User":
        if not user_list:
            st.sidebar.warning("No users found. Please create a new user.")
        else:
            default_idx = st.session_state.get("selected_user_index", 0)
            default_idx = default_idx if default_idx < len(user_list) else 0
            
            active_user = st.sidebar.selectbox("Select your profile:", user_list, index=default_idx)
            st.session_state.selected_user_index = user_list.index(active_user)
            
            
    # --- UI Part 2: Sessions ---
    active_thread_id = None
    
    if active_user:
        st.sidebar.markdown("---")
        st.sidebar.subheader(f"📂 Sessions for {active_user}")
        
        users_data = load_users() 
        user_sessions = users_data[active_user].get("sessions", {})
        session_names = list(user_sessions.keys())
        
        if "session_mode" not in st.session_state:
            st.session_state.session_mode = "Select Existing Session" if session_names else "Create New Session"
            
        session_mode = st.sidebar.radio(
            "Manage Sessions:", 
            ["Select Existing Session", "Create New Session"],
            key="session_mode"
        )
        
        if session_mode == "Create New Session":
            st.sidebar.text_input("Enter a name for this trip/session:", key="new_session_input")
            # Pass the active_user argument into the callback
            st.sidebar.button("Start New Session", on_click=handle_new_session, args=(active_user,))
            
            if "session_error" in st.session_state:
                st.sidebar.error(st.session_state.session_error)
                del st.session_state.session_error
                
        elif session_mode == "Select Existing Session":
            if not session_names:
                st.sidebar.info("No active sessions. Create one above.")
            else:
                default_session_idx = st.session_state.get("selected_session_index", 0)
                default_session_idx = default_session_idx if default_session_idx < len(session_names) else 0
                
                selected_session = st.sidebar.selectbox(
                    "Choose a session:", 
                    session_names, 
                    index=default_session_idx
                )
                
                st.session_state.selected_session_index = session_names.index(selected_session)
                active_thread_id = user_sessions[selected_session]
                
                
    # --- UI Part 3: Visuals ---
    if active_thread_id:
        total_spent = get_session_total_expense(active_thread_id)
        
        st.sidebar.markdown("---")
        st.sidebar.metric(label="Total Trip Expenses", value=f"₹{total_spent:,.2f}")
        
        st.sidebar.markdown("**Expense Breakdown**")
        donut_chart = get_expense_donut_chart(active_thread_id)
        
        with st.sidebar:
            if donut_chart:
                st.plotly_chart(donut_chart, use_container_width=True)
            else:
                st.info("No expenses logged for this trip yet.")

    return active_user, active_thread_id


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

# if __name__ == "__main__":
#     render_sidebar()