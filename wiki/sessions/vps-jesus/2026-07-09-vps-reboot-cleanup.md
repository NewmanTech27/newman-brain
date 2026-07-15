# VPS Reboot Recovery and Boot-Race Cleanup

**Summary**: After the VPS turned off, brought the agent stack back up and removed two boot-failure sources: disabled vault-fetch.service (raced Vault at boot, failing the 5 agents) and removed the broken NordVPN snap mount.
**Tags**: #newman #vps #systemd #ops
**Created**: 2026-07-09
**Source**: newman-vps session 13116f3e-37d1-459c-a4ce-ce96dfb4999c.jsonl, user jesus

---

## Content
- Trigger: "seems the vps turned off" — checked/restarted agent tmux sessions after reboot.
- `vault-fetch.service` disabled (not deleted; unit remains at /etc/systemd/system/vault-fetch.service): it ran before Vault was ready, causing the 5 agent services to fail-then-retry at every boot.
- `snap-nordvpn-73.mount` permanently failed — snap revision 73's file gone from disk; removed the broken nordvpn snap entirely; `systemctl --failed` now zero.
- Healthy end state: all 7 Newman services running (5 agents + SSO + WhatsApp notifier), Vault active and unsealed, cloudflared tunnel up, excalidraw + curvas serving.
- This reboot is what killed the flock and prompted the 2026-07-10 overnight relaunch directive.

## Related Notes
- [[2026-07-10-flock-overnight-golden-proof]]
- [[newman-agent-org]]
