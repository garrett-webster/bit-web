const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const runButton = document.getElementById("run-button");
const stopButton = document.getElementById("stop-button");
const codeEl = document.getElementById("code");
const worldContainer = document.getElementById("world-container");
const recordInfoEl = document.getElementById("record-info");
const frameCounterEl = document.getElementById("frame-counter");
const firstFrameButton = document.getElementById("first-frame-button");
const prevFrameButton = document.getElementById("prev-frame-button");
const nextFrameButton = document.getElementById("next-frame-button");
const lastFrameButton = document.getElementById("last-frame-button");

let editor = null;
let bitWorker = null;
let timeoutId = null;
let isPyodideReady = false;
let isRunning = false;
let currentRunId = 0;
let histories = {};
let activeHistoryName = null;
let activeFrameIndex = 0;
let highlightedLine = null;

const RUN_TIMEOUT_MS = 5000;

const starterCode = `from byubit import Bit


@Bit.worlds("open-line")
def main(bit):
    bit.paint("green")
    while bit.can_move_front():
        bit.move()
        bit.paint("blue")


main(Bit.new_bit)
`;

function writeLine(text, className = "") {
    const line = document.createElement("span");
    line.textContent = text;
    if (className) {
        line.className = className;
    }
    line.classList.add("output-line");
    outputEl.appendChild(line);
}

function clearOutput() {
    outputEl.textContent = "";
}

function initializeEditor() {
    editor = CodeMirror.fromTextArea(codeEl, {
        mode: "python",
        theme: "idea",
        lineNumbers: true,
        indentUnit: 4,
        tabSize: 4,
        indentWithTabs: false,
        lineWrapping: true,
    });
    editor.setValue(starterCode);
}

function setControlsEnabled() {
    runButton.disabled = !isPyodideReady || isRunning;
    stopButton.disabled = !isRunning;

    const history = getActiveHistory();
    const hasFrames = history.length > 0;
    firstFrameButton.disabled = !hasFrames || activeFrameIndex === 0;
    prevFrameButton.disabled = !hasFrames || activeFrameIndex === 0;
    nextFrameButton.disabled = !hasFrames || activeFrameIndex >= history.length - 1;
    lastFrameButton.disabled = !hasFrames || activeFrameIndex >= history.length - 1;
}

function getActiveHistory() {
    if (!activeHistoryName || !histories[activeHistoryName]) {
        return [];
    }
    return histories[activeHistoryName];
}

function stopTimeout() {
    if (timeoutId !== null) {
        clearTimeout(timeoutId);
        timeoutId = null;
    }
}

function startTimeout() {
    stopTimeout();
    timeoutId = setTimeout(() => {
        writeLine(`Execution stopped after ${RUN_TIMEOUT_MS / 1000} seconds. Did you write a loop that never ends?`, "error");
        restartWorker("Execution timed out. Reloading Python...");
    }, RUN_TIMEOUT_MS);
}

function startWorker(statusText = "Loading Pyodide...") {
    isPyodideReady = false;
    isRunning = false;
    setControlsEnabled();
    statusEl.textContent = statusText;

    bitWorker = new Worker("./bit-worker.js");
    bitWorker.addEventListener("message", handleWorkerMessage);
    bitWorker.addEventListener("error", (error) => {
        writeLine(error.message, "error");
        restartWorker("Pyodide worker failed. Reloading Python...");
    });
}

function stopWorker() {
    stopTimeout();
    if (bitWorker) {
        bitWorker.terminate();
        bitWorker = null;
    }
}

function restartWorker(statusText = "Reloading Python...") {
    stopWorker();
    isRunning = false;
    isPyodideReady = false;
    setControlsEnabled();
    startWorker(statusText);
}

function finishRun(statusText) {
    stopTimeout();
    isRunning = false;
    statusEl.textContent = statusText;
    setControlsEnabled();
}

