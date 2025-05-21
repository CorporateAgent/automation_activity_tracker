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

# Initialize colorama for colored terminal output
init()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Debug log for Supabase URL
logger.info(f"Supabase URL: {os.getenv('SUPABASE_URL')}")
logger.info(f"Supabase Key exists: {'Yes' if os.getenv('SUPABASE_KEY') else 'No'}")

# Define response models
class HealthResponse(BaseModel):
    status: str
    message: str

class ActivityData(BaseModel):
    status: str
    data: List[dict]

# Initialize FastAPI app
app = FastAPI(title="Gridline Data API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

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
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "message": "Gridline Data API is running"},
        media_type="application/json"
    )

@app.get("/activity", response_model=ActivityData, response_class=JSONResponse)
async def get_user_activity(api_key: str = Depends(verify_api_key)):
    """
    Get user activity metrics including emails generated and slack sessions.
    Returns a structured JSON response with user activity data.
    """
    # Ensure api_key (the result of verify_api_key) is handled correctly if it's a JSONResponse
    if isinstance(api_key, JSONResponse):
        return api_key # Propagate the error response

    try:
        logger.info(f"{Fore.BLUE}Fetching user activity summary from view...{Style.RESET_ALL}")
        
        # Query the view using Supabase client
        response = supabase.table(
            'user_activity'  # Name of your new view
        ).select('*').execute()
        
        logger.info(f"{Fore.GREEN}Query executed successfully against view{Style.RESET_ALL}")
        
        return JSONResponse(
            content={
                "status": "success",
                "data": response.data
            },
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"{Fore.RED}Error executing query against view: {str(e)}{Style.RESET_ALL}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)},
            media_type="application/json"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 