// Task 1 page: map, school preview and route results.
const form = document.getElementById("task1-form");
const locationInput = form.elements.location;
const radiusInput = form.elements.radius_km;
const button = form.querySelector("button");
const statusText = document.getElementById("task1-status");
const previewText = document.getElementById("task1-preview");

let map = null;
let sppgMarker = null;
let radiusCircle = null;
let schoolLayer = null;
let roadLayer = null;
let routeLayer = null;
let previewTimer = null;
// Goes up on every change, so an old slow response can't overwrite a newer one.
let requestId = 0;

function cssColor(name) {
  return getComputedStyle(document.body).getPropertyValue(name).trim();
}

function fixed(value, digits) {
  return typeof value === "number" ? value.toFixed(digits) : "-";
}

function readInputs() {
  const parts = locationInput.value.split(",");
  const lat = Number(parts[0]);
  const lng = Number(parts[1]);
  const radius = Number(radiusInput.value);
  if (parts.length !== 2 || !Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) {
    return null;
  }
  return { lat: lat, lng: lng, radius_km: radius };
}

function clearResults() {
  ["order", "distance", "eta", "solver-time"].forEach((id) => {
    document.getElementById(`task1-${id}`).textContent = "-";
  });
  if (routeLayer) routeLayer.clearLayers();
}

async function getJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok || data.status !== "success") {
    throw new Error(data.message || `Request failed (HTTP ${response.status})`);
  }
  return data;
}

function drawSchools(schools) {
  if (!map) return;
  schoolLayer.clearLayers();
  schools.forEach((school) => {
    const popup = document.createElement("div");
    popup.textContent = `${school.name} (${school.id})`;
    L.circleMarker([school.lat, school.lng], {
      radius: 6, color: cssColor("--card-2-heading"), fillColor: cssColor("--card-2-border"), fillOpacity: 0.9,
    }).bindPopup(popup).addTo(schoolLayer);
  });
}

async function previewSchools() {
  const input = readInputs();
  if (!input) {
    previewText.textContent = "Type the location as: latitude, longitude";
    return;
  }
  const myId = ++requestId;
  previewText.textContent = "Loading schools inside the radius...";
  try {
    const data = await getJson(`/api/task1/schools?${new URLSearchParams(input)}`);
    if (myId !== requestId) return;
    drawSchools(data.schools);
    if (map) {
      roadLayer.clearLayers();
      roadLayer.addData(data.roads);
    }
    let message = `${data.schools.length} schools inside ${input.radius_km} km. Source: ${data.source}.`;
    if (data.schools.length > data.max_schools) {
      message += ` That is more than ${data.max_schools}, make the radius smaller.`;
    }
    if (data.roads_cut) message += " Only some of the grey roads are drawn.";
    previewText.textContent = message;
  } catch (error) {
    if (myId === requestId) previewText.textContent = `Could not load schools: ${error.message}`;
  }
}

function onInputChange() {
  document.getElementById("task1-radius-value").textContent = `${radiusInput.value} km`;
  requestId++;
  clearResults();
  statusText.textContent = "Inputs changed. Press Find Route.";
  const input = readInputs();
  if (map && input) {
    sppgMarker.setLatLng([input.lat, input.lng]);
    radiusCircle.setLatLng([input.lat, input.lng]).setRadius(input.radius_km * 1000);
  }
  // Wait a bit so moving the slider doesn't send a request for every step.
  clearTimeout(previewTimer);
  previewTimer = setTimeout(previewSchools, 300);
}

function showResult(data) {
  const names = data.school_order.map((school) => school.name);
  document.getElementById("task1-order").textContent = ["SPPG", ...names, "SPPG"].join(" -> ");
  document.getElementById("task1-distance").textContent = `${fixed(data.total_distance_km, 3)} km`;
  document.getElementById("task1-eta").textContent = `${fixed(data.total_time_min, 2)} min`;
  document.getElementById("task1-solver-time").textContent = `${fixed(data.solver_time_ms, 3)} ms`;
  statusText.textContent = data.schools_count
    ? `Route found for all ${data.schools_count} schools.`
    : "No schools inside the radius.";

  if (map) {
    drawSchools(data.school_order);
    if (data.polyline.length > 1) {
      const line = L.polyline(data.polyline, { color: cssColor("--card-1-heading"), weight: 5 }).addTo(routeLayer);
      map.fitBounds(line.getBounds(), { padding: [24, 24] });
    }
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = readInputs();
  if (!input) {
    statusText.textContent = "Type the location as: latitude, longitude";
    return;
  }
  const myId = ++requestId;
  clearTimeout(previewTimer);
  clearResults();
  button.disabled = true;
  statusText.textContent = "Finding the route...";
  try {
    const data = await getJson("/api/task1/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    if (myId === requestId) showResult(data);
  } catch (error) {
    if (myId === requestId) statusText.textContent = `No route: ${error.message}`;
  } finally {
    button.disabled = false;
  }
});

locationInput.addEventListener("change", onInputChange);
radiusInput.addEventListener("input", onInputChange);

function setLocation(latlng) {
  locationInput.value = `${latlng.lat.toFixed(6)}, ${latlng.lng.toFixed(6)}`;
  onInputChange();
}

function setupMap() {
  const container = document.getElementById("task1-map");
  // The page still works without the map, for example if the CDN is blocked.
  if (!window.L) {
    container.textContent = "Map could not load. You can still type a location below.";
    return;
  }
  container.replaceChildren();
  const start = [-7.2825, 112.7944];
  map = L.map(container).setView(start, 14);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors",
  }).addTo(map);
  roadLayer = L.geoJSON(null, { style: { color: cssColor("--text-light"), weight: 2, opacity: 0.5 }, interactive: false }).addTo(map);
  radiusCircle = L.circle(start, { radius: 1000, color: cssColor("--card-1-heading"), fillOpacity: 0.1, interactive: false }).addTo(map);
  schoolLayer = L.layerGroup().addTo(map);
  routeLayer = L.layerGroup().addTo(map);
  sppgMarker = L.marker(start, {
    draggable: true,
    title: "SPPG (drag to move)",
    icon: L.divIcon({ className: "task1-facility-icon", html: "S", iconSize: [28, 28] }),
  }).addTo(map);
  sppgMarker.on("dragend", () => setLocation(sppgMarker.getLatLng()));
  map.on("click", (event) => setLocation(event.latlng));
}

setupMap();
previewSchools();
