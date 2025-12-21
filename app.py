import streamlit as st
import os
import time
import json
import uuid
import pyperclip # Optional: for real clipboard, but usually st.toast is safer for web

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Nexus AI Chat",
    page_icon="🤖",
    layout="centered"
)

# 2. CUSTOM CSS (The Visual Magic)
st.markdown("""
<style>
    /* Hide header/footer */
    .stApp > header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- SIDEBAR VISIBILITY (BLACK TEXT) --- */
    [data-testid="stSidebar"] .stButton button {
        text-align: left;
        border: none;
        background: transparent;
        color: #000000 !important; /* Force Black */
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: #e0e2e6;
        color: #000000 !important;
    }
    
    /* --- CHAT BUBBLE STYLING --- */
    
    /* USER BUBBLE (Grey Background, Left Aligned) */
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
        background-color: #f0f2f6; /* Light Grey from screenshot */
        border-radius: 12px;
        padding: 15px;
        color: #000000 !important;
        border: none;
    }
    /* Force user text to be black */
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] p,
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] div {
        color: #000000 !important;
    }

    /* AI BUBBLE (Dark Background, Right Aligned Visuals) */
    [data-testid="stChatMessage"][data-testid="stChatMessageAssistant"] {
        background-color: #262730;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #444;
    }
    
    /* --- ICON BUTTON STYLING (Minimalist) --- */
    .icon-btn {
        border: none;
        background: transparent;
        color: #888;
        font-size: 14px;
        cursor: pointer;
        padding: 0px 5px;
    }
    .icon-btn:hover {
        color: #000;
        font-weight: bold;
    }
    
    /* Streamlit Button override to look like icons */
    div[data-testid="column"] button {
        background: transparent;
        border: none;
        color: #888; /* Grey icons */
        padding: 0;
        font-size: 1.2rem;
    }
    div[data-testid="column"] button:hover {
        color: #FF4B4B; /* Highlight color */
        background: transparent;
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
            return msg["content"][:20] + "..."
    return "New Chat"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🤖 Nexus AI")
    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(uuid.uuid4())
        st.session_state.current_session_id = new_id
        st.session_state.all_chats[new_id] = []
        st.rerun()
    
    st.markdown("---")
    st.caption("HISTORY")
    
    # History List
    for session_id in reversed(list(st.session_state.all_chats.keys())):
        messages = st.session_state.all_chats[session_id]
        title = get_chat_title(messages)
        if title == "New Chat": continue
            
        label = f"🔹 {title}" if session_id == st.session_state.current_session_id else f"▫️ {title}"
        if st.button(label, key=session_id, use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()

# 6. MAIN INTERFACE
current_messages = st.session_state.all_chats[st.session_state.current_session_id]

if not current_messages:
    # Empty State
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #666;">
        <h1>Ready to Launch?</h1>
        <p>Type a product topic below to start the agent team.</p>
    </div>
    """, unsafe_allow_html=True)

# --- CHAT LOOP WITH ICON LOGIC ---
for i, msg in enumerate(current_messages):
    
    # === USER MESSAGE (Left, Grey) ===
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
        
        # Action Icons Row (Just below user bubble)
        col1, col2, col3 = st.columns([0.5, 0.5, 8])
        with col1:
            if st.button("✏️", key=f"edit_{i}", help="Edit Query"):
                st.toast("Edit mode active (Demo)")
        with col2:
            if st.button("📄", key=f"copy_u_{i}", help="Copy Text"):
                st.toast("Copied query to clipboard!")

    # === AI MESSAGE (Right/Standard, Dark) ===
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            
            # 1. Render Content
            if isinstance(msg["content"], str):
                st.markdown(msg["content"])
            elif isinstance(msg["content"], dict):
                # Complex Agent Output
                result = msg["content"]
                
                with st.expander("🗺️ Strategy Brief", expanded=False):
                    st.markdown(result.get("content_brief", "No brief."))
                
                content_pack = result.get("generated_content", [])
                if content_pack:
                    st.write("### 📦 Generated Assets")
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
                # Editor Score Card
                feedback = result.get("editor_feedback", {})
                score = feedback.get("overall_score", 0)
                decision = result.get("publishing_decision", "N/A")
                
                c1, c2 = st.columns([1, 3])
                c1.metric("Score", f"{score}/30")
                if score > 20:
                    c2.success(f"**Verdict:** {decision.upper()}")
                else:
                    c2.error(f"**Verdict:** {decision.upper()}")

        # Action Icons Row (At end of Answer)
        # We use columns to push them to the right or left
        col_a, col_b, col_c, spacer = st.columns([0.5, 0.5, 0.5, 8])
        with col_a:
            if st.button("📄", key=f"copy_ai_{i}", help="Copy Answer"):
                st.toast("Copied response!")
        with col_b:
            if st.button("👍", key=f"like_{i}"):
                st.toast("Thanks for the feedback!")
        with col_c:
            if st.button("👎", key=f"dislike_{i}"):
                st.toast("We'll improve next time.")
                
    # Add a small spacer between messages
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)


# 7. INPUT HANDLER
if prompt := st.chat_input("Type your marketing goal..."):
    
    # Save User Msg
    st.session_state.all_chats[st.session_state.current_session_id].append({"role": "user", "content": prompt})
    st.rerun() # Rerun to show user message immediately

# 8. AGENT EXECUTION (After Rerun)
# Check if last message was user, if so, trigger AI
last_msg = st.session_state.all_chats[st.session_state.current_session_id][-1] if st.session_state.all_chats[st.session_state.current_session_id] else None

if last_msg and last_msg["role"] == "user":
    
    with st.chat_message("assistant", avatar="🤖"):
        with st.status("🚀 Agents are collaborating...", expanded=True) as status:
            st.write("🧠 Strategist is researching trends...")
            time.sleep(1) # Visual pacing
            st.write("✍️ Writer is drafting content...")
            time.sleep(1)
            
            # Run Graph
            initial_state = {
                "user_query": last_msg["content"],
                "target_audience": "General",
                "brand_voice": "Professional",
                "frequency": "Weekly",
                "date": "2025-12-20",
                "revision_count": 0
            }
            result = st.session_state.marketing_graph.invoke(initial_state)
            status.update(label="Campaign Ready!", state="complete", expanded=False)
            
            # Save AI Response
            st.session_state.all_chats[st.session_state.current_session_id].append({"role": "assistant", "content": result})
            st.rerun()
