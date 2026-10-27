"""Common entity representation."""
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class HeadscaleEntity(CoordinatorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, node_id, key):
        super().__init__(coordinator)
        self.node_id = node_id
        self._attr_unique_id = f"{entry.entry_id}_{node_id}_{key}"
        node = coordinator.data[node_id]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_{node_id}")},
            name=node.get("givenName") or node.get("name") or f"Node {node_id}",
            manufacturer="Headscale", via_device_id=coordinator.hub_device_id,
        )

    @property
    def available(self):
        return super().available and self.node_id in self.coordinator.data

    @property
    def node(self):
        return self.coordinator.data.get(self.node_id, {})
