# Bundled FFmpeg notice

Some Windows builds of this project include separate `ffmpeg.exe` and
`ffprobe.exe` executables to enable **offline** video/audio processing.
They are invoked as subprocesses and are **not** modified or linked to
Tangerine's Python code.

- Project: [FFmpeg](https://ffmpeg.org/)
- Binaries: [BtbN FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds)
- Pinned bundle: `autobuild-2026-10-18-13-01`,
  `ffmpeg-N-127650-geceaa54a38-win64-gpl.zip` (Windows x64, static GPL variant with libx264)
- Archive SHA256:
  `86663ef1f04673cc92c9b18cf7f46bcef69bdae14c950435ca6a053792c0b60b`
- FFmpeg software license: GPL (selected for its libx264/H.264 encoder;
  FFmpeg and bundled GPL third-party dependencies remain separately licensed). See
  [FFmpeg's legal notes](https://ffmpeg.org/legal.html) for licensing
  requirements and build configuration.
- FFmpeg source code: [FFmpeg git](https://git.ffmpeg.org/ffmpeg.git)
  and [source downloads](https://ffmpeg.org/download.html).
- Source/build instructions and packaging scripts:
  [BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds).

The FFmpeg binaries and FFmpeg project are separate from this app; they
retain their own authorship, copyright and license terms. Consult any
`LICENSE`, `COPYING` and similar files delivered in the original upstream
FFmpeg archive, copied into the distribution where available.

The exact upstream binary is verified against its published checksum before
being included in each CI release. To use your own build, replace the two
executables in the installed `tools` directory. If FFmpeg is absent, the
converter can still use tools found on your system and image/document
features remain available.

This notice does not purport to grant rights beyond the upstream licenses.
