const formNodes = document.querySelectorAll(".solver-form");
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

const tourForm = document.getElementById("tour-form");
if (tourForm) {
  const tourError = document.getElementById("tour-error");
  const boardContainer = document.getElementById("board-container");
  const boardArea = document.getElementById("board-area");
  const boardNode = document.getElementById("board");
  const rowLabelsNode = document.getElementById("row-labels");
  const colLabelsNode = document.getElementById("col-labels");
  const solveBtn = document.getElementById("solve-tour");
  const resetBtn = document.getElementById("reset-tour");
  const tourStatus = document.getElementById("tour-status");
  const tourTime = document.getElementById("tour-time");
  const tourOrder = document.getElementById("tour-order");

  let storedOutcome = null;
  let animationToken = 0;

  const squareAt = (col, row) => boardNode.querySelector(`[data-col="${col}"][data-row="${row}"]`);

  const createKnight = () => {
    const knightImg = document.createElement("img");
    knightImg.className = "knight-piece";
    knightImg.src = "/static/knight.jpg";
    knightImg.alt = "knight";
    return knightImg;
  };

  const drawBoard = (cols, rows, startCol, startRow) => {
    boardArea.style.setProperty("--cols", cols);
    boardArea.style.setProperty("--rows", rows);
    boardNode.style.setProperty("--cols", cols);

    rowLabelsNode.replaceChildren();
    for (let row = 0; row < rows; row += 1) {
      const label = document.createElement("span");
      label.textContent = row;
      rowLabelsNode.append(label);
    }

    colLabelsNode.replaceChildren();
    for (let col = 0; col < cols; col += 1) {
      const label = document.createElement("span");
      label.textContent = col;
      colLabelsNode.append(label);
    }

    boardNode.replaceChildren();
    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < cols; col += 1) {
        const square = document.createElement("div");
        square.className = `square ${(col + row) % 2 ? "dark" : "light"}`;
        square.dataset.col = col;
        square.dataset.row = row;
        boardNode.append(square);
      }
    }

    const startSquare = squareAt(startCol, startRow);
    if (startSquare) {
      startSquare.append(createKnight());
    }

    boardContainer.hidden = false;
    solveBtn.hidden = false;
    solveBtn.disabled = false;
  };

  const resetAll = () => {
    animationToken += 1;
    storedOutcome = null;
    boardNode.replaceChildren();
    rowLabelsNode.replaceChildren();
    colLabelsNode.replaceChildren();
    boardContainer.hidden = true;
    solveBtn.hidden = true;
    solveBtn.disabled = false;
    tourError.textContent = "";
    tourError.hidden = true;
    tourStatus.textContent = "";
    tourTime.textContent = "";
    tourOrder.replaceChildren();
    tourForm.reset();
  };

  tourForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    animationToken += 1;

    const cols = Number(tourForm.elements.cols.value);
    const rows = Number(tourForm.elements.rows.value);
    const startCol = Number(tourForm.elements.start_col.value);
    const startRow = Number(tourForm.elements.start_row.value);

    const apiReply = await fetch("/api/task3/solve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cols, rows, start_col: startCol, start_row: startRow }),
    });
    const replyOutcome = await apiReply.json();

    if (replyOutcome.status === "invalid_input") {
      tourError.textContent = replyOutcome.message;
      tourError.hidden = false;
      boardNode.replaceChildren();
      rowLabelsNode.replaceChildren();
      colLabelsNode.replaceChildren();
      boardContainer.hidden = true;
      solveBtn.hidden = true;
      storedOutcome = null;
      return;
    }

    tourError.textContent = "";
    tourError.hidden = true;
    tourStatus.textContent = "";
    tourTime.textContent = "";
    tourOrder.replaceChildren();

    storedOutcome = replyOutcome;
    drawBoard(cols, rows, startCol, startRow);
  });

  solveBtn.addEventListener("click", async () => {
    if (!storedOutcome) return;

    if (storedOutcome.status === "path_not_found") {
      tourStatus.textContent = "path not found";
      tourTime.textContent = "";
      tourOrder.replaceChildren();
      return;
    }

    if (storedOutcome.status !== "solved") return;

    const currentToken = ++animationToken;
    solveBtn.disabled = true;
    tourStatus.textContent = "Solving...";
    tourTime.textContent = "";
    tourOrder.replaceChildren();

    boardNode.querySelectorAll(".square").forEach((square) => {
      square.replaceChildren();
    });

    const path = storedOutcome.path;
    for (let index = 0; index < path.length; index += 1) {
      if (currentToken !== animationToken) return;

      const [col, row] = path[index];
      const square = squareAt(col, row);
      if (square) {
        square.replaceChildren();
        const numberSpan = document.createElement("span");
        numberSpan.textContent = index + 1;
        square.append(numberSpan);

        const knightImg = createKnight();
        square.append(knightImg);

        await wait(60);

        if (index !== path.length - 1) {
          knightImg.remove();
        }
      }
    }

    if (currentToken !== animationToken) return;

    solveBtn.disabled = false;
    tourStatus.textContent = "Solved";
    tourTime.textContent = `Execution time: ${storedOutcome.execution_time_ms.toFixed(3)} ms`;

    tourOrder.replaceChildren();
    path.forEach(([col, row], index) => {
      const item = document.createElement("li");
      item.textContent = `${index + 1}. (${col}, ${row})`;
      tourOrder.append(item);
    });
  });

  resetBtn.addEventListener("click", resetAll);
}
