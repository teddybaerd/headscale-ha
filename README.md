# Headscale Monitor for Home Assistant

Experimental, read-only custom integration for a self-hosted Headscale control server. It is a separate integration; it does not replace the official Tailscale integration. The REST model is based on Headscale 0.29.4. This initial version has not yet been tested against a live Headscale installation.

## Devices and entities

For each node: connection to control server, IP address, last seen, key expiry, and counts of advertised, approved and subnet routes. The route lists and additional IP addresses are entity attributes. New nodes are discovered during polling; removed nodes become unavailable. A connection to the control server does not establish peer-to-peer reachability. Approved routes are not necessarily currently advertised or working. A missing key expiry is displayed as unknown. Tailscale cloud-specific update and network diagnostics are not available.

## Requirements and installation

- Home Assistant 2026.7 or later, HTTPS access to Headscale, and a Headscale API key.
- Install using HACS as a custom repository of type Integration once this repository is published; restart Home Assistant, then add **Headscale Monitor** in Settings → Devices & services.
- Alternatively copy `custom_components/headscale_monitor` into the matching Home Assistant configuration directory and restart.
- Enter the origin URL (for example `https://headscale.example.com`) and a dedicated API key in the Home Assistant configuration flow. Do not paste keys into GitHub issues or chat.

Create a dedicated key on the Headscale host with `sudo docker exec headscale headscale apikeys create`. Follow your Headscale version's instructions for expiry and revocation. When authentication fails, Home Assistant starts a reauthentication flow.

## Security

The integration sends only GET requests to `/api/v1/node`; it does not provide write actions. Nevertheless, a Headscale API key can administer Headscale and is not limited to read access merely because this integration only reads. Protect backups and configuration; restrict API exposure where practical, use TLS, use a separate key, and revoke it if compromised. Redirects are disabled for authenticated requests.

## Scope and limitations

Polling interval: 60 seconds. This is community software and may need changes for future Home Assistant or Headscale versions. The integration stores API credentials in the Home Assistant config entry, not in the repository. Node data may contain sensitive information; diagnostics or logs should be sanitized before sharing.

API reference: https://github.com/juanfont/headscale/blob/v0.29.4/proto/headscale/v1/node.proto
