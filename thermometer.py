import json
import sys
import datetime
import logging
import os
from os.path import exists
import schedule
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %I:%M:%S')


SENSOR_DIR = "/sys/bus/w1/devices"
SENSOR_FILE_NAME = "temperature"
MEASUREMENTS_DIR = "/home/pi/temperature-sensor-app/measurements"
CSV_DELIMITER = ";"
CSV_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
SETTINGS_FILE = "/home/pi/temperature-sensor-app/settings.json"

def main():
    schedule.every(10).seconds.do(run_measurement)
    while True:
        schedule.run_pending()
        time.sleep(1)

def open_settings():
    with open(SETTINGS_FILE) as settings_file:
        settings = json.load(settings_file)
    
    return settings

def prepare_sensor_list(settings):
    sensors = []
    sensors_folders = os.listdir(SENSOR_DIR)
    for s in sensors_folders:
        sensor_name = s
        sensor_enabled = True
        for mapping in settings['sensorMapping']:
            if mapping["id"] == s:
                sensor_name = mapping["name"]
                sensor_enabled = mapping["enabled"]
                break
        
        sensor_file = SENSOR_DIR + '/' + s + '/' + SENSOR_FILE_NAME

        if (sensor_enabled):
            sensors.append({
                "file": sensor_file,
                "name": sensor_name,
            })
    
    return sensors

def prepare_measurements_file(measurements_file_name, sensors):
    header_line = "date" + CSV_DELIMITER + CSV_DELIMITER.join(map(lambda x: x['name'], sensors))
    logging.debug(header_line)
    with open(measurements_file_name, "w") as data_file:
        data_file.write("sep=" + CSV_DELIMITER + "\n")
        data_file.write(header_line + "\n")

def read_sensors(sensors):
    measurements = []
    for sensor in sensors:
        if not exists(sensor['file']):
            logging.warning("Sensor file not found: " + str(sensor))
            measurements.append("Error")
        else:
            with open(sensor['file']) as sensor_file:
                temp = str(int(sensor_file.read()) / 1000.0).replace(".", ",")
                measurements.append(temp)
    
    return measurements

def update_last_measurement_time(time):
    settings = open_settings()
    new_settings = settings
    new_settings['lastMeasurement'] = time.isoformat()
    #logging.debug(json.dumps(new_settings, indent=4))

    with open(SETTINGS_FILE, 'w') as settings_file:
        settings_file.write(json.dumps(new_settings, indent=4))

def run_measurement():
    logging.debug('Starting papas thermometer app...')
    
    settings = open_settings()

    if not settings['measuring']:
        logging.debug("Nothing to do. Bye!")
        return
    
    now = datetime.datetime.now()
    last_measurement = datetime.datetime.fromisoformat(settings['lastMeasurement'])
    seconds_since_last_measurement = (now - last_measurement).seconds

    logging.debug("Seconds since last measurement: " + str(seconds_since_last_measurement))
    if(seconds_since_last_measurement < settings['intervalSeconds']):
        logging.debug("Not yet time to measure")
        return

    logging.debug("Doing new measurment")
    sensors = prepare_sensor_list(settings)            
    logging.debug("Sensors: " + str(sensors))

    measurements_file_name = MEASUREMENTS_DIR + "/" + settings['fileName']
    if not exists(measurements_file_name):
        logging.info("Creating new file " + measurements_file_name)
        prepare_measurements_file(measurements_file_name, sensors)

    measurements = read_sensors(sensors)    
    logging.info("Measured values: " + str(measurements))

    measurements_line = now.strftime(CSV_DATE_FORMAT) + CSV_DELIMITER + CSV_DELIMITER.join(measurements) + "\n"
    logging.debug("Add line to file: " + measurements_line)
    with open(measurements_file_name, "a") as data_file:
        data_file.write(measurements_line)

    update_last_measurement_time(now)

    logging.debug("Measuring done, bye!")


if __name__ == '__main__':
    main()
