"""Test the MicroAir_EasyTouch config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.components.microair_climate.config_flow import CannotConnect
from homeassistant.components.microair_climate.const import DOMAIN
from homeassistant.const import CONF_IP_ADDRESS, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {CONF_IP_ADDRESS: "1.1.1.1", CONF_NAME: "test-name"},
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Name of the device"
    assert result["data"] == {
        CONF_IP_ADDRESS: "1.1.1.1",
        CONF_NAME: "test-name",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.microair_climate.config_flow.PlaceholderHub.authenticate",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.1.1.1",
                CONF_NAME: "test-name",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    # Make sure the config flow tests finish with either an
    # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
    # we can show the config flow is able to recover from an error.

    with patch(
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.1.1.1",
                CONF_NAME: "test-name",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Name of the device"
    assert result["data"] == {
        CONF_IP_ADDRESS: "1.1.1.1",
        CONF_NAME: "test-name",
    }
    assert len(mock_setup_entry.mock_calls) == 1
