let pyodide = null;
let isRunning = false;
let activeRunId = null;

const WORLD_BASE_PATH = "./worlds/";
const BIT_RUNTIME_PATH = "./python/bit_runtime.py";

let bitRuntimeSource = null;


async function initializePyodide() {
    importScripts("https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pyodide.js");
    pyodide = await loadPyodide();
    bitRuntimeSource = await fetchRequiredText(BIT_RUNTIME_PATH);
    pyodide.setStdout({
        batched: (text) => self.postMessage({type: "stdout", runId: activeRunId, text}),
    });
    pyodide.setStderr({
        batched: (text) => self.postMessage({type: "stderr", runId: activeRunId, text}),
    });
    self.postMessage({type: "ready"});
}

function findScenarioNames(code) {
    const names = new Set();
    const worldsCalls = code.matchAll(/@Bit\.worlds\(([^)]*)\)/g);

    for (const call of worldsCalls) {
        const stringArgs = call[1].matchAll(/["']([^"']+)["']/g);
        for (const stringArg of stringArgs) {
            names.add(stringArg[1]);
        }
    }

    return [...names];
}

async function fetchTextIfPresent(path) {
    const response = await fetch(path);
    if (response.status === 404) {
        return null;
    }
    if (!response.ok) {
        throw new Error(`Could not load ${path}: ${response.status}`);
    }
    return response.text();
}

async function fetchRequiredText(path) {
    const response = await fetch(path);
    if (!response.ok) {
        throw new Error(`Could not load ${path}: ${response.status}`);
    }
    return response.text();
}

async function loadExternalScenarios(code) {
    const scenarios = {};

    for (const name of findScenarioNames(code)) {
        const start = await fetchTextIfPresent(`${WORLD_BASE_PATH}${name}.start.txt`);
        if (start === null) {
            throw new Error(`Could not find world: ${name}. Expected ${WORLD_BASE_PATH}${name}.start.txt`);
        }

        scenarios[name] = {
            start,
            finish: await fetchTextIfPresent(`${WORLD_BASE_PATH}${name}.finish.txt`),
        };
    }

    return scenarios;
}

async function runBit(runId, code) {
    if (isRunning) {
        return;
    }

    isRunning = true;
    activeRunId = runId;
    let globals = null;

    try {
        const externalScenarios = await loadExternalScenarios(code);
        globals = pyodide.toPy({
            __name__: "__main__",
            USER_CODE: code,
            EXTERNAL_SCENARIOS_JSON: JSON.stringify(externalScenarios),
        });
        await pyodide.runPythonAsync(`
${bitRuntimeSource}
exec(compile(USER_CODE, "<user_code>", "exec"), globals())
from byubit import Bit
RESULTS_JSON = json.dumps(Bit.get_json_results())
`, {globals});
        self.postMessage({
            type: "results",
            runId,
            results: JSON.parse(globals.get("RESULTS_JSON")),
        });
        self.postMessage({type: "finished", runId});
    } catch (error) {
        self.postMessage({type: "error", runId, text: error.message});
    } finally {
        if (globals) {
            globals.destroy();
        }
        activeRunId = null;
        isRunning = false;
    }
}

self.addEventListener("message", (event) => {
    if (event.data.type === "run") {
        runBit(event.data.runId, event.data.code);
    }
});

initializePyodide().catch((error) => {
    self.postMessage({type: "load-error", text: error.message});
});
