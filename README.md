# NFS Carbon Enhanced for Apple Silicon

Community graphics profiles and local launcher tools for the native macOS port
of *Need for Speed: Carbon* (2006). This downstream project is based on
[vasist15-source/nfs-carbon-mac](https://github.com/vasist15-source/nfs-carbon-mac);
the original port, recomp-kit, and all third-party attributions remain credited
under their existing licences. This project is not affiliated with Electronic
Arts.

The repository contains source code, profile configuration, and documentation.
It does **not** contain the game, `NFSC.exe`, game libraries or assets, a
compiled game application, saved games, or files from private security audits.
No crack, DRM bypass, or third-party graphics payload is provided.

## Install

1. Obtain a legally licensed PC copy of *Need for Speed: Carbon* that meets the
   [upstream port's current requirements](https://github.com/vasist15-source/nfs-carbon-mac#what-you-need).
   The required game files must come from your own installation. If the
   compatibility checks fail, stop and resolve that through a legitimate source;
   this project does not modify or replace the game's executable.
2. Build the native app locally using the
   [upstream Setup app](https://github.com/vasist15-source/nfs-carbon-mac/releases/latest),
   or run the upstream `setup.sh` from a source checkout with your own game path.
   The Setup app is not included in this project; the upstream project explains
   its build process and requirements.
3. Download the profile tools from this repository's
   [Releases](https://github.com/AlexPintilie08/nfs-carbon-enhanced-mac/releases),
   extract them, and run this from the extracted folder:

   ```sh
   python3 tools/setup_kit/make_profile_launchers.py \
     --app "/Applications/Need for Speed Carbon.app"
   ```

   If the port app is elsewhere, pass its path to `--app`. The tool checks the
   app's files and code signature, then creates three profile launchers in
   `~/Applications/NFS Carbon Profiles`. It does not start the game. No admin
   privileges or global macOS security changes are required.
4. Open **COOL 60**, **BALANCED 60**, or **Enhanced 60** when you are ready to
   play. A launcher saves the original graphics configuration once, applies
   its profile, and then opens the selected local port app. All profiles use the
   same save directory and preserve controller mappings and gameplay settings.

The profiles target a 2560×1664 display such as the 13-inch MacBook Air panel.
For another display, choose a supported resolution in the game's Video options.
The 60 FPS value is a cap target, not a performance guarantee; no sustained
frame-time or temperature claims are made without measurements.

## Profiles

| Profile | Game resolution | Display target | Frame cap | World filtering | MetalFX |
| --- | ---: | ---: | ---: | ---: | --- |
| COOL 60 | 1280×832 | 2560×1664 | 60 FPS | 8× anisotropic | Upscale to target |
| BALANCED 60 | 1920×1248 | 2560×1664 | 60 FPS | 8× anisotropic | Upscale to target |
| Enhanced 60 | 2560×1664 | 2560×1664 | 60 FPS | 16× anisotropic | Enabled; no upscale at native resolution |

All profiles select fullscreen, keep the port's even-physics-step setting and
native HD reflections, and turn the performance overlay off. HD texture loading
is enabled, but this repository includes no HD road, building, or car textures.
The installed port may separately contain its native HD UI assets. Read
[graphics-profiles.md](docs/graphics-profiles.md) for details and first-launch
checks.

## Restore and uninstall

To restore the graphics settings captured before the first profile was applied,
run this from the extracted tools folder:

```sh
python3 tools/setup_kit/restore_profile_configs.py
```

The restore tool touches only `mod-settings.json` and `registry.json`. It leaves
saves, logs, and the backup snapshot in place. To remove the profiles, move the
three generated launchers in `~/Applications/NFS Carbon Profiles` to the Trash.
The native port remains installed. For game removal, follow the upstream port's
instructions and keep its Application Support folder if you want to preserve
saves.

## Project contents and attribution

- `tools/setup_kit/profiles/` contains the three independent JSON presets.
- `make_profile_launchers.py`, `profile_launcher.py`, and
  `restore_profile_configs.py` generate local launchers, apply graphics-only
  settings, and restore the saved configuration.
- `tools/package_profile_release.py` builds and checks the game-free release ZIP
  from an explicit allowlist.
- `docs/graphics-mod-research.md` records compatibility and licensing findings.
- `CHANGELOG.md`, `LICENSE`, and `NOTICE` record project changes and attribution.

The source port is licensed under the root MIT license; `kit/` retains its own
MIT license and notices. Third-party dependencies keep their upstream licenses.
See [NOTICE](NOTICE) and [kit/NOTICE](kit/NOTICE). The original game and any
third-party mod assets retain their owners' rights.
