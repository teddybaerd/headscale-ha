"""Data coordinator."""
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import HeadscaleAuthError, HeadscaleError
from .const import DOMAIN


class HeadscaleCoordinator(DataUpdateCoordinator):
    """Retrieve all devices in one request."""

    def __init__(self, hass, entry: ConfigEntry, client):
        super().__init__(hass, logger=__import__("logging").getLogger(__name__),
                         name=DOMAIN, config_entry=entry, update_interval=timedelta(seconds=60))
        self.client = client

    async def _async_update_data(self):
        try:
            return await self.client.nodes()
        except HeadscaleAuthError as err:
            raise ConfigEntryAuthFailed("Headscale API key rejected") from err
        except HeadscaleError as err:
            raise UpdateFailed(str(err)) from err
