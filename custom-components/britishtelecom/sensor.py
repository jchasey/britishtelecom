"""
Support for BT Phone status.

For more details about this platform, please refer to the documentation at
https://github.com/jchasey/britishtelecom

"""

import logging
import voluptuous as vol
import mechanize
from bs4 import BeautifulSoup
import datetime
from datetime import date, datetime, timedelta

from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_USERNAME, CONF_PASSWORD,
    CONF_MONITORED_CONDITIONS, CONF_VERIFY_SSL)

DOMAIN = 'britishtelecom'
REQUIREMENTS = ["beautifulsoup4==4.8.0", "mechanize3==0.4.0"]
__version__ = "0.1"

_LOGGER = logging.getLogger(__name__)

# Only update once an hour
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60*60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_HOST): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):

    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    add_entities([BritishTelecomSensor(hass, name, host, username, password )], True)

    return True

class BritishTelecomSensor(Entity):

    def __init__(self, hass, name, host, username, password):
        """Initialize the sensor."""
        self._hass = hass
        self._name = name
        self._host = host
        self._username = username
        self._password = password
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return 'mdi:hotel'

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def state_attributes(self):
        """Return the device state attributes."""
        return self._attributes

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):

        # Browser
        br = mechanize.Browser()
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
        br.open('https://home.bt.com/login/loginform')

        # Select the first (index zero) form & login
        br.select_form(nr=0)
        br.form['USER'] = self._username
        br.form['PASSWORD'] = self._password
        br.submit()

        br.open('https://my.bt.com/consumerFaultTracking/secure/faults/tracking.do?pageId=31')
        br.select_form("healthecheck")
        br.form['phoneNumber'] = self._host
        br.submit()

        br.open('https://my.bt.com/consumerFaultTracking/secure/faults/tracking.do?pageId=30')

        soup = BeautifulSoup(br.response().read(),"html.parser")

        self._state = "OK"
        self._attributes = {}

        html_details = {    "Phone": [ "h4",{"class": "phone-icon"} ],
                            "BB":    [ "h4",{"class": "broadband-icon"} ],
                            "TV":    [ "h4",{"class": "tv-icon"} ],
                            "Sport": [ "h4",{"class": "sport-icon"} ],
                        }

        # Get a list of faults for our service and locally
        faults = soup.find_all("div",{"class": "faults"})

        if (faults[0]):
            for tag in html_details:
                for data in faults[0].find_all(html_details[tag][0],html_details[tag][1]):
                    status = data.next.next.next.string
                    self._attributes['Local_'+tag] = status
                    if (status != 'Everything seems OK'):
                        self._state = "Fault"

        if (faults[1]):
            for tag in html_details:
                for data in faults[1].find_all(html_details[tag][0],html_details[tag][1]):
                    status = data.next.next.next.string
                    self._attributes['Area_'+tag] = status
                    if (status != 'Everything seems OK'):
                        self._state = "Fault"

