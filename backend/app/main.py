from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, communities, posts, professionals, subscriptions, users

app = FastAPI(
    title="VSS — Veil Support System",
    description="Discreet addiction support platform with community feeds, anonymous confessions, and tiered professional care.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(communities.router)
app.include_router(posts.router)
app.include_router(professionals.router)
app.include_router(subscriptions.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
