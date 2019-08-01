# britishtelecom
Home Assistant Sensor to track BT phone &amp; BB status

This is a work-in-progress custom component that monitors the fault page on the BT website to check for any problems in your area.

https://my.bt.com/consumerFaultTracking/secure/faults/tracking.do?pageId=30

The above page requires a login with your BT username/password and submission of the telephone number in question and will then return an overview of the status.

A summary sensor will indicate if there are any faults, with attributes specifying more details if available.

Since this is based on scraping the website in question as opposed to an official API, this component may break at any time if BT changes the design.

In addition, please let me know if you have any errors reported and ideally send me the HTML of the page in question so I can improve the error handling and picking up of the correct data.

```yaml
# Example configuration.yaml entry
sensor:
  - platform: britishtelecom
    name: BTService       # Name of sensor
    host: 01234 567890    # Phone number to monitor status of
    username: user        # BT username
    password: pass        # BT password
```
