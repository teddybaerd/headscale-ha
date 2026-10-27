"""Set up or reauthenticate Headscale through Home Assistant."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import HeadscaleAuthError, HeadscaleClient, HeadscaleError, normalize_url
from .const import CONF_API_KEY, CONF_URL, DOMAIN

PASSWORD = selector.TextSelector(selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD))


class HeadscaleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            try:
                url = normalize_url(user_input[CONF_URL])
                await HeadscaleClient(async_get_clientsession(self.hass), url, user_input[CONF_API_KEY]).nodes()
            except ValueError:
                errors["base"] = "invalid_url"
            except HeadscaleAuthError:
                errors["base"] = "invalid_auth"
            except HeadscaleError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=url, data={CONF_URL: url, CONF_API_KEY: user_input[CONF_API_KEY]})
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required(CONF_URL, default=(user_input or {}).get(CONF_URL, "")): str,
            vol.Required(CONF_API_KEY): PASSWORD,
        }), errors=errors)

    async def async_step_reauth(self, entry_data):
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        errors = {}
        if user_input is not None:
            entry = self._get_reauth_entry()
            try:
                await HeadscaleClient(async_get_clientsession(self.hass), entry.data[CONF_URL], user_input[CONF_API_KEY]).nodes()
            except HeadscaleAuthError:
                errors["base"] = "invalid_auth"
            except HeadscaleError:
                errors["base"] = "cannot_connect"
            else:
                return self.async_update_reload_and_abort(entry, data_updates={CONF_API_KEY: user_input[CONF_API_KEY]})
        return self.async_show_form(step_id="reauth_confirm", data_schema=vol.Schema({vol.Required(CONF_API_KEY): PASSWORD}), errors=errors)
