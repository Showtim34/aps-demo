"""Assembleur des routes API v1.

Ce fichier joue un rôle simple mais important : il regroupe tous les routers
versionnés sous un même point d'entrée.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import alerts, auth, dashboard, demo, machines, measurements, sites, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(machines.router, prefix="/machines", tags=["machines"])
api_router.include_router(measurements.router, prefix="/measurements", tags=["measurements"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
