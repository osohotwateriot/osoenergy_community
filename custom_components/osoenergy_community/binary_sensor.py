"""Support for OSO Energy binary sensors."""
from collections.abc import Callable
from dataclasses import dataclass

from apyosoenergyapi import OSOEnergy
from apyosoenergyapi.helper.const import OSOEnergyBinarySensorData

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import OSOEnergyEntity
from .const import DOMAIN


@dataclass
class OSOEnergyBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Class describing OSO Energy heater binary sensor entities."""

    value: Callable[[OSOEnergy], StateType] = round


SENSOR_TYPES: tuple[OSOEnergyBinarySensorEntityDescription, ...] = (
    OSOEnergyBinarySensorEntityDescription(
        key="power_save",
        translation_key="power_save",
        value=lambda device: device.state,
    ),
    OSOEnergyBinarySensorEntityDescription(
        key="extra_energy",
        translation_key="extra_energy",
        value=lambda device: device.state,
    ),
    OSOEnergyBinarySensorEntityDescription(
        key="heater_state",
        translation_key="heater_state",
        value=lambda device: device.state,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up OSO Energy sensor."""
    osoenergy = hass.data[DOMAIN][entry.entry_id]
    devices = osoenergy.session.device_list.get("binary_sensor")
    entities = []
    if devices:
        for dev in devices:
            for description in SENSOR_TYPES:
                if dev.osoEnergyType.lower() == description.key:
                    entities.append(OSOEnergyBinarySensor(osoenergy, description, dev))

    async_add_entities(entities, True)


class OSOEnergyBinarySensor(
    OSOEnergyEntity[OSOEnergyBinarySensorData], BinarySensorEntity
):
    """OSO Energy Sensor Entity."""

    _attr_has_entity_name = True
    entity_description: OSOEnergyBinarySensorEntityDescription

    def __init__(
        self,
        instance: OSOEnergy,
        description: OSOEnergyBinarySensorEntityDescription,
        osoenergy_device: OSOEnergyBinarySensorData,
    ) -> None:
        """Initialize the Advantage Air timer control."""
        super().__init__(instance, osoenergy_device)

        device_id = osoenergy_device.device_id
        self._attr_unique_id = f"{device_id}_{description.key}"
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return the state of the sensor."""
        return self.entity_description.value(self.device)

    async def async_update(self):
        """Update all data for OSO Energy."""
        await self.osoenergy.session.update_data()
        self.device = await self.osoenergy.binary_sensor.get_sensor(self.device)
