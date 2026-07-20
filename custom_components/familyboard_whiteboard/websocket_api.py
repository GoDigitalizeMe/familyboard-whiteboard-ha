"""WebSocket API exposing whiteboard content (strokes + text notes) to the
frontend card, and letting it save changes back.
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN


@websocket_api.websocket_command(
    {
        vol.Required("type"): "familyboard_whiteboard/get_board",
        vol.Required("config_entry_id"): str,
    }
)
@websocket_api.async_response
async def ws_get_board(hass: HomeAssistant, connection, msg) -> None:
    store = hass.data.get(DOMAIN, {}).get("store")
    if store is None:
        connection.send_error(msg["id"], "not_found", "Familyboard Whiteboard is not set up")
        return
    connection.send_result(msg["id"], store.board(msg["config_entry_id"]))


@websocket_api.websocket_command(
    {
        vol.Required("type"): "familyboard_whiteboard/save_board",
        vol.Required("config_entry_id"): str,
        vol.Required("strokes"): list,
        vol.Required("notes"): list,
    }
)
@websocket_api.async_response
async def ws_save_board(hass: HomeAssistant, connection, msg) -> None:
    store = hass.data.get(DOMAIN, {}).get("store")
    if store is None:
        connection.send_error(msg["id"], "not_found", "Familyboard Whiteboard is not set up")
        return
    board = await store.async_save_board(msg["config_entry_id"], msg["strokes"], msg["notes"])

    sensor = hass.data[DOMAIN]["sensors"].get(msg["config_entry_id"])
    if sensor is not None:
        sensor.async_write_ha_state()

    connection.send_result(msg["id"], board)


def async_setup_websocket_api(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_get_board)
    websocket_api.async_register_command(hass, ws_save_board)
