const canvas = document.getElementById('staff');
const ctx = canvas.getContext('2d');
const message = document.getElementById('message');
const buttons = document.querySelectorAll('.note-buttons button');

// Dimensions et espacement des lignes
const lineHeight = 20; // Distance entre deux lignes
const startY = 50; // Position verticale de la première ligne
const width = canvas.width; // Largeur totale du canvas

// Dessiner la portée musicale
function drawStaff() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 1; i <= 5; i++) {
        ctx.beginPath();
        ctx.moveTo(0, i * 30);
        ctx.lineTo(canvas.width, i * 30);
        ctx.stroke();
    }
}

// Notes de la gamme de sol et leurs positions sur la portée
const notes = ["G", "A", "B", "C", "D", "E", "F#"];
const notePositions = {
    "G": 150,
    "A": 140,
    "B": 130,
    "C": 120,
    "D": 110,
    "E": 100,
    "F#": 90
};

let currentNote = null; // Note actuelle
let notesOnScreen = []; // Liste des notes affichées


// Ajouter une nouvelle note
function addNote() {
    const randomIndex = Math.floor(Math.random() * notes.length);
    const note = notes[randomIndex];
    notesOnScreen.push({ note: note, x: canvas.width });
}

// Dessiner les notes sur la portée
function drawNotes() {
    notesOnScreen.forEach(noteObj => {
        ctx.beginPath();
        ctx.arc(noteObj.x, notePositions[noteObj.note], 10, 0, 2 * Math.PI);
        ctx.fill();
        ctx.closePath();
    });
}

if (!ctx) {
    console.error("Le canvas ne peut pas être initialisé. Vérifiez l'élément HTML.");
}

// Mettre à jour la position des notes
function updateNotes() {
    notesOnScreen.forEach(noteObj => {
        noteObj.x -= 2; // Déplace les notes vers la gauche
    });
    notesOnScreen = notesOnScreen.filter(noteObj => noteObj.x > 0); // Supprime les notes hors écran
}

// Vérifier la réponse de l'utilisateur
function checkAnswer(note) {
    if (notesOnScreen.length > 0) {
        const firstNote = notesOnScreen[0];
        if (note === firstNote.note) {
            message.textContent = "Correct! 🎉";
            message.style.color = "green";
            notesOnScreen.shift(); // Supprime la note si correcte
        } else {
            message.textContent = "Wrong! ❌";
            message.style.color = "red";
        }
    }
}

// Gestion des clics sur les boutons
buttons.forEach(button => {
    button.addEventListener('click', () => {
        const selectedNote = button.getAttribute('data-note');
        checkAnswer(selectedNote);
    });
});

// Boucle principale
function gameLoop() {
    drawStaff();
    drawNotes();
    updateNotes();

    // Ajouter une nouvelle note toutes les 3 secondes
    if (Math.random() < 0.01) {
        addNote();
    }

    requestAnimationFrame(gameLoop);
}

// Initialisation
drawStaff();
gameLoop();
