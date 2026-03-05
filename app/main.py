from fastapi import FastAPI
from app.routes import scrape, summarize, email

app = FastAPI(
    title="Reddit Thread Explorer",
    description="Scrape Reddit communities and threads by category, then summarize with Groq AI.",
    version="1.0.0",
)

app.include_router(scrape.router)
app.include_router(summarize.router)
app.include_router(email.router)


@app.get("/")
async def root():
    return {
        "message": "Reddit Thread Explorer API",
        "endpoints": {
            "scrape": "POST /scrape/",
            "summarize_communities": "POST /summarize/communities",
            "summarize_threads": "POST /summarize/threads",
            "send_single_email": "POST /email/send",
            "send_bulk_email": "POST /email/bulk",
            "docs": "/docs",
        },
    }
