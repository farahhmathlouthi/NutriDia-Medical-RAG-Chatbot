from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.chat import router as chat_router
from api.routes.health import router as health_router


app = FastAPI(
    title="NutriDia AI",
    description="Agentic RAG Assistant for Diabetes and Nutrition",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(health_router, prefix="/api/health", tags=["Health"])


@app.get("/")
def root():
    return {
        "message": "NutriDia AI Backend Running"
    }