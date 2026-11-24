"""Persist and serialize BVK login attempts."""
from __future__ import annotations

import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import UpdateFailed

from .const import DOMAIN


class LoginGuard:
    """Prevent automatic login attempts after an unconfirmed login."""

    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._hass = hass
        self._key = f"{DOMAIN}.login_guard.{entry_id}"
        locks = hass.data.setdefault(DOMAIN, {}).setdefault("_login_locks", {})
        self.lock: asyncio.Lock = locks.setdefault(entry_id, asyncio.Lock())

    def _store(self) -> Store[dict[str, bool]]:
        return Store(self._hass, 1, self._key, atomic_writes=True)

    async def async_is_blocked(self) -> bool:
        data = await self._store().async_load()
        return data is not None and data.get("blocked") is not False

    async def async_set_blocked(self, blocked: bool) -> None:
        await self._store().async_save({"blocked": blocked})
        if await self._store().async_load() != {"blocked": blocked}:
            raise UpdateFailed("Could not persist the BVK login safety state")

    async def async_remove(self) -> None:
        await self._store().async_remove()
