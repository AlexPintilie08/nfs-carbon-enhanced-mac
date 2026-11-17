# NFS Carbon graphics profiles for Apple Silicon

The launcher generator creates small local `.app` wrappers under
`~/Applications/NFS Carbon Profiles` for the app path supplied to the generator.
They do not copy or replace the game binary. Opening one applies that profile,
then hands off to the selected installed app. All three wrappers use the same
normal `NFS Carbon` profile so saves, controller mappings, physics and unrelated
preferences remain shared.

Before the first profile change, the helper preserves the current
`mod-settings.json` and `registry.json` in
`~/Library/Application Support/NFS Carbon Profile Backups/`. It then merges only
the listed graphics keys and the racing resolution. Reopening any launcher
selects that preset again; ordinary non-profile preferences are retained. The
backup metadata also records whether those config files existed before use.

| Profile | Display target | Game render resolution | Frame cap | Filtering | Reflections |
| --- | ---: | ---: | ---: | ---: | --- |
| COOL 60 | 2560×1664 fullscreen | 1280×832 | 60 FPS | 8× anisotropic | Native HD reflections at the lower game resolution |
| BALANCED 60 | 2560×1664 fullscreen | 1920×1248 | 60 FPS | 8× anisotropic | Native HD reflections at the middle game resolution |
| ENHANCED 60 | 2560×1664 fullscreen | 2560×1664 | 60 FPS | 16× anisotropic | Native HD reflections at full game resolution |

All three keep the port's MetalFX upscaling enabled, HD texture loading enabled,
`smooth_sim` enabled, and the performance overlay off to avoid extra rendering.
COOL renders one quarter as many internal pixels as the native mode
(1280×832 versus 2560×1664); BALANCED renders 56.25% fewer pixels than native.
The existing MetalFX spatial scaler enlarges both lower-resolution frames to
the display size. ENHANCED renders at native pixels, so MetalFX is enabled but
has no smaller source image to upscale. The selected display resolution is not changed by these profiles;
fullscreen is the port's borderless desktop fullscreen and follows the current
display mode. The local app used to prepare these profiles contains HD UI assets;
other builds only have them if enabled through the upstream Setup flow. No world
texture pack is present in `build/texture-pack`, so the HD texture
loading flag remains ready for one but cannot add HD roads/buildings by itself.

The settings target 60 FPS and lower work in COOL and BALANCED, but sustained
frame pacing, energy use, and temperature have not been measured. No gameplay
or benchmark was run. In the first manual session, confirm the fullscreen mode,
the game's displayed resolution, MetalFX activation in the log when COOL is
selected, controller detection, reflection quality, and save continuity. If the
Mac is connected to an external display, the 2560×1664 target may need another
resolution choice in the game's Video options.

The profiles do not set shadows, bloom, color grading, rain, draw distance, or
car-specific textures. Existing Carbon night color treatment and gameplay
defaults are preserved. The port's native HD reflections and HD UI remain
available; the researched Windows-only packs are not copied into the app.
