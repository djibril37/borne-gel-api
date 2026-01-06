from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger("uvicorn.error")

# 1. Créer le moteur de connexion à la base de données
try:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=True,  # Affiche les requêtes SQL dans le terminal
        pool_pre_ping=True
    )
    logger.info(f"Connexion à la base de données établie: {settings.DATABASE_URL}")
except Exception as e:
    logger.error(f"Erreur de connexion à la base de données: {str(e)}")
    raise

# 2. Créer une fabrique de sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 3. Base pour tous nos modèles SQLAlchemy
Base = declarative_base()

# 4. Fonction pour obtenir une session de base de données
def get_db():
    """
    Fournit une session de base de données pour chaque requête.
    Ferme automatiquement la session à la fin.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Erreur de session DB: {str(e)}")
        raise
    finally:
        db.close()
