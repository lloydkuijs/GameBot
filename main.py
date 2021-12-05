import pymem
import botvision
from time import sleep
import win32gui
import win32process
import numpy as np
import json

with open('addresses.json') as userInfo:
    data = json.load(userInfo)
    print(data)
