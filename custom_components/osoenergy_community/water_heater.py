"""Support for OSO Energy water heaters."""
from apyosoenergyapi import OSOEnergy
from apyosoenergyapi.helper.const import OSOEnergyWaterHeaterData
from typing import Any

import voluptuous as vol

from homeassistant.components.water_heater import (
    STATE_ECO,
    STATE_ELECTRIC,
    STATE_HIGH_DEMAND,
    STATE_OFF,
    WaterHeaterEntity,
    WaterHeaterEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.dt as dt_util

from . import OSOEnergyEntity
from .const import DOMAIN

ATTR_UNTIL_TEMP_LIMIT = "until_temp_limit"
ATTR_V40MIN = "v40_min"
CURRENT_OPERATION_MAP: dict[str, Any] = {
    "default": {
        "off": STATE_OFF,
        "powersave": STATE_OFF,
        "extraenergy": STATE_HIGH_DEMAND,
    },
    "oso": {
        "auto": STATE_ECO,
        "off": STATE_OFF,
        "powersave": STATE_OFF,
        "extraenergy": STATE_HIGH_DEMAND,
    },
}
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


class OSOEnergyWaterHeater(
    OSOEnergyEntity[OSOEnergyWaterHeaterData], WaterHeaterEntity
):
    """OSO Energy Water Heater Device."""

    _attr_name = None
    _attr_supported_features = WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.ON_OFF
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        instance: OSOEnergy,
        osoenergy_device: OSOEnergyWaterHeaterData,
    ) -> None:
        """Initialize the Advantage Air timer control."""
        super().__init__(instance, osoenergy_device)
        self._attr_unique_id = osoenergy_device.device_id

    @property
    def available(self) -> bool:
        """Return if the device is available."""
        return self.device.available

    @property
    def current_operation(self) -> str:
        """Return current operation."""
        status = self.device.current_operation
        if status == "off":
            return STATE_OFF

        optimization_mode = self.device.optimization_mode.lower()
        heater_mode = self.device.heater_mode.lower()
        if optimization_mode in CURRENT_OPERATION_MAP:
            return CURRENT_OPERATION_MAP[optimization_mode].get(
                heater_mode, STATE_ELECTRIC
            )

        return CURRENT_OPERATION_MAP["default"].get(heater_mode, STATE_ELECTRIC)

    @property
    def current_temperature(self) -> float:
        """Return the current temperature of the heater."""
        return self.device.current_temperature

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.device.target_temperature

    @property
    def target_temperature_high(self) -> float:
        """Return the temperature we try to reach."""
        return self.device.target_temperature_high

    @property
    def target_temperature_low(self) -> float:
        """Return the temperature we try to reach."""
        return self.device.target_temperature_low

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return self.device.min_temperature

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return self.device.max_temperature

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
        profile = self.device.profile

        for hour in range(24):
            hour_key = f"hour_{hour:02d}"

            if hour_key in kwargs:
                profile[_get_utc_hour(hour)] = kwargs[hour_key]

        await self.osoenergy.hotwater.set_profile(self.device, profile)

    async def async_update(self) -> None:
        """Update all Node data from Hive."""
        await self.osoenergy.session.update_data()
        self.device = await self.osoenergy.hotwater.get_water_heater(self.device)
