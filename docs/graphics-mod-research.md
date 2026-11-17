# NFS Carbon visual-mod compatibility review

Reviewed 2026-11-17 for the native ARM64/Metal port. No external mod archive was
downloaded or installed. A Windows/DirectX asset injector is not treated as
compatible merely because its replacement textures are conventional game art.

| Mod | Author / version / terms | Format and dependencies | Native Apple Silicon status |
| --- | --- | --- | --- |
| [4K Textures](https://www.nexusmods.com/needforspeedcarbon/mods/31) | Awesome Mods; v1.0, page updated 2025-01-05; Nexus page restricts re-use/conversion of its assets | `.tpf` texture package through uMod/TexMod and the Windows game | Not loadable by this port's resource path. Do not convert or copy without author permission. |
| [HD Textures](https://www.nexusmods.com/needforspeedcarbon/mods/47) | Awesome Mods; v1.0, page updated 2025-09-28; page restricts re-use/conversion | `.tpf` through TexMod | Not native-compatible; requires a separate Metal resource importer and permission for conversion. |
| [NFS HD Reflections](https://github.com/AeroWidescreen/NFSHDReflections) | Aero_; GPL-3.0 source license | Windows `.asi`, scripts, Ultimate ASI Loader and `dinput8.dll`; optional cubemap | Not loadable as-is. This project already has a native C implementation of the reflection changes; keep using it. |
| [NFS HD Content Support](https://github.com/AeroWidescreen/NFSHDContentSupport) | AeroWidescreen; GPL-3.0; repository archived 2024-11-01 | `.asi` loaded through Ultimate ASI Loader/`dinput8.dll`, including HD UI resources | Windows loader incompatible. The installed Carbon app already contains the native HD UI conversion. |
| [Custom Visual Treatment](https://github.com/xan1242/NFSC_CustomVT) | xan1242; repository states MIT | HLSL shader files, Visual Studio project, Carbon Shader Compiler/Loader or ASI-based shader loader | Shader source is a reference only; it is not Metal shader code and needs a new native implementation. |
| [NextGenFX](https://github.com/Lucent-Mods/NFSC-NextGenFX) | Lucent-Mods; latest listed v2.1; repository has a CC0 license, while README separately limits modification and sharing | `FX/` and `SCRIPTS/`, with its own Windows shader loader | Not compatible with the Metal renderer; the author does not permit customization without asking. Its heavy grading/film effects also depart from the requested 2006 look. |
| [Beautiful Rain](https://www.nexusmods.com/needforspeedcarbon/mods/52) | itsslava; v1.0, uploaded 2026-03-15; Nexus page says assets require permission and forbids conversion to another game | ReShade preset/effects for wet-road reflections | Windows ReShade injection is not part of this port; conversion is expressly disallowed. |
| [Sunrise and Sunset Visuals and Sky Shaders](https://www.nfsaddons.com/downloads/nfsc/tools/8445/nfs-carbon-day-and-night-visuals-and-sky-shaders.html) | RacerMaker; page added 2024-03-12, updated 2024-04-25; 83.35 MB; asset license not stated in listing | Sky dome and visual resource replacement; listing claims vanilla/Collector's Edition compatibility | Windows-resource format and asset permissions were not verifiable without the archive. Not downloaded. It changes the time-of-day look, so it is not part of the night-focused preset. |
| [NFS Carbon RTX Remix compatibility mod](https://github.com/xoxor4d/nfsc-rtx) / [Remix mod on ModDB](https://www.moddb.com/mods/nfsc-remix) | xoxor4d compatibility code; code license not established in this review; Remix content credited to community authors | NVIDIA RTX Remix runtime, Direct3D 9 interception, `.asi` plugin, `d3d9` runtime; source notes a possible CPU bottleneck from draw-call changes | Incompatible with Metal/Apple GPU APIs. No Remix runtime or Windows plugin was added. |
| [Project Palmont v1.3](https://www.nfsaddons.com/downloads/nfsc/tools/8415/project-palmont-v13.html) | PAIN; NFSAddons lists 2024-03-01; asset permissions and package format not stated | Page claims W2C/Vanilla retexture, 4K MW2012 roads, HD plants and scenery; listed file is only 326 bytes | Payload/format cannot be established from metadata. Not downloaded or installed pending a trustworthy, inspectable asset archive and permission details. |
| [Need for Speed Carbon - Retex v2](https://www.nexusmods.com/needforspeedcarbon/mods/28?tab=docs) | CiPHER; v2, updated 2025-02-28; author prohibits reuse of assets in other mods | Listed at about 91.4 MB; `TexturePacks/` plus `Scripts/`, including `Texwizard.asi` and JSON; Windows ASI/texture-loader path | Not compatible with the native Metal resource loader. The archive was not downloaded or inspected. |
| [NFS Carbon RX-8 (SE3P) Extended Customization](https://www.nexusmods.com/needforspeedcarbon/mods/18?tab=docs) | VeeTec; v1, uploaded 2024-02-28; asset-reuse terms not established in the visible readme | Requires NFS C Unlimiter, Extended Customization, Binary 2.9.0+, and OGVI (or Vlt-Ed); replaces/configures a vehicle rather than providing a verified texture-only pack | Windows game-data workflow; not compatible with the installed port resource set without a native importer and careful save/config review. Not installed. |
| [Mazda RX-8 replacement](https://www.nfsaddons.com/downloads/nfsc/cars/mazda/9731/mazda-mazda-rx-8.html) | Cross 007, Dominator_CZ & Eclipse 72rus; added 2025-03-08; permission terms not shown on listing | 4.17 MB listing; requires Extended Customization 3.0+, Binary 2.8.3 or 2.9.0, and OGVI; replacement car with body kits/custom parts | Not a texture-only pack and may change vehicle configuration. No native compatibility or asset permission verified; not installed. |
| [HD RETextured](https://nfspolska.pl/downloads/67/need-for-speed-carbon-hd-retextured) | Mr.Progfessional; freeware listing, 2014; asset license/redistribution terms not established | Texture replacement installed via TexMod; download page requires an account | Windows texture injection is incompatible; the package was not downloaded. |

Native features retained for the profiles are the port's Metal renderer,
MetalFX spatial scaling, built-in HD reflections, HD UI, 60 FPS cap, and
anisotropic world filtering. The game already supplies its original rain, night
lighting, bloom/color treatment, sky and vehicle resources. These remain at the
port's existing values where no native control is exposed or where a mod would
need a Windows loader.

For the requested categories, the practical split is: road/building/vegetation
and vehicle texture packs use TexMod/uMod or game-resource replacement;
reflection mods often require ASI hooks; bloom and grading projects replace
HLSL/FX shaders; wet-road effects use ReShade or RTX Remix; sky/vegetation/view
distance packages replace Windows game resources or patch the renderer. The
port can use its own native HD-reflection, MetalFX and anisotropic-filtering
controls, but it cannot load those injection layers. No standalone Mazda RX-8
texture pack with a verified native-compatible format and reuse permission was
found; the listed RX-8 entries are model/config replacements.

## Review limitations

Nexus and ModDB restrict automated page access, so file payloads, precise
licenses and package hashes could not be independently inspected from those
sites in this review. GitHub READMEs and NFSAddons listing metadata were
available. No private files were uploaded to reputation services and no mod
payload was downloaded.

Retex v2 and the RX-8 details above come from listing/documentation metadata;
their archives were not downloaded, so payload contents, malware status, and
actual compatibility were not independently verified. No directly compatible
native shadow, antialiasing, or shader package was verified in this pass.
