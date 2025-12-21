import streamlit as st
import os
import time
import json
import uuid

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Nexus AI Chat",
    page_icon="🤖",
    layout="centered"
)

# 2. CUSTOM CSS (SIDEBAR BLACK TEXT FIX)
st.markdown("""
<style>
    /* Hide header/footer */
    .stApp > header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- MAIN CHAT VISIBILITY --- */
    /* Chat bubbles (Dark Theme) */
    .stChatMessage {
        background-color: #262730;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #333;
    }
    .stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage h1, .stChatMessage h2, .stChatMessage h3, .stChatMessage li {
        color: #ffffff !important; /* White text inside chat bubbles */
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E; 
        border: 1px solid #444;
    }
    
    /* --- SIDEBAR VISIBILITY FIX --- */
    /* Force Sidebar History Buttons to be BLACK */
    [data-testid="stSidebar"] .stButton button {
        text-align: left;
        border: none;
        background: transparent;
        color: #000000 !important; /* <--- CHANGED TO BLACK */
        opacity: 1.0; /* Full visibility */
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* Hover effect: Light Grey background, keep text Black */
    [data-testid="stSidebar"] .stButton button:hover {
        background: #f0f2f6;
        color: #000000 !important;
        padding-left: 10px;
    }
    
    /* Login Button Style (Bottom Left) */
    .login-btn button {
        background-color: #FF4B4B !important;
        color: white !important; /* Keep login button white text on red background */
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# 3. SECRETS
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 4. IMPORT BACKEND
from backend import build_marketing_workflow

# Initialize Graph
if "marketing_graph" not in st.session_state:
    st.session_state.marketing_graph = build_marketing_workflow()

# 5. SESSION MANAGEMENT
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

if "current_session_id" not in st.session_state:
    new_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_id
    st.session_state.all_chats[new_id] = []

def get_chat_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            return msg["content"][:25] + "..."
    return "New Chat"

# --- LOGIN POPUP ---
@st.dialog("Welcome to Nexus AI")
def login_dialog():
    st.markdown("Sign in to sync your campaigns.")
    username = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Log In", use_container_width=True):
        st.success(f"Welcome back, {username}!")
        time.sleep(1)
        st.rerun()
        
    st.markdown("---")
    st.caption("Don't have an account? Sign Up")

# 6. SIDEBAR
with st.sidebar:
    st.title("🤖 Nexus AI")
    
    # New Chat
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_session_id = new_id
        st.session_state.all_chats[new_id] = []
        st.rerun()
    
    st.markdown("---")
    st.caption("RECENT HISTORY")
    
    # History List
    history_found = False
    for session_id in reversed(list(st.session_state.all_chats.keys())):
        messages = st.session_state.all_chats[session_id]
        title = get_chat_title(messages)
        
        if title == "New Chat":
            continue
            
        history_found = True
        
        # Highlight active chat
        label = f"🔹 {title}" if session_id == st.session_state.current_session_id else f"▫️ {title}"
        
        if st.button(label, key=session_id, use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()

    if not history_found:
        st.caption("No saved campaigns yet.")

    # Spacer & Login
    st.markdown("<br>" * 5, unsafe_allow_html=True) 
    st.markdown("---")
    
    if st.button("👤 Log In / Sign Up", use_container_width=True):
        login_dialog()

# 7. MAIN CHAT INTERFACE
current_messages = st.session_state.all_chats[st.session_state.current_session_id]

if not current_messages:
    with st.chat_message("assistant"):
        st.markdown("Hello! I am your AI Marketing Team. Ready to launch a new campaign?")

for msg in current_messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"])
        elif isinstance(msg["content"], dict):
            # Render Logic
            result = msg["content"]
            with st.expander("🗺️ Strategy Brief", expanded=False):
                st.markdown(result.get("content_brief", "No brief."))
            
            content_pack = result.get("generated_content", [])
            if content_pack:
                st.write("### 📦 Assets")
                tabs = st.tabs(["Twitter", "LinkedIn", "Email"])
                with tabs[0]:
                    for p in content_pack:
                        if "twitter" in p.platform.lower(): st.info(f"**{p.title}**\n\n{p.content}")
                with tabs[1]:
                    for p in content_pack:
                        if "linkedin" in p.platform.lower(): st.success(f"**{p.title}**\n\n{p.content}")
                with tabs[2]:
                    for p in content_pack:
                        if "email" in p.platform.lower(): st.warning(f"**{p.title}**\n\n{p.content}")
            
            st.divider()
            feedback = result.get("editor_feedback", {})
            c1, c2 = st.columns([1, 3])
            c1.metric("Score", f"{feedback.get('overall_score', 0)}/30")
            c2.caption(f"**Verdict:** {result.get('publishing_decision', 'N/A').upper()}")

# 8. INPUT
if prompt := st.chat_input("Type a marketing goal..."):
    st.session_state.all_chats[st.session_state.current_session_id].append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.status("Agents working...", expanded=True) as status:
            initial_state = {
                "user_query": prompt,
                "target_audience": "General",
                "brand_voice": "Professional",
                "frequency": "Weekly",
                "date": "2025-12-20",
                "revision_count": 0
            }
            result = st.session_state.marketing_graph.invoke(initial_state)
            status.update(label="Done", state="complete", expanded=False)
        
        st.success("Campaign generated! (See details above)")
        st.session_state.all_chats[st.session_state.current_session_id].append({"role": "assistant", "content": result})
        
    st.rerun()
