# Changelog

## 0.1.2

- Allow deleting obsolete node devices and all associated entities from Home Assistant.
- Verify node absence with a fresh Headscale request; protect registered/offline nodes and the hub, and reject deletion on API/authentication failure.
- Bundle Headscale-derived light/dark icons and logos with BSD-3-Clause attribution.
- Preserve manual cleanup: no automatic deletions and no changes to Headscale.

## 0.1.1

- Fixed Home Assistant device registry compatibility by registering the Headscale hub before linking node devices.
- Clarified the route sensors and their descriptions, including subnet and exit routes.
- Added English and German entity descriptions.
- Clarified the limitations of the online status, route data, last-seen timestamp and node expiry in the documentation.

This integration is experimental. Basic polling and entity creation have been checked against a live Headscale installation; further testing is needed.
