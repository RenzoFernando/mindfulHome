from app.api.endpoints import analyses, auth, comparison, simulation
from fastapi import APIRouter
from app.api.endpoints import users

api_router = APIRouter(prefix="/mindfulhome")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(analyses.router)
api_router.include_router(simulation.router)
api_router.include_router(comparison.router)
