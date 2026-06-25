const lookupState = {
  mons: [],
  selectedMon: null,
};

const lookupElements = {};

const normalizeName = (value) => value.trim().toLowerCase().replace(/\s+/g, " ");

const escapeHtml = (value) =>
  String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");

const setStatus = (message) => {
  lookupElements.status.textContent = message;
};

const renderEmptyState = (message) => {
  lookupElements.result.innerHTML = `<div class="lookup-empty-state">${escapeHtml(message)}</div>`;
};

const renderMatches = (matches, query) => {
  if (matches.length <= 1) {
    lookupElements.matches.classList.add("is-hidden");
    lookupElements.matches.innerHTML = "";
    return;
  }

  const buttons = matches
    .slice(0, 12)
    .map(
      (mon) =>
        `<button class="lookup-match-button" type="button" data-mon-name="${escapeHtml(mon.name)}">${escapeHtml(mon.name)}</button>`
    )
    .join("");

  lookupElements.matches.classList.remove("is-hidden");
  lookupElements.matches.innerHTML = `
    <h3 class="lookup-matches-title">Multiple matches for &quot;${escapeHtml(query)}&quot;</h3>
    <div class="lookup-match-list">${buttons}</div>
  `;
};

const renderMon = (mon) => {
  lookupElements.result.innerHTML = `
    <article class="lookup-card">
      <div class="lookup-card-header">
        <div class="lookup-sprite">
          <img src="${escapeHtml(mon.sprite)}" alt="${escapeHtml(mon.name)} sprite" />
        </div>
        <div class="lookup-title">
          <h2>${escapeHtml(mon.name)}</h2>
          <p>Single-mon stat card</p>
        </div>
      </div>

      <div class="lookup-stats">
        <div class="lookup-stat"><span class="lookup-stat-label">Points</span><span class="lookup-stat-value">${mon.points}</span></div>
        <div class="lookup-stat"><span class="lookup-stat-label">Games played</span><span class="lookup-stat-value">${mon.gamesPlayed}</span></div>
        <div class="lookup-stat"><span class="lookup-stat-label">Winrate</span><span class="lookup-stat-value">${mon.winrate}%</span></div>
        <div class="lookup-stat"><span class="lookup-stat-label">Kills</span><span class="lookup-stat-value">${mon.kills}</span></div>
        <div class="lookup-stat"><span class="lookup-stat-label">Deaths</span><span class="lookup-stat-value">${mon.deaths}</span></div>
        <div class="lookup-stat"><span class="lookup-stat-label">Diff</span><span class="lookup-stat-value">${mon.diff}</span></div>
        <div class="lookup-stat"><span class="lookup-stat-label">KPG</span><span class="lookup-stat-value">${mon.kpg}</span></div>
      </div>
    </article>
  `;
};

const searchMon = (rawQuery) => {
  const query = rawQuery.trim();

  if (!query) {
    lookupState.selectedMon = null;
    renderMatches([], query);
    renderEmptyState("Start typing a name to load a mon card.");
    setStatus(`Loaded ${lookupState.mons.length} mons.`);
    return;
  }

  const normalizedQuery = normalizeName(query);
  const exactMatch = lookupState.mons.find((mon) => normalizeName(mon.name) === normalizedQuery);

  if (exactMatch) {
    lookupState.selectedMon = exactMatch;
    renderMon(exactMatch);
    renderMatches([exactMatch], query);
    setStatus(`Showing ${exactMatch.name}.`);
    return;
  }

  const partialMatches = lookupState.mons.filter((mon) => normalizeName(mon.name).includes(normalizedQuery));

  if (partialMatches.length === 0) {
    lookupState.selectedMon = null;
    renderMatches([], query);
    renderEmptyState(`No mon found for "${query}".`);
    setStatus(`No matches for ${query}.`);
    return;
  }

  lookupState.selectedMon = partialMatches[0];
  renderMon(partialMatches[0]);
  renderMatches(partialMatches, query);
  setStatus(`Showing ${partialMatches[0].name}.`);
};

const initializeLookup = async () => {
  lookupElements.form = document.getElementById("lookup-form");
  lookupElements.input = document.getElementById("mon-query");
  lookupElements.status = document.getElementById("lookup-status");
  lookupElements.result = document.getElementById("lookup-result");
  lookupElements.matches = document.getElementById("lookup-matches");
  lookupElements.names = document.getElementById("mon-names");

  try {
    lookupState.mons = Array.isArray(window.DRAFT_DB_MON_DATA) ? window.DRAFT_DB_MON_DATA : [];

    lookupElements.names.innerHTML = lookupState.mons
      .map((mon) => `<option value="${escapeHtml(mon.name)}"></option>`)
      .join("");

    setStatus(`Loaded ${lookupState.mons.length} mons.`);
    renderEmptyState("Start typing a name to load a mon card.");
    searchMon(lookupElements.input.value);
  } catch (error) {
    console.error(error);
    setStatus("Could not load mon data.");
    renderEmptyState("Unable to load the mon list right now.");
  }

  lookupElements.form.addEventListener("submit", (event) => {
    event.preventDefault();
    searchMon(lookupElements.input.value);
  });

  lookupElements.input.addEventListener("input", () => {
    searchMon(lookupElements.input.value);
  });

  lookupElements.matches.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-mon-name]");
    if (!button) {
      return;
    }

    lookupElements.input.value = button.dataset.monName || "";
    searchMon(lookupElements.input.value);
    lookupElements.input.focus();
  });
};

document.addEventListener("DOMContentLoaded", initializeLookup);