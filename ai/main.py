import uvicorn
from fastapi import FastAPI

from api.routes.main import api_router

app = FastAPI()
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8001)

