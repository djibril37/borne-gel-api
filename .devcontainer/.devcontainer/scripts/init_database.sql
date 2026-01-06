-- Création de la base de données (déjà fait par setup.sh, mais au cas où)
CREATE DATABASE IF NOT EXISTS borne_gel_db;
USE borne_gel_db;

-- Table utilisateurs
CREATE TABLE IF NOT EXISTS utilisateurs (
    id_utilisateur INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe_hash VARCHAR(255) NOT NULL,
    nom VARCHAR(100),
    prenom VARCHAR(100),
    role ENUM('fournisseur', 'responsable_technique', 'responsable_agent', 'agent') NOT NULL,
    date_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
    est_actif BOOLEAN DEFAULT TRUE
);

-- Table sites
CREATE TABLE IF NOT EXISTS sites (
    id_site INT PRIMARY KEY AUTO_INCREMENT,
    nom_site VARCHAR(255) NOT NULL,
    adresse TEXT,
    id_responsable_technique INT,
    FOREIGN KEY (id_responsable_technique) REFERENCES utilisateurs(id_utilisateur)
);

-- Table bornes
CREATE TABLE IF NOT EXISTS bornes (
    id_borne INT PRIMARY KEY AUTO_INCREMENT,
    uuid_esp VARCHAR(255) UNIQUE NOT NULL,
    nom_borne VARCHAR(100) DEFAULT 'Borne sans nom',
    id_site INT NOT NULL,
    salle_local VARCHAR(100) NOT NULL,
    seuil_alerte_gel INT DEFAULT 10,
    seuil_alerte_batterie INT DEFAULT 10,
    id_agent_affecte INT,
    date_installation DATE,
    est_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_site) REFERENCES sites(id_site),
    FOREIGN KEY (id_agent_affecte) REFERENCES utilisateurs(id_utilisateur),
    INDEX idx_site (id_site),
    INDEX idx_agent (id_agent_affecte)
);

-- Table mesures
CREATE TABLE IF NOT EXISTS mesures (
    id_mesure BIGINT PRIMARY KEY AUTO_INCREMENT,
    id_borne INT NOT NULL,
    niveau_gel INT NOT NULL,
    niveau_batterie INT NOT NULL,
    horodatage DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_borne) REFERENCES bornes(id_borne),
    INDEX idx_borne_horodatage (id_borne, horodatage DESC)
);

-- Table alertes
CREATE TABLE IF NOT EXISTS alertes (
    id_alerte INT PRIMARY KEY AUTO_INCREMENT,
    id_borne INT NOT NULL,
    type_alerte ENUM('gel_bas', 'batterie_basse', 'gel_critique', 'batterie_critique') NOT NULL,
    niveau_valeur INT NOT NULL,
    statut ENUM('nouvelle', 'assignee', 'resolue') DEFAULT 'nouvelle',
    id_agent_assignee INT,
    date_declenchement DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_resolution DATETIME,
    FOREIGN KEY (id_borne) REFERENCES bornes(id_borne),
    FOREIGN KEY (id_agent_assignee) REFERENCES utilisateurs(id_utilisateur),
    INDEX idx_statut (statut),
    INDEX idx_borne (id_borne)
);

-- Table interventions
CREATE TABLE IF NOT EXISTS interventions (
    id_intervention INT PRIMARY KEY AUTO_INCREMENT,
    id_borne INT NOT NULL,
    id_agent INT NOT NULL,
    type_intervention ENUM('remplissage_gel', 'changement_batterie', 'maintenance') NOT NULL,
    date_intervention DATETIME DEFAULT CURRENT_TIMESTAMP,
    commentaire TEXT,
    FOREIGN KEY (id_borne) REFERENCES bornes(id_borne),
    FOREIGN KEY (id_agent) REFERENCES utilisateurs(id_utilisateur)
);

-- Insertion d'un utilisateur administrateur de test (mot de passe: admin123)
INSERT INTO utilisateurs (email, mot_de_passe_hash, nom, prenom, role) VALUES
('admin@bornegel.fr', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'Admin', 'System', 'fournisseur');

-- Insertion d'un site de test
INSERT INTO sites (nom_site, adresse, id_responsable_technique) VALUES
('Lycée Jean Rostand - Bâtiment A', '123 Avenue de la République, Villepinte', 1);

-- Insertion d'une borne de test
INSERT INTO bornes (uuid_esp, nom_borne, id_site, salle_local, seuil_alerte_gel, seuil_alerte_batterie) VALUES
('ESP32-001', 'Borne Entrée Principale', 1, 'Hall RDC', 15, 20);