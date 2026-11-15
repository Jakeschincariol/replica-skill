"use strict";

const STORAGE_KEY = "stars-makers-demo-v1";
const AGE_KEY = "stars-makers-age-confirmed";
const songs = [
  { title: "Neon Hearts", artist: "Luna Vale", language: "FR", rating: "4.9", color: "pink", icon: "✧" },
  { title: "Velvet Sky", artist: "Juno Reed", language: "EN", rating: "4.8", color: "blue", icon: "◉" },
  { title: "Bajo la luna", artist: "Sol Maré", language: "ES", rating: "4.8", color: "orange", icon: "☼" },
  { title: "Paper Satellites", artist: "Kai North", language: "JP", rating: "4.7", color: "green", icon: "✳" },
  { title: "Echo Bloom", artist: "Nia Sol", language: "FR", rating: "4.6", color: "blue", icon: "❋" },
  { title: "Sakura Transit", artist: "Mika Miro", language: "JP", rating: "4.6", color: "pink", icon: "✿" },
  { title: "Golden Hourglass", artist: "Eli Nova", language: "EN", rating: "4.5", color: "orange", icon: "◌" },
];

const startingDuets = [
  { title: "Minuit électrique", pair: "Luna Vale · Tess R.", count: "42 duos", color: "pink" },
  { title: "Velvet Sky", pair: "Juno Reed · Alex M.", count: "28 duos", color: "blue" },
  { title: "Bajo la luna", pair: "Sol Maré · Camila J.", count: "19 duos", color: "orange" },
];

function loadState() {
  const initial = { credits: 12, contestJoined: false, duets: [], subscription: "" };
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (!saved || typeof saved !== "object") return initial;
    return {
      credits: Number.isInteger(saved.credits) && saved.credits >= 0 ? saved.credits : initial.credits,
      contestJoined: saved.contestJoined === true,
      duets: Array.isArray(saved.duets) ? saved.duets.filter((item) => item && typeof item.title === "string" && typeof item.pair === "string").slice(0, 20) : [],
      subscription: saved.subscription === "Plus" || saved.subscription === "Studio" ? saved.subscription : "",
    };
  } catch (error) {
    return initial;
  }
}

let state = loadState();
let confirmAction = null;
let previousFocus = null;

const byId = (id) => document.getElementById(id);
const modal = byId("action-modal");
const modalTitle = byId("action-title");
const modalDescription = byId("action-description");
const modalExtra = byId("action-extra");
const modalConfirm = byId("action-confirm");
const modalFootnote = byId("action-footnote");

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (error) {
    showToast("La démo continue, mais cette session ne peut pas être enregistrée sur cet appareil.");
  }
}

function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.textContent = message;
  byId("toast-region").append(toast);
  window.setTimeout(() => toast.remove(), 3500);
}

function updateCredits() {
  ["sidebar-credits", "top-credits", "gift-credits"].forEach((id) => {
    byId(id).textContent = String(state.credits);
  });
  document.querySelectorAll(".credit-pill").forEach((button) => {
    button.setAttribute("aria-label", `${state.credits} crédits démo, voir les abonnements`);
  });
}

