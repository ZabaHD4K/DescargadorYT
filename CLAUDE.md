# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

YTDownloader4K: a single-file Tkinter GUI (`src/descargador.py`) that wraps **yt-dlp** to download YouTube videos up to 4K, or extract MP3 audio. Distributed to end users as **one standalone Windows exe** (`YTDownloader4k.exe`, ~37 MB, built with PyInstaller and committed to the repo root). Almost all real logic lives in that one Python file — there is no package structure, no tests, and no backend.

## Commands

```bash
pip install -r src/requirements.txt   # yt-dlp + pillow (ffmpeg is NOT pip-installed)
python src/descargador.py             # run from source
python -m unittest discover -s tests -v   # regression tests (stdlib only, no deps)
pyinstaller src/YTDownloader4k.spec   # rebuild the exe (run from inside src/)
```

Tests cover the fragile format-selection logic in `src/formatos.py` (see below). There is no linter; the `.sonar/` config exists but is not part of a local workflow.

## Release process (this is the critical workflow)

The shipped exe **auto-updates itself in place** by polling GitHub. As of v1.7.0 the exe is **distributed via GitHub Releases** (it is no longer committed to `main`), and a CI workflow builds it:

**Normal release (v1.7.0+):**
1. Bump `__version__` in `src/descargador.py` (line ~10).
2. Add a `CHANGELOG.md` entry.
3. Commit, then push a tag `vX.Y.Z`. The `.github/workflows/release.yml` workflow runs the tests, builds the exe with PyInstaller, and publishes a GitHub Release with `YTDownloader4k.exe` as an asset.
4. The running exe checks the **Releases API** (`api.github.com/.../releases/latest`), compares the `tag_name` against its own `__version__` with **semver** comparison, and downloads the asset from `releases/latest/download/YTDownloader4k.exe`.

**`version.txt`** (repo root) is now only a compat shim for the *old* pre-1.7.0 updater, which fetched it from raw `main` and compared string-equal. Keep it updated during the transition so v1.6.9 users can still reach the bridge release; it can be dropped once no old clients remain.

The git remote is `ZabaHD4K/DescargadorYT`, commits authored as `Zabalex`. Version-bump commit messages follow `release: vX.Y.Z - <summary>`. The exe is **not** tracked in git anymore (`dist/` and update temp files are gitignored).

## Architecture notes

**Startup sequence** runs three self-maintenance steps at import time (module level, before the GUI is built), each wrapped in its own try/except so a failure is non-fatal:
- `verificar_actualizacion_app()` — only when frozen (`sys.frozen`). Downloads the new exe to a temp file, writes a self-deleting `_update.bat` that waits for the current PID to die (with a force-kill fallback), swaps the exe in place, and relaunches. This is why the exe can update seamlessly.
- `verificar_dependencias()` — ensures ffmpeg. See below.
- `verificar_actualizaciones()` — only when **not** frozen. `pip install --upgrade` for yt-dlp/Pillow.

**ffmpeg handling** — ffmpeg is required for merging video+audio and MP3 conversion but is *not* bundled and *not* pip-installed. On first run the app downloads `ffmpeg.exe`/`ffprobe.exe` into `%LOCALAPPDATA%\YTDownloader4k\ffmpeg\`. The global `ffmpeg_location` is threaded into every yt-dlp call via `obtener_opciones_ydl()` — always build yt-dlp option dicts through that helper so ffmpeg is found.

**Format extraction (`cargar_video`)** — the single most fragile area, historically broken by YouTube's PO-token throttling. Deliberate design: do **one** `extract_info` call with yt-dlp's *default* client selection. Do **not** force `player_client` (web/android/tv) — that requires PO tokens and drops resolutions. The format list is then processed by `procesar_formatos_video()` in **`src/formatos.py`** (a pure, unit-tested module): formats are deduplicated by a `height_vcodec_fps_dynamicRange` key (HDR kept separate from SDR), keeping the highest-`tbr` variant on collision, and **HLS (`m3u8`) formats are discarded** — yt-dlp exposes them as inflated-`tbr` "Untested" duplicates of the DASH (`https`) formats, and their mp4 has unset timestamps that break the MKV merge (`Can't write packet with unknown timestamp`). Extraction runs in a `ThreadPoolExecutor` with a hard 90s timeout so a hung extractor can't freeze the UI. This logic lives in a separate module specifically so it stays testable without launching the GUI.

**Threading/UI** — Tkinter is single-threaded; every network/download op runs in a `daemon=True` thread and updates widgets via `root.update_idletasks()`. Download progress flows through yt-dlp `progress_hooks`. On window close, `cerrar_app()` calls `os._exit(0)` to hard-kill lingering daemon threads (zombie-process fix).

**Downloads** — video saved as MKV (`%(title)s [<h>p].mkv`) with `merge_output_format=mkv`; audio-only extracts to 192 kbps MP3. Always to the user's `~/Downloads`.

**Single-instance lock** — when frozen, a PID lockfile in the temp dir (checked via `psutil`) prevents a second copy running.

## Conventions

- Code, comments, and identifiers are in **Spanish**; user-facing UI strings are in **English**. Keep both consistent when editing.
- Everything is one file on purpose. New features go into `src/descargador.py` unless there's a strong reason to split.
