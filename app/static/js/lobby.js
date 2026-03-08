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
    const query = searchInput.value;
    const artistId = idInput.value; // Grab the ID we saved

    if (!query) {
      alert("Please select an artist!");
      return;
    }

    // Pass both name and ID for maximum reliability
    artistParam = `&artist=${encodeURIComponent(query)}&artist_id=${artistId}&mode=single`;
  } else {
    const count = document.getElementById("collection-limit").value;
    artistParam = `&pool_size=${count}&mode=collection`;
  }

  const url = `/game?type={{ game_type }}&limit=${roundLimit}&diff=${difficulty}${artistParam}`;
  window.location.href = url;
}
let debounceTimer;
const searchInput = document.getElementById("artist-query");
const resultsDiv = document.getElementById("search-results");
const idInput = document.getElementById("selected-artist-id");

searchInput.addEventListener("input", (e) => {
  clearTimeout(debounceTimer);
  const query = e.target.value;

  if (query.length < 2) {
    resultsDiv.classList.add("hidden");
    return;
  }

  debounceTimer = setTimeout(async () => {
    const response = await fetch(
      `/api/search-artist?q=${encodeURIComponent(query)}`,
    );
    const artists = await response.json();

    if (artists.length > 0) {
      resultsDiv.innerHTML = artists
        .map(
          (a) => `
                <div class="flex items-center p-3 hover:bg-gray-700 cursor-pointer border-b border-gray-700 last:border-0" 
                     onclick="selectArtist('${a.name}', '${a.id}')">
                    <img src="${a.image}" class="w-10 h-10 rounded-full mr-3 object-cover">
                    <span class="font-bold">${a.name}</span>
                </div>
            `,
        )
        .join("");
      resultsDiv.classList.remove("hidden");
    } else {
      resultsDiv.classList.add("hidden");
    }
  }, 300); // Wait 300ms after user stops typing
});

function selectArtist(name, id) {
  searchInput.value = name;
  idInput.value = id;
  resultsDiv.classList.add("hidden");
}
