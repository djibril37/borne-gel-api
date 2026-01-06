from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base de données
    DATABASE_URL: str = "mysql+pymysql://api_user:apipassword@localhost:3306/borne_gel_db"
    
    # JWT (JSON Web Tokens pour l'authentification)
    JWT_SECRET_KEY: str = "votre_super_secret_key_changez_moi_en_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

# Créer une instance de settings
settings = Settings()
