"""BVK Water Monitor integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .auth_guard import LoginGuard
from .const import DOMAIN, SUEZ_TOKEN_STORE_KEY
from .coordinator import BVKWaterCoordinator

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BVK Water Monitor from a config entry."""
    coordinator = BVKWaterCoordinator(hass, entry)

    # First refresh authenticates and fetches initial data.
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator: BVKWaterCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove persistent login state when the integration is removed."""
    await LoginGuard(hass, entry.entry_id).async_remove()
    await Store(
        hass,
        1,
        f"{DOMAIN}.{SUEZ_TOKEN_STORE_KEY}.{entry.entry_id}",
        atomic_writes=True,
    ).async_remove()
