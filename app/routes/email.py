import asyncio
import csv
import io
import json
from typing import Annotated, AsyncGenerator

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.models.email import BulkEmailRequest, SingleEmailRequest
from app.services.email_service import send_single_email

router = APIRouter(prefix="/email", tags=["email"])


@router.post("/send")
async def send_single(request: SingleEmailRequest):
    try:
        await send_single_email(
            to=request.to_email,
            subject=request.subject,
            salutation=request.salutation,
            body=request.body,
        )
        return {"status": "sent", "to": request.to_email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _stream_bulk_emails(
    rows: list[dict],
    subject: str,
    body: str,
    delay: float,
) -> AsyncGenerator[str, None]:
    for i, row in enumerate(rows):
        name = row["name"].strip()
        email = row["email"].strip()
        salutation = f"Dear {name},"

        try:
            await send_single_email(
                to=email,
                subject=subject,
                salutation=salutation,
                body=body,
            )
            yield json.dumps({
                "index": i + 1,
                "total": len(rows),
                "name": name,
                "email": email,
                "status": "sent",
            }) + "\n"
        except Exception as e:
            yield json.dumps({
                "index": i + 1,
                "total": len(rows),
                "name": name,
                "email": email,
                "status": "failed",
                "error": str(e),
            }) + "\n"

        if i < len(rows) - 1:
            await asyncio.sleep(delay)


@router.post("/bulk")
async def send_bulk(
    request: Annotated[BulkEmailRequest, Depends(BulkEmailRequest.as_form)],
    csv_file: UploadFile = File(...),
):
    try:
        content = await csv_file.read()
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))

        rows = []
        for i, row in enumerate(reader, start=2):
            normalized = {k.strip().lower(): v for k, v in row.items()}
            name = normalized.get("name", "").strip()
            email = normalized.get("email", "").strip()
            if not name or not email:
                raise HTTPException(status_code=422, detail=f"Row {i} is missing name or email")
            rows.append({"name": name, "email": email})

        if not rows:
            raise HTTPException(status_code=422, detail="CSV file is empty or has no valid rows")

        return StreamingResponse(
            _stream_bulk_emails(rows, request.subject, request.body, request.delay),
            media_type="application/x-ndjson",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
