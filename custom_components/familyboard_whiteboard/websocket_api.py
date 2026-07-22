"""WebSocket API exposing whiteboard content (strokes + text notes) to the
frontend card, and letting it save changes back.
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant

from .const import DOMAIN

# Any authenticated HA user (not just an admin) can reach save_board, and
# the card renders color/text fields straight into the DOM. Without these
# limits a malicious or compromised client could store data crafted to
# break out of an HTML attribute in the card (stored XSS) or bloat the
# board's storage file indefinitely.
_HEX_COLOR = vol.Match(r"^#[0-9a-fA-F]{6}$")
_UNIT_FLOAT = vol.All(vol.Coerce(float), vol.Range(min=-1, max=2))
_POINT_SCHEMA = vol.All([_UNIT_FLOAT], vol.Length(min=1, max=2))

_STROKE_SCHEMA = vol.Schema(
    {
        vol.Required("tool"): vol.In(["pen", "eraser"]),
        vol.Required("color"): vol.All(str, _HEX_COLOR),
        vol.Required("width"): vol.All(vol.Coerce(float), vol.Range(min=0.5, max=300)),
        vol.Required("points"): vol.All([_POINT_SCHEMA], vol.Length(max=5000)),
    }
)

_NOTE_SCHEMA = vol.Schema(
    {
        vol.Required("id"): vol.All(str, vol.Length(max=64)),
        vol.Required("text"): vol.All(str, vol.Length(max=2000)),
        vol.Required("x"): _UNIT_FLOAT,
        vol.Required("y"): _UNIT_FLOAT,
        vol.Required("color"): vol.All(str, _HEX_COLOR),
    }
)


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
        vol.Required("strokes"): vol.All([_STROKE_SCHEMA], vol.Length(max=5000)),
        vol.Required("notes"): vol.All([_NOTE_SCHEMA], vol.Length(max=200)),
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
