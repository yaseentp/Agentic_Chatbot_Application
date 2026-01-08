# Agentic Chatbot Application

An agentic chatbot application with a Streamlit-based user interface and a FastAPI backend.  
The system is designed to perform autonomous reasoning, real-time web search, and contextual conversations using a modular, production-oriented architecture.

---

## 🚀 Capabilities

- Interactive chatbot interface built with **Streamlit**
- Backend API powered by **FastAPI**
- Agent-based conversation flow implemented using **LangGraph**
- Real-time web search to fetch up-to-date information
- External web search integration using **Google Serper**
- Persistent conversational memory stored in **PostgreSQL**
- Context-aware responses using historical user interactions
- Modular architecture enabling easy extension of agents, tools, and workflows

---

## 🧠 Architecture Overview

The system is composed of three main layers:

### Frontend (Streamlit)
- Provides an interactive chat interface
- Sends user queries to the backend API
- Displays agent responses to the user

### Backend (FastAPI)
- Acts as the orchestration layer
- Exposes REST APIs for chat interactions
- Handles request routing and integrations with agent workflows

### Agent Layer (LangGraph)
- Implements agent reasoning and decision-making logic
- Performs web search when up-to-date information is required
- Retrieves and stores conversational memory in PostgreSQL

---

## 🛠 Tech Stack

- **Python 3.11**
- **Streamlit** – Chatbot UI
- **FastAPI** – Backend API framework
- **LangGraph** – Agent workflow orchestration
- **PostgreSQL** – Persistent conversational memory
- **Google Serper API** – Web search results
- **uv** – Python dependency and environment management

---

## 📁 Project Structure
.
├── pyproject.toml # Project metadata and dependencies
├── uv.lock # Locked dependency versions
├── app.py # Streamlit chatbot UI
├── src/
│ ├── api/ # FastAPI routes and controllers
│ ├── agents/ # LangGraph agent definitions
│ ├── tools/ # External tools (web search, memory, etc.)
│ ├── memory/ # PostgreSQL memory handling
│ └── main.py # FastAPI application entry point
├── .env.example # Example environment variables
└── README.md

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone git@github.com:yaseentp/Agentic_Chatbot_Application.git
cd Agentic_Chatbot_Application
```
### 2. Create and activate virtual environment
#### MacOS/Linux
```bash
uv venv
source .venv/bin/activate
```
#### Windows
```bash
uv venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
uv sync
```

## Running the Application

#### Start the FastAPI Backend
```bash
python src/run_service.py
```
#### Start the Streamlit UI (in a separate terminal)
```bash
streamlit run src/streamlit_app.py
```
---

## 🔐 Configuration

The application requires environment variables for:

LLM provider credentials (Currently support OpenAI only)

Google Serper API key

Create a .env file using .env.example as reference before running the application.

---

## 📌 Notes

Designed for experimentation, learning, and showcasing agentic AI systems

Modular structure allows easy extension with new agents and tools

Suitable for local development and future production deployment