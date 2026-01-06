from sqlalchemy.orm import Session
from app import models
from datetime import datetime

def verifier_et_creer_alertes(db: Session, borne: models.Borne, mesure: models.Mesure):
    """
    Vérifie si une nouvelle mesure doit générer des alertes.
    
    Cette fonction est appelée après chaque enregistrement de mesure.
    Elle vérifie les seuils de gel et batterie et crée des alertes si nécessaire.
    """
    alertes_crees = []
    
    # Vérifier le niveau de gel
    if mesure.niveau_gel <= 5:  # Niveau critique
        alerte = models.Alerte(
            id_borne=borne.id_borne,
            type_alerte=models.TypeAlerteEnum.GEL_CRITIQUE,
            niveau_valeur=mesure.niveau_gel,
            statut=models.StatutAlerteEnum.NOUVELLE
        )
        db.add(alerte)
        alertes_crees.append(alerte)
        
    elif mesure.niveau_gel <= borne.seuil_alerte_gel:
        alerte = models.Alerte(
            id_borne=borne.id_borne,
            type_alerte=models.TypeAlerteEnum.GEL_BAS,
            niveau_valeur=mesure.niveau_gel,
            statut=models.StatutAlerteEnum.NOUVELLE
        )
        db.add(alerte)
        alertes_crees.append(alerte)
    
    # Vérifier le niveau de batterie
    if mesure.niveau_batterie <= 5:  # Niveau critique
        alerte = models.Alerte(
            id_borne=borne.id_borne,
            type_alerte=models.TypeAlerteEnum.BATTERIE_CRITIQUE,
            niveau_valeur=mesure.niveau_batterie,
            statut=models.StatutAlerteEnum.NOUVELLE
        )
        db.add(alerte)
        alertes_crees.append(alerte)
        
    elif mesure.niveau_batterie <= borne.seuil_alerte_batterie:
        alerte = models.Alerte(
            id_borne=borne.id_borne,
            type_alerte=models.TypeAlerteEnum.BATTERIE_BASSE,
            niveau_valeur=mesure.niveau_batterie,
            statut=models.StatutAlerteEnum.NOUVELLE
        )
        db.add(alerte)
        alertes_crees.append(alerte)
    
    if alertes_crees:
        db.commit()
        for alerte in alertes_crees:
            db.refresh(alerte)
    
    return alertes_crees

def get_alertes_actives(db: Session, borne_id: Optional[int] = None):
    """
    Récupère toutes les alertes actives (non résolues).
    
    Si borne_id est spécifié, ne retourne que les alertes de cette borne.
    """
    query = db.query(models.Alerte).filter(
        models.Alerte.statut.in_([models.StatutAlerteEnum.NOUVELLE, models.StatutAlerteEnum.ASSIGNEE])
    )
    
    if borne_id:
        query = query.filter(models.Alerte.id_borne == borne_id)
    
    return query.order_by(models.Alerte.date_declenchement.desc()).all()

def resoudre_alerte(db: Session, alerte_id: int, agent_id: int, commentaire: str = ""):
    """
    Marque une alerte comme résolue.
    
    Crée également une intervention pour tracer l'action.
    """
    alerte = db.query(models.Alerte).filter(models.Alerte.id_alerte == alerte_id).first()
    
    if not alerte:
        return None
    
    # Mettre à jour l'alerte
    alerte.statut = models.StatutAlerteEnum.RESOLUE
    alerte.date_resolution = datetime.utcnow()
    
    # Créer une intervention correspondante
    if alerte.type_alerte in [models.TypeAlerteEnum.GEL_BAS, models.TypeAlerteEnum.GEL_CRITIQUE]:
        type_intervention = models.TypeInterventionEnum.REMPLISSAGE_GEL
    else:
        type_intervention = models.TypeInterventionEnum.CHANGEMENT_BATTERIE
    
    intervention = models.Intervention(
        id_borne=alerte.id_borne,
        id_agent=agent_id,
        type_intervention=type_intervention,
        commentaire=commentaire or f"Résolution alerte {alerte.type_alerte.value}"
    )
    
    db.add(intervention)
    db.commit()
    db.refresh(alerte)
    db.refresh(intervention)
    
    return alerte
