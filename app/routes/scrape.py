import json
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.models.reddit import ScrapeRequest, ScrapeResponse
from app.services.reddit_scraper import scrape_reddit

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("/", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest):
    try:
        communities = scrape_reddit(
            category=request.category,
            max_communities=request.max_communities,
            max_threads=request.max_threads,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{request.category.replace(' ', '_')}_{timestamp}.json"
        file_path = os.path.join("data", file_name)

        os.makedirs("data", exist_ok=True)

        response = ScrapeResponse(
            category=request.category,
            scraped_at=datetime.now().isoformat(),
            file_path=file_path,
            communities=communities,
        )

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(response.model_dump(), f, indent=2, ensure_ascii=False)

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
