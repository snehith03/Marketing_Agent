import os
import json
from typing import TypedDict, List, Literal, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI

# ---------- CONFIG ----------
# We do NOT set the key here. It will be loaded from the environment/Streamlit secrets.
PERFORMANCE_JSON_PATH = "performance.json"

# Global LLM instance - relies on OPENAI_API_KEY being in os.environ
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

@dataclass
class ContentPiece:
    platform: str
    title: str
    content: str
    format_type: str  # "thread", "tweet", "post", "email", etc.

class MarketingState(TypedDict, total=False):
    # Initial inputs
    user_query: str
    target_audience: str
    brand_voice: str
    frequency: Literal["Daily", "Weekly"]
    date: str

    # Strategist extras
    historical_performance: Dict[str, Any]

    # Agent outputs
    content_brief: str
    generated_content: List[ContentPiece]
    editor_feedback: Dict[str, Any]
    publishing_decision: Literal["accept", "needs_improvement", "reject"]

    # Feedback loop
    revision_count: int
    performance_metrics: Optional[Dict[str, float]]
    final_content_pack: Optional[List[ContentPiece]]

    # Tracking
    current_cycle: int

# =====================================
# HELPER FUNCTIONS
# =====================================

def load_performance_json() -> Dict[str, Any]:
    """Load persistent performance stats from disk."""
    if not os.path.exists(PERFORMANCE_JSON_PATH):
        return {"topic_stats": {}}
    try:
        with open(PERFORMANCE_JSON_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"topic_stats": {}}

