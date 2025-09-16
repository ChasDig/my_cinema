from api.external.v1 import users_router as ex_users_router
from api.inner.v1 import users_router as in_users_router
from core.app_config import config
from core.events import register_events
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from middlewares import ProcessTimeHeaderMiddleware

app = FastAPI(
    title="Auth Service",
    description="Service for authorization and registration users",
    version="0.1.0",
    root_path="/auth",
)

# Middleware:
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.allow_origins,
    allow_methods=config.allow_methods,
    allow_headers=config.allow_headers,
)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=config.allowed_hosts,
)
app.add_middleware(ProcessTimeHeaderMiddleware)

# External API:
app.include_router(ex_users_router)

# Inner API:
app.include_router(in_users_router)

# Events:
register_events(app)
