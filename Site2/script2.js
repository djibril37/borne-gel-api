const BORNES = [
    { id: 101, lieu: "Accueil", gel: 5, batt: 90 },
    { id: 102, lieu: "Cafétéria", gel: 55, batt: 8 },
    { id: 103, lieu: "Salle 102", gel: 80, batt: 95 }
];

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.onsubmit = (e) => {
        e.preventDefault();
        const role = document.getElementById('role').value;
        window.location.href = `Page-${role}.html`;
    };
}

function showTab(tabId) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

function chargerBornes() {
    const grid = document.getElementById('borneGrid');
    const badge = document.getElementById('alertCount');
    if (!grid) return;

    let alertes = 0;
    grid.innerHTML = "";

    BORNES.forEach(b => {
        const isCritical = (b.gel < 10 || b.batt < 10);
        if (isCritical) alertes++;

        grid.innerHTML += `
            <div class="card ${isCritical ? 'alert' : ''}">
                <h3>Borne #${b.id}</h3>
                <p style="color:#64748b;">📍 ${b.lieu}</p>
                <p>Gel : <strong>${b.gel}%</strong></p>
                <p>Batterie : <strong>${b.batt}%</strong></p>
            </div>
        `;
    });
    if (badge) badge.innerText = alertes;
}

function logout() {
    window.location.href = "Connexion.html";
}

window.onload = chargerBornes;