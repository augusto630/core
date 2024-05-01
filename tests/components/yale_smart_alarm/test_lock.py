"""The test for the Yale Smart ALarm lock platform."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from unittest.mock import Mock

import pytest
from syrupy.assertion import SnapshotAssertion
from yalesmartalarmclient.lock import YaleDoorManAPI

from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.const import (
    ATTR_CODE,
    ATTR_ENTITY_ID,
    SERVICE_LOCK,
    SERVICE_UNLOCK,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from tests.common import MockConfigEntry, snapshot_platform


@pytest.mark.parametrize(
    "load_platforms",
    [[Platform.LOCK]],
)
async def test_lock(
    hass: HomeAssistant,
    load_config_entry: tuple[MockConfigEntry, Mock],
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Yale Smart Alarm lock."""
    entry = load_config_entry[0]
    await snapshot_platform(hass, entity_registry, snapshot, entry.entry_id)


@pytest.mark.parametrize(
    "load_platforms",
    [[Platform.LOCK]],
)
async def test_lock_service_calls(
    hass: HomeAssistant,
    load_json: dict[str, Any],
    load_config_entry: tuple[MockConfigEntry, Mock],
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
) -> None:
    """Test the Yale Smart Alarm lock."""

    client = load_config_entry[1]

    data = deepcopy(load_json)
    data["data"] = data.pop("DEVICES")

    client.auth.get_authenticated = Mock(return_value=data)
    client.auth.post_authenticated = Mock(return_value={"code": "000"})
    client.lock_api = YaleDoorManAPI(client.auth)

    state = hass.states.get("lock.device1")
    assert state.state == "locked"

    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_UNLOCK,
        {ATTR_ENTITY_ID: "lock.device1", ATTR_CODE: "123456"},
        blocking=True,
    )
    client.auth.post_authenticated.assert_called_once()
    state = hass.states.get("lock.device1")
    assert state.state == "unlocked"
    client.auth.post_authenticated.reset_mock()
    await hass.services.async_call(
        LOCK_DOMAIN,
        SERVICE_LOCK,
        {ATTR_ENTITY_ID: "lock.device1", ATTR_CODE: "123456"},
        blocking=True,
    )
    client.auth.post_authenticated.assert_called_once()
    state = hass.states.get("lock.device1")
    assert state.state == "locked"
