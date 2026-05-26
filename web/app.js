const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const runButton = document.getElementById("run-button");
const codeEl = document.getElementById("code");

let editor = null;
let pyodideWorker = null;
let timeoutId = null;
let isPyodideReady = false;
let isRunning = false;
let shouldAutoRunOnReady = true;

const RUN_TIMEOUT_MS = 5000;

const starterCode = `import sys

print("hello from Python")
print(f"Python runtime: {sys.version.split()[0]}")
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

function setRunButtonEnabled() {
    runButton.disabled = !isPyodideReady || isRunning;
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
        statusEl.textContent = "Python timed out.";
        restartWorker();
    }, RUN_TIMEOUT_MS);
}

function startWorker() {
    isPyodideReady = false;
    isRunning = false;
    setRunButtonEnabled();
    statusEl.textContent = "Loading Pyodide...";

    pyodideWorker = new Worker("./pyodide-worker.js");
    pyodideWorker.addEventListener("message", handleWorkerMessage);
    pyodideWorker.addEventListener("error", (error) => {
        writeLine(error.message, "error");
        statusEl.textContent = "Pyodide worker failed.";
        restartWorker();
    });
}

function stopWorker() {
    stopTimeout();
    if (pyodideWorker) {
        pyodideWorker.terminate();
        pyodideWorker = null;
    }
}

function restartWorker() {
    stopWorker();
    isRunning = false;
    isPyodideReady = false;
    setRunButtonEnabled();
    startWorker();
}

function finishRun(statusText) {
    stopTimeout();
    isRunning = false;
    statusEl.textContent = statusText;
    setRunButtonEnabled();
}

function handleWorkerMessage(event) {
    const message = event.data;

    switch (message.type) {
        case "ready":
            isPyodideReady = true;
            statusEl.textContent = "Pyodide ready.";
            setRunButtonEnabled();
            if (shouldAutoRunOnReady) {
                shouldAutoRunOnReady = false;
                runPython();
            }
            break;
        case "stdout":
            writeLine(message.text);
            break;
        case "stderr":
            writeLine(message.text, "error");
            break;
        case "finished":
            finishRun("Python finished.");
            break;
        case "error":
            writeLine(message.text, "error");
            finishRun("Python failed.");
            break;
        case "load-error":
            writeLine(message.text, "error");
            statusEl.textContent = "Could not load Pyodide.";
            isPyodideReady = false;
            setRunButtonEnabled();
            break;
    }
}

function runPython() {
    if (!isPyodideReady || isRunning) {
        return;
    }

    clearOutput();
    runButton.disabled = true;
    statusEl.textContent = "Running Python...";
    isRunning = true;
    setRunButtonEnabled();
    startTimeout();
    pyodideWorker.postMessage({
        type: "run",
        code: editor.getValue(),
    });
}

runButton.addEventListener("click", runPython);
window.addEventListener("DOMContentLoaded", () => {
    initializeEditor();
    startWorker();
});
