from distutils.command.config import config
import requests 

from configparser import ConfigParser, ExtendedInterpolation

from os import listdir


def upload_files(config: ConfigParser):
    url = config["upload"]["url"]

    param_name = config["upload"]["param_name"]
    path = config["upload"]["path"]
    files = [f for f in listdir(path)]

    for f in files: 
        filepath = "{}/{}".format(path, f)
        files = {param_name: open(filepath, "rb")}
        r = requests.post(url, files=files)
        print(r.text)


config = ConfigParser(interpolation=ExtendedInterpolation())
config.read("./config.ini") 
upload_files(config)