function makeElement(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function renderSongs(query) {
  const list = byId("song-list");
  list.replaceChildren();
  const normalized = query.trim().toLocaleLowerCase();
  const matches = songs.filter((song) => `${song.title} ${song.artist} ${song.language}`.toLocaleLowerCase().includes(normalized));
  byId("clear-search").hidden = !normalized;

  if (matches.length === 0) {
    list.append(makeElement("p", "empty-search", "Aucun titre pour cette recherche. Essaie un autre mot ou une autre langue."));
    return;
  }

  matches.forEach((song) => {
    const row = makeElement("div", "song-row");
    const art = makeElement("span", `song-art ${song.color}`, song.icon);
    art.setAttribute("aria-hidden", "true");
    const main = makeElement("span", "song-main");
    main.append(makeElement("strong", "", song.title), makeElement("small", "", song.artist));
    const language = makeElement("span", "song-language", song.language);
    const rating = makeElement("span", "song-rating");
    rating.append(makeElement("span", "", "★"), document.createTextNode(` ${song.rating}`));
    const actions = makeElement("span", "song-actions");
    const sing = makeElement("button", "song-action", "♫");
    sing.type = "button";
    sing.dataset.sing = song.title;
    sing.setAttribute("aria-label", `Lancer une session démo pour ${song.title}`);
    const share = makeElement("button", "song-action song-share", "↗");
    share.type = "button";
    share.dataset.shareSong = song.title;
    share.setAttribute("aria-label", `Partager le titre démo ${song.title}`);
    actions.append(sing, share);
    row.append(art, main, language, rating, actions);
    list.append(row);
  });
}

function renderDuets() {
  const list = byId("duet-list");
  list.replaceChildren();
  const duets = [...state.duets.map((duet) => ({ ...duet, count: "nouveau duo", color: "pink" })), ...startingDuets].slice(0, 5);
  duets.forEach((duet) => {
    const row = makeElement("div", "duet-row");
    const art = makeElement("span", `duet-art ${duet.color}`, "♫");
    art.setAttribute("aria-hidden", "true");
    const info = makeElement("span", "duet-info");
    info.append(makeElement("strong", "", duet.title), makeElement("small", "", duet.pair));
    const count = makeElement("span", "duet-count", duet.count);
    const join = makeElement("button", "duet-join", "+");
    join.type = "button";
    join.dataset.duet = duet.pair.split(" · ")[0];
    join.dataset.song = duet.title;
    join.setAttribute("aria-label", `Créer un duo démo sur ${duet.title}`);
    row.append(art, info, count, join);
    list.append(row);
  });
}

function openModal({ icon = "♫", kicker = "TA SCÈNE", title, description, extra = "", confirm = "Continuer", footnote = "", handler }) {
  previousFocus = document.activeElement;
  confirmAction = handler;
  byId("action-icon").textContent = icon;
  byId("action-kicker").textContent = kicker;
  modalTitle.textContent = title;
  modalDescription.textContent = description;
  modalExtra.replaceChildren();
  if (typeof extra === "string") modalExtra.innerHTML = extra;
  else if (extra instanceof Node) modalExtra.append(extra);
  modalConfirm.innerHTML = `${confirm} <span aria-hidden="true">→</span>`;
  modalFootnote.textContent = footnote;
  modal.hidden = false;
  byId("modal-close").focus();
}

function closeModal() {
  modal.hidden = true;
  confirmAction = null;
  modalExtra.replaceChildren();
  if (previousFocus && typeof previousFocus.focus === "function") previousFocus.focus();
}

function startSing(songTitle) {
  openModal({
    icon: "♫",
    kicker: "STUDIO DE LA COMMUNAUTÉ",
    title: `Ta version de « ${songTitle} »`,
    description: "Le studio de cette démo ne capte pas de voix et ne diffuse pas de musique. Imagine ta performance, puis lance ta session fictive.",
    confirm: "Lancer la session démo",
    footnote: "Aucun micro utilisé · Aucun enregistrement créé",
    handler: () => {
      closeModal();
      showToast(`Session démo lancée : ${songTitle}. À toi d’imaginer la mélodie !`);
    },
  });
}

function inviteDuet(star, song) {
  openModal({
    icon: "♫",
    kicker: "INVITATION DE DUO",
    title: `À toi le refrain, avec ${star}.`,
    description: `Tu veux proposer un duo fictif sur « ${song} » ? L’invitation sera ajoutée à ta liste locale, sans être envoyée à une vraie personne.`,
    confirm: "Créer mon duo démo",
    footnote: "Artistes et titres entièrement imaginaires.",
    handler: () => {
      state.duets.unshift({ title: song, pair: `${star} · Toi` });
      saveState();
      renderDuets();
      closeModal();
      showToast(`Ton duo démo avec ${star} est dans ta liste.`);
    },
  });
}

function joinContest() {
  if (state.contestJoined) {
    showToast("Tu participes déjà au défi fictif de la semaine.");
    return;
  }
  openModal({
    icon: "✦",
    kicker: "DÉFI FICTIF",
    title: "Prends ta place sur scène.",
    description: "Rejoins la liste locale des participants au défi « Neon Hearts ». Aucun enregistrement ne sera envoyé ou publié.",
    confirm: "Rejoindre le défi démo",
    footnote: "Concours de démonstration · Aucun lot réel.",
    handler: () => {
      state.contestJoined = true;
      saveState();
      byId("contest-count").textContent = "129";
      document.querySelector("[data-join-contest]").textContent = "Tu participes déjà ✓";
      closeModal();
      showToast("Tu es inscrit·e au défi fictif. Bonne scène !");
    },
  });
}

function sendGift(cost, name) {
  if (state.credits < cost) {
    showToast("Pas assez de crédits démo pour ce cadeau. Découvre les abonnements simulés.");
    openSubscription();
    return;
  }
  openModal({
    icon: "✧",
    kicker: "CADEAU DE DÉMONSTRATION",
    title: `Envoyer ${name} ?`,
    description: `Ce cadeau fictif coûtera ${cost} crédits démo. L’envoi n’est visible que dans cette session et ne contacte personne.`,
    confirm: "Envoyer le cadeau démo",
    footnote: "Les crédits n’ont aucune valeur monétaire.",
    handler: () => {
      state.credits -= cost;
      saveState();
      updateCredits();
      closeModal();
      showToast(`${name} envoyé en démo. Il te reste ${state.credits} crédits.`);
    },
  });
}

async function shareSong(songTitle) {
  const url = new URL(window.location.href);
  url.searchParams.set("titre", songTitle);
  url.hash = "decouvrir";
  const shareData = { title: `Stars Makers · ${songTitle}`, text: `Découvre le titre fictif « ${songTitle} » sur Stars Makers.`, url: url.toString() };
  try {
    if (navigator.share) {
      await navigator.share(shareData);
    } else if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(shareData.url);
      showToast(`Lien de démo copié pour « ${songTitle} ».`);
    } else {
      openModal({
        icon: "↗",
        kicker: "PARTAGE DE DÉMONSTRATION",
        title: `Partager « ${songTitle} »`,
        description: "Ce lien ouvre la fiche du titre fictif dans Stars Makers.",
        extra: makeElement("p", "choice-option", shareData.url),
        confirm: "Compris",
        footnote: "Aucun extrait musical n’est partagé.",
        handler: closeModal,
      });
    }
  } catch (error) {
    if (error.name !== "AbortError") showToast("Le partage n’a pas abouti. Tu peux réessayer.");
  }
}

