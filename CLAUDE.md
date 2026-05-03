# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common commands

Dependencies are managed by `uv` (lockfile `uv.lock`, Python pinned to `==3.13.*`).

```powershell
uv sync                              # install deps
uv sync --extra process              # also install psutil (optional, used by launcher to terminate the running main app)
uv run main.py -s 123                # run main app in dev mode (password gate is required)
uv run main.py -d -s 123             # same, with --debug
uv run python Better-Tools-Launcher.py   # run the updater/launcher window
uv run auto_build.py                 # interactive PyInstaller build (5 modes; see below)
uv run pytest test/                  # tests
uv run pytest test/test_run_app.py   # single test file
```

VS Code launch configs (`.vscode/launch.json`) wrap `main.py -s 123` and `main.py --debug -s 123`.

`auto_build.py` is interactive — it prompts for a mode (1=main, 2=launcher, 3=fast no-console, 4=test with console, 5=full + zip). Mode 1 and 2 produce two separate PyInstaller targets:
- `dist/Better-Tools/` — main app, `--onedir`, bundles `src/`, `pyproject.toml`, and `plugins/ps_of_py/*` via `--add-data`.
- `dist/Better-Tools-Launcher.exe` — single-file updater that bundles `Better-Tools-Launcher.html`.

After mode 1 the script also writes `dist/latest.json` (with an `auto_build.MMDDHHMM` version suffix), copies it plus `assets/`, `README.md`, `CHANGELOG.md`, `pyproject.toml` into the dist tree, and (mode 5) zips the result.

## Three-process architecture

`main.py` orchestrates three concurrent components inside one process tree (`src/app/start_app.py`):

1. **Streamlit** — launched via `multiprocessing.Process` (separate process), serves the UI at `localhost:38501`. Entry script: `src/ui/streamlit_app.py`.
2. **FastAPI** — launched in a **daemon thread** of the main process at `localhost:38502/api/v1/`. Entry: `src/fast_api/fastapi_app.py` → `api/v1/main.py`.
3. **pywebview** — `webview.create_window(...)` + `webview.start()` runs on the main thread and points at the Streamlit URL.

The thread/process split matters: FastAPI lives in the **same process** as pywebview, so `/api/v1/pywebview/window/{get,set}` can directly mutate `webview.windows[0]` (resize, toggle_fullscreen, on_top). Streamlit lives in a **separate process** and cannot touch pywebview directly — `src/ui/window.py` therefore drives the window through HTTP calls to the FastAPI bridge. When adding window-control features, follow this Streamlit → FastAPI → pywebview pattern; do not try to import `webview` from Streamlit code.

Ports (`src/app/app_info.py`): Streamlit 38501, FastAPI 38502. Defaults differ from the README's mention of 8501/8000.

## App metadata and resource resolution

`src/app/app_info.py` reads `pyproject.toml` + `assets/latest.json` at import time via `Config_reader`, exposing `App`, `App_streamlit`, `App_fastapi` dataclasses. Streamlit code consumes these for sidebar version badges. The two reader classes have different responsibilities:

- `Config_reader` (`src/utils/config_reader.py`) — read-only TOML/JSON; constructor accepts either a single path or a **list of candidates** and picks the first existing one (used for dev vs `_MEIPASS` frozen paths). `None` entries are skipped.
- `ConfigManager` (`src/utils/config_manager.py`) — read/write, scoped to a named subsection of a TOML/JSON file (used for `config.json`'s `app_config` and similar mutable state).

Resource path helpers handle frozen builds: `src/utils/__init__.py:get_resource_path` and `src/ui/utils/__init__.py:get_path` both branch on `sys._MEIPASS`. When frozen, `main.py` chdirs to `os.path.dirname(sys.executable)` (not `_MEIPASS`) before `init()` runs, so runtime data lives next to the exe while bundled resources resolve through `_MEIPASS`.

Single-instance guard (`src/app/app_utils.py:check_single_instance`) uses an exclusive `os.O_EXCL` lockfile in CWD; Start Menu / desktop shortcuts are recreated on first run by `init()`.

## Pages and plugins

Streamlit navigation is driven by the `PAGES` dict in `src/ui/pages/__init__.py`. The bottom of that file does:

```python
try:
    from plugins.ps_of_py.src.ui import pages
    PAGES |= pages
except ImportError as e:
    print(f"未找到插件{e}")
```

So plugins under `plugins/<name>/` extend the page tree by exporting their own `pages` dict. The `plugins/` directory is gitignored — it's expected to be missing in clean checkouts. `Plugins_Manager.load_plugins` (`src/manager/plugins_manager.py`) auto-discovers any subdir of `plugins/` that contains a `pyproject.toml` and reads the `[project]` section for the sidebar badge — also looks under `sys._MEIPASS/plugins/` when frozen. Adding a new plugin requires (a) creating `plugins/<name>/pyproject.toml` plus the page module(s), and (b) adding it to `auto_build.py`'s `add_data` list so it's bundled. The existing import in `src/ui/pages/__init__.py` (`from plugins.ps_of_py.src.ui import pages`) is still hardcoded, so a new plugin also needs its own import line there.

## Updater flow

`Better-Tools-Launcher.py` is a standalone pywebview app that polls `https://irx999.fun/img/assets/Better-Tools/latest.json`, downloads/extracts the new build, terminates `Better-Tools.exe` (uses `psutil` if installed — the import is inside `try/except ImportError` and degrades to a logged warning), replaces files, and relaunches the main app with `-s 123`. The HTML UI calls back into Python via pywebview's `js_api` (the `UpdaterAPI` class).

The `-s 123` password on `main.py` exists to prevent users from launching the main exe directly by double-clicking — they're meant to go through the launcher, which supplies the flag.
