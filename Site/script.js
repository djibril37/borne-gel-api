/** * DONNÉES SIMULÉES (Dossier Projet BTS CIEL)
 * [cite: 119, 120, 121, 122]
 */
const bornes = [
    { id: 1, nom: "Borne Entrée Hall", gel: 45, batterie: 80 },
    { id: 2, nom: "Borne Couloir B2", gel: 8, batterie: 12 },
    { id: 3, nom: "Borne Salle Rostand", gel: 65, batterie: 90 },
    { id: 4, nom: "Borne Accueil", gel: 4, batterie: 55 }
];

// Seuils par défaut [cite: 128]
let seuilGel = 10;
let seuilBatt = 10;

const pageType = document.body.getAttribute('data-page');
const container = document.getElementById('bornes-container');

/**
 * Fonction de rendu de l'interface
 */
function displayBornes() {
    container.innerHTML = "";
    
    bornes.forEach(borne => {
        // Logique d'alerte [cite: 113, 129, 144]
        const needsMaintenance = (borne.gel < seuilGel) || (borne.batterie < seuilBatt);
        
        const card = document.createElement('div');
        card.className = `card ${needsMaintenance ? 'alert' : 'ok'}`;
        
        card.innerHTML = `
            <div class="card-header">
                <h3>${borne.nom}</h3>
                <span class="status-icon">${needsMaintenance ? '⚠️' : '✅'}</span>
            </div>
            <p>ID Matériel : ESP32-${borne.id}</p>
            <div class="metric">Niveau Gel : ${borne.gel}%</div>
            <div class="metric">Batterie : ${borne.batterie}%</div>
            <p><em>Statut : ${needsMaintenance ? 'MAINTENANCE REQUISE' : 'OPÉRATIONNEL'}</em></p>
        `;
        container.appendChild(card);
    });
}

/**
 * Logique spécifique à l'administrateur 
 */
if (pageType === 'admin') {
    const btnApply = document.getElementById('btn-apply');
    const inputGel = document.getElementById('input-gel');
    const inputBatt = document.getElementById('input-batt');

    btnApply.addEventListener('click', () => {
        seuilGel = parseInt(inputGel.value);
        seuilBatt = parseInt(inputBatt.value);
        displayBornes();
    });
}

// Premier affichage au chargement
displayBornes();