def save_performance_json(data: Dict[str, Any]) -> None:
    """Write performance stats back to disk."""
    with open(PERFORMANCE_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

# =====================================
# AGENT NODES
# =====================================

def load_historical_signals(state: MarketingState) -> MarketingState:
    performance_data = load_performance_json()
    state["historical_performance"] = performance_data.get("topic_stats", {})
    return state

def discover_trending_topics(state: MarketingState) -> MarketingState:
    # Stubbed for demo - in production replace with Tavily
    query = f"{state['user_query']} marketing trends"
    topics = [{
        "name": f"Trends for {state['user_query']}",
        "why_it_matters": "High search volume",
        "audience_relevance": "Direct impact on strategy"
    }]
    state["trending_topics_temp"] = topics
    return state

def analyze_sentiment(state: MarketingState) -> MarketingState:
    state["sentiment_summary_temp"] = {
        "dominant_sentiment": "Curious",
        "pain_points": ["Efficiency", "Cost"],
        "desires": ["Automation", "Results"]
    }
    return state

def analyze_competitors(state: MarketingState) -> MarketingState:
    state["competitor_summary_temp"] = {
        "competitors": [{"name": "Generic Competitor", "move": "Launching AI tools"}],
        "gaps": ["Personalization"]
    }
    return state

def strategist_synthesizer(state: MarketingState) -> MarketingState:
    system_prompt = """
    You are the Strategist Agent. Generate ONLY the content brief.
    OUTPUT FORMAT:
    Content Brief for Writer Agent
    1. Key Trending Topics
    2. Customer Sentiment Insights
    3. Competitor Intelligence
    4. Writing Instructions (Message, Tone, Keywords)
    """
    
    context = f"""
    Query: {state['user_query']}
    Audience: {state['target_audience']}
    Brand Voice: {state['brand_voice']}
    Historical Performance: {json.dumps(state.get("historical_performance", {}))}
    """
    response = llm.invoke([HumanMessage(content=system_prompt + context)])
    state["content_brief"] = response.content
    return state

def writer_agent_node(state: MarketingState) -> MarketingState:
    content_brief = state["content_brief"]
    feedback = state.get("editor_feedback", {})
    revision_count = state.get("revision_count", 0)

    extra_instructions = ""
    if feedback and revision_count > 0:
        issues = feedback.get("rationale", "")
        extra_instructions = f"REVISION REQUIRED: Fix these issues: {issues}"

    prompt = f"""
    You are a content generator.
    CONTENT BRIEF: {content_brief}
    {extra_instructions}
    
    GENERATE EXACTLY 5 pieces in JSON array format:
    [
      {{"platform": "twitter", "format_type": "thread", "title": "...", "content": "..."}},
      {{"platform": "linkedin", "format_type": "post", "title": "...", "content": "..."}}
    ]
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip().replace("```json", "").replace("```", "")

    try:
        content_list = json.loads(raw)
        state["generated_content"] = [ContentPiece(**item) for item in content_list]
    except Exception:
        # Fallback
        state["generated_content"] = [
            ContentPiece("twitter", "Error", "JSON Parsing Failed", "tweet")
        ]
    return state

def editor_agent_node(state: MarketingState) -> MarketingState:
    content_pack = state["generated_content"]
    content_text = "\n".join([f"{c.title}: {c.content[:100]}..." for c in content_pack])

    prompt = f"""
    Evaluate content.
    BRAND: {state['brand_voice']}
    CONTENT: {content_text}
    
    RETURN JSON:
    {{
      "tone_score": number,
      "fact_score": number,
      "brand_score": number,
      "rationale": string
    }}
    """
    response = llm.invoke([HumanMessage(content=prompt)])
    raw = response.content.strip().replace("```json", "").replace("```", "")

    try:
        feedback = json.loads(raw)
    except:
        feedback = {"tone_score": 5, "fact_score": 5, "brand_score": 5, "rationale": "Parsing Error"}

    total = feedback.get("tone_score", 0) + feedback.get("fact_score", 0) + feedback.get("brand_score", 0)
    feedback["overall_score"] = min(total, 30)

    if feedback["overall_score"] >= 24:
        judgement = "accept"
    elif feedback["overall_score"] >= 15:
        judgement = "needs_improvement"
    else:
        judgement = "reject"

    feedback["judgement"] = judgement
    state["editor_feedback"] = feedback
    state["publishing_decision"] = judgement
    state["revision_count"] = state.get("revision_count", 0) + 1
    return state

def route_editor_decision(state: MarketingState) -> Literal["writer_agent", "publish", "fail"]:
    decision = state.get("publishing_decision", "needs_improvement")
    revision_count = state.get("revision_count", 0)

    if decision == "accept":
        return "publish"
    elif decision == "needs_improvement" and revision_count < 3:
        return "writer_agent"
    else:
        return "fail"

def log_performance(state: MarketingState) -> MarketingState:
    perf_data = load_performance_json()
    topic_key = state["user_query"].strip().lower()
    score = state["editor_feedback"].get("overall_score", 0)
    
    topic_stats = perf_data.get("topic_stats", {})
    current = topic_stats.get(topic_key, {"runs": 0, "avg_score": 0.0})
    
    new_runs = current["runs"] + 1
    new_avg = ((current["avg_score"] * current["runs"]) + score) / new_runs
    
    topic_stats[topic_key] = {
        "runs": new_runs, 
        "avg_score": new_avg, 
        "last_score": score,
        "last_updated": datetime.utcnow().isoformat()
    }
    
    perf_data["topic_stats"] = topic_stats
    save_performance_json(perf_data)
    state["performance_metrics"] = topic_stats[topic_key]
    return state

def publish_content(state: MarketingState) -> MarketingState:
    state["final_content_pack"] = state["generated_content"].copy()
    state["current_cycle"] = state.get("current_cycle", 0) + 1
    return state

def handle_failure(state: MarketingState) -> MarketingState:
    state["final_content_pack"] = []
    return state

# =====================================
# GRAPH BUILDER
# =====================================

def build_marketing_workflow():
    """Constructs and returns the compiled graph."""
    workflow = StateGraph(MarketingState)

    workflow.add_node("load_historical_signals", load_historical_signals)
    workflow.add_node("strategist_trends", discover_trending_topics)
    workflow.add_node("strategist_sentiment", analyze_sentiment)
    workflow.add_node("strategist_competitors", analyze_competitors)
    workflow.add_node("strategist_brief", strategist_synthesizer)
    workflow.add_node("writer_agent", writer_agent_node)
    workflow.add_node("editor_agent", editor_agent_node)
    workflow.add_node("publish", publish_content)
    workflow.add_node("log_performance", log_performance)
    workflow.add_node("fail", handle_failure)

    workflow.set_entry_point("load_historical_signals")

    workflow.add_edge("load_historical_signals", "strategist_trends")
    workflow.add_edge("strategist_trends", "strategist_sentiment")
    workflow.add_edge("strategist_sentiment", "strategist_competitors")
    workflow.add_edge("strategist_competitors", "strategist_brief")
    workflow.add_edge("strategist_brief", "writer_agent")
    workflow.add_edge("writer_agent", "editor_agent")

    workflow.add_conditional_edges(
        "editor_agent",
        route_editor_decision,
        {
            "writer_agent": "writer_agent",
            "publish": "publish",
            "fail": "fail"
        }
    )

    workflow.add_edge("publish", "log_performance")
    workflow.add_edge("log_performance", END)
    workflow.add_edge("fail", END)

    return workflow.compile()