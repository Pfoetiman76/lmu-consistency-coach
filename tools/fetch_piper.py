#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_piper.py  (0.4.8.4)
=========================
Beschafft Piper (Windows) + die deutsche Thorsten-High-Stimme deterministisch
und legt sie im Ordner ``piper/`` neben der App ab -- genau das Layout, das
tts.py auto-erkennt (``piper/piper.exe`` + ``*.onnx``).

Aufruf (lokal oder in der CI, VOR dem PyInstaller-Schritt):

    python tools/fetch_piper.py

Optionen:
    --dest DIR        Zielordner (Default: ./piper)
    --force           vorhandene Dateien neu laden
    --dry-run         nur URLs anzeigen, nichts laden
    --no-binary       nur die Stimme laden (piper.exe nicht anfassen)

Bewusst nur Standardbibliothek (urllib) -- kein pip-Dependency, passt zur
etablierten Projektlinie ("REST ueber urllib, kein SDK"). Exit-Code != 0 bei
jedem Fehlschlag, damit die CI *laut* scheitert statt still eine Version ohne
Stimme zu releasen (deshalb: continue-on-error am Bundling-Schritt entfernen).
"""
from __future__ import annotations

import argparse
import hashlib
import io
import os
import shutil
import sys
import tempfile
import urllib.request
import urllib.error
import zipfile
from pathlib import Path

# --- Piper-Windows-Binary --------------------------------------------------
# Letztes Binary-Release der Original-Engine; Asset entpackt direkt zu piper/.
PIPER_RELEASE = "2023.11.14-2"
PIPER_ASSET = "piper_windows_amd64.zip"
PIPER_URL = (
    f"https://github.com/rhasspy/piper/releases/download/"
    f"{PIPER_RELEASE}/{PIPER_ASSET}"
)

# --- Deutsche Thorsten-Stimme (High), fester HF-Tag v1.0.0 -----------------
VOICE_BASE = (
    "https://huggingface.co/rhasspy/piper-voices/resolve/"
    "v1.0.0/de/de_DE/thorsten/high"
)
VOICE_MODEL = "de_DE-thorsten-high.onnx"
VOICE_CONFIG = "de_DE-thorsten-high.onnx.json"
VOICE_MODEL_URL = f"{VOICE_BASE}/{VOICE_MODEL}?download=true"
VOICE_CONFIG_URL = f"{VOICE_BASE}/{VOICE_CONFIG}?download=true"

# Optionales Integritaets-Pinning. Leer lassen = keine Pruefung.
# Wenn du die echten SHA256 hast, hier eintragen -> harte Verifikation.
VOICE_MODEL_SHA256 = ""
VOICE_CONFIG_SHA256 = ""

_UA = {"User-Agent": "lmu-consistency-coach-fetch-piper/0.4.8.4"}


def _log(msg: str) -> None:
    print(f"[fetch_piper] {msg}", flush=True)


def _download(url: str, dst: Path, *, force: bool, expect_sha: str = "") -> None:
    if dst.exists() and not force:
        _log(f"vorhanden, ueberspringe: {dst.name}")
        if expect_sha:
            _verify_sha(dst, expect_sha)
        return
    _log(f"lade {url}")
    req = urllib.request.Request(url, headers=_UA)
    tmp = dst.with_suffix(dst.suffix + ".part")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as fh:
            shutil.copyfileobj(resp, fh)
    except urllib.error.HTTPError as exc:
        raise SystemExit(f"HTTP {exc.code} bei {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Netzwerkfehler bei {url}: {exc.reason}") from exc
    size = tmp.stat().st_size
    if size < 1024:
        tmp.unlink(missing_ok=True)
        raise SystemExit(f"Download zu klein ({size} B), vermutlich Fehlerseite: {url}")
    tmp.replace(dst)
    _log(f"fertig: {dst.name} ({size/1_048_576:.1f} MiB)")
    if expect_sha:
        _verify_sha(dst, expect_sha)


def _verify_sha(path: Path, expect: str) -> None:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got.lower() != expect.lower():
        raise SystemExit(f"SHA256-Mismatch {path.name}: erwartet {expect}, ist {got}")
    _log(f"SHA256 ok: {path.name}")


def _fetch_binary(dest: Path, *, force: bool) -> None:
    exe = dest / "piper.exe"
    if exe.exists() and not force:
        _log("piper.exe vorhanden, ueberspringe Binary-Download")
        return
    _log(f"lade Piper-Binary {PIPER_URL}")
    req = urllib.request.Request(PIPER_URL, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            blob = resp.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise SystemExit(f"Piper-Binary konnte nicht geladen werden: {exc}") from exc

    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        with zipfile.ZipFile(io.BytesIO(blob)) as zf:
            zf.extractall(tdp)
        # piper.exe irgendwo im entpackten Baum finden und dessen Ordner uebernehmen
        found = next(iter(tdp.rglob("piper.exe")), None)
        if found is None:
            raise SystemExit("piper.exe im ZIP nicht gefunden -- Asset-Layout geaendert?")
        srcdir = found.parent
        dest.mkdir(parents=True, exist_ok=True)
        for item in srcdir.iterdir():
            target = dest / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            shutil.move(str(item), str(target))
    _log(f"Piper-Binary entpackt nach {dest}/ (piper.exe + Laufzeit)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Piper + Thorsten-High beschaffen")
    ap.add_argument("--dest", default="piper", help="Zielordner (Default: ./piper)")
    ap.add_argument("--force", action="store_true", help="vorhandene Dateien neu laden")
    ap.add_argument("--dry-run", action="store_true", help="nur URLs zeigen")
    ap.add_argument("--no-binary", action="store_true", help="piper.exe nicht laden")
    args = ap.parse_args(argv)

    dest = Path(args.dest).resolve()

    if args.dry_run:
        _log("DRY-RUN, keine Downloads:")
        if not args.no_binary:
            _log(f"  BINARY : {PIPER_URL}")
        _log(f"  MODELL : {VOICE_MODEL_URL}")
        _log(f"  CONFIG : {VOICE_CONFIG_URL}")
        _log(f"  ZIEL   : {dest}/")
        return 0

    dest.mkdir(parents=True, exist_ok=True)

    if not args.no_binary:
        _fetch_binary(dest, force=args.force)

    _download(dest / VOICE_MODEL, VOICE_MODEL_URL, force=args.force,
              expect_sha=VOICE_MODEL_SHA256)
    _download(dest / VOICE_CONFIG, VOICE_CONFIG_URL, force=args.force,
              expect_sha=VOICE_CONFIG_SHA256)

    # Abschluss-Verifikation: genau das, was tts.py zum Auto-Erkennen braucht
    exe_ok = (dest / "piper.exe").exists() or args.no_binary
    onnx_ok = (dest / VOICE_MODEL).exists()
    cfg_ok = (dest / VOICE_CONFIG).exists()
    if not (exe_ok and onnx_ok and cfg_ok):
        raise SystemExit(
            f"Unvollstaendig: piper.exe={exe_ok} onnx={onnx_ok} json={cfg_ok}"
        )
    _log("OK -- piper/ ist vollstaendig (Binary + Thorsten-High).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
