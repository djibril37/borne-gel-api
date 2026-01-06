from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.core.alerts import verifier_et_creer_alertes

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def recevoir_mesure(
    mesure: schemas.MesureCreate,
    db: Session = Depends(get_db)
):
    """
    Endpoint pour recevoir les données d'une borne.
    
    **Cet endpoint sera appelé par l'ESP32 après chaque utilisation.**
    
    - **uuid_esp**: Identifiant unique de la carte ESP32 (ex: "ESP32-001")
    - **niveau_gel**: Pourcentage de gel restant (0-100)
    - **niveau_batterie**: Pourcentage de batterie restante (0-100)
    
    Retourne la mesure enregistrée avec son ID et horodatage.
    """
    try:
        # 1. Trouver la borne correspondante à l'uuid_esp
        borne = db.query(models.Borne).filter(
            models.Borne.uuid_esp == mesure.uuid_esp
        ).first()
        
        if not borne:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Borne avec uuid_esp '{mesure.uuid_esp}' non trouvée"
            )
        
        # 2. Créer la nouvelle mesure
        nouvelle_mesure = models.Mesure(
            id_borne=borne.id_borne,
            niveau_gel=mesure.niveau_gel,
            niveau_batterie=mesure.niveau_batterie
        )
        
        db.add(nouvelle_mesure)
        db.commit()
        db.refresh(nouvelle_mesure)
        
        # 3. Vérifier si des alertes doivent être créées
        verifier_et_creer_alertes(db, borne, nouvelle_mesure)
        
        # 4. Retourner un simple message de succès
        return {
            "message": "Mesure enregistrée avec succès",
            "id_mesure": nouvelle_mesure.id_mesure,
            "id_borne": nouvelle_mesure.id_borne,
            "horodatage": nouvelle_mesure.horodatage.isoformat()
        }
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur d'intégrité des données"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur: {str(e)}"
        )

@router.get("/borne/{borne_id}", response_model=List[schemas.Mesure])
async def get_mesures_par_borne(
    borne_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique des mesures d'une borne spécifique.
    
    - **borne_id**: ID de la borne
    - **limit**: Nombre maximum de mesures à retourner (par défaut: 100)
    
    Retourne la liste des mesures triées par date (plus récentes en premier).
    """
    mesures = db.query(models.Mesure).filter(
        models.Mesure.id_borne == borne_id
    ).order_by(
        models.Mesure.horodatage.desc()
    ).limit(limit).all()
    
    if not mesures:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune mesure trouvée pour la borne ID {borne_id}"
        )
    
    return mesures

@router.get("/derniere/borne/{borne_id}", response_model=schemas.Mesure)
async def get_derniere_mesure(
    borne_id: int,
    db: Session = Depends(get_db)
):
    """
    Récupère la dernière mesure enregistrée pour une borne.
    
    Utile pour afficher l'état actuel d'une borne.
    """
    mesure = db.query(models.Mesure).filter(
        models.Mesure.id_borne == borne_id
    ).order_by(
        models.Mesure.horodatage.desc()
    ).first()
    
    if not mesure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune mesure trouvée pour la borne ID {borne_id}"
        )
    
    return mesure

@router.get("/stats/borne/{borne_id}")
async def get_stats_borne(
    borne_id: int,
    db: Session = Depends(get_db)
):
    """
    Retourne des statistiques pour une borne.
    
    Inclut:
    - Dernière mesure
    - Moyennes des niveaux
    - Nombre total de mesures
    """
    mesures = db.query(models.Mesure).filter(
        models.Mesure.id_borne == borne_id
    ).all()
    
    if not mesures:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Aucune mesure trouvée pour la borne ID {borne_id}"
        )
    
    dernieres_mesures = mesures[:10]  # 10 dernières mesures
    
    stats = {
        "borne_id": borne_id,
        "total_mesures": len(mesures),
        "derniere_mesure": {
            "niveau_gel": mesures[0].niveau_gel if mesures else None,
            "niveau_batterie": mesures[0].niveau_batterie if mesures else None,
            "horodatage": mesures[0].horodatage if mesures else None
        },
        "moyennes": {
            "gel": sum(m.niveau_gel for m in mesures) / len(mesures) if mesures else 0,
            "batterie": sum(m.niveau_batterie for m in mesures) / len(mesures) if mesures else 0
        },
        "historique_recent": [
            {
                "niveau_gel": m.niveau_gel,
                "niveau_batterie": m.niveau_batterie,
                "horodatage": m.horodatage
            } for m in dernieres_mesures
        ]
    }
    
    return stats
