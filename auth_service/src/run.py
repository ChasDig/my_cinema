from api.v1 import users_router
from core.events import register_events
from fastapi import FastAPI

app = FastAPI(
    title="Auth Service",
    description="Service for authorization and registration users",
    version="0.1.0",
    root_path="/auth",
)
app.include_router(users_router)
register_events(app)
