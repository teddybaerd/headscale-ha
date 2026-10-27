"""Headscale Monitor: a read-only Home Assistant integration."""
from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import device_registry as dr

from .api import HeadscaleClient
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
