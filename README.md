# Genna - Generative Annotation System

**Genna (GENerative ANNotation)** is an LLM-centric text annotation system designed for the efficient text annotation and comparison of AI model outputs. Genna makes it easy to test out different LLMs, prompts, temperatures, and scalability of structured calls.

## Key Features

- 🤖 **AI Model Integration**: Configure multiple AI models as annotators. Directly supports **OpenAI**, **Anthropic**, and **OpenRouter**.
- 📊 **Custom Dataset Management**: Evolve your dataset, add new files, remove files, while tracking annotation metrics.
- 📋 **Human Annotation Interface**:
  - Interactive annotation with thumbs up/down feedback.
  - Real-time disagreement detection between AI models.
  - Expandable annotation view for each row.
  - Dark/Light mode support for comfortable, prolonged viewing (featuring a Financial Times-inspired sophisticated light aesthetic).
- 🔍 **Smart Filtering**:
  - Filter by content across any column.
  - Show only rows with AI model disagreements.
  - Category-based multi-filtering.
- 📈 **Annotation Analysis**:
  - Visual indicators for model agreements/disagreements.
  - Summary views showing differences between model outputs.
  - Quick toggle to show/hide all annotations.

## Architecture & Tech Stack
- **Frontend**: Vue 3 + Vite, Vue Router, Pinia
- **Backend**: FastAPI (Python 3.12)
- **Database & Auth**: Firebase Firestore + Firebase Authentication
- **Deployment**: Railway

## Getting Started

### Backend
1. `cd backend/`
2. Ensure you have Python 3.12 and `venv` installed (`sudo apt install -y python3.12-venv`).
3. Create venv: `python3 -m venv venv && source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run server: `uvicorn main:app --reload --port 8000`

### Frontend
1. `cd frontend/`
2. Install defaults: `npm install`
3. Run dev server: `npm run dev`

---
*Built incrementally by Antigravity*
