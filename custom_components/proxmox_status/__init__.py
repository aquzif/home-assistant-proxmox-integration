"""Proxmox Status integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOST, CONF_NODE, CONF_TOKEN, DEFAULT_SCAN_INTERVAL, DOMAIN, PLATFORMS

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_NODE): cv.string,
                vol.Required(CONF_TOKEN): cv.string,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up integration from YAML."""
    domain_config = config.get(DOMAIN)
    if domain_config is None:
        return True

    hass.data.setdefault(DOMAIN, {})

    coordinator = ProxmoxDataCoordinator(
        hass=hass,
        host=domain_config[CONF_HOST],
        node=domain_config[CONF_NODE],
        token=domain_config[CONF_TOKEN],
        scan_interval=domain_config[CONF_SCAN_INTERVAL],
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN]["coordinator"] = coordinator
    await hass.helpers.discovery.async_load_platform("binary_sensor", DOMAIN, {}, config)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Proxmox from a config entry (not used yet)."""
    return True


class ProxmoxDataCoordinator(DataUpdateCoordinator[dict[str, list[dict[str, Any]]]]):
    """Class to manage fetching Proxmox API data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        node: str,
        token: str,
        scan_interval: int,
    ) -> None:
        self.host = host.rstrip("/")
        self.node = node
        self.token = token

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, list[dict[str, Any]]]:
        """Fetch data from Proxmox API."""
        timeout = aiohttp.ClientTimeout(total=15)

        headers = {
            "Authorization": self.token,
            "Accept": "application/json",
        }

        lxc_url = f"{self.host}/api2/json/nodes/{self.node}/lxc"
        qemu_url = f"{self.host}/api2/json/nodes/{self.node}/qemu"

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(lxc_url, headers=headers) as lxc_resp:
                    if lxc_resp.status != 200:
                        raise UpdateFailed(
                            f"LXC API call failed with HTTP {lxc_resp.status}"
                        )
                    lxc_payload = await lxc_resp.json()

                async with session.get(qemu_url, headers=headers) as qemu_resp:
                    if qemu_resp.status != 200:
                        raise UpdateFailed(
                            f"QEMU API call failed with HTTP {qemu_resp.status}"
                        )
                    qemu_payload = await qemu_resp.json()

        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Error communicating with Proxmox API: {err}") from err

        return {
            "lxc": lxc_payload.get("data", []),
            "qemu": qemu_payload.get("data", []),
        }
