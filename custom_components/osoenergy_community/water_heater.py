"""Support for OSO Energy water heaters."""
from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.components.water_heater import (
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_OFF, STATE_ON, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from . import OSOEnergyEntity
from .const import DOMAIN

ATTR_UNTIL_TEMP_LIMIT = "until_temp_limit"
ATTR_V40MIN = "v40_min"
EXTRA_HEATER_ATTR: dict[str, dict[str, Any]] = {
    "heater_state": {
        "ha_name": "heater_state",
        "value_mapping": {
            "on": STATE_ON,
            "off": STATE_OFF,
        },
    },
    "heater_mode": {
        "ha_name": "heater_mode",
        "value_mapping": {
            "auto": "auto",
            "manual": "manual",
            "off": STATE_OFF,
            "legionella": "legionella",
            "powersave": "power_save",
            "extraenergy": "extra_energy",
            "voltage": "voltage",
            "ffr": "ffr",
        },
    },
    "optimization_mode": {
        "ha_name": "optimization_mode",
        "value_mapping": {
            "off": STATE_OFF,
            "oso": "oso",
            "gridcompany": "grid_company",
            "smartcompany": "smart_company",
            "advanced": "advanced",
        },
    },
    "profile": {"ha_name": "profile", "is_profile": True},
    "volume": {"ha_name": "volume"},
    "v40_min": {"ha_name": "v40_min"},
    "v40_level_min": {"ha_name": "v40_level_min"},
    "v40_level_max": {"ha_name": "v40_level_max"},
}
HEATER_MIN_TEMP = 10
HEATER_MAX_TEMP = 80
MANUFACTURER = "OSO Energy"
SERVICE_TURN_ON = "turn_on"
SERVICE_TURN_OFF = "turn_off"
SERVICE_SET_V40MIN = "set_v40_min"
SERVICE_SET_PROFILE = "set_profile"


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up OSO Energy heater based on a config entry."""
    osoenergy = hass.data[DOMAIN][entry.entry_id]
    devices = osoenergy.session.device_list.get("water_heater")
    entities = []
    if devices:
        for dev in devices:
            entities.append(OSOEnergyWaterHeater(osoenergy, dev))
    async_add_entities(entities, True)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        SERVICE_TURN_ON,
        {vol.Required(ATTR_UNTIL_TEMP_LIMIT): vol.All(cv.boolean)},
        "async_oso_turn_on",
    )

    platform.async_register_entity_service(
        SERVICE_TURN_OFF,
        {vol.Required(ATTR_UNTIL_TEMP_LIMIT): vol.All(cv.boolean)},
        "async_oso_turn_off",
    )

    platform.async_register_entity_service(
        SERVICE_SET_V40MIN,
        {
            vol.Required(ATTR_V40MIN): vol.All(
                vol.Coerce(float), vol.Range(min=200, max=550)
            ),
        },
        "async_set_v40_min",
    )

    service_set_profile_schema = {}
    for hour in range(24):
        service_set_profile_schema[vol.Optional(f"hour_{hour:02d}")] = vol.All(
            vol.Coerce(int), vol.Range(min=10, max=75)
        )

    platform.async_register_entity_service(
        SERVICE_SET_PROFILE,
        service_set_profile_schema,
        "async_set_profile",
    )


def _get_utc_hour(local_hour: int):
    """Get the utc hour."""
    now = dt_util.now()
    local_time = now.replace(hour=local_hour, minute=0, second=0, microsecond=0)
    utc_hour = dt_util.as_utc(local_time)
    return utc_hour.hour


def _get_local_hour(utc_hour: int):
    """Get the local hour."""
    now = dt_util.utcnow()
    now_local = dt_util.now()
    utc_time = now.replace(hour=utc_hour, minute=0, second=0, microsecond=0)
    local_hour = dt_util.as_local(utc_time)
    local_hour = local_hour.replace(
        year=now_local.year, month=now_local.month, day=now_local.day
    )
    return local_hour


def _convert_profile_to_local(values):
    """Convert UTC profile to local."""
    profile = [None] * 24
    for hour in range(24):
        local_hour = _get_local_hour(hour)
        local_hour_string = local_hour.strftime("%Y-%m-%dT%H:%M:%S%z")
        profile[local_hour.hour] = {local_hour_string: values[hour]}

    return profile


class OSOEnergyWaterHeater(OSOEnergyEntity, WaterHeaterEntity):
    """OSO Energy Water Heater Device."""

    _attr_name = None
    _attr_supported_features = WaterHeaterEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_translation_key = "saga_heater"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device["device_id"])},
            manufacturer=MANUFACTURER,
            model=self.device["device_type"],
            name=self.device["device_name"],
        )

    @property
    def available(self) -> bool:
        """Return if the device is available."""
        return self.device.get("attributes", {}).get("available", False)

    @property
    def current_operation(self) -> str:
        """Return current operation."""
        return self.device["status"]["current_operation"]

    @property
    def current_temperature(self) -> float:
        """Return the current temperature of the heater."""
        return self.device.get("attributes", {}).get("current_temperature", 0)

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.device.get("attributes", {}).get("target_temperature", 0)

    @property
    def target_temperature_high(self) -> float:
        """Return the temperature we try to reach."""
        return self.device.get("attributes", {}).get("target_temperature_high", 0)

    @property
    def target_temperature_low(self) -> float:
        """Return the temperature we try to reach."""
        return self.device.get("attributes", {}).get("target_temperature_low", 0)

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.device.get("attributes", {}).get("min_temperature", HEATER_MIN_TEMP)

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.device.get("attributes", {}).get("max_temperature", HEATER_MAX_TEMP)

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        """Return the state attributes."""
        attr: dict[str, Any] = {}

        for attribute, attribute_config in EXTRA_HEATER_ATTR.items():
            value = self.device.get("attributes", {}).get(attribute)
            final = value

            value_mappings = attribute_config.get("value_mapping")
            is_profile = attribute_config.get("is_profile")
            if is_profile:
                final = _convert_profile_to_local(value)
            elif value_mappings:
                value_key = f"{value}".lower()
                final = value_mappings.get(value_key, final)

            attr.update({str(attribute_config.get("ha_name")): final})

        return attr

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on hotwater."""
        await self.osoenergy.hotwater.turn_on(self.device, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off hotwater."""
        await self.osoenergy.hotwater.turn_off(self.device, True)

    async def async_oso_turn_on(self, until_temp_limit) -> None:
        """Handle the service call."""
        await self.osoenergy.hotwater.turn_on(self.device, until_temp_limit)

    async def async_oso_turn_off(self, until_temp_limit) -> None:
        """Handle the service call."""
        await self.osoenergy.hotwater.turn_off(self.device, until_temp_limit)

    async def async_set_v40_min(self, v40_min) -> None:
        """Handle the service call."""
        await self.osoenergy.hotwater.set_v40_min(self.device, v40_min)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        target_temperature = int(kwargs.get("temperature", self.target_temperature))
        profile = [target_temperature] * 24

        await self.osoenergy.hotwater.set_profile(self.device, profile)

    async def async_set_profile(self, **kwargs: Any) -> None:
        """Handle the service call."""
        profile = self.device.get("attributes", {}).get("profile")

        for hour in range(24):
            hour_key = f"hour_{hour:02d}"

            if hour_key in kwargs:
                profile[_get_utc_hour(hour)] = kwargs[hour_key]

        await self.osoenergy.hotwater.set_profile(self.device, profile)

    async def async_update(self) -> None:
        """Update all Node data from Hive."""
        await self.osoenergy.session.update_data()
        self.device = await self.osoenergy.hotwater.get_water_heater(self.device)
