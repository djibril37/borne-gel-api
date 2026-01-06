from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app import models, schemas
from app.core import security
from app.core.config import settings

router = APIRouter()

# Schéma OAuth2 pour l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentifie un utilisateur et retourne un token JWT.
    
    - **username**: Email de l'utilisateur
    - **password**: Mot de passe
    
    Retourne un token JWT valide pour les requêtes suivantes.
    """
    # Rechercher l'utilisateur par email
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == form_data.username
    ).first()
    
    # Vérifier si l'utilisateur existe et le mot de passe est correct
    if not utilisateur or not security.verify_password(form_data.password, utilisateur.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier si le compte est actif
    if not utilisateur.est_actif:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte désactivé",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer le token JWT
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": utilisateur.email, "role": utilisateur.role.value},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/register", response_model=schemas.Utilisateur, status_code=status.HTTP_201_CREATED)
async def register(
    utilisateur: schemas.UtilisateurCreate,
    db: Session = Depends(get_db)
):
    """
    Crée un nouveau compte utilisateur.
    
    **Note**: Dans une version réelle, cet endpoint serait protégé
    et seul un administrateur pourrait créer certains types de comptes.
    """
    # Vérifier si l'email est déjà utilisé
    existing_user = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == utilisateur.email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe déjà"
        )
    
    # Créer le nouvel utilisateur
    nouvel_utilisateur = models.Utilisateur(
        email=utilisateur.email,
        mot_de_passe_hash=security.get_password_hash(utilisateur.mot_de_passe),
        nom=utilisateur.nom,
        prenom=utilisateur.prenom,
        role=utilisateur.role
    )
    
    try:
        db.add(nouvel_utilisateur)
        db.commit()
        db.refresh(nouvel_utilisateur)
        
        return nouvel_utilisateur
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )

@router.get("/me", response_model=schemas.Utilisateur)
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Retourne les informations de l'utilisateur connecté.
    
    Utilise le token JWT pour identifier l'utilisateur.
    """
    email = security.get_current_user_email(token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    
    utilisateur = db.query(models.Utilisateur).filter(
        models.Utilisateur.email == email
    ).first()
    
    if not utilisateur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    return utilisateur

@router.get("/users", response_model=list[schemas.Utilisateur])
async def get_all_users(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Retourne la liste de tous les utilisateurs.
    
    **Accès restreint**: Seuls les administrateurs (fournisseur) peuvent utiliser cet endpoint.
    """
    # Vérifier le rôle de l'utilisateur via le token
    payload = security.verify_token(token)
    if not payload or payload.get("role") != "fournisseur":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit: droits insuffisants"
        )
    
    utilisateurs = db.query(models.Utilisateur).all()
    return utilisateurs
