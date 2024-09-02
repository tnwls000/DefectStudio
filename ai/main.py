import uvicorn
from fastapi import FastAPI

from api.main import api_router

app = FastAPI(
    prefix="/api"
)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)

