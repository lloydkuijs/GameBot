import os
from time import sleep
import json
import win32gui
import shutil

import player
import ctypes

address_file = open('gameAttributes.json')
game_attributes = json.loads(address_file.read())

address_file = open('addresses.json')
player_attributes = json.loads(address_file.read())

exe_name = game_attributes['exeName']
exe_path = game_attributes['exePath']
account_file_path = game_attributes['accountPath']

def init_accounts():
    with open('userInfo.json') as userInfo:
        data = json.load(userInfo)

        for acc in data['accounts']:
            change_login(acc['username'], acc['password'])

            start_game()
            break


#init_accounts()

sleep(5)
player.open_friend_list()



