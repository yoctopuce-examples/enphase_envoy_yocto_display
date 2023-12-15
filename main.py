# This is a sample Python script.
"""
This example provides functionality to interact with the Enphase® IQ Gateway API for monitoring
solar energy production and consumption data on the command line.

The functions in this module allow you to:
- Establish a secure gateway session
- Fetch production, consumption, and storage status from Enphase® IQ Gateway devices
- Retrieve human-readable power values
"""

import json  # This script makes heavy use of JSON parsing.
import os.path  # We check whether a file exists.
import sys  # We check whether we are running on Windows® or not.

# All the shared Enphase® functions are in these packages.
from enphase_api.cloud.authentication import Authentication
from enphase_api.local.gateway import Gateway
from yoctopuce.yocto_api import YAPI, YRefParam
from yoctopuce.yocto_display import YDisplayLayer, YDisplay


def get_secure_gateway_session(credentials):
    """
    Establishes a secure session with the Enphase® IQ Gateway API.

    This function manages the authentication process to establish a secure session with
    an Enphase® IQ Gateway.

    It handles JWT validation, token acquisition (if required) and initialises
    the Gateway API wrapper for subsequent interactions.

    It also downloads and stores the certificate from the gateway for secure communication.

    Args:
        credentials (dict): A dictionary containing the required credentials.

    Returns:
        Gateway: An initialised Gateway API wrapper object for interacting with the gateway.

    Raises:
        ValueError: If authentication fails or if required credentials are missing.
    """

    # Do we have a valid JSON Web Token (JWT) to be able to use the service?
    if not (credentials.get('gateway_token')
            and Authentication.check_token_valid(
                token=credentials['gateway_token'],
                gateway_serial_number=credentials.get('gateway_serial_number'))):
        # It is not valid so clear it.
        credentials['gateway_token'] = None

    # Do we still not have a Token?
    if not credentials.get('gateway_token'):
        # Do we have a way to obtain a token?
        if credentials.get('enphase_username') and credentials.get('enphase_password'):
            # Create a Authentication object.
            authentication = Authentication()

            # Authenticate with Entrez (French for "Access").
            if not authentication.authenticate(
                    username=credentials['enphase_username'],
                    password=credentials['enphase_password']):
                raise ValueError('Failed to login to Enphase® Authentication server ("Entrez")')

            # Does the user want to target a specific gateway or all uncommissioned ones?
            if credentials.get('gateway_serial_number'):
                # Get a new gateway specific token (installer = short-life, owner = long-life).
                credentials['gateway_token'] = authentication.get_token_for_commissioned_gateway(
                    gateway_serial_number=credentials['gateway_serial_number']
                )
            else:
                # Get a new uncommissioned gateway specific token.
                credentials['gateway_token'] = authentication.get_token_for_uncommissioned_gateway()

            # Update the file to include the modified token.
            with open('config.json', mode='w', encoding='utf-8') as json_file:
                json.dump(credentials, json_file, indent=4)
        else:
            # Let the user know why the program is exiting.
            raise ValueError('Unable to login to the gateway (bad, expired or missing token in credentials.json).')

    # Did the user override the library default hostname to the Gateway?
    host = credentials.get('gateway_host')

    # Download and store the certificate from the gateway so all future requests are secure.
    if not os.path.exists('gateway.cer'):
        Gateway.trust_gateway(host, "gateway.cer")

    # Instantiate the Gateway API wrapper (with the default library hostname if None provided).
    gateway = Gateway(host)

    # Are we not able to login to the gateway?
    if not gateway.login(credentials['gateway_token']):
        # Let the user know why the program is exiting.
        raise ValueError('Unable to login to the gateway (bad, expired or missing token in credentials.json).')

    # Return the initialised gateway object.
    return gateway


def get_solar_stats(gateway):
    """
      Get production and consumption statistics from the Solar Envoy Gateway
      Args:
           gateway: An initialised Gateway API wrapper object for interacting with the gateway.

      Returns:
          the current production and consumption in watt

      """
    production_statistics = gateway.api_call('/production.json')
    production = 0
    for device in production_statistics['production']:
        if device['type'] == 'inverters':
            production = device["wNow"]
            break
    consumption = 0

    for device in production_statistics['consumption']:
        if device['type'] == 'eim' and (
                device['measurementType'] == 'net-consumption' or device['measurementType'] == 'total-consumption'):
            consumption = device['wNow']
            break
    return production, consumption


def format_watts(watts):
    watts = round(watts)
    if abs(watts) < 1000:
        return "%d W" % watts
    return "%.1f W" % (watts / 1000.0)


def main():
    # Load credentials.
    print("Use Yoctopuce Library version %s" % YAPI.GetAPIVersion())
    if not os.path.exists('config.json'):
        print('No config.json file found.')
        sys.exit(1)

    with open('config.json', mode='r', encoding='utf-8') as json_file:
        config = json.load(json_file)

    # configure Yoctopuce library
    errmsg = YRefParam()
    res = YAPI.RegisterHub(config['yoctopuce_url'], errmsg)
    if res < 0:
        print('Unable to connect to %s (%s)' % (config['yoctopuce_url'], errmsg.value))
        sys.exit(1)

    # ensure we have a Yoctodisplay connected
    disp = YDisplay.FirstDisplay()
    if disp is None:
        print('No Yocto-MaxiDisplay connected on ' + config['yoctopuce_url'])
        sys.exit(1)

    # display clean up
    disp.resetAll()
    # retrieve the display size
    w = disp.get_displayWidth()
    h = disp.get_displayHeight()
    # retrieve the first layer
    l0 = disp.get_displayLayer(0)
    l0.clear()

    # Use a secure gateway initialisation flow.
    gateway = get_secure_gateway_session(config)

    while disp.isOnline():
        production, consumption = get_solar_stats(gateway)
        avail = production - consumption
        # display a text in the middle of the screen
        l0.clear()
        l0.selectFont('Large.yfm')
        l0.drawText(w / 2, h / 3, YDisplayLayer.ALIGN.CENTER, format_watts(avail))
        l0.selectFont('Medium.yfm')
        l0.drawText(w / 2, h * 2 / 3, YDisplayLayer.ALIGN.CENTER, "(" + format_watts(production) + ")")
        # sleep 5 seconds
        YAPI.Sleep(5000, errmsg)


# Launch the main method if invoked directly.
if __name__ == '__main__':
    main()
