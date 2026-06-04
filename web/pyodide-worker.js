let pyodide = null;
let isRunning = false;

async function initializePyodide() {
    importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js");
    pyodide = await loadPyodide();
    pyodide.setStdout({
        batched: (text) => self.postMessage({type: "stdout", runId: activeRunId, text}),
    });
    pyodide.setStderr({
        batched: (text) => self.postMessage({type: "stderr", runId: activeRunId, text}),
    });
    self.postMessage({type: "ready"});
}

let activeRunId = null;

async function runPython(runId, code) {
    if (isRunning) {
        return;
    }

    isRunning = true;
    activeRunId = runId;
    const globals = pyodide.toPy({
        __name__: "__main__",
    });

    try {
        await pyodide.runPythonAsync(code, {globals});
        self.postMessage({type: "finished", runId});
    } catch (error) {
        self.postMessage({type: "error", runId, text: error.message});
    } finally {
        globals.destroy();
        activeRunId = null;
        isRunning = false;
    }
}

self.addEventListener("message", (event) => {
    if (event.data.type === "run") {
        runPython(event.data.runId, event.data.code);
    }
});

initializePyodide().catch((error) => {
    self.postMessage({type: "load-error", text: error.message});
});
