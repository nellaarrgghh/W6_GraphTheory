const formNodes = document.querySelectorAll(".solver-form");
const boardNode = document.getElementById("board");
const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

// Leaflet Map Initialization for Task 2
const mapContainer = document.getElementById("map-task2");
let task2Map = null;
let task2LayerGroup = null;

if (mapContainer) {
  task2Map = L.map('map-task2').setView([-7.2825, 112.7944], 14);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(task2Map);
  task2LayerGroup = L.layerGroup().addTo(task2Map);
}

formNodes.forEach((formNode) => {
  const radiusNode = formNode.querySelector("[name=radius_km]");
  if (radiusNode) {
    radiusNode.addEventListener("input", () => {
      formNode.querySelector("output").textContent = `${radiusNode.value} km`;
    });
  }

  formNode.addEventListener("submit", async (event) => {
    event.preventDefault();
    const routeType = formNode.dataset.task;
    
    if (routeType === "task2") {
      const locationInput = formNode.elements.location.value.split(",").map(Number);
      const payload = { lat: locationInput[0], lng: locationInput[1], radius_km: Number(radiusNode.value) };
      
      formNode.parentElement.querySelector(".solver-status").textContent = "Solving Directed Chinese Postman Problem...";
      
      const routeReply = await fetch(`/api/task2/solve`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
      });
      const routeState = await routeReply.json();
      
      formNode.parentElement.querySelector(".solver-status").textContent = routeState.status;
      
      if (routeState.status === "Solved") {
        document.getElementById("t2-distance").textContent = `${routeState.total_distance_km} km`;
        document.getElementById("t2-time").textContent = `${routeState.est_time_mins} mins`;
        document.getElementById("t2-exec").textContent = `${routeState.exec_time_sec} s`;
        
        const orderList = routeState.street_order.join(", ");
        document.getElementById("t2-order").textContent = orderList;

        if (task2Map && task2LayerGroup) {
          task2LayerGroup.clearLayers();
          task2Map.setView(routeState.base, 14);

          // Add base marker
          L.marker(routeState.base).addTo(task2LayerGroup)
            .bindPopup("DLH Dump Truck Base")
            .openPopup();

          // Add route polylines
          if (routeState.route_coords && routeState.route_coords.length > 0) {
            L.polyline(routeState.route_coords, { color: 'blue', weight: 4, opacity: 0.8 }).addTo(task2LayerGroup);
          }
        }
      }
    }
  });
});

if (boardNode) {
  const tourStatus = document.getElementById("tour-status");
  const tourOrder = document.getElementById("tour-order");
  const tourEndpoints = document.getElementById("tour-endpoints");
  const tourTime = document.getElementById("tour-time");
  const animationSpeed = document.getElementById("animation-speed");
  const animationDelays = { slow: 220, normal: 65, fast: 15 };
  let start = [2, 2];
  let animationId = 0;

  for (let row = 0; row < 8; row += 1) {
    for (let col = 0; col < 8; col += 1) {
      const square = document.createElement("button");
      square.type = "button";
      square.className = `square ${(col + row) % 2 ? "dark" : "light"}`;
      square.dataset.col = col;
      square.dataset.row = row;
      square.setAttribute("aria-label", `Column ${col}, row ${row}`);
      boardNode.append(square);
    }
  }

  const squareAt = (col, row) => boardNode.querySelector(`[data-col="${col}"][data-row="${row}"]`);
  const clearBoard = () => boardNode.querySelectorAll(".square").forEach((square) => {
    square.classList.remove("selected", "start-point", "end-point");
    square.replaceChildren();
  });
  const showStart = () => {
    clearBoard();
    const square = squareAt(start[0], start[1]);
    square.classList.add("selected", "start-point");
    const knight = document.createElement("img");
    knight.className = "knight-piece";
    knight.src = "/static/knight.jpg";
    knight.alt = "knight";
    square.append(knight);
  };
  const showOrder = (path) => {
    tourOrder.replaceChildren();
    path.forEach(([col, row]) => {
      const move = document.createElement("li");
      move.textContent = `(${col}, ${row})`;
      tourOrder.append(move);
    });
  };
  const animateTour = async (path, token) => {
    for (let index = 0; index < path.length; index += 1) {
      if (token !== animationId) return;
      const [col, row] = path[index];
      const square = squareAt(col, row);
      const number = document.createElement("span");
      number.textContent = index + 1;
      square.replaceChildren(number);
      square.classList.toggle("start-point", index === 0);
      square.classList.toggle("end-point", index === path.length - 1);
      const knight = document.createElement("img");
      knight.className = "knight-piece";
      knight.src = "/static/knight.jpg";
      knight.alt = "knight";
      square.append(knight);
      await wait(animationDelays[animationSpeed.value]);
      if (index !== path.length - 1) knight.remove();
    }
  };
  boardNode.addEventListener("click", (event) => {
    const square = event.target.closest(".square");
    if (!square) return;
    animationId += 1;
    start = [Number(square.dataset.col), Number(square.dataset.row)];
    showStart();
    tourStatus.textContent = `Start: ${start[0]},${start[1]}`;
    tourEndpoints.textContent = `Starting point: (${start[0]}, ${start[1]})`;
    tourOrder.textContent = "";
    tourTime.textContent = "";
  });
  document.getElementById("solve-tour").addEventListener("click", async () => {
    const token = ++animationId;
    clearBoard();
    tourStatus.textContent = "Solving...";
    const requestReply = await fetch("/api/task3/solve", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cols: 8, rows: 8, start_col: start[0], start_row: start[1] }),
    });
    const tourState = await requestReply.json();
    tourTime.textContent = `Execution time: ${tourState.execution_time_ms.toFixed(3)} ms`;
    tourStatus.textContent = tourState.found ? "Solved" : "path not found";
    if (!tourState.found) {
      tourEndpoints.textContent = "";
      tourOrder.replaceChildren();
      return;
    }
    const firstSquare = tourState.path[0];
    const lastSquare = tourState.path[tourState.path.length - 1];
    tourEndpoints.textContent = `Starting point: (${firstSquare[0]}, ${firstSquare[1]}) | Final point: (${lastSquare[0]}, ${lastSquare[1]})`;
    showOrder(tourState.path);
    await animateTour(tourState.path, token);
  });
  document.getElementById("reset-tour").addEventListener("click", () => {
    animationId += 1;
    start = [2, 2];
    showStart();
    tourStatus.textContent = "Choose a starting square.";
    tourEndpoints.textContent = `Starting point: (${start[0]}, ${start[1]})`;
    tourOrder.replaceChildren();
    tourTime.textContent = "";
  });
  showStart();
  tourEndpoints.textContent = `Starting point: (${start[0]}, ${start[1]})`;
}
