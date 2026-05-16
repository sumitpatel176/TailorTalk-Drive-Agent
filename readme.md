# TailorTalk AI Drive Agent 🤖

A smart AI-powered agent built with **FastAPI** and **Google Gemini** that allows users to search files in Google Drive using natural language.

## Features 🚀
- **Natural Language Search:** Find files by name, type, or content description.
- **Direct Drive Integration:** Uses Google Drive API with a service account for secure access.
- **AI-Powered Logic:** Uses Google Gemini 1.5 Flash to convert user queries into Drive search parameters.
- **Fast UI:** Built with **Streamlit** for a smooth user experience.

## Tech Stack 🛠️
- **Backend:** Python, FastAPI, Uvicorn
- **AI:** Google Generative AI (Gemini 1.5 Flash)
- **APIs:** Google Drive API v3
- **Frontend:** Streamlit

## How it Works 🧠
Instead of using heavy wrappers like LangChain, this project uses **Direct API Integration** with Gemini. The model acts as a "Reasoning Engine" that takes the user's input, processes it, and generates a structured JSON query for the Google Drive API.

## Installation 💻
1. Clone the repo: `git clone https://github.com/sumitpatel176/TailorTalk-Drive-Agent.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Run Backend: `uvicorn app:app --reload --port 8001`
4. Run Frontend: `streamlit run main.py`

---
Developed by **Sumit Patel**