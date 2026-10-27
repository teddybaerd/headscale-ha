"""Headscale node connectivity sensors."""
from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from .entity import HeadscaleEntity


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = entry.runtime_data
    known = set()

    def add_new():
        new = set(coordinator.data) - known
        known.update(new)
        async_add_entities(HeadscaleOnline(coordinator, entry, node) for node in new)

    add_new()
    entry.async_on_unload(coordinator.async_add_listener(add_new))


class HeadscaleOnline(HeadscaleEntity, BinarySensorEntity):
    _attr_translation_key = "online"
    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator, entry, node_id):
        super().__init__(coordinator, entry, node_id, "online")

    @property
    def is_on(self):
        value = self.node.get("online", False)
        return value if isinstance(value, bool) else None
