#!/usr/bin/env python3
"""Restore the profile settings captured before the first NFS Carbon preset."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

PROFILE_DIR = Path.home() / "Library/Application Support/NFS Carbon"
BACKUP_DIR = Path.home() / "Library/Application Support/NFS Carbon Profile Backups"
MARKERS = ("profile-launcher-original-configs-v2.json",
           "profile-launcher-original-configs-v1.json")
CONFIG_NAMES = {"mod-settings.json", "registry.json"}


class RestoreError(Exception):
    """A saved profile snapshot could not be restored safely."""


def reject_symlink(path: Path) -> None:
    if path.is_symlink():
        raise RestoreError(f"Refusing to follow a symbolic link: {path}")


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RestoreError(f"Cannot read profile backup metadata: {exc}") from exc
    if not isinstance(value, dict):
        raise RestoreError("Profile backup metadata is not a JSON object")
    return value


def atomic_restore(source: Path, destination: Path) -> None:
    reject_symlink(source)
    reject_symlink(destination)
    if not source.is_file():
        raise RestoreError(f"A saved config is missing: {source}")
    mode = source.stat().st_mode & 0o777
    fd, temp_name = tempfile.mkstemp(prefix=".nfs-carbon-restore-", suffix=".tmp",
                                     dir=destination.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as out, source.open("rb") as inp:
            shutil.copyfileobj(inp, out)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(temp, mode)
        os.replace(temp, destination)
    finally:
        try:
            temp.unlink()
        except FileNotFoundError:
            pass


def restore() -> list[str]:
    reject_symlink(BACKUP_DIR)
    markers = [BACKUP_DIR / name for name in MARKERS if (BACKUP_DIR / name).exists()]
    if len(markers) != 1:
        raise RestoreError("Expected exactly one profile backup marker; none or multiple were found")
    marker_path = markers[0]
    reject_symlink(marker_path)
    marker = read_object(marker_path)
    snapshot_name = marker.get("snapshot")
    if not isinstance(snapshot_name, str) or not snapshot_name.startswith("before-profile-"):
        raise RestoreError("The backup snapshot name is invalid")
    snapshot = BACKUP_DIR / snapshot_name
    reject_symlink(snapshot)
    if snapshot.parent != BACKUP_DIR or not snapshot.is_dir():
        raise RestoreError("The saved profile snapshot directory is missing or invalid")

    if marker_path.name == MARKERS[0] and marker.get("version") == 2:
        states = marker.get("files")
        if not isinstance(states, dict) or set(states) != CONFIG_NAMES:
            raise RestoreError("The saved profile file list is invalid")
        existed = {}
        for name, state in states.items():
            if not isinstance(state, dict) or type(state.get("existed")) is not bool:
                raise RestoreError(f"The saved state for {name} is invalid")
            existed[name] = state["existed"]
        profile_dir_existed = marker.get("profile_dir_existed")
        if type(profile_dir_existed) is not bool:
            raise RestoreError("The saved profile directory state is invalid")
    elif marker_path.name == MARKERS[1]:
        legacy_files = marker.get("files")
        if not isinstance(legacy_files, list) or set(legacy_files) != CONFIG_NAMES:
            raise RestoreError("The legacy saved profile file list is invalid")
        existed = {name: True for name in CONFIG_NAMES}
        profile_dir_existed = True
    else:
        raise RestoreError("Unsupported profile backup format")

    reject_symlink(PROFILE_DIR)
    restored = []
    for name in sorted(CONFIG_NAMES):
        destination = PROFILE_DIR / name
        reject_symlink(destination)
        if existed[name]:
            if destination.exists() and not destination.is_file():
                raise RestoreError(f"Refusing to replace a non-file profile path: {destination}")
            PROFILE_DIR.mkdir(parents=True, exist_ok=True)
            atomic_restore(snapshot / name, destination)
            restored.append(f"restored {name}")
        elif destination.exists():
            if not destination.is_file():
                raise RestoreError(f"Refusing to remove a non-file profile path: {destination}")
            destination.unlink()
            restored.append(f"removed newly created {name}")
    marker_path.unlink()
    if not profile_dir_existed:
        try:
            PROFILE_DIR.rmdir()
        except OSError:
            pass  # Preserve saves, logs, or any other files in the profile directory.
    return restored


def main() -> int:
    try:
        actions = restore()
    except RestoreError as exc:
        print(f"NFS Carbon profile restore stopped: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"NFS Carbon profile restore stopped: {exc}", file=sys.stderr)
        return 1
    print("Original graphics configuration restored; save data was not touched.")
    for action in actions:
        print(f"- {action}")
    print(f"Backup files remain in: {BACKUP_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
