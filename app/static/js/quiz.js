// Game Configuration & State
let playerDeviceID = null;
let spotifyPlayer = null;
let quizData = null;
let currentRoundIndex = 0;
let lives = 2;

const gameContainer = document.getElementById("game-container");
const TOKEN = gameContainer.dataset.token;

// --- 1. INITIALIZE SPOTIFY ---
window.onSpotifyWebPlaybackSDKReady = () => {
  spotifyPlayer = new Spotify.Player({
    name: "Music Quiz Player",
    getOAuthToken: (cb) => {
      cb(TOKEN);
    },
    volume: 0.5,
  });

  spotifyPlayer.addListener("ready", ({ device_id }) => {
    playerDeviceID = device_id;
    document.getElementById("loading-msg").classList.add("hidden");
    document.getElementById("start-btn").classList.remove("hidden");
  });

  spotifyPlayer.connect();
};

// --- 2. FETCH QUIZ PACKAGE ---
async function fetchQuiz() {
  const response = await fetch("/api/get-quiz-package");
  quizData = await response.json();
}

// --- 3. GAME LOOP LOGIC ---
async function startGame() {
  await fetchQuiz();
  await spotifyPlayer.activateElement();

  document.getElementById("start-overlay").style.display = "none";
  document.getElementById("game-hud").classList.remove("hidden");

  await fetch(`/transfer/${playerDeviceID}`);
  loadRound();
}

function loadRound() {
  const round = quizData.rounds[currentRoundIndex];

  // Update UI
  document.getElementById("question-text").innerText = round.question;
  document.getElementById("round-display").innerText =
    `Round ${currentRoundIndex + 1}/5`;
  document.getElementById("music-icon").classList.add("animate-bounce");

  // Clear and build buttons
  const container = document.getElementById("options-container");
  container.innerHTML = "";

  round.options.forEach((option) => {
    const btn = document.createElement("button");
    btn.className =
      "option-btn bg-gray-700 hover:bg-gray-600 py-4 px-6 rounded-lg transition-colors font-semibold";
    btn.innerText = option;
    btn.onclick = () => handleAnswer(btn, option, round.correct_name);
    container.appendChild(btn);
  });

  // Play Song
  fetch(`/play/${playerDeviceID}/${round.track_uri}`);
}

function handleAnswer(selectedBtn, choice, correctAnswer) {
  const allBtns = document.querySelectorAll(".option-btn");
  allBtns.forEach((b) => (b.disabled = true));
  document.getElementById("music-icon").classList.remove("animate-bounce");

  if (choice === correctAnswer) {
    selectedBtn.classList.replace("bg-gray-700", "bg-green-500");
  } else {
    selectedBtn.classList.replace("bg-gray-700", "bg-red-500");
    lives--;
    updateLivesUI();
    allBtns.forEach((b) => {
      if (b.innerText.trim() === correctAnswer) b.classList.add("bg-green-500");
    });
  }

  setTimeout(() => {
    if (lives <= 0) {
      endGame(false);
    } else if (currentRoundIndex >= 4) {
      endGame(true);
    } else {
      currentRoundIndex++;
      loadRound();
    }
  }, 2000);
}

function updateLivesUI() {
  document.getElementById("lives-display").innerText = "❤️".repeat(lives);
}

function endGame(win) {
  spotifyPlayer.pause();
  const overlay = document.getElementById("start-overlay");
  overlay.style.display = "flex";
  document.getElementById("overlay-title").innerText = win
    ? "🏆 WINNER!"
    : "💀 GAME OVER";
  document.getElementById("overlay-msg").innerText = win
    ? "You named all 5 songs!"
    : "Better luck next time.";
  const btn = document.getElementById("start-btn");
  btn.innerText = "PLAY AGAIN";
  btn.onclick = () => location.reload();
}

// --- 4. VOLUME CONTROL ---
document.getElementById("volume-control").addEventListener("input", (e) => {
  if (spotifyPlayer) spotifyPlayer.setVolume(e.target.value / 100);
});

document.getElementById("start-btn").addEventListener("click", startGame);
