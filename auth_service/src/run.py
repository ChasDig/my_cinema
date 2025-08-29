from api.external.v1 import users_router as ex_users_router
from api.inner.v1 import users_router as in_users_router
from core.events import register_events
from fastapi import FastAPI

app = FastAPI(
    title="Auth Service",
    description="Service for authorization and registration users",
    version="0.1.0",
    root_path="/auth",
)
# External:
app.include_router(ex_users_router)

# Inner:
app.include_router(in_users_router)

# Events:
register_events(app)
