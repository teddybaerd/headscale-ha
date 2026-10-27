"""Headscale node sensors."""
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers import device_registry as dr
from homeassistant.util.dt import parse_datetime

from .const import DOMAIN
from .entity import HeadscaleEntity

SENSORS = ("ip", "last_seen", "expiry", "available_routes", "approved_routes", "subnet_routes")


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    dr.async_get(hass).async_get_or_create(config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)}, name="Headscale", manufacturer="Headscale")
    known = set()

    def add_new():
        new = set(coordinator.data) - known
        known.update(new)
        async_add_entities(HeadscaleSensor(coordinator, entry, node, key) for node in new for key in SENSORS)

    add_new()
    entry.async_on_unload(coordinator.async_add_listener(add_new))


class HeadscaleSensor(HeadscaleEntity, SensorEntity):
    def __init__(self, coordinator, entry, node_id, key):
        super().__init__(coordinator, entry, node_id, key)
        self.key = key
        self._attr_translation_key = key
        self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if key in ("last_seen", "expiry"):
            self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self):
        node = self.node
        if self.key == "ip":
            ips = node.get("ipAddresses") or []
            return ips[0] if ips else None
        if self.key in ("last_seen", "expiry"):
            value = node.get({"last_seen": "lastSeen", "expiry": "expiry"}[self.key])
            return parse_datetime(value) if isinstance(value, str) else None
        value = node.get({"available_routes": "availableRoutes", "approved_routes": "approvedRoutes", "subnet_routes": "subnetRoutes"}[self.key])
        return len(value) if isinstance(value, list) else 0

    @property
    def extra_state_attributes(self):
        keys = {"available_routes": "availableRoutes", "approved_routes": "approvedRoutes", "subnet_routes": "subnetRoutes"}
        if self.key in keys:
            return {"routes": self.node.get(keys[self.key]) or []}
        if self.key == "ip":
            return {"addresses": self.node.get("ipAddresses") or []}
        return None
