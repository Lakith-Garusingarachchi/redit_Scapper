from fastapi import FastAPI
from app.routes import scrape, summarize

app = FastAPI(
    title="Reddit Thread Explorer",
    description="Scrape Reddit communities and threads by category, then summarize with Groq AI.",
    version="1.0.0",
)

app.include_router(scrape.router)
app.include_router(summarize.router)


@app.get("/")
async def root():
    return {
        "message": "Reddit Thread Explorer API",
        "endpoints": {
            "scrape": "POST /scrape/",
            "summarize_communities": "POST /summarize/communities",
            "summarize_threads": "POST /summarize/threads",
            "docs": "/docs",
        },
    }
