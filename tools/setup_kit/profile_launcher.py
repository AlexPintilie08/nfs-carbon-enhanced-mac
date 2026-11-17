#!/usr/bin/env python3
"""Apply one graphics preset to the installed Carbon profile, then hand off to its launcher.

The helper changes only the explicitly listed graphics settings and the racing
resolution. Saves, controller bindings and unrelated settings remain in the
existing NFS Carbon profile. A one-time copy of the previous registry and
settings is kept under Application Support before the first change.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROFILE_DIR = Path.home() / "Library/Application Support/NFS Carbon"
BACKUP_DIR = Path.home() / "Library/Application Support/NFS Carbon Profile Backups"
ALLOWED_SETTINGS = {
    "core.nfsc/hd_reflections": {1},
    "core.nfsc/render_scale": {2},
    "core.nfsc/smooth_sim": {1},
    "core.nfsc/upscaling": {1},
    "host.display/frame_limit": {2},
    "host.display/hd_textures": {1},
    "host.display/performance_overlay": {0},
    "host.display/texture_filtering": {3, 4},
    "host.display/window": {2},
}


class ProfileError(Exception):
    """A profile or installed-app precondition failed before launch."""


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProfileError(f"Cannot read valid JSON from {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProfileError(f"Expected a JSON object in {path}")
    return value


def validate_preset(preset: dict[str, Any]) -> tuple[dict[str, int], dict[str, Any]]:
    """Accept only the small, known graphics-only override surface."""
    settings = preset.get("mod_settings")
    registry = preset.get("registry_values")
    if not isinstance(settings, dict) or set(settings) != set(ALLOWED_SETTINGS):
        raise ProfileError("The preset does not contain the complete graphics key set")
    for key, allowed in ALLOWED_SETTINGS.items():
        if type(settings[key]) is not int or settings[key] not in allowed:
            raise ProfileError(f"Unexpected value for {key}: {settings[key]!r}")
    resolution = preset.get("game_resolution_px")
    if (not isinstance(resolution, list) or len(resolution) != 2 or
            any(type(part) is not int or part <= 0 for part in resolution)):
        raise ProfileError("The preset has an invalid game resolution")
    packed = 0x80000000 | (resolution[0] << 16) | resolution[1]
    expected = registry.get("g_RacingResolution") if isinstance(registry, dict) else None
    if expected != {"type": 4, "data": packed}:
        raise ProfileError("The packed racing resolution does not match the preset dimensions")
    return settings, registry


def reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise ProfileError(f"Refusing to write through a symbolic link: {path}")


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    """Replace one config atomically in its own directory."""
    old_mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, tmp_name = tempfile.mkstemp(prefix=".nfs-carbon-profile-", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(value, out, indent=2, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.chmod(tmp, old_mode)
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def preserve_original_configs(paths: list[Path], profile_dir_existed: bool,
                              originals: dict[str, bool]) -> None:
    """Save only the original graphics config files once for a later restore."""
    markers = (BACKUP_DIR / "profile-launcher-original-configs-v2.json",
               BACKUP_DIR / "profile-launcher-original-configs-v1.json")
    for marker in markers:
        if marker.is_symlink():
            raise ProfileError(f"Refusing a symbolic-link backup marker: {marker}")
    existing = [marker for marker in markers if marker.exists()]
    if existing:
        if len(existing) != 1 or not existing[0].is_file():
            raise ProfileError("The existing profile backup marker is ambiguous or invalid")
        saved = read_object(existing[0])
        snapshot_name = saved.get("snapshot")
        if not isinstance(snapshot_name, str) or not snapshot_name.startswith("before-profile-"):
            raise ProfileError("The existing profile snapshot name is invalid")
        snapshot = BACKUP_DIR / snapshot_name
        reject_symlink(snapshot)
        if snapshot.parent != BACKUP_DIR or not snapshot.is_dir():
            raise ProfileError("The existing profile snapshot directory is missing")
        if existing[0].name == markers[0].name and saved.get("version") == 2:
            states = saved.get("files")
            if not isinstance(states, dict) or set(states) != {p.name for p in paths}:
                raise ProfileError("The existing profile snapshot file list is invalid")
            for path in paths:
                state = states.get(path.name)
                if not isinstance(state, dict) or type(state.get("existed")) is not bool:
                    raise ProfileError(f"The existing saved state for {path.name} is invalid")
                if state["existed"] and not (snapshot / path.name).is_file():
                    raise ProfileError(f"The saved config is missing: {snapshot / path.name}")
        elif existing[0].name == markers[1].name:
            legacy_files = saved.get("files")
            if not isinstance(legacy_files, list) or set(legacy_files) != {p.name for p in paths}:
                raise ProfileError("The legacy profile snapshot file list is invalid")
            if any(not (snapshot / path.name).is_file() for path in paths):
                raise ProfileError("A config from the legacy profile snapshot is missing")
        else:
            raise ProfileError("The existing profile backup format is unsupported")
        return
    reject_symlink(BACKUP_DIR)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot = BACKUP_DIR / f"before-profile-{stamp}"
    snapshot.mkdir()
    for path in paths:
        if originals[path.name]:
            reject_symlink(path)
            shutil.copy2(path, snapshot / path.name)
    marker = markers[0]
    marker.write_text(json.dumps({"version": 2, "saved_at_utc": stamp,
                                  "snapshot": snapshot.name,
                                  "profile_dir_existed": profile_dir_existed,
                                  "files": {p.name: {"existed": originals[p.name]} for p in paths}},
                                 indent=2) + "\n",
                      encoding="utf-8")


def apply(preset_path: Path, app: Path) -> None:
    preset = read_object(preset_path)
    settings_overrides, registry_overrides = validate_preset(preset)
    launch = app / "Contents/MacOS/Launch"
    defaults = app / "Contents/Resources/Defaults"
    if not launch.is_file() or not os.access(launch, os.X_OK):
        raise ProfileError(f"The installed app launcher is unavailable: {launch}")
    if not (app / "Contents/MacOS/CarbonRecomp").is_file():
        raise ProfileError("The installed CarbonRecomp binary is missing")
    if PROFILE_DIR.is_symlink():
        raise ProfileError(f"Refusing to use a symbolic-link profile directory: {PROFILE_DIR}")
    profile_dir_existed = PROFILE_DIR.exists()
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    settings_path = PROFILE_DIR / "mod-settings.json"
    registry_path = PROFILE_DIR / "registry.json"
    paths = [settings_path, registry_path]
    originals = {path.name: path.is_file() for path in paths}
    if any(path.exists() and not originals[path.name] for path in paths):
        raise ProfileError("A profile config path exists but is not a regular file")
    preserve_original_configs(paths, profile_dir_existed, originals)
    for name, destination in (("mod-settings.json", settings_path), ("registry.json", registry_path)):
        reject_symlink(destination)
        if not destination.exists():
            source = defaults / name
            if not source.is_file():
                raise ProfileError(f"The installed app's default config is missing: {source}")
            shutil.copy2(source, destination)
    settings = read_object(settings_path)
    for key, value in settings_overrides.items():
        settings[key] = value
    registry = read_object(registry_path)
    if not registry:
        raise ProfileError("The registry configuration has no root key")
    root = next(iter(registry.values()))
    if not isinstance(root, dict):
        raise ProfileError("The registry configuration has an invalid root")
    root.update(registry_overrides)

    atomic_json(settings_path, settings)
    atomic_json(registry_path, registry)
    env = dict(os.environ)
    env["RECOMP_PROFILE_DIR"] = str(PROFILE_DIR)
    env["RECOMP_REGISTRY"] = str(registry_path)
    env["RECOMP_EXE"] = str(app / "Contents/Resources/Game/NFSC.exe")
    os.execve(str(launch), [str(launch)], env)


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: profile_launcher.py /path/to/profile.json '/path/to/Need for Speed Carbon.app'",
              file=sys.stderr)
        return 2
    try:
        app = Path(sys.argv[2]).expanduser().resolve()
        if not app.is_dir():
            raise ProfileError(f"The installed app folder is unavailable: {app}")
        apply(Path(sys.argv[1]).resolve(), app)
    except ProfileError as exc:
        print(f"NFS Carbon profile not applied: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"NFS Carbon profile not applied: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
