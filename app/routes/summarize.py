import json
import os
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.models.reddit import SummarizeRequest, Community, Thread
from app.services.summarizer import summarize_community, summarize_thread

router = APIRouter(prefix="/summarize", tags=["summarize"])

DATA_DIR = "data"


def _list_data_files() -> list[str]:
    if not os.path.exists(DATA_DIR):
        return []
    return [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.endswith(".json") and f != ".gitkeep"
    ]


def _needs_community_summary(data: dict) -> bool:
    return any(c.get("community_summary") is None for c in data["communities"])


def _needs_thread_summary(data: dict) -> bool:
    return any(
        t.get("thread_summary") is None
        for c in data["communities"]
        for t in c["threads"]
    )


def _resolve_files(request: SummarizeRequest) -> list[str]:
    if request.mode == "specific":
        path = os.path.join(DATA_DIR, request.file_name)
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        return [path]
    return _list_data_files()


async def _stream_community_summaries(files: list[str]) -> AsyncGenerator[str, None]:
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not _needs_community_summary(data):
            yield json.dumps({"file": file_path, "status": "skipped — already summarized"}) + "\n"
            continue

        for community_data in data["communities"]:
            if community_data.get("community_summary") is not None:
                continue

            community = Community(**community_data)
            summary = summarize_community(community)
            community_data["community_summary"] = summary

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            yield json.dumps({
                "file": file_path,
                "community": community_data["name"],
                "status": "done",
                "summary": summary,
            }) + "\n"


async def _stream_thread_summaries(files: list[str]) -> AsyncGenerator[str, None]:
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not _needs_thread_summary(data):
            yield json.dumps({"file": file_path, "status": "skipped — already summarized"}) + "\n"
            continue

        for community_data in data["communities"]:
            for thread_data in community_data["threads"]:
                if thread_data.get("thread_summary") is not None:
                    continue

                thread = Thread(**thread_data)
                summary = summarize_thread(thread)
                thread_data["thread_summary"] = summary

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)

                yield json.dumps({
                    "file": file_path,
                    "community": community_data["name"],
                    "thread": thread_data["title"],
                    "status": "done",
                    "summary": summary,
                }) + "\n"


@router.post("/communities")
async def summarize_communities(request: SummarizeRequest):
    try:
        files = _resolve_files(request)
        return StreamingResponse(
            _stream_community_summaries(files),
            media_type="application/x-ndjson",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/threads")
async def summarize_threads(request: SummarizeRequest):
    try:
        files = _resolve_files(request)
        return StreamingResponse(
            _stream_thread_summaries(files),
            media_type="application/x-ndjson",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
