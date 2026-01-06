from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import des routeurs
from app.api.endpoints import mesures, auth, bornes

# Création de l'application FastAPI
app = FastAPI(
    title="API Borne Gel Connectée",
    description="API REST pour la gestion des bornes de gel hydroalcoolique - Projet BTS CIEL",
    version="1.0.0",
    contact={
        "name": "Équipe Borne Gel",
        "email": "contact@bornegel.fr",
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routeurs
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(mesures.router, prefix="/api/mesures", tags=["Mesures"])
app.include_router(bornes.router, prefix="/api/bornes", tags=["Bornes"])

# Route racine
@app.get("/", tags=["Accueil"])
async def root():
    return {
        "message": "Bienvenue sur l'API Borne Gel Connectée",
        "version": "1.0.0",
        "documentation": "/docs",
        "description": "API pour la gestion des bornes de gel hydroalcoolique connectées"
    }

# Route de santé
@app.get("/health", tags=["Système"])
async def health_check():
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "borne-gel-api",
        "timestamp": datetime.utcnow().isoformat()
    }

# Route d'information
@app.get("/info", tags=["Système"])
async def system_info():
    return {
        "debug_mode": settings.DEBUG,
        "database_url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else None,
        "jwt_algorithm": settings.JWT_ALGORITHM,
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }
