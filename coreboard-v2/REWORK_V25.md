# Coreboard V2.5 · 吏部审查返工记录 / Audit rework

**Basis:** 吏部 Claude Code 2026-11-27 audit report for task T-7b0e302c6a, frozen commit 430a4ee (previous version V2.4).

## Corrected / 修复

| Audit finding | Change | Proof |
|---|---|---|
| first/play.mp3 “Play time” reused for “Favourite play” | Distinct FIRST_PRESETS ID first/play-favourite; corresponding new Piper recording; both names remain accurate | Whisper large-v3-turbo recognised “Favourite play”; browser tested linked MP3 |
| Now border/highlight but unchanged card size | Increase Now card main height, icon and EN/ZH font; preserve two-lane layout | Browser asserts Now title and card size larger on five viewports |
| Full 11-column board overflows iPad 1024px | Responsive grid with no mandatory 1300px minimum; shrink full-view labels and seven footer number buttons while leaving left/right pages large and unchanged | Browser asserts no horizontal overflow on 1194, 1024, 834, 768 and 390px |
| One unfinished step incorrectly shows Then=All done | Show “Choose a favourite activity / 选一个喜欢的活动” instead; only truly all-done has rest/finished state | Browser tests daily focus and First/Then |
| Old now/next/done loses correct current-card focus after migration | One-time migration promotes previous status=now card to top without duplicating or dropping items; import-backup path also migrates | Legacy data injection with now at non-first position, 5 unique cards and photo preservation; persisted migration |
| Favicon 404 | Explicit rel=icon to existing icon-192.png | Network resource available |
| English volume inconsistency | Rebuild ALL 119 clips directly from Piper with per-file loudness normalization, RMS gain toward -19dB and peak limiting | 119/119 files decode; mean-vol span -19.1..-18.9 dB (0.2dB) |
| School PDF has adult teaching rings | Print media removes target shadows; re-export clean one-page A3 board | Print DOM test and pdfinfo/pdftotext/pdfimages |
| Piper model provenance unavailable | Versioned source+SHA and spoken-text manifest; reproducible generator; preserved private source model (not uploaded to public repo) | audio/VOICE_PROVENANCE.md, audio/manifest.json, tools/rebuild_piper_audio.py; matching ONNX checksums |

**Tests:** coreboard-v2/tests/regression_v25.py, automated result at coreboard-v2/tests/v25-regression-results.json (89 checks pass), voice measurements at coreboard-v2/tests/v25-audio-validation.json (119 files, 0.2dB span). Real pointer events are simulated with Chromium/Playwright, not touched on an actual iPad. Source code syntax checks pass.

**Scope preserved:** 7×11 fixed-word positions, 77 bilingual labels, six opposite symbol pairs, four action symbol contrasts; Choice Board unchanged; default 2-column routine, First/Then presets; all four mini-games. Same v2 localStorage key and backup format; no forced reset.

## Not independently closed / 仍需外部复核

1. **Physical iPad**: Safari/Home Screen PWA install, offline restart, tap/drag, Chinese fallback speech, built-in MP3 audibility, and parents' perception of voice naturalness need actual hardware test. Chromium iPad-sized viewport does not prove Safari hardware success.
2. **Therapist's “Not Available” reference image**: the original attached picture is not present in the project reference folder. The generic red barred mark works, but pixel-for-pixel correspondence remains BLOCKED. Do not mark this as PASS without source.
3. **Independent acceptance**: This is development evidence, not a PASS signature. Re-open a new independent Claude/吏部 review against the new frozen commit and preserve DSH as next reviewer. School release stays conditional.

**Release gate:** do not call this an iPad hardware-validated or therapist-approved school final product. Share A3 print preview for review; defer physical school hand-off until the blocked checks are closed.
