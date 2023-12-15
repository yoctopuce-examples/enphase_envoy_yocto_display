# Enphase Envoy Yocto Display

A small program that displays the current production of the building's photovoltaic panels on a
Yocto-MaxiDisplay. The script fetches production and consumption data from an Envoy S Metered gateway
using the [Enphase-API library](https://github.com/Matthew1471/Enphase-API). The Yocto-MaxiDisplay is controlled
using [our Python library](https://github.com/yoctopuce/yoctolib_python)

You can read the article on that application on our web
site: https://www.yoctopuce.com/EN/article/displaying-solar-production-on-a-yoctodisplay

## Prerequisites

- [Yocto-MaxiDisplay](https://www.yoctopuce.com/EN/products/usb-displays/yocto-maxidisplay)
- [YoctoHub-Wireless-n](https://www.yoctopuce.com/EN/products/extensions-and-networking/yoctohub-wireless-n)
- Python 3.x
- [Enphase-API library](https://github.com/Matthew1471/Enphase-API)
- [Yoctopuce library for Python](https://github.com/yoctopuce/yoctolib_python)

## Installation

1. Clone this repository:

```
git clone https://github.com/your-username/your-project.git
```

2. Install dependencies:

```
pip install Enphase-API
pip install yoctopuce
```

3. Create a `config.json` file with the connections parameters (See `config.json.example`)
4. Run the Python script `display_solar_production.py`.

## Project Structure

- `display_solar_production.py`: Main script.
- `config.json.example`: a template of configuration.
- `README.md`: This file describing the project.
