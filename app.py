import streamlit as st
import os
import time
import json
import uuid
# Removed pyperclip import to prevent cloud errors

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Nexus AI Chat",
    page_icon="🤖",
    layout="centered"
)

# 2. CUSTOM CSS (Visual Magic)
st.markdown("""
<style>
    /* Hide header/footer */
    .stApp > header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- SIDEBAR VISIBILITY --- */
    [data-testid="stSidebar"] .stButton button {
        text-align: left;
        border: none;
        background: transparent;
        color: #000000 !important;
        font-weight: 600;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background: #e0e2e6;
        color: #000000 !important;
    }
    
    /* --- CHAT BUBBLES --- */
    
    /* USER (Grey, Left) */
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] {
        background-color: #f0f2f6; 
        border-radius: 12px;
        padding: 15px;
        color: #000000 !important;
        border: none;
    }
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] p,
    [data-testid="stChatMessage"][data-testid="stChatMessageUser"] div {
        color: #000000 !important;
    }

    /* AI (Dark, Right) */
    [data-testid="stChatMessage"][data-testid="stChatMessageAssistant"] {
        background-color: #262730;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #444;
    }
    
    /* --- ICONS --- */
    div[data-testid="column"] button {
        background: transparent;
        border: none;
        color: #888; 
        padding: 0;
        font-size: 1.2rem;
    }
    div[data-testid="column"] button:hover {
        color: #FF4B4B;
        background: transparent;
    }
</style>
""", unsafe_allow_html=True)

# 3. SECRETS
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 4. IMPORT BACKEND
from backend import build_marketing_workflow

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
    
    for session_id in reversed(list(st.session_state.all_chats.keys())):
        messages = st.session_state.all_chats[session_id]
        title = get_chat_title(messages)
        if title == "New Chat": continue
            
        label = f"🔹 {title}" if session_id == st.session_state.current_session_id else f"▫️ {title}"
        if st.button(label, key=session_id, use_container_width=True):
            st.session_state.current_session_id = session_id
            st.rerun()

# 6. MAIN CHAT INTERFACE
current_messages = st.session_state.all_chats[st.session_state.current_session_id]

if not current_messages:
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; color: #666;">
        <h1>Ready to Launch?</h1>
        <p>Type a product topic below to start the agent team.</p>
    </div>
    """, unsafe_allow_html=True)

for i, msg in enumerate(current_messages):
    
    # === USER MESSAGE ===
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.markdown(msg["content"])
        
        # Icons Row (Below User)
        col1, col2, spacer = st.columns([0.05, 0.05, 0.9])
        with col1:
            if st.button("✏️", key=f"edit_{i}", help="Edit"):
                st.toast("Edit feature coming soon!")
        with col2:
            if st.button("📄", key=f"copy_u_{i}", help="Copy"):
                st.toast("Copied to clipboard!")

    # === AI MESSAGE ===
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            
            if isinstance(msg["content"], str):
                st.markdown(msg["content"])
            elif isinstance(msg["content"], dict):
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
                feedback = result.get("editor_feedback", {})
                score = feedback.get("overall_score", 0)
                decision = result.get("publishing_decision", "N/A")
                
                c1, c2 = st.columns([1, 3])
                c1.metric("Score", f"{score}/30")
                if score > 20:
                    c2.success(f"**Verdict:** {decision.upper()}")
                else:
                    c2.error(f"**Verdict:** {decision.upper()}")

        # Icons Row (End of AI)
        col_a, col_b, col_c, spacer = st.columns([0.05, 0.05, 0.05, 0.85])
        with col_a:
            if st.button("📄", key=f"copy_ai_{i}"):
                st.toast("Copied response!")
        with col_b:
            if st.button("👍", key=f"like_{i}"):
                st.toast("Feedback recorded!")
        with col_c:
            if st.button("👎", key=f"dislike_{i}"):
                st.toast("Feedback recorded!")
                
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)


# 7. INPUT
if prompt := st.chat_input("Type your marketing goal..."):
    st.session_state.all_chats[st.session_state.current_session_id].append({"role": "user", "content": prompt})
    st.rerun()

# 8. RUN AGENTS
last_msg = st.session_state.all_chats[st.session_state.current_session_id][-1] if st.session_state.all_chats[st.session_state.current_session_id] else None

if last_msg and last_msg["role"] == "user":
    with st.chat_message("assistant", avatar="🤖"):
        with st.status("🚀 Agents are collaborating...", expanded=True) as status:
            st.write("🧠 Strategist is researching trends...")
            time.sleep(1)
            st.write("✍️ Writer is drafting content...")
            time.sleep(1)
            
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
            
            st.session_state.all_chats[st.session_state.current_session_id].append({"role": "assistant", "content": result})
            st.rerun()
