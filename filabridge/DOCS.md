# FilaBridge Home Assistant App

This prerelease App is distributed as the prebuilt, multi-architecture `ghcr.io/nebhale/ha-filabridge:1.3.1-pr51-2` image. It wraps `ghcr.io/nebhale/filabridge:1.3.1-pr.51`, built from [FilaBridge PR #51](https://github.com/sargonas/filabridge/pull/51), with native Home Assistant Ingress. FilaBridge connects supported printers to Spoolman and records filament consumption against the spools mapped to each toolhead.

## Before starting

You need:

- A reachable Spoolman server.
- A PrusaLink-compatible printer with PrusaLink enabled.
- The printer's LAN address and PrusaLink password/API key.

## First-run setup

1. Start the App.
2. Select **Open Web UI**, or enable **Show in sidebar** and open FilaBridge there.
3. Choose **Start Configuration** in FilaBridge.
4. Enter the Spoolman URL.
5. Add the printer's name, LAN address, PrusaLink password/API key, and toolhead count.
6. Save the configuration. FilaBridge applies it immediately.

If you installed Bytenoodle's **Spoolman-Ingress** App from its usual repository, try this internal URL:

```text
http://2c829f0e-spoolman-ingress:7912
```

The `2c829f0e` repository identifier is derived from Bytenoodle's repository URL. If your Spoolman App came from another repository, use that repository's identifier and the App's slug. If Spoolman runs outside Home Assistant, use its normal LAN URL.

This App deliberately has no Home Assistant configuration options. FilaBridge manages its settings through its own Web UI and stores them in SQLite.

## Storage and backups

The App sets `FILABRIDGE_DB_PATH=/data`, placing `filabridge.db` and its SQLite companion files in persistent Supervisor-managed storage. Configuration, printer definitions, mappings, in-flight prints, and history survive restarts and App upgrades.

Backups are cold: Home Assistant stops FilaBridge before snapshotting its data and starts it afterward. Restoring the App data restores FilaBridge's database, and upstream database migrations run automatically on startup.

## Networking and security

The Web UI is available only through Home Assistant Ingress. No FilaBridge port is published on the Home Assistant host.

> [!WARNING]
> FilaBridge has no built-in authentication. Keep it behind Home Assistant Ingress, where access requires a Home Assistant session, and do not expose its internal ports directly to an untrusted network.

The wrapper follows the Spoolman-Ingress design. On startup it reads the unique ingress URL from Supervisor, configures FilaBridge with that base path, and starts nginx on the ingress port. nginx restores the path prefix stripped by Supervisor and proxies HTTP and WebSocket traffic to FilaBridge on an internal port.

## Health check

The inherited image health check requests `http://127.0.0.1:5000/healthz` inside the container. nginx forwards it to FilaBridge with the generated ingress prefix restored. The endpoint also reports the running FilaBridge version.

## Troubleshooting

### Web UI unavailable

- Confirm the App is running and inspect its log.
- Confirm the log reports an ingress URL and a successful nginx start.
- Reload the sidebar entry or use **Open Web UI** from the App page.

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
