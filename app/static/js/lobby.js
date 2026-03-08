let selectedDifficulty = "mid";
let artistMode = "single"; // Default mode
function selectDiff(btn, val) {
  selectedDifficulty = val;
  document.querySelectorAll(".diff-btn").forEach((b) => {
    b.classList.replace("bg-green-500", "bg-gray-700");
    b.classList.remove("text-black");
  });
  btn.classList.replace("bg-gray-700", "bg-green-500");
  btn.classList.add("text-black");
}

function toggleArtistMode(mode) {
  artistMode = mode;
  const singleSection = document.getElementById("section-single");
  const collectionSection = document.getElementById("section-collection");
  const btnS = document.getElementById("btn-single");
  const btnC = document.getElementById("btn-collection");

  if (mode === "single") {
    singleSection.classList.remove("hidden");
    collectionSection.classList.add("hidden");
    btnS.className =
      "mode-btn flex-1 py-2 rounded-lg font-bold bg-green-500 text-black";
    btnC.className = "mode-btn flex-1 py-2 rounded-lg font-bold text-gray-400";
  } else {
    singleSection.classList.add("hidden");
    collectionSection.classList.remove("hidden");
    btnC.className =
      "mode-btn flex-1 py-2 rounded-lg font-bold bg-green-500 text-black";
    btnS.className = "mode-btn flex-1 py-2 rounded-lg font-bold text-gray-400";
  }
}

function launch() {
  const roundLimit = document.getElementById("limit").value;
  const difficulty = selectedDifficulty; // From previous step

  let artistParam = "";
  if (artistMode === "single") {
    const query = document.getElementById("artist-query").value;
    if (!query) {
      alert("Please enter an artist name!");
      return;
    }
    artistParam = `&artist=${encodeURIComponent(query)}&mode=single`;
  } else {
    const count = document.getElementById("collection-limit").value;
    artistParam = `&pool_size=${count}&mode=collection`;
  }

  const url = `/game?type={{ game_type }}&limit=${roundLimit}&diff=${difficulty}${artistParam}`;
  window.location.href = url;
}