function openSubscription() {
  openModal({
    icon: "✦",
    kicker: "ABONNEMENTS · MODE DÉMO",
    title: "Plus de place pour briller.",
    description: "Choisis une formule fictive. L’activation ajoute des crédits de démonstration, sans achat ni renouvellement.",
    extra: `<div class="choice-grid">
      <button class="choice-option selected" type="button" data-plan="Plus" data-credits="120" aria-pressed="true"><span><strong>Plus</strong><br><small>4,99 € / mois · prix fictif</small></span><span>+120 ✦</span></button>
      <button class="choice-option" type="button" data-plan="Studio" data-credits="350" aria-pressed="false"><span><strong>Studio</strong><br><small>9,99 € / mois · prix fictif</small></span><span>+350 ✦</span></button>
    </div>`,
    confirm: "Activer Plus (simulation)",
    footnote: "Aucun paiement, abonnement ou renouvellement ne sera créé.",
    handler: () => {
      const selected = modalExtra.querySelector(".choice-option.selected");
      if (!selected) return;
      state.credits += Number(selected.dataset.credits);
      state.subscription = selected.dataset.plan;
      saveState();
      updateCredits();
      closeModal();
      showToast(`Formule ${state.subscription} simulée : tes crédits démo sont prêts.`);
    },
  });
}

