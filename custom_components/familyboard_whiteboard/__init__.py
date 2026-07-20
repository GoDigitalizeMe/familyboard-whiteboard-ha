"""The Familyboard Whiteboard integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .storage import FamilyboardWhiteboardStore
from .websocket_api import async_setup_websocket_api


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    store = FamilyboardWhiteboardStore(hass)
    await store.async_load()
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["store"] = store
    hass.data[DOMAIN].setdefault("sensors", {})

    async_setup_websocket_api(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN]["sensors"].pop(entry.entry_id, None)
    return unload_ok
