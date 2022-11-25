# Temperature sensor app for raspberry pi

App that measures temperature sensors on a set interval via 1-Wire protocol (DSXXX) and saves the values to a csv-file. It can be controlled by a webinterface

## Sensor Daemon

It consists of a Python daemon. The daemon can be controlled by the settings.json file that must be present. An example file is in settings-example.json. The daemon runs every 10 seconds and checks if the last measurement is longer ago than the set interval. If this is the case, it reads all the sensors and adds a line to the csv data file. All data files can be found in the measurements directory

The daemon can be installed with systemd by using the linux/temperature-sensor-daemon.service file

## Web Frontend

For easy usage there is a node webfrontend, that also edits the settings.json file

Prepare the frontend by running npm install in server/ and install it with the systemd config file linux/tmeperature-sensor-frontend.service

## Dependencies

### Daemon
* python3
* python schedule library

### Frontend
* node 16
* npm

### wire-1 driver
* linux kernel XXX