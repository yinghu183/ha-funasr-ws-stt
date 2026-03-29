"""Config flow for FunASR WebSocket STT."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HOST,
    CONF_HOTWORDS,
    CONF_ITN,
    CONF_MODE,
    CONF_NAME,
    CONF_PORT,
    CONF_SSL,
    CONF_TIMEOUT,
    DEFAULT_HOST,
    DEFAULT_HOTWORDS,
    DEFAULT_ITN,
    DEFAULT_MODE,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SSL,
    DEFAULT_TIMEOUT,
    DOMAIN,
    MODES,
)


class FunAsrWsSttConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for FunASR WebSocket STT."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            unique = f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{int(user_input[CONF_SSL])}"
            await self.async_set_unique_id(unique)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=65535)
                ),
                vol.Required(CONF_SSL, default=DEFAULT_SSL): bool,
                vol.Required(CONF_MODE, default=DEFAULT_MODE): vol.In(MODES),
                vol.Optional(CONF_HOTWORDS, default=DEFAULT_HOTWORDS): str,
                vol.Required(CONF_ITN, default=DEFAULT_ITN): bool,
                vol.Required(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Get options flow for this handler."""
        return FunAsrWsSttOptionsFlow(config_entry)


class FunAsrWsSttOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self._config_entry.data
        options = self._config_entry.options

        schema = vol.Schema(
            {
                vol.Required(CONF_MODE, default=options.get(CONF_MODE, data.get(CONF_MODE, DEFAULT_MODE))): vol.In(MODES),
                vol.Optional(CONF_HOTWORDS, default=options.get(CONF_HOTWORDS, data.get(CONF_HOTWORDS, DEFAULT_HOTWORDS))): str,
                vol.Required(CONF_ITN, default=options.get(CONF_ITN, data.get(CONF_ITN, DEFAULT_ITN))): bool,
                vol.Required(CONF_TIMEOUT, default=options.get(CONF_TIMEOUT, data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT))): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=300)
                ),
            }
        )

        return self.async_show_form(step_id="init", data_schema=schema)
