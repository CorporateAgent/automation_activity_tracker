from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from colorama import Fore, Style, init
import logging
from supabase import create_client, Client

init()
load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info(f"{Fore.GREEN}Successfully connected to Supabase{Style.RESET_ALL}")

app = FastAPI(title="Gridline Data API")

# response models
class HealthResponse(BaseModel):
    status: str
    message: str

class ActivityData(BaseModel):
    status: str
    data: List[dict]

async def verify_api_key(api_key: str = Header(...)):
    """Verify the API key from the request header."""
    if api_key != os.getenv("API_KEY"):
        logger.error(f"{Fore.RED}Invalid API key provided{Style.RESET_ALL}")
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid API key"},
            media_type="application/json"
        )
    return api_key

@app.get("/", response_model=HealthResponse, response_class=JSONResponse)
async def root():
    """Root endpoint."""
    return JSONResponse(
        content={"status": "online"},
        media_type="application/json"
    )

# /table/{table_name}?offset=0&limit=1000
@app.get("/table/{table_name}")
async def get_table_page(
    table_name: str,
    offset: int = 0,
    limit: int = 1000,
    api_key: str = Depends(verify_api_key)
):
    if isinstance(api_key, JSONResponse):
        return api_key

    limit = max(1, min(limit, 1000))
    start = max(0, offset)
    end = start + limit - 1

    # exact count: returns .count on response
    page = supabase.table(table_name).select("*", count="exact").range(start, end).execute()
    rows = page.data or []
    total = page.count or 0

    has_more = (start + len(rows)) < total

    return JSONResponse({
        "status": "success",
        "data": rows,
        "offset": start,
        "limit": limit,
        "total": total,
        "has_more": has_more
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 