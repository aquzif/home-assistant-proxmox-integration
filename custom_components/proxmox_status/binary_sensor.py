"""Binary sensors for Proxmox containers and virtual machines."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_platform(
    hass: HomeAssistant,
    config: dict[str, Any],
    async_add_entities: AddEntitiesCallback,
    discovery_info: dict[str, Any] | None = None,
) -> None:
    """Set up Proxmox status binary sensors."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    entities: list[ProxmoxStatusBinarySensor] = []

    for vm in coordinator.data.get("lxc", []):
        entities.append(ProxmoxStatusBinarySensor(coordinator, vm, "lxc"))

    for vm in coordinator.data.get("qemu", []):
        entities.append(ProxmoxStatusBinarySensor(coordinator, vm, "qemu"))

    async_add_entities(entities, True)


class ProxmoxStatusBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Represents power status of one Proxmox LXC/QEMU instance."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, coordinator, vm_data: dict[str, Any], vm_type: str) -> None:
        super().__init__(coordinator)
        self._vmid = vm_data.get("vmid")
        self._type = vm_type
        self._name = vm_data.get("name") or f"{vm_type}-{self._vmid}"
        self._attr_unique_id = f"proxmox_{self._type}_{self._vmid}_status"
        self._attr_name = f"Proxmox {self._name} status"

    @property
    def is_on(self) -> bool:
        """Return True if VM/CT is running."""
        vm = self._get_current_vm()
        return vm is not None and vm.get("status") == "running"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes from Proxmox."""
        vm = self._get_current_vm() or {}
        return {
            "vmid": vm.get("vmid", self._vmid),
            "type": self._type,
            "name": vm.get("name", self._name),
            "status": vm.get("status"),
            "node": self.coordinator.node,
            "uptime": vm.get("uptime"),
            "cpu": vm.get("cpu"),
            "mem": vm.get("mem"),
            "maxmem": vm.get("maxmem"),
        }

    def _get_current_vm(self) -> dict[str, Any] | None:
        """Find current VM data in coordinator payload."""
        for vm in self.coordinator.data.get(self._type, []):
            if vm.get("vmid") == self._vmid:
                return vm
        return None
