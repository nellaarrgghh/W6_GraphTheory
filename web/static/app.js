const formNodes = document.querySelectorAll(".solver-form");
const boardNode = document.getElementById("board");
const wait = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

formNodes.forEach((formNode) => {
  const radiusNode = formNode.querySelector("[name=radius_km]");
  radiusNode.addEventListener("input", () => {
    formNode.querySelector("output").textContent = `${radiusNode.value} km`;
  });
  formNode.addEventListener("submit", async (event) => {
    event.preventDefault();
    const location = formNode.elements.location.value.split(",").map(Number);
    const payload = { lat: location[0], lng: location[1], radius_km: Number(radiusNode.value) };
    const routeType = formNode.dataset.task;
    const routeReply = await fetch(`/api/${routeType}/solve`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload),
    });
    const routeState = await routeReply.json();
    formNode.parentElement.querySelector(".solver-status").textContent = routeState.status;
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
