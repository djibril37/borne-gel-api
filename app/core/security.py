from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Configuration du hachage des mots de passe
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Fonctions pour le hachage et vérification des mots de passe
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe en clair correspond au hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Crée un hash sécurisé d'un mot de passe."""
    return pwd_context.hash(password)

# Fonctions pour les tokens JWT
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT d'accès."""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """
    Vérifie et décode un token JWT.
    
    Retourne les données décodées si le token est valide.
    Retourne None si le token est invalide.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def get_current_user_email(token: str) -> Optional[str]:
    """
    Extrait l'email de l'utilisateur depuis un token JWT.
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")  # "sub" est le standard JWT pour le sujet (ici l'email)
    return None
