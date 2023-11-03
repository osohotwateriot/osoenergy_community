# OSO Energy Community

![Last release](https://img.shields.io/github/release-date/osohotwateriot/osoenergy_community?style=flat-square)
![Version](https://img.shields.io/github/v/release/osohotwateriot/osoenergy_community
)
![Code size](https://img.shields.io/github/languages/code-size/osohotwateriot/osoenergy_community?style=flat-square)

The OSO Energy Community custom integration allows you to interact with supported devices and services offered by [OSO Energy](https://www.osoenergy.no)

This OSO Energy Community custom integration uses a subscription key, which users can create for their accounts on the [OSO Energy website](https://portal.osoenergy.no/), to configure it within Home Assistant. Once configured Home Assistant will detect and add all OSO Energy devices.

## Installation

### Manual installation

Download the `osoenergy_community` folder and all of it's contents from the [repository](https://github.com/osohotwateriot/osoenergy_community) and copy it to your Home Assistant's `/config/custom_components` folder. Create the `custom_components` folder it it does not exist.
Restart Home Assistant.

### HACS installation

Search for the `OSO Energy HACS` integration and download it.
Restart Home Assistant.

### Custom repoditory installation

If you don't see the OSO Energy Community integration in HACS you can add it as a custom repository:

* Navigate to `HACS` and click on the three dots in the top right corner.
* Select `Custom repositories`
* Fill `osohotwateriot/osoenergy_community` for repository and select `Integration` for category
* Click on `ADD`

After executing the steps above the integration should appear on your HACS page and you can download it.
Restart Home Assistant.

### Add the integration

To add devices execute the following steps:

* Navigate to `Settings` &rarr; `Devices and services` &rarr; `+ ADD INTEGRATION`
* Search for `OSO Energy HACS` and select it
* Enter the generated subscription key for your account

For multiple accounts execute the steps above again.

## Services

### Service `osoenergy_community.turn_on`

You can use the service `osoenergy_community.turn_on` to turn on the heating on your device for one hour or until the maximum temperature is reached.

| Service data attribute | Optional | Description                                                                                                      |
| ---------------------- | -------- | ---------------------------------------------------------------------------------------------------------------- |
| `entity_id`            | no       | String, Name of entity e.g., `water_heater.heater`                                                               |
| `until_temp_limit`     | no       | Choose if heating should be on until maximum temperature (`True`) is reached or for one hour (`False`), e.g., `True` |

Examples:

```yaml
# Example script to turn on heating, until temp limit specified.
script:
  turn_on:
    sequence:
      - service: osoenergy_community.turn_on
        target:
          entity_id: water_heater.heater
        data:
          until_temp_limit: true
```

### Service `osoenergy_community.turn_off`

You can use the service `osoenergy_community.turn_off` to turn off the heating on your device for one hour or until the minimum temperature is reached.

| Service data attribute | Optional | Description                                                                                                       |
| ---------------------- | -------- | ----------------------------------------------------------------------------------------------------------------- |
| `entity_id`            | no       | String, Name of entity e.g., `water_heater.heater`                                                                |
| `until_temp_limit`     | no       | Choose if heating should be off until minimum temperature (`True`) is reached or for one hour (`False`), e.g., `True` |

Examples:

```yaml
# Example script to turn off heating, until temp limit specified.
script:
  turn_off:
    sequence:
      - service: osoenergy_community.turn_off
        target:
          entity_id: water_heater.heater
        data:
          until_temp_limit: true
```

### Service `osoenergy_community.set_v40_min`

You can use the service `osoenergy_community.set_v40_min` to set the minimum quantity of water at 40°C for a water heater.

| Service data attribute | Optional | Description                                                                   |
| ---------------------- | -------- | ----------------------------------------------------------------------------- |
| `entity_id`            | no       | String, Name of entity e.g., `water_heater.heater`                            |
| `v40_min`              | no       | Specify the minimum quantity of water at 40°C for a water heater, e.g., `240` |

Examples:

```yaml
# Example script to set minimum water level on a water heater, v40 min specified.
script:
  set_v40:
    sequence:
      - service: osoenergy_community.set_v40_min
        target:
          entity_id: water_heater.heater
        data:
          v40_min: 240
```

### Service `osoenergy_community.set_profile`

You can use the service `osoenergy_community.set_profile` to set the temperature profile for a water heater.

| Service data attribute | Optional | Description                                        |
| ---------------------- | -------- | -------------------------------------------------- |
| `entity_id`            | no       | String, Name of entity e.g., `water_heater.heater` |
| `hour_00`              | yes      | The temperature at hour 00:00 (Local) for a heater   |
| `hour_01`              | yes      | The temperature at hour 01:00 (Local) for a heater   |
| `hour_02`              | yes      | The temperature at hour 02:00 (Local) for a heater   |
| `hour_03`              | yes      | The temperature at hour 03:00 (Local) for a heater   |
| `hour_04`              | yes      | The temperature at hour 04:00 (Local) for a heater   |
| `hour_05`              | yes      | The temperature at hour 05:00 (Local) for a heater   |
| `hour_06`              | yes      | The temperature at hour 06:00 (Local) for a heater   |
| `hour_07`              | yes      | The temperature at hour 07:00 (Local) for a heater   |
| `hour_08`              | yes      | The temperature at hour 08:00 (Local) for a heater   |
| `hour_09`              | yes      | The temperature at hour 09:00 (Local) for a heater   |
| `hour_10`              | yes      | The temperature at hour 10:00 (Local) for a heater   |
| `hour_11`              | yes      | The temperature at hour 11:00 (Local) for a heater   |
| `hour_12`              | yes      | The temperature at hour 12:00 (Local) for a heater   |
| `hour_13`              | yes      | The temperature at hour 13:00 (Local) for a heater   |
| `hour_14`              | yes      | The temperature at hour 14:00 (Local) for a heater   |
| `hour_15`              | yes      | The temperature at hour 15:00 (Local) for a heater   |
| `hour_16`              | yes      | The temperature at hour 16:00 (Local) for a heater   |
| `hour_17`              | yes      | The temperature at hour 17:00 (Local) for a heater   |
| `hour_18`              | yes      | The temperature at hour 18:00 (Local) for a heater   |
| `hour_19`              | yes      | The temperature at hour 19:00 (Local) for a heater   |
| `hour_20`              | yes      | The temperature at hour 20:00 (Local) for a heater   |
| `hour_21`              | yes      | The temperature at hour 21:00 (Local) for a heater   |
| `hour_22`              | yes      | The temperature at hour 22:00 (Local) for a heater   |
| `hour_23`              | yes      | The temperature at hour 23:00 (Local) for a heater   |

Examples:

```yaml
# Example script to set minimum water level on a water heater, v40 min specified.
script:
  set_profile:
    sequence:
      - service: osoenergy_community.set_optimization_mode
        target:
          entity_id: water_heater.heater
        data:
          hour_00: 70
          hour_01: 70
          hour_02: 70
          hour_03: 70
          hour_04: 70
          hour_05: 70
          hour_06: 70
          hour_07: 70
          hour_08: 70
          hour_09: 70
          hour_10: 70
          hour_11: 70
          hour_12: 70
          hour_13: 70
          hour_14: 70
          hour_15: 70
          hour_16: 70
          hour_17: 70
          hour_18: 70
          hour_19: 70
          hour_20: 70
          hour_21: 70
          hour_22: 70
          hour_23: 70
```

## Platforms

### Sensor

The `osoenergy` sensor integration exposes OSO Energy data as a sensor.

The platform exposes the following sensors:

* Power Save status for water heaters.
* Extra Energy status for water heaters.
* Power load (kW) for water heaters.
* Tapping capacity (kWh) for water heaters.
* Capacity mixed water at 40°C (L) for water heaters.
* V40 Min (L) for water heaters.

### Water Heater

The `osoenergy_community` water heater platform integrates your OSO Energy devices into Home Assistant.

The platform supports the following OSO Energy devices:

* Water Heaters