function handleWorkerMessage(event) {
    const message = event.data;
    const isRunMessage = ["stdout", "stderr", "results", "finished", "error"].includes(message.type);

    if (isRunMessage && message.runId !== currentRunId) {
        return;
    }

    switch (message.type) {
        case "ready":
            isPyodideReady = true;
            statusEl.textContent = "Pyodide ready.";
            setControlsEnabled();
            break;
        case "stdout":
            writeLine(message.text);
            break;
        case "stderr":
            writeLine(message.text, "error");
            break;
        case "results":
            renderResults(message.results);
            break;
        case "finished":
            finishRun("Bit run finished.");
            break;
        case "error":
            writeLine(message.text, "error");
            finishRun("Python failed.");
            break;
        case "load-error":
            writeLine(message.text, "error");
            statusEl.textContent = "Could not load Pyodide.";
            isPyodideReady = false;
            setControlsEnabled();
            break;
    }
}

function runPython() {
    if (!isPyodideReady || isRunning) {
        return;
    }

    clearOutput();
    runButton.disabled = true;
    statusEl.textContent = "Running Bit...";
    isRunning = true;
    currentRunId += 1;
    setControlsEnabled();
    startTimeout();
    bitWorker.postMessage({
        type: "run",
        runId: currentRunId,
        code: editor.getValue(),
    });
}

function stopPython() {
    if (!isRunning) {
        return;
    }

    writeLine("Execution stopped by user.", "error");
    restartWorker("Execution stopped. Reloading Python...");
}

function renderResults(nextHistories) {
    histories = nextHistories || {};
    activeHistoryName = Object.keys(histories)[0] || null;
    activeFrameIndex = 0;
    renderFrame();
}

function renderFrame() {
    const history = getActiveHistory();
    worldContainer.innerHTML = "";

    if (!history.length) {
        frameCounterEl.textContent = "No run yet";
        recordInfoEl.textContent = "";
        clearHighlightedLine();
        setControlsEnabled();
        return;
    }

    const record = history[activeFrameIndex];
    frameCounterEl.textContent = `${activeHistoryName} ${activeFrameIndex + 1} / ${history.length}`;
    const lineLabel = record.line_number ? `line ${record.line_number}` : "line unavailable";
    recordInfoEl.textContent = `${record.name} (${lineLabel})${record.error_message ? `: ${record.error_message}` : ""}`;
    recordInfoEl.classList.toggle("error-text", Boolean(record.error_message));
    highlightLine(record.line_number);

    const rows = record.world.length;
    const cols = record.world[0].length;
    const grid = document.createElement("div");
    grid.className = "bit-grid";
    grid.style.gridTemplateColumns = `repeat(${cols}, minmax(24px, 1fr))`;

    for (let row = rows - 1; row >= 0; row -= 1) {
        for (let col = 0; col < cols; col += 1) {
            const cell = document.createElement("div");
            cell.className = "bit-cell";
            cell.style.backgroundColor = record.world[row][col];

            if (record.pos[0] === row && record.pos[1] === col) {
                const marker = document.createElement("div");
                marker.className = `bit-marker ${orientationClass(record.orientation)}`;
                cell.appendChild(marker);
            }

            grid.appendChild(cell);
        }
    }

    worldContainer.appendChild(grid);
    setControlsEnabled();
}

function clearHighlightedLine() {
    if (highlightedLine !== null) {
        editor.removeLineClass(highlightedLine, "background", "highlighted-line");
        highlightedLine = null;
    }
}

function highlightLine(lineNumber) {
    clearHighlightedLine();
    if (!lineNumber) {
        return;
    }

    highlightedLine = lineNumber - 1;
    editor.addLineClass(highlightedLine, "background", "highlighted-line");
    editor.scrollIntoView({line: highlightedLine, ch: 0}, 80);
}

function orientationClass(orientation) {
    return ["right", "up", "left", "down"][orientation] || "right";
}

function setFrame(index) {
    const history = getActiveHistory();
    if (!history.length) {
        return;
    }
    activeFrameIndex = Math.max(0, Math.min(index, history.length - 1));
    renderFrame();
}

runButton.addEventListener("click", runPython);
stopButton.addEventListener("click", stopPython);
firstFrameButton.addEventListener("click", () => setFrame(0));
prevFrameButton.addEventListener("click", () => setFrame(activeFrameIndex - 1));
nextFrameButton.addEventListener("click", () => setFrame(activeFrameIndex + 1));
lastFrameButton.addEventListener("click", () => setFrame(getActiveHistory().length - 1));

window.addEventListener("DOMContentLoaded", () => {
    initializeEditor();
    startWorker();
});
