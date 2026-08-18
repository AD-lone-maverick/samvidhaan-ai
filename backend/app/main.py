from fastapi import FastAPI

app = FastAPI(
    title="Samvidhan AI API",
    description="Indian Constitution Research Assistant",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "Samvidhan AI API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }