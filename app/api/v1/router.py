from fastapi import APIRouter

from app.api.v1 import applications, auth, institutions, opportunities, skills, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(skills.router)
api_router.include_router(opportunities.router)
api_router.include_router(applications.router)
api_router.include_router(institutions.router)
