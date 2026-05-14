# NutriDia AI — Frontend

React frontend for the NutriDia diabetes & nutrition chatbot.

## Stack
- React 18
- Lucide React (icons)
- DM Serif Display + DM Sans (Google Fonts)

## Setup

```bash
npm install
npm start
```

Opens at **http://localhost:3000**

## Environment

Edit `.env` to point at your backend:

```
REACT_APP_API_URL=http://127.0.0.1:8000
```

## Features

| Feature | Description |
|---|---|
| 💬 Chat | Ask questions about diabetes & nutrition |
| 📄 PDF Upload | Upload medical PDFs to expand the AI's knowledge |
| 💡 Suggestions | Pre-built quick questions in the sidebar |
| ⌨️ Enter to send | Shift+Enter for new lines |

## API Endpoints Used

| Method | URL | Purpose |
|---|---|---|
| POST | `/api/chat/` | Send a question |
| POST | `/api/upload/` | Upload a PDF |
| GET  | `/api/health/` | Health check |
