"""Support for OSO Energy Switches."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from apyosoenergyapi import OSOEnergy
from apyosoenergyapi.helper.const import OSOEnergySwitchData

from config.custom_components.osoenergy_community import OSOEnergyEntity
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from .const import DOMAIN


@dataclass
class OSOEnergySwitchEntityDescription(SwitchEntityDescription):
    """Class describing OSO Energy switch entities."""

    value: Callable[[OSOEnergySwitchData], StateType] = round
    turn_on: Callable[[OSOEnergy, OSOEnergySwitchData], bool] = round
    turn_off: Callable[[OSOEnergy, OSOEnergySwitchData], bool] = round


SWITCH_TYPES: tuple[OSOEnergySwitchEntityDescription, ...] = (
    OSOEnergySwitchEntityDescription(
        key="holiday_mode",
        translation_key="holiday_mode",
        value=lambda device: device.state,
        turn_on=lambda osoenergy, device: osoenergy.switch.enable_holiday_mode(device),
        turn_off=lambda osoenergy, device: osoenergy.switch.disable_holiday_mode(
            device
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up OSO Energy switch based on a config entry."""
    osoenergy = hass.data[DOMAIN][entry.entry_id]
    devices = osoenergy.session.device_list.get("switch")
    entities = []
    if devices:
        for dev in devices:
            for description in SWITCH_TYPES:
                if dev.osoEnergyType.lower() == description.key:
                    entities.append(OSOEnergySwitch(osoenergy, description, dev))

    async_add_entities(entities, True)


class OSOEnergySwitch(OSOEnergyEntity[OSOEnergySwitchData], SwitchEntity):
    """Representation of an OSO Energy switch."""

    _attr_has_entity_name = True
    entity_description: OSOEnergySwitchEntityDescription

    def __init__(
        self,
        instance: OSOEnergy,
        description: OSOEnergySwitchEntityDescription,
        osoenergy_device: OSOEnergySwitchData,
    ) -> None:
        """Initialize the switch."""
        super().__init__(instance, osoenergy_device)

        device_id = osoenergy_device.device_id
        self._attr_unique_id = f"{device_id}_{description.key}"
        self.entity_description = description

    @property
    def is_on(self) -> bool:
        """Return true if the switch is on."""
        return self.entity_description.value(self.device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on(self.osoenergy, self.device)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off(self.osoenergy, self.device)

    async def async_update(self):
        """Update all data for OSO Energy."""
        await self.osoenergy.session.update_data()
        self.device = await self.osoenergy.switch.get_switch(self.device)
