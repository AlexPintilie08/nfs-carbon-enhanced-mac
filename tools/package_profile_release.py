#!/usr/bin/env python3
"""Create a reproducible, game-free ZIP of the NFS Carbon profile toolkit."""
from __future__ import annotations

import argparse
import hashlib
import stat
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
ARCHIVE_ROOT = f"nfs-carbon-enhanced-mac-{VERSION}"
FILES = (
    "README.md",
    "CHANGELOG.md",
    "LICENSE",
    "NOTICE",
    "docs/enhanced-installation.md",
    "docs/graphics-mod-research.md",
    "docs/graphics-profiles.md",
    "tools/setup_kit/make_profile_launchers.py",
    "tools/setup_kit/profile_launcher.py",
    "tools/setup_kit/restore_profile_configs.py",
    "tools/setup_kit/profiles/balanced-60.json",
    "tools/setup_kit/profiles/cool-60.json",
    "tools/setup_kit/profiles/enhanced-60.json",
)
FORBIDDEN_PARTS = {"cars", "frontend", "global", "sound", "tracks", "nfsc-clean-input",
                   "security-audit", "build", "original", "analysis"}
FORBIDDEN_SUFFIXES = {".app", ".dmg", ".exe", ".dll", ".asi", ".tpk", ".zip", ".rar", ".sf2"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def package(output_dir: Path) -> tuple[Path, str]:
    archive = output_dir / f"nfs-carbon-enhanced-mac-{VERSION}.zip"
    checksum = output_dir / f"nfs-carbon-enhanced-mac-{VERSION}.zip.sha256"
    if archive.exists() or checksum.exists():
        raise SystemExit(f"Refusing to overwrite an existing release artifact in {output_dir}")
    files: list[tuple[str, Path, bytes, int]] = []
    for relative in FILES:
        rel = PurePosixPath(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise SystemExit(f"Unsafe archive path: {relative}")
        if any(part.lower() in FORBIDDEN_PARTS for part in rel.parts) or rel.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise SystemExit(f"Forbidden content path: {relative}")
        source = ROOT.joinpath(*rel.parts)
        if source.is_symlink() or not source.is_file():
            raise SystemExit(f"Release source is missing, non-file, or a symlink: {relative}")
        data = source.read_bytes()
        mode = stat.S_IMODE(source.stat().st_mode)
        files.append((relative, source, data, mode))

    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
        for relative, _source, data, mode in sorted(files):
            info = zipfile.ZipInfo(f"{ARCHIVE_ROOT}/{relative}", date_time=(2026, 11, 17, 0, 0, 0))
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | mode) << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    expected = {f"{ARCHIVE_ROOT}/{relative}": digest(data) for relative, _source, data, _mode in files}
    with zipfile.ZipFile(archive, "r") as check:
        if check.testzip() is not None:
            raise SystemExit("ZIP CRC validation failed")
        names = check.namelist()
        if set(names) != set(expected) or len(names) != len(expected):
            raise SystemExit("ZIP member list does not match the release allowlist")
        for name, expected_hash in expected.items():
            if digest(check.read(name)) != expected_hash:
                raise SystemExit(f"ZIP member hash mismatch: {name}")

    archive_hash = digest(archive.read_bytes())
    checksum.write_text(f"{archive_hash}  {archive.name}\n", encoding="ascii")
    return archive, archive_hash


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="dist", help="release output directory (default: dist)")
    args = parser.parse_args()
    archive, archive_hash = package((ROOT / args.output_dir).resolve())
    print(f"Created and verified {archive}")
    print(f"SHA-256 {archive_hash}")
    print(f"Checksum file {archive}.sha256")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
