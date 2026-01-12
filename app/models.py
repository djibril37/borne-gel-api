from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, ForeignKey, Date, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

# Enumérations pour les rôles
class RoleEnum(str, enum.Enum):
    fournisseur = "fournisseur"
    responsable_technique = "responsable_technique"
    responsable_agent = "responsable_agent"
    agent = "agent"

# Enumération pour les types d'alerte
class TypeAlerteEnum(str, enum.Enum):
    GEL_BAS = "gel_bas"
    BATTERIE_BASSE = "batterie_basse"
    GEL_CRITIQUE = "gel_critique"
    BATTERIE_CRITIQUE = "batterie_critique"

# Enumération pour le statut des alertes
class StatutAlerteEnum(str, enum.Enum):
    NOUVELLE = "nouvelle"
    ASSIGNEE = "assignee"
    RESOLUE = "resolue"

# Enumération pour les types d'intervention
class TypeInterventionEnum(str, enum.Enum):
    REMPLISSAGE_GEL = "remplissage_gel"
    CHANGEMENT_BATTERIE = "changement_batterie"
    MAINTENANCE = "maintenance"

# Table utilisateurs
class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    
    id_utilisateur = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    mot_de_passe_hash = Column(String(255), nullable=False)
    nom = Column(String(100))
    prenom = Column(String(100))
    role = Column(Enum(RoleEnum), nullable=False)
    date_creation = Column(DateTime, server_default=func.now())
    est_actif = Column(Boolean, default=True)
    
    # Relations
    sites_responsable = relationship("Site", back_populates="responsable_technique")
    bornes_affectees = relationship("Borne", back_populates="agent_affecte")
    alertes_assignees = relationship("Alerte", back_populates="agent_assignee")
    interventions = relationship("Intervention", back_populates="agent")

# Table sites
class Site(Base):
    __tablename__ = "sites"
    
    id_site = Column(Integer, primary_key=True, index=True)
    nom_site = Column(String(255), nullable=False)
    adresse = Column(Text)
    id_responsable_technique = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))
    
    # Relations
    responsable_technique = relationship("Utilisateur", back_populates="sites_responsable")
    bornes = relationship("Borne", back_populates="site")

# Table bornes
class Borne(Base):
    __tablename__ = "bornes"
    
    id_borne = Column(Integer, primary_key=True, index=True)
    uuid_esp = Column(String(255), unique=True, nullable=False, index=True)
    nom_borne = Column(String(100), default="Borne sans nom")
    id_site = Column(Integer, ForeignKey("sites.id_site"), nullable=False)
    salle_local = Column(String(100), nullable=False)
    seuil_alerte_gel = Column(Integer, default=10)
    seuil_alerte_batterie = Column(Integer, default=10)
    id_agent_affecte = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))
    date_installation = Column(Date)
    est_active = Column(Boolean, default=True)
    
    # Relations
    site = relationship("Site", back_populates="bornes")
    agent_affecte = relationship("Utilisateur", back_populates="bornes_affectees")
    mesures = relationship("Mesure", back_populates="borne")
    alertes = relationship("Alerte", back_populates="borne")
    interventions = relationship("Intervention", back_populates="borne")

# Table mesures
class Mesure(Base):
    __tablename__ = "mesures"
    
    id_mesure = Column(BigInteger, primary_key=True, index=True)
    id_borne = Column(Integer, ForeignKey("bornes.id_borne"), nullable=False)
    niveau_gel = Column(Integer, nullable=False)  # Pourcentage (0-100)
    niveau_batterie = Column(Integer, nullable=False)  # Pourcentage (0-100)
    horodatage = Column(DateTime, server_default=func.now())
    
    # Relations
    borne = relationship("Borne", back_populates="mesures")

# Table alertes
class Alerte(Base):
    __tablename__ = "alertes"
    
    id_alerte = Column(Integer, primary_key=True, index=True)
    id_borne = Column(Integer, ForeignKey("bornes.id_borne"), nullable=False)
    type_alerte = Column(Enum(TypeAlerteEnum), nullable=False)
    niveau_valeur = Column(Integer, nullable=False)
    statut = Column(Enum(StatutAlerteEnum), default=StatutAlerteEnum.NOUVELLE)
    id_agent_assignee = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"))
    date_declenchement = Column(DateTime, server_default=func.now())
    date_resolution = Column(DateTime)
    
    # Relations
    borne = relationship("Borne", back_populates="alertes")
    agent_assignee = relationship("Utilisateur", back_populates="alertes_assignees")

# Table interventions
class Intervention(Base):
    __tablename__ = "interventions"
    
    id_intervention = Column(Integer, primary_key=True, index=True)
    id_borne = Column(Integer, ForeignKey("bornes.id_borne"), nullable=False)
    id_agent = Column(Integer, ForeignKey("utilisateurs.id_utilisateur"), nullable=False)
    type_intervention = Column(Enum(TypeInterventionEnum), nullable=False)
    date_intervention = Column(DateTime, server_default=func.now())
    commentaire = Column(Text)
    
    # Relations
    borne = relationship("Borne", back_populates="interventions")
    agent = relationship("Utilisateur", back_populates="interventions")
