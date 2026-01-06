from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from app.database import get_db
from app import models, schemas
from app.core import security
from app.core.alerts import get_alertes_actives

router = APIRouter()

# Dépendance pour vérifier l'authentification
def get_current_user_role(token: str = Depends(security.oauth2_scheme)) -> dict:
    """Récupère le rôle de l'utilisateur depuis le token JWT."""
    payload = security.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré"
        )
    return {"email": payload.get("sub"), "role": payload.get("role")}

@router.get("/", response_model=List[schemas.BorneAvecDetails])
async def get_bornes(
    user: dict = Depends(get_current_user_role),
    site_id: Optional[int] = Query(None, description="Filtrer par site"),
    avec_alertes: bool = Query(False, description="Inclure uniquement les bornes avec alertes actives"),
    db: Session = Depends(get_db)
):
    """
    Retourne la liste des bornes.
    
    Les permissions dépendent du rôle:
    - **fournisseur**: Voir toutes les bornes
    - **responsable_technique**: Voir les bornes de ses sites
    - **responsable_agent**: Voir toutes les bornes (pour affectation)
    - **agent**: Voir uniquement les bornes qui lui sont affectées
    
    Filtres disponibles:
    - **site_id**: Filtrer par site
    - **avec_alertes**: Retourner uniquement les bornes avec alertes actives
    """
    query = db.query(models.Borne).options(
        joinedload(models.Borne.site),
        joinedload(models.Borne.agent_affecte)
    )
    
    # Filtrer par rôle
    if user["role"] == "agent":
        # Un agent ne voit que ses bornes affectées
        query = query.filter(models.Borne.id_agent_affecte != None)
    
    # Filtrer par site
    if site_id:
        query = query.filter(models.Borne.id_site == site_id)
    
    # Filtrer par alertes actives
    if avec_alertes:
        borne_ids_avec_alertes = [
            alerte.id_borne for alerte in get_alertes_actives(db)
        ]
        if borne_ids_avec_alertes:
            query = query.filter(models.Borne.id_borne.in_(borne_ids_avec_alertes))
        else:
            return []
    
    bornes = query.all()
    
    # Enrichir les données avec les dernières mesures
    result = []
    for borne in bornes:
        derniere_mesure = db.query(models.Mesure).filter(
            models.Mesure.id_borne == borne.id_borne
        ).order_by(models.Mesure.horodatage.desc()).first()
        
        borne_dict = {
            **borne.__dict__,
            "site_nom": borne.site.nom_site if borne.site else None,
            "agent_nom": f"{borne.agent_affecte.prenom} {borne.agent_affecte.nom}" if borne.agent_affecte else None,
            "dernier_niveau_gel": derniere_mesure.niveau_gel if derniere_mesure else None,
            "dernier_niveau_batterie": derniere_mesure.niveau_batterie if derniere_mesure else None,
            "derniere_mesure": derniere_mesure.horodatage if derniere_mesure else None
        }
        result.append(borne_dict)
    
    return result

@router.get("/{borne_id}", response_model=schemas.BorneAvecDetails)
async def get_borne(
    borne_id: int,
    user: dict = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    Récupère les détails d'une borne spécifique.
    """
    borne = db.query(models.Borne).options(
        joinedload(models.Borne.site),
        joinedload(models.Borne.agent_affecte)
    ).filter(models.Borne.id_borne == borne_id).first()
    
    if not borne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borne ID {borne_id} non trouvée"
        )
    
    # Récupérer la dernière mesure
    derniere_mesure = db.query(models.Mesure).filter(
        models.Mesure.id_borne == borne_id
    ).order_by(models.Mesure.horodatage.desc()).first()
    
    # Récupérer les alertes actives
    alertes = get_alertes_actives(db, borne_id)
    
    return {
        **borne.__dict__,
        "site_nom": borne.site.nom_site if borne.site else None,
        "agent_nom": f"{borne.agent_affecte.prenom} {borne.agent_affecte.nom}" if borne.agent_affecte else None,
        "dernier_niveau_gel": derniere_mesure.niveau_gel if derniere_mesure else None,
        "dernier_niveau_batterie": derniere_mesure.niveau_batterie if derniere_mesure else None,
        "derniere_mesure": derniere_mesure.horodatage if derniere_mesure else None,
        "alertes_actives": len(alertes)
    }

@router.put("/{borne_id}/affecter", response_model=schemas.Borne)
async def affecter_borne(
    borne_id: int,
    agent_id: int,
    user: dict = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    Affecte une borne à un agent pour maintenance.
    
    **Permissions**: responsable_technique ou responsable_agent uniquement.
    """
    if user["role"] not in ["responsable_technique", "responsable_agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit: seuls les responsables peuvent affecter des bornes"
        )
    
    # Vérifier que la borne existe
    borne = db.query(models.Borne).filter(models.Borne.id_borne == borne_id).first()
    if not borne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borne ID {borne_id} non trouvée"
        )
    
    # Vérifier que l'agent existe et a le bon rôle
    agent = db.query(models.Utilisateur).filter(
        models.Utilisateur.id_utilisateur == agent_id,
        models.Utilisateur.role == "agent"
    ).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent ID {agent_id} non trouvé ou n'a pas le rôle 'agent'"
        )
    
    # Affecter la borne
    borne.id_agent_affecte = agent_id
    
    try:
        db.commit()
        db.refresh(borne)
        return borne
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de l'affectation: {str(e)}"
        )

@router.put("/{borne_id}/seuils", response_model=schemas.Borne)
async def mettre_a_jour_seuils(
    borne_id: int,
    seuil_gel: int = Query(..., ge=1, le=100, description="Nouveau seuil d'alerte pour le gel (1-100%)"),
    seuil_batterie: int = Query(..., ge=1, le=100, description="Nouveau seuil d'alerte pour la batterie (1-100%)"),
    user: dict = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    Met à jour les seuils d'alerte d'une borne.
    
    **Permissions**: responsable_technique ou responsable_agent uniquement.
    """
    if user["role"] not in ["responsable_technique", "responsable_agent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit: seuls les responsables peuvent modifier les seuils"
        )
    
    borne = db.query(models.Borne).filter(models.Borne.id_borne == borne_id).first()
    
    if not borne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borne ID {borne_id} non trouvée"
        )
    
    borne.seuil_alerte_gel = seuil_gel
    borne.seuil_alerte_batterie = seuil_batterie
    
    try:
        db.commit()
        db.refresh(borne)
        return borne
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )

@router.get("/{borne_id}/alertes")
async def get_alertes_borne(
    borne_id: int,
    user: dict = Depends(get_current_user_role),
    db: Session = Depends(get_db)
):
    """
    Retourne les alertes d'une borne spécifique.
    """
    borne = db.query(models.Borne).filter(models.Borne.id_borne == borne_id).first()
    
    if not borne:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borne ID {borne_id} non trouvée"
        )
    
    alertes = get_alertes_actives(db, borne_id)
    
    return {
        "borne_id": borne_id,
        "nom_borne": borne.nom_borne,
        "alertes": [
            {
                "id_alerte": a.id_alerte,
                "type_alerte": a.type_alerte.value,
                "niveau_valeur": a.niveau_valeur,
                "statut": a.statut.value,
                "date_declenchement": a.date_declenchement
            } for a in alertes
        ],
        "total_alertes": len(alertes)
    }
