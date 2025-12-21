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

# 2. CUSTOM CSS
st.markdown("""
<style>
    /* Hide header/footer */
    .stApp > header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat bubbles */
    .stChatMessage {
        background-color: #262730;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        color: #ffffff !important;
        border: 1px solid #333;
    }
    .stChatMessage p, .stChatMessage div, .stChatMessage span {
        color: #ffffff !important;
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E; 
        border: 1px solid #444;
    }
    
    /* Sidebar History Buttons */
    .stButton button {
        text-align: left;
        border: none;
        background: transparent;
        color: #ccc;
    }
    .stButton button:hover {
        background: #333;
        color: white;
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

# 5. SESSION MANAGEMENT (The Logic for History)
if "all_chats" not in st.session_state:
    # This stores ALL conversations: { "session_id": [messages] }
    st.session_state.all_chats = {}

if "current_session_id" not in st.session_state:
    # Start with a default session
    new_id = str(uuid.uuid4())
    st.session_state.current_session_id = new_id
    st.session_state.all_chats[new_id] = [
        {"role": "assistant", "content": "Hello! I am your AI Marketing Team. Ready to launch a new campaign?"}
    ]

# Helper to get current chat title (based on first user prompt)
def get_chat_title(messages):
    for msg in messages:
        if msg["role"] == "user":
            return msg["content"][:25] + "..." # Take first 25 chars
    return "New Chat"

# 6. SIDEBAR
with st.sidebar:
    st.title("🤖 Nexus AI")
    
    # --- NEW CHAT BUTTON ---
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_session_id = new_id
        st.session_state.all_chats[new_id] = [
            {"role": "assistant", "content": "Hello! Ready for a new campaign strategy."}
        ]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**History**")
    
    # --- HISTORY LIST ---
    # We iterate through all stored chats and make buttons
    # Reverse order so newest is top
    for session_id in reversed(list(st.session_state.all_chats.keys())):
        messages = st.session_state.all_chats[session_id]
        title = get_chat_title(messages)
        
        # Highlight the active chat
        if session_id == st.session_state.current_session_id:
            if st.button(f"🔹 {title}", key=session_id, use_container_width=True):
                pass # Already active
        else:
            if st.button(f"▫️ {title}", key=session_id, use_container_width=True):
                st.session_state.current_session_id = session_id
                st.rerun()

    st.markdown("---")
    st.caption("Active Agents: Strategist • Writer • Editor")

# 7. MAIN CHAT INTERFACE
# Get the messages for the CURRENTLY selected session
current_messages = st.session_state.all_chats[st.session_state.current_session_id]

# Display them
for msg in current_messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], str):
            st.markdown(msg["content"])
        elif isinstance(msg["content"], dict):
            # Render Complex Output (Same as before)
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

# 8. INPUT HANDLER
if prompt := st.chat_input("Type a marketing goal..."):
    
    # Append to current session
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
        
        # Simple render for immediate view (abbreviated for code brevity)
        st.success("Campaign generated! (See details above)")
        
        # Save result to current session
        st.session_state.all_chats[st.session_state.current_session_id].append({"role": "assistant", "content": result})
        
    st.rerun() # Force refresh to update sidebar title
