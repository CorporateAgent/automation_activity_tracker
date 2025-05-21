# Gridline Data API

A simple FastAPI application that serves as an endpoint for Google Apps Script to fetch data from Supabase.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   API_KEY=your_api_key_for_security
   ```

## Running Locally

```bash
uvicorn main:app --reload
```

## API Endpoints

### Health Check
- `GET /`
- Returns the API status

### Query Data
- `POST /query`
- Headers: `api-key: your_api_key`
- Body:
  ```json
  {
    "table": "your_table_name"
  }
  ```

## Deployment

This API is designed to be deployed on Vercel. Make sure to set up the environment variables in your Vercel project settings.

## Security

- API key authentication is required for all endpoints
- CORS is enabled for all origins (customize in production)
- All sensitive data is stored in environment variables 