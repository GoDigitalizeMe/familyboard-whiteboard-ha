"""Config flow for the Familyboard Whiteboard integration.

Deliberately minimal - a whiteboard has nothing to link up (no calendars,
no to-do lists), so setup is just naming the board.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries

from .const import DOMAIN


class FamilyboardWhiteboardConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Familyboard Whiteboard."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title=user_input["title"], data={})

        schema = vol.Schema({vol.Required("title", default="Whiteboard"): str})
        return self.async_show_form(step_id="user", data_schema=schema)
