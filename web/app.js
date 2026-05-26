const statusEl = document.getElementById("status");
const outputEl = document.getElementById("output");
const runButton = document.getElementById("run-button");
const codeEl = document.getElementById("code");

let pyodide = null;
let editor = null;

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

async function runPython() {
    if (!pyodide) {
        return;
    }

    clearOutput();
    runButton.disabled = true;
    statusEl.textContent = "Running Python...";

    const globals = pyodide.toPy({
        __name__: "__main__",
    });

    try {
        await pyodide.runPythonAsync(editor.getValue(), {globals});
        statusEl.textContent = "Python finished.";
    } catch (error) {
        writeLine(error.message, "error");
        statusEl.textContent = "Python failed.";
    } finally {
        globals.destroy();
        runButton.disabled = false;
    }
}

async function initializePyodide() {
    try {
        pyodide = await loadPyodide();
        pyodide.setStdout({batched: (text) => writeLine(text)});
        pyodide.setStderr({batched: (text) => writeLine(text, "error")});

        statusEl.textContent = "Pyodide ready.";
        runButton.disabled = false;
        await runPython();
    } catch (error) {
        writeLine(error.message, "error");
        statusEl.textContent = "Could not load Pyodide.";
    }
}

runButton.addEventListener("click", runPython);
window.addEventListener("DOMContentLoaded", () => {
    initializeEditor();
    initializePyodide();
});
