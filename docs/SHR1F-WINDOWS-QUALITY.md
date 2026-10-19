# SHR1F Windows build and quality checklist

This fork starts from the independent MIT-licensed Tangerine-for-Windows project
by CristianO2601 and contributors. Preserve the LICENSE and upstream credit.
It is **not** the original macOS app, and pixel-perfect fidelity is **not yet
certified** by side-by-side visual measurement.

## Using the app

- Windows 11: download the newest `Tangerine-*-Setup.exe` from
  [this fork's Releases](https://github.com/SHR1F/tangerine-windows/releases).
- For a portable installation, download the `*-windows-portable.zip`, extract
  the **entire** archive, and launch `Tangerine.exe`. The portable EXE must
  remain next to its `_internal` folder; it is not a standalone single file.
- Keep source images/video safe: conversions should output new sibling files,
  not overwrite original inputs.
- FFmpeg/ffprobe are needed for audio/video/GIF features and must be installed
  separately when not bundled. See README for supported locations.
- These binaries are **not code signed**. Windows may display a SmartScreen
  reputation warning. Verify the repository, release source, and publisher;
  don't disable Windows security protections simply to install it.

## Build an installer from this fork

GitHub commonly disables Actions for a newly created fork. Open the
[Actions tab](https://github.com/SHR1F/tangerine-windows/actions) and enable
workflows if GitHub asks you to. Then:

1. Open
   [Build Windows installer](https://github.com/SHR1F/tangerine-windows/actions/workflows/build-installer.yml).
2. Choose **Run workflow** and branch `main` (or the feature branch for
   a non-release validation build).
3. The workflow installs dependencies, runs pytest with offscreen Qt, packages
   the Windows application, launches the frozen executable smoke tests,
   and uploads `Tangerine-windows` with the setup EXE and portable ZIP.
4. A **successful push build on main** also creates/updates a versioned GitHub
   Release with those downloads. A branch build only uploads temporary Actions
   artifacts. Do not publish an installer as validated if the build fails.

No GitHub Actions run means **no fork-specific executable was built**. A release
from `CristianO2601/tangerine-windows` is upstream, not your fork's release.

## Interaction polish in 1.10.3

- When the pointer crosses petals rapidly, old hover and capsule Qt animations
  are stopped and scheduled for cleanup before replacements are started.
- Repeated dismiss transitions cannot call an obsolete farewell callback.
- High-resolution wheel deltas are accumulated to a standard wheel notch,
  and pixel-only touchpad scrolls accumulate to a short gesture.
- Dedicated tests cover cancellation/replacement and scroll accumulation.

## Acceptance tests before saying “1:1”

- [ ] Test the wheel on Windows 11 at 100%, 125%, 150% and 200% DPI.
- [ ] Compare Mac Tangerine and Windows screenshots side by side in light/dark.
- [ ] Compare bloom, hover, close, drag/drop and keyboard interactions.
- [ ] Test with a real Windows Explorer drag of 1 and multiple files.
- [ ] Test all formats and editor actions advertised in README, including
      optional FFmpeg-dependent paths and failure handling.
- [ ] Run the CI suite and packaged smoke checks on real Windows.
- [ ] Verify setup, uninstall, startup, Explorer integration and upgrade.
- [ ] Verify SmartScreen/signing expectations and release checksums.

Automated Qt offscreen screenshots are useful regression evidence, but cannot
replace real desktop usability and visual-parity validation.
