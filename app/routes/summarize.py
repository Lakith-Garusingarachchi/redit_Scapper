import json

from fastapi import APIRouter, HTTPException

from app.models.reddit import SummarizeRequest, Community, Thread
from app.services.summarizer import summarize_community, summarize_thread

router = APIRouter(prefix="/summarize", tags=["summarize"])


@router.post("/communities")
async def summarize_communities(request: SummarizeRequest):
    try:
        with open(request.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        summarized = 0
        for community_data in data["communities"]:
            community = Community(**community_data)
            community_data["community_summary"] = summarize_community(community)
            summarized += 1

        with open(request.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            "message": "Community summaries added successfully",
            "file_path": request.file_path,
            "communities_summarized": summarized,
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threads")
async def summarize_threads(request: SummarizeRequest):
    try:
        with open(request.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        total_threads = 0
        for community_data in data["communities"]:
            for thread_data in community_data["threads"]:
                thread = Thread(**thread_data)
                thread_data["thread_summary"] = summarize_thread(thread)
                total_threads += 1

        with open(request.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return {
            "message": "Thread summaries added successfully",
            "file_path": request.file_path,
            "threads_summarized": total_threads,
        }

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
