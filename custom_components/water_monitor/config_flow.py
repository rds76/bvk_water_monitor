"""Config flow for BVK Water Monitor."""
from __future__ import annotations

from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from .auth_guard import LoginGuard
from .const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    DOMAIN,
)
from .coordinator import _HEADERS, _async_bvk_login

_CREDENTIALS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class WaterMonitorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BVK Water Monitor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Single-step setup: validate BVK credentials and save."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]

            error = await self._validate_credentials(username, password)
            if error:
                errors["base"] = error
            else:
                await self.async_set_unique_id(username.lower())
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"BVK Water ({username})",
                    data={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_CREDENTIALS_SCHEMA,
            errors=errors,
            description_placeholders={"bvk_url": "https://zis.bvk.cz"},
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> ConfigFlowResult:
        """Triggered by ConfigEntryAuthFailed (wrong BVK credentials)."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Re-enter BVK credentials."""
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input[CONF_USERNAME].strip()
            password = user_input[CONF_PASSWORD]

            entry = self._get_reauth_entry()
            guard = LoginGuard(self.hass, entry.entry_id)
            async with guard.lock:
                try:
                    await guard.async_set_blocked(True)
                    error = await self._validate_credentials(username, password)
                    if not error:
                        await guard.async_set_blocked(False)
                except UpdateFailed:
                    error = "cannot_save"
            if error:
                errors["base"] = error
            else:
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates={
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                    },
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=_CREDENTIALS_SCHEMA,
            errors=errors,
        )

    async def _validate_credentials(self, username: str, password: str) -> str | None:
        """Perform one login attempt for this explicit form submission."""
        try:
            async with aiohttp.ClientSession(
                cookie_jar=aiohttp.CookieJar(unsafe=True), headers=_HEADERS
            ) as session:
                await _async_bvk_login(session, username, password)
        except ConfigEntryAuthFailed:
            return "invalid_auth"
        except UpdateFailed:
            return "cannot_connect"
        return None
