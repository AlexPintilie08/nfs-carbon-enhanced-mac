# Installation guide

This release adds three graphics profiles to the existing native Carbon port.
It is a **profile toolkit**, not a standalone game installer and not a compiled
game application. It does not include `NFSC.exe`, game DLLs, game data, or a
prebuilt app.

## Requirements

- An Apple Silicon Mac and an installation of the native port built locally
  from your own legally licensed PC copy.
- The compatible PC game files required by the
  [upstream port](https://github.com/vasist15-source/nfs-carbon-mac#what-you-need).
- Python 3 and the macOS `codesign` utility (included with macOS).

The original port's Setup app lets you select your own game folder and builds
the app locally. Get it from the
[upstream releases](https://github.com/vasist15-source/nfs-carbon-mac/releases/latest)
or use the upstream `setup.sh` workflow. Follow that project's current
requirements. This toolkit neither distributes compatible game files nor
provides a way to alter the game's DRM.

## Create the profile launchers

1. Download the profile ZIP from this project's Releases and extract it to a
   folder you control, for example `~/Games/NFS-Carbon-Enhanced/`.
2. If the native app is at `/Applications/Need for Speed Carbon.app`, run:

   ```sh
   python3 tools/setup_kit/make_profile_launchers.py
   ```

   For an app at a different path, pass it explicitly:

   ```sh
   python3 tools/setup_kit/make_profile_launchers.py \
     --app "/path/to/Need for Speed Carbon.app"
   ```

   To choose another destination for the launchers, add `--output-dir`.
   The default is `~/Applications/NFS Carbon Profiles`.
3. Open the launcher for the profile you want to use. It changes the graphics
   values and hands control to the local game app. All profile launchers use the
   same NFS Carbon save and settings directory.

The generator checks for the expected app files and runs `codesign --verify`;
it does not start the game. It creates local ad-hoc signed wrappers without a
game icon or game binary. The signature is not a Developer ID signature or
notarization. No global security settings are changed.

## What the profiles change

The profiles change only the listed display settings and the racing resolution.
They preserve controller mappings, gameplay values and saves. Resolution values
are authored for a 2560×1664 display; choose a supported video resolution in
the game for another display. MetalFX is useful for COOL and BALANCED where the
game resolution is lower than the output. Enhanced is native resolution, so the
MetalFX option remains enabled but the scaler does not need to enlarge the frame.

`hd_textures` enables the port's texture-pack support. The release does not
include a world texture pack; install no third-party texture assets through this
tool. HD reflections are part of the native port. No Windows ASI, ReShade,
DirectX, or RTX Remix components are included.

## Restore settings

Before applying the first profile, the launcher saves the previous
`mod-settings.json` and `registry.json` in:

```text
~/Library/Application Support/NFS Carbon Profile Backups/
```

To restore that saved graphics configuration without starting the game, run:

```sh
python3 tools/setup_kit/restore_profile_configs.py
```

Only the two configuration files are restored. Saves, logs, and the backup
snapshot remain untouched. Remove the generated launchers by moving
`~/Applications/NFS Carbon Profiles` to the Trash. The native game app remains
installed.

## Validation limits

No launcher or game is run as part of generating the release. The profile
JSONs, shell launch scripts and app bundle metadata receive static validation.
Actual fullscreen behavior, controller detection, frame pacing, energy use and
thermal behavior require the user to validate them in a first manual session.
