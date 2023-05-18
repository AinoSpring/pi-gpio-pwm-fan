import RPi.GPIO as GPIO
import json
import os
import time
import pathlib


abs_path = str(pathlib.Path(os.path.abspath(__file__)).parent)


def load_conf(path):
    with open(path, "r") as config_file:
        return json.load(config_file)


def calc_speed(temp, min_temp, max_temp, curve):
    temp_range = max_temp - min_temp
    temp_delta = (temp - min_temp) / temp_range
    return max(min(curve(temp_delta), 1), 0)


def fetch_temp(cmd):
    temp = os.popen(cmd).readline()
    return int(temp)


def main():
    conf = load_conf(os.path.join(abs_path, "config.json"))
    fan = GPIO.PWM(conf.get("fan_pin"))

    def curve(td):
        return eval(conf.get("curve"))

    try:
        while True:
            temp = fetch_temp(conf.get("cmd"))
            speed = calc_speed(temp, conf.get("min_temp"), conf.get("max_temp"), curve)
            fan.start(speed * 100)
            time.sleep(conf.get("refresh_time") / 1000)
    except KeyboardInterrupt:
        print("Program exited by user.")


if __name__ == "__main__":
    if not os.path.isfile(os.path.join(abs_path, "config.json")):
        with open(os.path.join(abs_path, "default_config.json"), "r") as def_conf_file:
            with open("config.json", "w") as conf_file:
                conf_file.write(def_conf_file.read())
    main()
