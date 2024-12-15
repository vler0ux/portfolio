const canvas = document.getElementById("staff");
const ctx = canvas.getContext("2d");

const lineSpacing = 20; // Spacing between staff lines
const numberOfLines = 5; // Number of staff lines
const noteRadius = 10; // Radius of the notes
const notes = []; // Array to hold the notes
const errorSound = new Audio('note/error.mp3');
const noteSounds = {
    DO: new Audio('note/do.mp3'),
    RE: new Audio('note/re.mp3'),
    MI: new Audio('note/mi.mp3'),
    FA: new Audio('note/fa.mp3'),
    SOL: new Audio('note/sol.mp3')
};

// Draw the staff
function drawStaff() {
    ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
    ctx.strokeStyle = "black";
    ctx.lineWidth = 2;

    for (let i = 0; i < numberOfLines; i++) {
        const y = 50 + i * lineSpacing;
        ctx.beginPath();
        ctx.moveTo(50, y);
        ctx.lineTo(canvas.width - 50, y);
        ctx.stroke();
    }
}

// Create a new note at a random position
function createNote() {
    const positions = [50, 70, 90, 110, 130]; // Positions corresponding to the staff lines
    const y = positions[Math.floor(Math.random() * positions.length)];
    notes.push({ x: canvas.width - 50, y: y }); // Add a note starting from the right
}

// Draw and animate the notes
function animateNotes() {
    drawStaff(); // Redraw the staff

    // Draw each note
    notes.forEach((note, index) => {
        ctx.beginPath();
        ctx.arc(note.x, note.y, noteRadius, 0, Math.PI * 2);
        ctx.fillStyle = "black";
        ctx.fill();
        ctx.closePath();

        // Move the note to the left
        note.x -= 1;

        // Remove notes that have moved off the canvas
        if (note.x + noteRadius < 0) {
            notes.splice(index, 1);
        }
    });

    // Request the next frame
    requestAnimationFrame(animateNotes);
}

document.querySelectorAll(".note-buttons button").forEach(button => {
    button.addEventListener("click", (e) => {
        const noteName = e.target.dataset.note;

        // Vérifie si une note sur la portée correspond au bouton
        const matchingNoteIndex = notes.findIndex(note => note.name === noteName && note.x > 50);
        
        if (matchingNoteIndex !== -1) {
            noteSounds[noteName].play(); // Jouer le son correspondant
        } else {
            errorSound.play();        }
    });
});


// Start the animation and create notes at intervals
function startGame() {
    setInterval(createNote, 2000); // Create a new note every second
    animateNotes(); // Start animating
}


// Start the game
startGame();
