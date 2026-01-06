from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date
from typing import Optional, List
from enum import Enum

# Enums pour Pydantic
class RoleEnum(str, Enum):
    fournisseur = "fournisseur"
    responsable_technique = "responsable_technique"
    responsable_agent = "responsable_agent"
    agent = "agent"

class TypeAlerteEnum(str, Enum):
    gel_bas = "gel_bas"
    batterie_basse = "batterie_basse"
    gel_critique = "gel_critique"
    batterie_critique = "batterie_critique"

class StatutAlerteEnum(str, Enum):
    nouvelle = "nouvelle"
    assignee = "assignee"
    resolue = "resolue"

class TypeInterventionEnum(str, Enum):
    remplissage_gel = "remplissage_gel"
    changement_batterie = "changement_batterie"
    maintenance = "maintenance"

# Modèles de base (sans ID)
class MesureBase(BaseModel):
    uuid_esp: str = Field(..., min_length=1, max_length=255)
    niveau_gel: int = Field(..., ge=0, le=100, description="Niveau de gel en pourcentage (0-100)")
    niveau_batterie: int = Field(..., ge=0, le=100, description="Niveau de batterie en pourcentage (0-100)")

class BorneBase(BaseModel):
    uuid_esp: str = Field(..., min_length=1, max_length=255)
    nom_borne: str = Field(..., max_length=100)
    id_site: int
    salle_local: str = Field(..., max_length=100)
    seuil_alerte_gel: int = Field(default=10, ge=1, le=100)
    seuil_alerte_batterie: int = Field(default=10, ge=1, le=100)
    id_agent_affecte: Optional[int] = None

class UtilisateurBase(BaseModel):
    email: EmailStr
    nom: str = Field(..., max_length=100)
    prenom: str = Field(..., max_length=100)
    role: RoleEnum

class UtilisateurCreate(UtilisateurBase):
    mot_de_passe: str = Field(..., min_length=6)

class UtilisateurLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

# Modèles avec ID (pour les réponses)
class Mesure(MesureBase):
    id_mesure: int
    id_borne: int
    horodatage: datetime
    
    class Config:
        from_attributes = True

class Borne(BorneBase):
    id_borne: int
    est_active: bool
    date_installation: Optional[date] = None
    
    class Config:
        from_attributes = True

class Utilisateur(UtilisateurBase):
    id_utilisateur: int
    est_actif: bool
    date_creation: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class AlerteBase(BaseModel):
    type_alerte: TypeAlerteEnum
    niveau_valeur: int
    statut: StatutAlerteEnum = StatutAlerteEnum.nouvelle

class Alerte(AlerteBase):
    id_alerte: int
    id_borne: int
    date_declenchement: datetime
    date_resolution: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Réponses pour l'API
class BorneAvecDetails(Borne):
    site_nom: Optional[str] = None
    agent_nom: Optional[str] = None
    dernier_niveau_gel: Optional[int] = None
    dernier_niveau_batterie: Optional[int] = None
    derniere_mesure: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SiteBase(BaseModel):
    nom_site: str = Field(..., max_length=255)
    adresse: Optional[str] = None
    id_responsable_technique: Optional[int] = None

class Site(SiteBase):
    id_site: int
    
    class Config:
        from_attributes = True
