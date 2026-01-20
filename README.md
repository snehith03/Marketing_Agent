# AgentMark 🚀

> A **LangGraph-powered** autonomous marketing agency that simulates a real-world content team. Strategist, Writer, and Editor agents collaborate to plan, create, and refine high-quality marketing campaigns.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-Stateful%20Agents-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Interactive%20UI-red)
![OpenAI](https://img.shields.io/badge/LLM-GPT--4o--mini-green)

## 📖 Overview
**AgentMark** is a multi-agent AI system designed to automate the creative workflow of a digital marketing agency. Unlike simple "prompt-response" bots, this system uses **stateful graph architecture** to maintain context across different stages of production.

The system features a **self-correcting feedback loop**: if the "Editor" agent rejects a piece of content based on quality scores, it automatically sends it back to the "Writer" with specific revision instructions—simulating a real human review process.

## ✨ Key Features
* **🤖 Multi-Agent Collaboration:** Three specialized agents (Strategist, Writer, Editor) work in a directed graph.
* **🔄 Adaptive Feedback Loops:** The workflow autonomously routes content back for revision if quality thresholds (Brand, Tone, Fact scores) are not met.
* **🧠 "Memory" & Learning:** Tracks historical performance of topics in `performance.json`, allowing the Strategist to refine future briefs based on past success.
* **📊 Interactive Dashboard:** A **Streamlit** frontend that allows users to input campaign goals, view real-time agent status, and inspect the final "Quality Report."
* **🛡️ Robust Architecture:** Built with **LangGraph StateGraph** to manage complex, non-linear workflows and conditional edges.

## 🛠️ Tech Stack
* **Orchestration:** LangGraph, LangChain
* **LLM:** OpenAI GPT-4o-mini
* **Frontend:** Streamlit
* **Data Persistence:** JSON (Local storage for performance metrics)

## 📂 Project Structure
```text
AgentMark
├── app.py              # Streamlit Frontend (UI & User Inputs)
├── backend.py          # LangGraph Logic (Nodes, Edges, Agents)
├── performance.json    # Persistent storage for campaign stats
└── requirements.txt    # Project dependencies
```

## 🔌 The Workflow (Graph Architecture)
The system follows a strict stateful workflow defined in `backend.py`:

### 1. Strategist Nodes
* **`load_historical_signals`**: Fetches past performance data.
* **`discover_trending_topics`**: Researches market trends.
* **`strategist_brief`**: Synthesizes data into a cohesive Content Brief.

### 2. Writer Node
* Generates platform-specific content (Twitter Threads, LinkedIn Posts) based on the brief.

### 3. Editor Node (The Gatekeeper)
* Scores content on **Tone**, **Facts**, and **Brand Voice** (0-10 scale).
* **Decision Logic:**
    * **Accept** (>24 pts) → Publish.
    * **Needs Improvement** (15-24 pts) → **Loop back to Writer** (Revision).
    * **Reject** (<15 pts) → End workflow.

## 🚀 Getting Started

### Prerequisites
* Python 3.10+
* OpenAI API Key

### Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/yourusername/AgentMark.git](https://github.com/yourusername/AgentMark.git)
    cd AgentMark
    ```

2.  **Install Dependencies**
    ```bash
    pip install langchain langgraph streamlit openai
    ```

3.  **Configure Secrets**
    Create a `.streamlit/secrets.toml` file in the root directory (or use Streamlit Cloud secrets):
    ```toml
    OPENAI_API_KEY = "sk-your-openai-key-here"
    ```

4.  **Run the Application**
    ```bash
    streamlit run app.py
    ```

## 📊 Usage Guide
1.  Open the app in your browser (usually `http://localhost:8501`).
2.  **Sidebar Inputs:** Enter your Product (e.g., "AI Coffee Maker"), Audience (e.g., "Tech Professionals"), and desired Tone (e.g., "Witty").
3.  Click **"▶️ Start Campaign"**.
4.  Watch the **Status Container** as agents work through the nodes.
5.  **Review Results:**
    * **Strategy Tab:** See the research and brief.
    * **Content Tab:** View the generated tweets/posts.
    * **Quality Report:** Check the Editor's scores and feedback.
