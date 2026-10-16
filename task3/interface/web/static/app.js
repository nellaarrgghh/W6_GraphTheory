const board = document.getElementById("board");
const statusText = document.getElementById("status");
const orderText = document.getElementById("order");
const timeText = document.getElementById("time");
let start = { col: 2, row: 2 };
let cells = [];
let animationToken = 0;

function buildBoard() {
  board.replaceChildren();
  cells = [];
  for (let row = 0; row < 8; row += 1) {
    for (let col = 0; col < 8; col += 1) {
      const square = document.createElement("button");
      square.type = "button";
      square.className = `square ${(col + row) % 2 ? "dark" : "light"}`;
      square.dataset.col = col;
      square.dataset.row = row;
      square.setAttribute("aria-label", `Column ${col}, row ${row}`);
      square.addEventListener("click", () => selectStart(col, row));
      board.append(square);
      cells.push(square);
    }
  }
  renderStart();
}

function cellAt(col, row) {
  return cells[row * 8 + col];
}

function selectStart(col, row) {
  animationToken += 1;
  start = { col, row };
  clearBoard();
  renderStart();
  statusText.textContent = `Start: ${col},${row}`;
  orderText.textContent = "";
  timeText.textContent = "";
}

function renderStart() {
  const square = cellAt(start.col, start.row);
  square.classList.add("selected");
  const knight = document.createElement("span");
  knight.className = "knight";
  knight.textContent = "♞";
  square.append(knight);
}

function clearBoard() {
  cells.forEach((square) => {
    square.classList.remove("selected");
    square.replaceChildren();
  });
}

async function solve() {
  const token = ++animationToken;
  clearBoard();
  statusText.textContent = "Solving...";
  orderText.textContent = "";
  timeText.textContent = "";
  const response = await fetch("/api/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cols: 8, rows: 8, start_col: start.col, start_row: start.row }),
  });
  const result = await response.json();
  if (token !== animationToken) return;
  timeText.textContent = `Execution time: ${result.execution_time_ms.toFixed(3)} ms`;
  if (!result.found) {
    statusText.textContent = "path not found";
    return;
  }
  statusText.textContent = "Solved";
  orderText.textContent = `Visit order: ${result.path.map(([col, row]) => `${col},${row}`).join(" ")}`;
  await animate(result.path, token);
}

async function animate(path, token) {
  for (let index = 0; index < path.length; index += 1) {
    if (token !== animationToken) return;
    const [col, row] = path[index];
    const square = cellAt(col, row);
    square.replaceChildren();
    const number = document.createElement("span");
    number.className = "number";
    number.textContent = index + 1;
    square.append(number);
    const knight = document.createElement("span");
    knight.className = "knight";
    knight.textContent = "♞";
    square.append(knight);
    await new Promise((resolve) => setTimeout(resolve, 70));
    knight.remove();
  }
}

document.getElementById("solve").addEventListener("click", solve);
document.getElementById("reset").addEventListener("click", () => {
  animationToken += 1;
  start = { col: 2, row: 2 };
  clearBoard();
  renderStart();
  statusText.textContent = "Choose a starting square.";
  orderText.textContent = "";
  timeText.textContent = "";
});

buildBoard();
