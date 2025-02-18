import uvicorn
from fastapi import FastAPI

from app.api.api_v1.endpoints import organizations_ep, auth_ep


app = FastAPI()

app.include_router(organizations_ep.router, dependencies=[], tags=["Organizations"])
app.include_router(auth_ep.router, dependencies=[], tags=["Authentication"])

if __name__ == '__main__':
    uvicorn.run(host="localhost", port=82, app="main:app", reload=True)
