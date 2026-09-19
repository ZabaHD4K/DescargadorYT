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

The shipped exe **auto-updates itself in place** by polling GitHub. As of v1.7.0 the **primary distribution channel is GitHub Releases**: pushing a tag `vX.Y.Z` triggers `.github/workflows/release.yml`, which runs the tests, installs UPX, builds the exe with PyInstaller (from `src/`), and publishes a Release with `YTDownloader4k.exe` + `version.txt` as assets.

**Release steps (see the v1.7.3 history for the exact pattern):**
1. Bump `__version__` in `src/descargador.py` (line ~10) **and** `version.txt` (repo root) — commit together with the code change.
2. Add a `CHANGELOG.md` entry and bump the version badge in `README.md` (`docs:` commit).
3. Rebuild the exe locally (`pyinstaller src/YTDownloader4k.spec` from inside `src/`), copy `src/dist/YTDownloader4k.exe` to the repo root, and commit it as `release: vX.Y.Z - <summary>`.
4. Push `main` and push the tag `vX.Y.Z` (CI builds and publishes the Release).
5. The running exe checks the **Releases API** (`api.github.com/.../releases/latest`), compares `tag_name` against its own `__version__` with **semver** comparison (only updates if strictly greater), and downloads `releases/latest/download/YTDownloader4k.exe`.

**Compat shims still on `main`:** despite the Releases migration, the root `YTDownloader4k.exe` (~46 MB) **is still tracked in git and recommitted on every release**, and `version.txt` is kept in sync — both exist so *pre-1.7.0* clients (which fetched raw `main` and compared version strings for equality) and the README's `raw/main/...` download links keep working. They can be dropped once no old clients remain. What's gitignored is `dist/`, `build/`, and the updater's temp files — not the root exe.

The git remote is `ZabaHD4K/DescargadorYT`, commits authored as `Zabalex`.

## Architecture notes

**Startup sequence** runs three self-maintenance steps at import time (module level, before the GUI is built), each wrapped in its own try/except so a failure is non-fatal:
- `verificar_actualizacion_app()` — only when frozen (`sys.frozen`). Downloads the new exe to `%TEMP%`, **verifies the download size matches Content-Length exactly** (a truncated exe fails at startup with "Failed to load Python DLL"), then writes a self-deleting `.bat` (also in `%TEMP%`) that waits for the current PID to die (force-kill fallback), renames the old exe to a `.bak` before moving the new one in (rollback if the move fails), waits ~5s for filesystem/antivirus to release the binary, and relaunches **via `explorer.exe`** so the new process has a valid parent (avoids EDR complaints). Hard-won details from v1.7.1–1.7.3 — don't simplify them away.
- `verificar_dependencias()` — ensures ffmpeg. See below.
- `verificar_actualizaciones()` — only when **not** frozen. `pip install --upgrade` for yt-dlp/Pillow.

**ffmpeg handling** — ffmpeg is required for merging video+audio and MP3 conversion but is *not* bundled and *not* pip-installed. On first run the app downloads `ffmpeg.exe`/`ffprobe.exe` into `%LOCALAPPDATA%\YTDownloader4k\ffmpeg\`. The global `ffmpeg_location` is threaded into every yt-dlp call via `obtener_opciones_ydl()` — always build yt-dlp option dicts through that helper so ffmpeg is found.

**Format extraction (`cargar_video`)** — the single most fragile area, historically broken by YouTube's PO-token throttling. Deliberate design: do **one** `extract_info` call with yt-dlp's *default* client selection. Do **not** force `player_client` (web/android/tv) — that requires PO tokens and drops resolutions. The format list is then processed by `procesar_formatos_video()` in **`src/formatos.py`** (a pure, unit-tested module): formats are deduplicated by a `height_vcodec_fps_dynamicRange` key (HDR kept separate from SDR), keeping the highest-`tbr` variant on collision, and **HLS (`m3u8`) formats are discarded** — yt-dlp exposes them as inflated-`tbr` "Untested" duplicates of the DASH (`https`) formats, and their mp4 has unset timestamps that break the MKV merge (`Can't write packet with unknown timestamp`). Extraction runs in a `ThreadPoolExecutor` with a hard 90s timeout so a hung extractor can't freeze the UI. This logic lives in a separate module specifically so it stays testable without launching the GUI.

**Anti-bot wall** — when YouTube answers with its "sign in to confirm you're not a bot" wall, `ejecutar_detectando_bloqueo()` converts the yt-dlp error into a `YouTubeBloqueado` exception so the user sees a friendly warning (`MENSAJE_BLOQUEO`) instead of a raw traceback. Both extraction and download are wrapped with it — keep new yt-dlp calls wrapped too.

**Threading/UI** — Tkinter is single-threaded; every network/download op runs in a `daemon=True` thread and updates widgets via `root.update_idletasks()`. Download progress flows through yt-dlp `progress_hooks`. On window close, `cerrar_app()` calls `os._exit(0)` to hard-kill lingering daemon threads (zombie-process fix).

**Downloads** — video saved as MKV (`%(title)s [<h>p].mkv`) with `merge_output_format=mkv`; the format selector requests the chosen `format_id+bestaudio` with `[protocol^=http]` fallbacks (same HLS-avoidance rationale as above). Audio-only extracts to 192 kbps MP3. Always to the user's `~/Downloads`.

**Single-instance lock** — when frozen, a PID lockfile in the temp dir (checked via `psutil`) prevents a second copy running. Note `psutil` is *not* in `requirements.txt`; the check degrades gracefully (`ImportError` is swallowed) if it isn't bundled.

## Conventions

- Code, comments, and identifiers are in **Spanish**; user-facing UI strings are in **English**. Keep both consistent when editing.
- Everything is one file on purpose. New features go into `src/descargador.py` unless there's a strong reason to split.
