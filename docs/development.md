# Local Development & Testing Guide

This guide describes how to run and test the complete stack locally.

---

## 1. Prerequisites
- **Python**: 3.11+
- **Node.js**: 18+ & npm
- **MySQL**: 8.0+ running on `localhost:3306`
- **Google Gemini API Key**: [Obtain from Google AI Studio](https://aistudio.google.com/)

---

## 2. Environment Setup

### Backend
1. Initialize virtual environment and install packages:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   pip install langgraph-checkpoint-sqlite aiosqlite
   ```
2. Configure `.env` in `backend/.env`:
   ```ini
   GOOGLE_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-3.5-flash
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=business_analytics
   DB_USER=root
   DB_PASSWORD=password
   ```

### MySQL Database Setup
Run the automated schema creation and 3-year seed data generation script:
```bash
python database/setup_database.py
```
This builds all 11 tables and populates **1,103 orders and 1,948 sales records** totaling INR 61.91 Million.

---

## 3. Running Services

### Start Backend
```bash
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`.

---

## 4. Running Test Suites

Execute all automated unit and integration tests across all phases:
```bash
pytest tests/ -v -o "pythonpath=backend"
```
