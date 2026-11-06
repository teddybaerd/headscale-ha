"""Headscale Monitor: a read-only Home Assistant integration."""
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr

from .api import HeadscaleClient, HeadscaleError
from .const import CONF_API_KEY, CONF_URL, DOMAIN
from .coordinator import HeadscaleCoordinator

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass, entry):
    client = HeadscaleClient(async_get_clientsession(hass), entry.data[CONF_URL], entry.data[CONF_API_KEY])
    coordinator = HeadscaleCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    coordinator.hub_device_id = dr.async_get(hass).async_get_or_create(
        config_entry_id=entry.entry_id, identifiers={(DOMAIN, entry.entry_id)},
        name="Headscale", manufacturer="Headscale",
    ).id
    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass, entry):
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(hass, entry, device_entry):
    """Allow local removal only after Headscale confirms a node is gone."""
    coordinator = getattr(entry, "runtime_data", None)
    if coordinator is None or device_entry.id == coordinator.hub_device_id:
        return False

    prefix = f"{entry.entry_id}_"
    node_ids = {
        identifier[len(prefix):]
        for domain, identifier in device_entry.identifiers
        if domain == DOMAIN and identifier.startswith(prefix)
    }
    if not node_ids or "" in node_ids:
        return False

    # Do not trust a cached snapshot: a node may have returned since the last poll.
    # This remains read-only on Headscale; HA removes the device and its entities.
    try:
        nodes = await coordinator.client.nodes()
    except HeadscaleError:
        return False
    return node_ids.isdisjoint(nodes)
