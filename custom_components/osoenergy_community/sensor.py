"""Support for OSO Energy sensors."""
from apyosoenergyapi import OSOEnergy
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfEnergy, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import OSOEnergyEntity
from .const import DOMAIN


@dataclass
class OSOEnergySensorEntityDescription(SensorEntityDescription):
    """Class describing OSO Energy heater sensor entities."""

    value: Callable[[OSOEnergy], StateType] = round


SENSOR_TYPES: tuple[OSOEnergySensorEntityDescription, ...] = (
    OSOEnergySensorEntityDescription(
        key="power_save",
        translation_key="power_save",
        device_class=SensorDeviceClass.ENUM,
        value=lambda device: device["status"]["state"],
    ),
    OSOEnergySensorEntityDescription(
        key="extra_energy",
        translation_key="extra_energy",
        device_class=SensorDeviceClass.ENUM,
        value=lambda device: device["status"]["state"],
    ),
    OSOEnergySensorEntityDescription(
        key="power_load",
        translation_key="power_load",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        value=lambda device: device["status"]["state"],
    ),
    OSOEnergySensorEntityDescription(
        key="tapping_capacity_kwh",
        translation_key="tapping_capacity_kwh",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value=lambda device: device["status"]["state"],
    ),
    OSOEnergySensorEntityDescription(
        key="capacity_mixed_water_40",
        translation_key="capacity_mixed_water_40",
        device_class=SensorDeviceClass.VOLUME,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        value=lambda device: device["status"]["state"],
    ),
    OSOEnergySensorEntityDescription(
        key="v40_min",
        translation_key="v40_min",
        device_class=SensorDeviceClass.VOLUME,
        native_unit_of_measurement=UnitOfVolume.LITERS,
        value=lambda device: device["status"]["state"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up OSO Energy sensor."""
    osoenergy = hass.data[DOMAIN][entry.entry_id]
    devices = osoenergy.session.device_list.get("sensor")
    entities = []
    if devices:
        for dev in devices:
            for description in SENSOR_TYPES:
                if dev["osoEnergyType"].lower() == description.key:
                    entities.append(OSOEnergySensor(osoenergy, description, dev))

    async_add_entities(entities, True)


class OSOEnergySensor(OSOEnergyEntity, SensorEntity):
    """OSO Energy Sensor Entity."""

    _attr_has_entity_name = True
    entity_description: OSOEnergySensorEntityDescription

    def __init__(
        self,
        instance: OSOEnergy,
        description: OSOEnergySensorEntityDescription,
        osoenergy_device: dict[str, Any],
    ) -> None:
        """Initialize the Advantage Air timer control."""
        super().__init__(instance, osoenergy_device)

        device_id = osoenergy_device["device_id"]
        self._attr_unique_id = f"{device_id}_{description.key}"
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value(self.device)

    async def async_update(self):
        """Update all data for OSO Energy."""
        await self.osoenergy.session.update_data()
        self.device = await self.osoenergy.sensor.get_sensor(self.device)
