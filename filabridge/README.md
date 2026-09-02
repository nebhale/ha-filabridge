# FilaBridge

Run [FilaBridge](https://github.com/sargonas/filabridge) as a managed Home Assistant App.

FilaBridge connects PrusaLink-compatible printers to Spoolman, maps physical spools to printer toolheads, and automatically records filament consumption when prints finish. This App uses the official upstream multi-architecture image and adds Home Assistant lifecycle management, persistent storage, logs, backups, and an **Open Web UI** action.

## Features

- Supports `amd64` and `aarch64`, including Raspberry Pi 5.
- Persists all FilaBridge state in Home Assistant App storage.
- Uses cold backups for consistent SQLite snapshots.
- Connects to Spoolman over the private Home Assistant App network or your LAN.
- Exposes the FilaBridge Web UI on port 7913 by default.

> [!WARNING]
> FilaBridge has no built-in authentication. Do not expose its Web UI directly to the internet.

See the **Documentation** tab after installation for setup and troubleshooting instructions.
