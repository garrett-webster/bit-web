# Project Handoff: Browser-Based Bit Playground

## Goal

This repository originally provided a local Python teaching library. A Python
script used `byubit.Bit`, generated an HTML replay, and opened it in a browser.

The current goal is to turn that workflow into a static, GitHub Pages-compatible
web application:

- Students edit Python in the browser.
- Pyodide executes the code locally in the browser.
- The Bit world and execution history render live.
- No backend is required.
- The generic Python console remains available as a separate page so the site
  can eventually support tools beyond Bit.

The current checkpoint commit is:

```text
084e74a Add browser Bit playground runtime
```

## Important Working Preference

The user runs the local HTTP server manually. Do not start it unless explicitly
asked.

Local command:

```bash
python3 -m http.server 8000 --directory web
```

Pages:

```text
http://127.0.0.1:8000/              # Bit playground
http://127.0.0.1:8000/console.html  # Generic Python console
```

Internet access is currently required because Pyodide and CodeMirror load from
CDNs.

## Current Architecture

### Generic Python Console

- `web/console.html`: standalone generic Python console page.
- `web/app.js`: CodeMirror editor and main-thread UI logic.
- `web/pyodide-worker.js`: loads Pyodide and executes arbitrary Python in a Web
  Worker.

The console includes:

- Editable CodeMirror editor.
- Captured stdout/stderr.
- Fresh Python globals for each run.
- Five-second timeout.
- Manual Stop button.
- Worker restart after timeout/stop.
- Run IDs to ignore stale worker messages.

### Bit Playground

- `web/index.html`: Bit-specific page.
- `web/bit-app.js`: editor, run controls, world renderer, history stepper, and
  UI state.
- `web/bit-worker.js`: loads Pyodide, discovers requested worlds, loads the Bit
  Python runtime, and runs user code.
- `web/python/bit_runtime.py`: browser-safe Python implementation of the Bit
  API.
- `web/worlds/`: static world files.
- `web/styles.css`: styles shared by the console and Bit pages.

The Bit worker was deliberately split from the generic console worker. Keep the
generic console functional while developing Bit.

## Bit Execution Flow

1. `bit-app.js` sends editor code and a run ID to `bit-worker.js`.
2. The worker finds string arguments in `@Bit.worlds(...)`.
3. For each requested name, it fetches:

   ```text
   ./worlds/<name>.start.txt
   ./worlds/<name>.finish.txt  # optional
   ```

4. A missing `.start.txt` is an error displayed in the output console.
5. The worker fetches `./python/bit_runtime.py` during initialization.
6. The worker injects loaded scenarios into Pyodide as JSON.
7. User code is compiled with filename `<user_code>` so stack inspection can
   record source line numbers.
8. `Bit.get_json_results()` is serialized and posted to `bit-app.js`.
9. The UI starts at the first history frame and allows stepping through the
   replay.

## Current Bit API

The browser runtime currently supports:

- `@Bit.worlds(...)`
- `@Bit.empty_world(...)`
- `Bit.new_bit`
- `Bit.new_world(...)`
- `move()`
- `turn_left()` / `left`
- `turn_right()` / `right`
- `can_move_front()` / `front_clear`
- `can_move_left()` / `left_clear`
- `can_move_right()` / `right_clear`
- `paint(color)`
- `erase()`
- `get_color()`
- `is_on_blue()` / `is_blue`
- `is_on_green()` / `is_green`
- `is_on_red()` / `is_red`
- `is_on_white()` / `is_empty`
- `snapshot(title)`

Each registered operation records:

- action name
- world grid
- Bit position
- orientation
- optional error/annotations
- user-code line number

## World File Format

Example: `web/worlds/open-line.start.txt`

```text
------------
------------
------------
0 0
0
```

The final two lines are position and orientation. Orientation values:

- `0`: right
- `1`: up
- `2`: left
- `3`: down

Color codes:

- `-`: white
- `k`: black/blocked
- `o`: orange
- `g`: green
- `y`: yellow
- `b`: blue
- `r`: red
- `p`: purple

The parser reverses grid rows so row zero is displayed at the bottom.

## Current UI Behavior

The Bit page:

- Has a larger world column than editor column.
- Keeps both columns at matching heights.
- Starts every completed replay at its first frame.
- Highlights the CodeMirror line associated with the current frame.
- Displays the action and source line number.
- Keeps prior results visible if code changes.
- Shows a yellow stale-results overlay after code changes.
- Shows a red failure overlay and greys out the world if a new run fails.
- Disables frame navigation after a failed run.
- Has Run and Stop controls.
- Applies a five-second timeout and restarts Pyodide after timeout/stop.

## Validation Commands

These checks have been used:

```bash
node --check web/app.js
node --check web/pyodide-worker.js
node --check web/bit-app.js
node --check web/bit-worker.js
python3 -m py_compile web/python/bit_runtime.py
```

Browser behavior still needs manual testing through the local server.

## Known Limitations and Suggested Next Work

### High Priority

1. **Reduce duplication with the original package**

   `web/python/bit_runtime.py` is currently a browser-specific copy of behavior
   from `byubit/bit.py`. Changes can drift. Decide whether to extract a shared
   pure-Python core or formally maintain separate adapters.

2. **Improve scenario discovery**

   `bit-worker.js` currently uses a regular expression to find literal strings
   inside `@Bit.worlds(...)`. It will not handle variables, unusual formatting,
   aliases, or dynamically constructed names. A scenario selector/registry may
   be a better long-term design.

3. **Multiple worlds**

   The runtime can return multiple histories, but the current UI selects only
   the first history. Add tabs or a selector similar to the old generated HTML
   renderer.

4. **Finish-world comparison UI**

   The runtime accepts optional `.finish.txt` files and records annotations,
   but the new renderer does not yet visualize expected colors/positions the
   way the old renderer does.

5. **Tests**

   Add browser-side tests for:

   - successful world loading
   - missing start world
   - optional finish world
   - source line tracking
   - stale replay state
   - failed-run overlay
   - timeout/Stop recovery
   - state isolation between runs

### Later Features

- Preset scenario selector with starter code, start world, finish world, and
  instructions.
- Keyboard controls for stepping through history.
- Snapshot jump controls.
- Better traceback formatting and source-line highlighting for syntax errors.
- GitHub Pages deployment workflow/configuration.
- Persist editor text locally.
- Consider CodeMirror 6 or another maintained editor integration.

## Original Repository Caveats

The original package is in `byubit/`. Its tests and some demos appear stale:

- `test_bitlib.py` imports missing `byubit.core`.
- Tests expect NumPy-style world indexing and APIs absent from current
  `byubit/bit.py`.
- Some demos reference removed APIs such as `Bit.pictures`.
- Checked-in `__pycache__` artifacts suggest older source files existed.

Do not treat the existing test suite as authoritative without reconciling it
with the current package.

## Git Notes

The working tree was clean when this handoff was written. Python cache files are
ignored via `.gitignore`.

Before changing code:

```bash
git status --short
git log -1 --oneline
```

Keep changes scoped and preserve `web/console.html` as the generic Python
runtime while extending `web/index.html` as the Bit playground.
