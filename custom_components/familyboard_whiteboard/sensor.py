"""Sensor platform for Familyboard Whiteboard.

Exposes one lightweight entity per board (last-edited timestamp + stroke/
note counts) that the frontend card uses as its anchor: it reads
`config_entry_id` from the attributes and then fetches/saves the actual
board content on demand via the WebSocket API in websocket_api.py. Also
implements the `clear_board` entity service.
"""

from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN, SERVICE_CLEAR_BOARD
from .storage import FamilyboardWhiteboardStore


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    store: FamilyboardWhiteboardStore = hass.data[DOMAIN]["store"]
    sensor = FamilyboardWhiteboardSensor(entry, store)
    hass.data[DOMAIN]["sensors"][entry.entry_id] = sensor
    async_add_entities([sensor])

    platform = entity_platform.async_get_current_platform()
    platform.async_register_entity_service(SERVICE_CLEAR_BOARD, {}, "async_clear_board")


class FamilyboardWhiteboardSensor(SensorEntity):
    """Represents one whiteboard (last edited + how much is on it)."""

    _attr_has_entity_name = True
    _attr_name = "Whiteboard"
    _attr_icon = "mdi:draw-pen"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, entry: ConfigEntry, store: FamilyboardWhiteboardStore) -> None:
        self._entry = entry
        self._store = store
        self._attr_unique_id = f"{entry.entry_id}_whiteboard"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Familyboard Whiteboard",
            model="Board",
        )

    @property
    def native_value(self):
        updated_at = self._store.board(self._entry.entry_id).get("updated_at")
        return dt_util.parse_datetime(updated_at) if updated_at else None

    @property
    def extra_state_attributes(self) -> dict:
        board = self._store.board(self._entry.entry_id)
        return {
            "config_entry_id": self._entry.entry_id,
            "stroke_count": len(board.get("strokes", [])),
            "note_count": len(board.get("notes", [])),
        }

    async def async_clear_board(self) -> None:
        await self._store.async_clear_board(self._entry.entry_id)
        self.async_write_ha_state()
