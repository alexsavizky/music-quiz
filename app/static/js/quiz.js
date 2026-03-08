// Game Configuration & State
let playerDeviceID = null;
let spotifyPlayer = null;
let quizData = null;
let currentRoundIndex = 0;
let lives = 2;

// --- NEW: Grab settings from URL (Sent by lobby.js) ---
const urlParams = new URLSearchParams(window.location.search);
const gameType = urlParams.get("type") || "name_that_tune";

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

// --- 2. FETCH DYNAMIC QUIZ PACKAGE ---
async function fetchQuiz() {
  // We append the current URL's search params (limit, diff, mode, etc.)
  // to the API call so the backend knows what to generate.
  const response = await fetch(`/api/get-quiz-package?${urlParams.toString()}`);
  quizData = await response.json();
}

// --- 3. GAME LOOP LOGIC ---
async function startGame() {
  await fetchQuiz();

  if (!quizData || quizData.rounds.length === 0) {
    alert("Could not generate quiz. Try a different artist or settings.");
    window.location.href = "/";
    return;
  }

  await spotifyPlayer.activateElement();
  document.getElementById("start-overlay").style.display = "none";
  document.getElementById("game-hud").classList.remove("hidden");

  await fetch(`/transfer/${playerDeviceID}`);
  loadRound();
}

function loadRound() {
  const round = quizData.rounds[currentRoundIndex];
  const totalRounds = quizData.rounds.length;

  // Update UI Dynamically
  document.getElementById("question-text").innerText = round.question;
  document.getElementById("round-display").innerText =
    `Round ${currentRoundIndex + 1}/${totalRounds}`;
  document.getElementById("music-icon").classList.add("animate-bounce");
  updateLivesUI();

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
  fetch(`/play/${playerDeviceID}/${round.track_uri}/${round.start_at_ms}`);
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
    } else if (currentRoundIndex >= quizData.rounds.length - 1) {
      endGame(true);
    } else {
      currentRoundIndex++;
      loadRound();
    }
  }, 2000);
}

function updateLivesUI() {
  document.getElementById("lives-display").innerText = "❤️".repeat(
    Math.max(0, lives),
  );
}

function endGame(win) {
  spotifyPlayer.pause();
  const overlay = document.getElementById("start-overlay");
  overlay.style.display = "flex";

  document.getElementById("overlay-title").innerText = win
    ? "🏆 WINNER!"
    : "💀 GAME OVER";
  document.getElementById("overlay-msg").innerText = win
    ? `Impressive! You finished all ${quizData.rounds.length} rounds.`
    : "You ran out of lives!";

  const btn = document.getElementById("start-btn");
  btn.innerText = "RETURN TO MENU";
  btn.classList.replace("bg-green-500", "bg-white");
  btn.classList.replace("text-white", "text-black");

  btn.onclick = () => {
    window.location.href = "/";
  };
}

// Volume & Start Listeners
document.getElementById("volume-control").addEventListener("input", (e) => {
  if (spotifyPlayer) spotifyPlayer.setVolume(e.target.value / 100);
});

document.getElementById("start-btn").addEventListener("click", startGame);
