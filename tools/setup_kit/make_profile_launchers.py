#!/usr/bin/env python3
"""Generate reversible, small .app launchers for the three 60 FPS profiles.

The generated apps delegate to the already-installed NFS Carbon app. They do
not contain or replace the game binary and do not launch it during generation.
"""
from __future__ import annotations

import argparse
import json
import plistlib
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

SETUP = Path(__file__).resolve().parent
PROFILE_DIR = SETUP / "profiles"
PRESETS = (
    ("cool-60.json", "Need for Speed Carbon COOL 60.app", "io.github.nfsc-native-mac.profile.cool60"),
    ("balanced-60.json", "Need for Speed Carbon Balanced 60.app", "io.github.nfsc-native-mac.profile.balanced60"),
    ("enhanced-60.json", "Need for Speed Carbon Enhanced 60.app", "io.github.nfsc-native-mac.profile.enhanced60"),
)


def require_installed_app(app: Path) -> None:
    for rel in ("Contents/MacOS/Launch", "Contents/MacOS/CarbonRecomp",
                "Contents/Resources/Game/NFSC.exe", "Contents/Resources/Defaults/mod-settings.json",
                "Contents/Resources/Defaults/registry.json"):
        if not (app / rel).is_file():
            raise SystemExit(f"Installed app is incomplete; missing {app / rel}")
    subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(app)], check=True)


def validate_preset(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or not value.get("id") or not value.get("name"):
        raise SystemExit(f"Invalid profile metadata: {path}")
    resolution = value.get("game_resolution_px")
    registry = value.get("registry_values", {}).get("g_RacingResolution")
    if not isinstance(resolution, list) or len(resolution) != 2:
        raise SystemExit(f"Invalid resolution in {path}")
    packed = 0x80000000 | (resolution[0] << 16) | resolution[1]
    if registry != {"type": 4, "data": packed}:
        raise SystemExit(f"Packed resolution does not match dimensions in {path}")
    return value


def create_app(profile_path: Path, app_name: str, bundle_id: str, app: Path, out: Path) -> Path:
    preset = validate_preset(profile_path)
    final = out / app_name
    if final.exists():
        raise SystemExit(f"Refusing to replace an existing output: {final}")
    temp = out / ("." + app_name + ".building")
    if temp.exists():
        raise SystemExit(f"Refusing to replace an existing temporary output: {temp}")
    macos = temp / "Contents/MacOS"
    resources = temp / "Contents/Resources"
    macos.mkdir(parents=True)
    resources.mkdir(parents=True)
    try:
        shutil.copy2(SETUP / "profile_launcher.py", resources / "profile_launcher.py")
        shutil.copy2(SETUP / "restore_profile_configs.py", resources / "restore_profile_configs.py")
        shutil.copy2(profile_path, resources / "profile.json")
        launch = macos / "Launch"
        launch.write_text(
            "#!/bin/sh\n"
            "set -eu\n"
            "bundle_contents=\"$(CDPATH= cd \"$(dirname \"$0\")/..\" && pwd -P)\"\n"
            "exec /usr/bin/python3 \"$bundle_contents/Resources/profile_launcher.py\" "
            "\"$bundle_contents/Resources/profile.json\" " + shlex.quote(str(app)) + "\n",
            encoding="utf-8",
        )
        launch.chmod(0o755)
        plist = {
            "CFBundleDevelopmentRegion": "en",
            "CFBundleDisplayName": preset["name"],
            "CFBundleExecutable": "Launch",
            "CFBundleIdentifier": bundle_id,
            "CFBundleInfoDictionaryVersion": "6.0",
            "CFBundleName": preset["name"],
            "CFBundlePackageType": "APPL",
            "CFBundleShortVersionString": "0.1.0",
            "CFBundleVersion": "0.1.0",
            "LSApplicationCategoryType": "public.app-category.racing-games",
            "LSMinimumSystemVersion": "13.0",
            "LSSupportsGameMode": True,
            "NSHighResolutionCapable": True,
            "NSPrincipalClass": "NSApplication",
        }
        (temp / "Contents/Info.plist").write_bytes(plistlib.dumps(plist, sort_keys=True))
        subprocess.run(["/usr/bin/codesign", "--force", "--sign", "-", "--timestamp=none", str(temp)],
                       check=True)
        temp.rename(final)
        subprocess.run(["/usr/bin/codesign", "--verify", "--deep", "--strict", str(final)], check=True)
        return final
    except BaseException:
        if temp.exists():
            shutil.rmtree(temp)
        if final.exists():
            shutil.rmtree(final)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Create local launchers for NFS Carbon graphics profiles.")
    parser.add_argument("--app", default="/Applications/Need for Speed Carbon.app",
                        help="path to the app built locally by the upstream port")
    parser.add_argument("--output-dir", default="~/Applications/NFS Carbon Profiles",
                        help="where to create launchers (default: ~/Applications/NFS Carbon Profiles)")
    args = parser.parse_args()
    app = Path(args.app).expanduser().resolve()
    out = Path(args.output_dir).expanduser().resolve()
    require_installed_app(app)
    out.mkdir(parents=True, exist_ok=True)
    for filename, name, bundle_id in PRESETS:
        path = create_app(PROFILE_DIR / filename, name, bundle_id, app, out)
        print(path)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"Profile launcher preparation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
