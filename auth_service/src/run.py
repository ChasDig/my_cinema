from fastapi import FastAPI

from api.v1 import users_router


app = FastAPI(
    title="Auth Service",
    description="Service for authorization and registration users",
    version="0.1.0",
    root_path="/auth",
)
app.include_router(users_router)
