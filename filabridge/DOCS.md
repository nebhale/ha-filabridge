# FilaBridge Home Assistant App

This App runs the official `ghcr.io/sargonas/filabridge` container under Home Assistant Supervisor. FilaBridge connects supported printers to Spoolman and records filament consumption against the spools mapped to each toolhead.

## Before starting

You need:

- A reachable Spoolman server.
- A PrusaLink-compatible printer with PrusaLink enabled.
- The printer's LAN address and PrusaLink password/API key.
- TCP port 5000 available on the Home Assistant host, or another host port selected on the App's **Network** tab.

## First-run setup

1. Start the App.
2. Select **Open Web UI**.
3. Choose **Start Configuration** in FilaBridge.
4. Enter the Spoolman URL.
5. Add the printer's name, LAN address, PrusaLink password/API key, and toolhead count.
6. Save the configuration. FilaBridge applies it immediately.

If you installed Bytenoodle's **Spoolman-Ingress** App from its usual repository, try this internal URL:

```text
http://20c49e40-spoolman-ingress:7912
```

The repository identifier at the beginning of that hostname is installation-specific. Use your App's actual internal hostname if it differs. If Spoolman runs outside Home Assistant, use its normal LAN URL.

This App deliberately has no Home Assistant configuration options. FilaBridge manages its settings through its own Web UI and stores them in SQLite.

## Storage and backups

The App sets `FILABRIDGE_DB_PATH=/data`, placing `filabridge.db` and its SQLite companion files in persistent Supervisor-managed storage. Configuration, printer definitions, mappings, in-flight prints, and history survive restarts and App upgrades.

Backups are cold: Home Assistant stops FilaBridge before snapshotting its data and starts it afterward. Restoring the App data restores FilaBridge's database, and upstream database migrations run automatically on startup.

## Networking and security

The Web UI is exposed directly on the Home Assistant host's port 5000 by default. You can select a different host port on the **Network** tab.

> [!WARNING]
> FilaBridge has no built-in authentication. Anyone who can reach the Web UI can change its printer, Spoolman, and webhook settings. Keep the port on a trusted LAN and never forward it directly from the internet.

Use a VPN or authenticating reverse proxy for remote access. Home Assistant Ingress is not enabled in this version of the wrapper.

## Health check

The upstream image checks `http://127.0.0.1:5000/healthz` inside the container. The endpoint also reports the running FilaBridge version.

## Troubleshooting

### Web UI unavailable

- Confirm the App is running and inspect its log.
- Check the configured host port on the **Network** tab.
- Resolve any port conflict on the Home Assistant host.

### Spoolman connection fails

- Recheck the configured URL.
- Confirm Spoolman is running.
- Verify the internal App hostname when using Supervisor networking.
- Use a LAN URL when Spoolman is hosted elsewhere.

### Printer connection fails

- Confirm PrusaLink is enabled.
- Verify the printer's LAN address and API key.
- Confirm network routing between Home Assistant and the printer.

### Usage is not recorded

- Map the correct spool to every active toolhead.
- Check dashboard warnings and the Home Assistant App log.
- Verify the print metadata contains filament usage data.

## Support

Report packaging and Home Assistant issues at [nebhale/ha-filabridge](https://github.com/nebhale/ha-filabridge/issues). Report FilaBridge application issues at [sargonas/filabridge](https://github.com/sargonas/filabridge/issues).
