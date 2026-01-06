from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
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
    docs_url="/docs",  # Documentation Swagger UI
    redoc_url="/redoc",  # Documentation ReDoc
)

# Configuration CORS (Cross-Origin Resource Sharing)
# Permet à votre API d'être appelée depuis d'autres domaines (frontend, app mobile, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En développement, autorise tout. En production, spécifiez les domaines.
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Tous les headers
)

# Inclure les routeurs (endpoints)
app.include_router(auth.router, prefix="/api/auth", tags=["Authentification"])
app.include_router(mesures.router, prefix="/api/mesures", tags=["Mesures"])
app.include_router(bornes.router, prefix="/api/bornes", tags=["Bornes"])

# Route racine
@app.get("/", tags=["Accueil"])
async def root():
    """
    Point d'entrée de l'API.
    Retourne des informations de base sur l'API.
    """
    return {
        "message": "Bienvenue sur l'API Borne Gel Connectée",
        "version": "1.0.0",
        "documentation": "/docs",
        "description": "API pour la gestion des bornes de gel hydroalcoolique connectées"
    }

# Route de santé (health check)
@app.get("/health", tags=["Système"])
async def health_check():
    """
    Vérifie que l'API fonctionne correctement.
    Utilisé par les systèmes de monitoring.
    """
    return {
        "status": "healthy",
        "service": "borne-gel-api",
        "timestamp": "{{timestamp}}"
    }

# Route d'information sur la base de données
@app.get("/info", tags=["Système"])
async def system_info():
    """
    Retourne des informations sur la configuration du système.
    """
    return {
        "debug_mode": settings.DEBUG,
        "database_url": settings.DATABASE_URL[:20] + "..." if settings.DATABASE_URL else None,
        "jwt_algorithm": settings.JWT_ALGORITHM,
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
