"""Run the API server for testing."""

import uvicorn
from api.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )