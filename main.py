from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import os
from dotenv import load_dotenv
from colorama import Fore, Style, init
import logging
from supabase import create_client, Client
import json

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
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "message": "Gridline Data API is running"}

@app.get("/user-activity")
async def get_user_activity(api_key: str = Depends(verify_api_key)):
    """
    Get user activity metrics including emails generated and slack sessions.
    Returns a structured JSON response with user activity data.
    """
    try:
        logger.info(f"{Fore.BLUE}Fetching user activity metrics...{Style.RESET_ALL}")
        
        # Execute the query using Supabase
        response = supabase.rpc(
            'get_user_activity_metrics'
        ).execute()
        
        logger.info(f"{Fore.GREEN}Query executed successfully{Style.RESET_ALL}")
        
        return {
            "status": "success",
            "data": response.data
        }
        
    except Exception as e:
        logger.error(f"{Fore.RED}Error executing query: {str(e)}{Style.RESET_ALL}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 