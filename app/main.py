from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from .routers import posts, users, auth
from .utils.helpers import format_response
from .config.database import engine
from .models.models import Base
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.middleware.cors import CORSMiddleware
import os
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("uploads", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.get("/")
@limiter.limit("10/minute")  
def root(request: Request):
    return {"message": "HERE World"}

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return format_response(
        data=None,
        message="Internal server error: " + str(exc),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        success=False
    )
