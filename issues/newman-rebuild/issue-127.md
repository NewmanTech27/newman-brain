# #127: Mini executor crashes spawning harvest_one when Nix GC unlinks the devshell python mid-session

- State: CLOSED
- Created: 2026-07-13T15:28:57Z  Closed: 2026-07-15T09:01:28Z
- URL: https://github.com/NewmanTech27/newman-rebuild/issues/127

## Body

During a long session the endpoint (`com.newman.pipeline-endpoint`, runs under `nix develop`) started failing every `harvest_one` spawn with:
`FileNotFoundError: [Errno 2] No such file or directory: '/nix/store/…-python3-3.13.13-env/bin/python3'`

Root cause: **Nix GC unlinked the devshell's python store path** while the endpoint process was still running (it holds the open inode, so it keeps serving `/health`, but `subprocess.run([python, '-m', 'harvest_one'])` from that now-unlinked path fails). Restarting the endpoint (`launchctl kickstart -k`) re-resolves a live path and fixes it — until the next GC.

This is the "Nix GC kills venvs" hazard (cf. polymarket). Fix options: pin the endpoint's devshell as a **gcroot** (e.g. `nix develop --profile ~/.newman-devshell-profile` or an out-link), or add `keep-outputs`/`keep-derivations` + a gcroot so GC can't reap the running shell. Relates to #104 (unpinned deps).
