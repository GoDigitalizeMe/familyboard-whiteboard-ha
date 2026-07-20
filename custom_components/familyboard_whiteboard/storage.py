"""Persistent storage for Familyboard Whiteboard boards.

Unlike the Planner/Tasks integrations, a whiteboard has no external data
source to poll (calendars, to-do lists, ...) - its entire content
(freehand strokes and text notes) is created directly by the user through
the card, so this is a thin wrapper around a single HA Store rather than a
DataUpdateCoordinator. "Saving" always replaces a board's full content;
there's no per-item merge/patch, which keeps this simple at the cost of
last-write-wins semantics if two clients edit at the exact same time -
an acceptable trade-off for a family wall display, not a real-time
collaborative editor.
"""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import STORAGE_KEY, STORAGE_VERSION

EMPTY_BOARD = {"strokes": [], "notes": [], "updated_at": None}


class FamilyboardWhiteboardStore:
    """Wraps a single HA Store instance holding every board's content."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store: Store = Store(hass, STORAGE_VERSION, STORAGE_KEY)
        self._data: dict[str, Any] = {"boards": {}}

    async def async_load(self) -> None:
        data = await self._store.async_load()
        if data:
            self._data = data
            self._data.setdefault("boards", {})

    def board(self, entry_id: str) -> dict[str, Any]:
        return dict(self._data["boards"].get(entry_id, EMPTY_BOARD))

    async def async_save_board(
        self, entry_id: str, strokes: list[dict[str, Any]], notes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        board = {
            "strokes": strokes,
            "notes": notes,
            "updated_at": dt_util.utcnow().isoformat(),
        }
        self._data["boards"][entry_id] = board
        await self._store.async_save(self._data)
        return board

    async def async_clear_board(self, entry_id: str) -> dict[str, Any]:
        return await self.async_save_board(entry_id, [], [])

    async def async_forget_board(self, entry_id: str) -> None:
        if self._data["boards"].pop(entry_id, None) is not None:
            await self._store.async_save(self._data)
