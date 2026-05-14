



app = FastAPI(
    title="NutriDia AI",
    description="Agentic RAG Assistant for Diabetes and Nutrition",
    version="1.0.0"
)

app.include_router(chat_router)
app.include_router(health_router)


@app.get("/")
def root():
    return {
        "message": "NutriDia AI Backend Running"
    }