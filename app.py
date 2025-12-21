import streamlit as st
import os
import time

# 1. PAGE CONFIG
st.set_page_config(
    page_title="Nexus AI Chat",
    page_icon="🤖",
    layout="centered" # "Centered" looks more like ChatGPT
)

# 2. CUSTOM CSS (To make it look like a clean chat app)
st.markdown("""
<style>
    /* Hide the Streamlit header and footer */
    .stApp > header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style the chat bubbles */
    .stChatMessage {
        background-color: #262730;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    /* User bubble color */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E; 
    }
</style>
""", unsafe_allow_html=True)

# 3. SECRETS SETUP
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# 4. IMPORT BACKEND
from backend import build_marketing_workflow, llm

# Initialize Graph (Cache it so it doesn't reload on every run)
if "marketing_graph" not in st.session_state:
    st.session_state.marketing_graph = build_marketing_workflow(llm)

# 5. SESSION STATE FOR CHAT HISTORY
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Marketing Team. Tell me what product or topic you want to launch, and I'll handle the Strategy, Content, and Quality Control."}
    ]

# 6. SIDEBAR (Minimal)
with st.sidebar:
    st.title("🤖 Nexus AI")
    st.caption("Multi-Agent System")
    
    st.markdown("---")
    st.markdown("**Agents Active:**")
    st.checkbox("🧠 Strategist", value=True, disabled=True)
    st.checkbox("✍️ Writer", value=True, disabled=True)
    st.checkbox("🧐 Editor", value=True, disabled=True)
    
    st.markdown("---")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# 7. DISPLAY CHAT HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        # If the content is simple text, show it
        if isinstance(msg["content"], str):
            st.markdown(msg["content"])
        # If it's our complex result dictionary, render it nicely
        elif isinstance(msg["content"], dict):
            result = msg["content"]
            
            # A. Strategy
            with st.expander("🗺️ View Strategy Brief", expanded=False):
                st.markdown(result.get("content_brief", "No brief."))
            
            # B. Content (Tabs)
            content_pack = result.get("generated_content", [])
            if content_pack:
                st.write("### 📦 Generated Assets")
                # Group by platform for cleaner tabs
                platform_tabs = st.tabs(["Twitter", "LinkedIn", "Email/Blog"])
                
                with platform_tabs[0]:
                    for p in content_pack:
                        if "twitter" in p.platform.lower():
                            st.info(f"**{p.title}**\n\n{p.content}")
                with platform_tabs[1]:
                    for p in content_pack:
                        if "linkedin" in p.platform.lower():
                            st.success(f"**{p.title}**\n\n{p.content}")
                with platform_tabs[2]:
                    for p in content_pack:
                        if "email" in p.platform.lower() or "blog" in p.platform.lower():
                            st.warning(f"**{p.title}**\n\n{p.content}")
            
            # C. Editor Score
            st.divider()
            feedback = result.get("editor_feedback", {})
            score = feedback.get("overall_score", 0)
            decision = result.get("publishing_decision", "N/A")
            
            c1, c2 = st.columns([1, 3])
            c1.metric("Quality Score", f"{score}/30")
            c2.caption(f"**Editor Verdict:** {decision.upper()}\n\n_{feedback.get('rationale', '')}_")


# 8. CHAT INPUT HANDLER
if prompt := st.chat_input("E.g., Launch a marketing campaign for a vegan energy drink"):
    
    # A. Display User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # B. Generate Assistant Response
    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=True) as status:
            
            # 1. Prepare State
            st.write("🧠 Strategist is analyzing market trends...")
            initial_state = {
                "user_query": prompt,
                "target_audience": "General Audience", # Defaulting for chat simplicity
                "brand_voice": "Professional",        # Defaulting for chat simplicity
                "frequency": "Weekly",
                "date": "2025-12-20",
                "revision_count": 0
            }
            
            # 2. Run Graph
            result = st.session_state.marketing_graph.invoke(initial_state)
            
            st.write("✍️ Writer is drafting content...")
            time.sleep(0.5) # UI pacing
            
            st.write("🧐 Editor is grading quality...")
            time.sleep(0.5) # UI pacing
            
            status.update(label="Process Complete", state="complete", expanded=False)
        
        # 3. Render Output (Same logic as history loop above)
        # We duplicate the rendering logic here to show it immediately
        
        st.success("Here is your campaign package:")
        
        # Strategy
        with st.expander("🗺️ View Strategy Brief", expanded=False):
            st.markdown(result.get("content_brief", "No brief."))
        
        # Content
        content_pack = result.get("generated_content", [])
        if content_pack:
            st.write("### 📦 Generated Assets")
            platform_tabs = st.tabs(["Twitter", "LinkedIn", "Email/Blog"])
            
            with platform_tabs[0]:
                for p in content_pack:
                    if "twitter" in p.platform.lower():
                        st.info(f"**{p.title}**\n\n{p.content}")
            with platform_tabs[1]:
                for p in content_pack:
                    if "linkedin" in p.platform.lower():
                        st.success(f"**{p.title}**\n\n{p.content}")
            with platform_tabs[2]:
                for p in content_pack:
                    if "email" in p.platform.lower() or "blog" in p.platform.lower():
                        st.warning(f"**{p.title}**\n\n{p.content}")
        else:
            st.error("Content was rejected by the Editor.")

        # Editor Stats
        st.divider()
        feedback = result.get("editor_feedback", {})
        score = feedback.get("overall_score", 0)
        decision = result.get("publishing_decision", "N/A")
        
        c1, c2 = st.columns([1, 3])
        c1.metric("Quality Score", f"{score}/30")
        c2.caption(f"**Editor Verdict:** {decision.upper()}\n\n_{feedback.get('rationale', '')}_")

    # C. Save Result to History
    # We save the raw result dict so we can re-render it nicely later
    st.session_state.messages.append({"role": "assistant", "content": result})
