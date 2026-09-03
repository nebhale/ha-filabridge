# FilaBridge

Run the [FilaBridge PR #51](https://github.com/sargonas/filabridge/pull/51) test image as a managed Home Assistant App.

FilaBridge connects PrusaLink-compatible printers to Spoolman, maps physical spools to printer toolheads, and automatically records filament consumption when prints finish. This prerelease is distributed as the prebuilt `ghcr.io/nebhale/ha-filabridge:1.3.1-pr51-2` multi-architecture image. It wraps `ghcr.io/nebhale/filabridge:1.3.1-pr.51` and adds Home Assistant lifecycle management, persistent storage, logs, backups, and native Ingress.

## Features

- Supports `amd64` and `aarch64`, including Raspberry Pi 5.
- Pulls a tested, versioned wrapper image instead of building on the Home Assistant host.
- Persists all FilaBridge state in Home Assistant App storage.
- Uses cold backups for consistent SQLite snapshots.
- Connects to Spoolman over the private Home Assistant App network or your LAN.
- Opens the FilaBridge Web UI through Home Assistant Ingress and the sidebar.
- Exposes no FilaBridge Web UI port on the Home Assistant host.
- Discovers Supervisor's generated ingress URL and restores its stripped prefix
  before forwarding to the PR build.

> [!WARNING]
> FilaBridge has no built-in authentication. Keep it behind Home Assistant Ingress and do not publish its internal ports directly.

See the **Documentation** tab after installation for setup and troubleshooting instructions.
