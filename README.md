# VoiceMind AI — Customer Support Agent

VoiceMind AI is an AI-powered customer support project designed to answer e-commerce customer questions using a voice agent and a Python backend.

## Features

* Customer support for delivery, cancellations, refunds, returns, and payment questions
* Retrieval-Augmented Generation (RAG) using a policy knowledge base
* Gemini-powered response generation
* FastAPI backend
* Order lookup tool

## Tech Stack

* Python
* FastAPI
* Google Gemini
* FAISS
* Sentence Transformers
* ElevenLabs Voice Agent

## Project Structure

* `agents/` — Customer support agent logic
* `Knowledge/` — Customer support policy documents
* `rag/` — Knowledge retrieval
* `services/` — Gemini service
* `tools/` — Order lookup utilities
* `api.py` — FastAPI application

## Setup

1. Install dependencies from `requirements.txt`.
2. Add your `GEMINI_API_KEY` to a local `.env` file.
3. Run the API using:

```bash
python -m uvicorn api:app --reload
```

API documentation: `http://127.0.0.1:8000/docs`

**Security:** Keep `.env` and all API keys private. Do not upload secrets to GitHub.