function showProfile() {
  const details = document.createElement("div");
  [["Âge requis", "18+"], ["Formule démo", state.subscription || "Aucune"]].forEach(([label, value]) => {
    const row = makeElement("div", "choice-option");
    row.append(makeElement("span", "", label), makeElement("strong", "", value));
    details.append(row);
  });
  openModal({
    icon: "M",
    kicker: "TON ESPACE",
    title: "Bienvenue sur ta scène.",
    description: "Profil local de démonstration. Pas de compte, de photo, de classement personnel ou de données envoyées à un serveur.",
    extra: details,
    confirm: "Fermer mon profil",
    footnote: "Les choix de cette démo sont enregistrés uniquement sur cet appareil.",
    handler: closeModal,
  });
}

function handleClick(event) {
  const target = event.target.closest("button, a");
  if (!target) return;
  if (target.hasAttribute("data-close-modal")) return closeModal();
  if (target.hasAttribute("data-open-subscription")) return openSubscription();
  if (target.hasAttribute("data-open-profile")) return showProfile();
  if (target.hasAttribute("data-go")) {
    const section = byId(target.dataset.go);
    section?.scrollIntoView({ behavior: "smooth" });
    return;
  }
  if (target.dataset.sing) return startSing(target.dataset.sing);
  if (target.dataset.shareSong) return shareSong(target.dataset.shareSong);
  if (target.dataset.duet) return inviteDuet(target.dataset.duet, target.dataset.song || "Minuit électrique");
  if (target.hasAttribute("data-join-contest")) return joinContest();
  if (target.hasAttribute("data-gift")) return sendGift(Number(target.dataset.gift), target.dataset.giftName);
  if (target.hasAttribute("data-show-duets")) {
    byId("duos").scrollIntoView({ behavior: "smooth" });
    return showToast("Choisis un duo et ajoute ta voix à la liste locale.");
  }
}

byId("age-confirm").addEventListener("change", (event) => {
  byId("enter-app").disabled = !event.target.checked;
});

byId("enter-app").addEventListener("click", () => {
  if (!byId("age-confirm").checked) return;
  try {
    localStorage.setItem(AGE_KEY, "true");
  } catch (error) {
    showToast("La confirmation d’âge ne sera conservée que pendant cette visite.");
  }
  document.querySelector(".app-shell").inert = false;
  byId("age-gate").hidden = true;
  document.querySelector(".hero .button-primary").focus();
});

document.addEventListener("click", handleClick);
modalConfirm.addEventListener("click", () => {
  if (typeof confirmAction === "function") confirmAction();
});
modalExtra.addEventListener("click", (event) => {
  const option = event.target.closest("[data-plan]");
  if (!option) return;
  modalExtra.querySelectorAll("[data-plan]").forEach((item) => {
    item.classList.toggle("selected", item === option);
    item.setAttribute("aria-pressed", String(item === option));
  });
  modalConfirm.innerHTML = `Activer ${option.dataset.plan} (simulation) <span aria-hidden="true">→</span>`;
});
modal.addEventListener("click", (event) => {
  if (event.target === modal) closeModal();
});
document.addEventListener("keydown", (event) => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
    event.preventDefault();
    byId("search-input").focus();
  }
  if (event.key === "Escape" && !modal.hidden) closeModal();
  if (event.key === "Tab" && !modal.hidden) {
    const focusable = [...modal.querySelectorAll("button:not(:disabled), input:not(:disabled), [href], [tabindex]:not([tabindex='-1'])")];
    if (focusable.length < 2) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }
});
byId("search-input").addEventListener("input", (event) => renderSongs(event.target.value));
byId("clear-search").addEventListener("click", () => {
  byId("search-input").value = "";
  byId("search-input").focus();
  renderSongs("");
});

function initialize() {
  updateCredits();
  const sharedSong = new URLSearchParams(window.location.search).get("titre") || "";
  byId("search-input").value = sharedSong;
  renderSongs(sharedSong);
  renderDuets();
  if (state.contestJoined) {
    byId("contest-count").textContent = "129";
    document.querySelector("[data-join-contest]").textContent = "Tu participes déjà ✓";
  }
  try {
    if (localStorage.getItem(AGE_KEY) === "true") byId("age-gate").hidden = true;
  } catch (error) {
    byId("age-gate").hidden = false;
  }
  if (!byId("age-gate").hidden) {
    document.querySelector(".app-shell").inert = true;
    byId("age-confirm").focus();
  }
}

initialize();
