import pydirectinput as input
import os
from time import sleep
import json
import win32gui
import shutil
import ctypes
from botvision import BotVision

import botvision

class Account:
    def __init__(self, username, password, role, gameClass):
        self.username = username
        self.password = password
        self.role = role
        self.gameClass = gameClass

class LoginAutomator:
    hwnd = None
    bot_vision = None

    def __init__(self, account):
        self.account = account

        with open('gameAttributes.json', 'r') as attrsFile:
            game_attributes = json.loads(attrsFile.read())
            self.account_path = game_attributes['accountPath']
            self.exe_path = game_attributes['exePath']
            self.exe_name = game_attributes['exeName']

    def skip_startup(self):
        self.hwnd = win32gui.GetForegroundWindow()
        self.bot_vision = BotVision(self.hwnd)

    def startup(self):

        # Reset login file
        shutil.copyfile('account_file.ini', self.account_path)

        # Read in the file
        with open('account_file.ini', 'r') as file:
            file_data = file.read()
            file_data = file_data.replace('ACCOUNT=', 'ACCOUNT=' + self.username)
            file_data = file_data.replace('PASSWORD=', 'PASSWORD=' + self.password)

            # Write the file out again
            with open(self.account_path, 'w') as target_file:
                target_file.write(file_data)

        cur_dic = os.getcwd()

        os.chdir(self.exe_path)

        os.startfile(self.exe_path + "\\" + self.exe_name)
        sleep(30)

        os.chdir(cur_dic)

        self.hwnd = win32gui.GetForegroundWindow()
        self.bot_vision = BotVision(self.hwnd)

        pos, match = self.bot_vision.match_template('resources/login_button.png')

        if match < 0.9:
            ctypes.windll.user32.MessageBoxW(None, "ERROR: Could not find login button", "GameBot", 0)
            return False

        self.bot_vision.click(pos)

        sleep(2)

        self.bot_vision.click()

        sleep(3)

        pos, match = self.bot_vision.match_template('resources/start_button.png')

        if match < 0.9:
            ctypes.windll.user32.MessageBoxW(None, "ERROR: Could not find start button", "GameBot", 0)
            return False

        self.bot_vision.click(pos)

        sleep(5)

    def invite_team(self):
        self.bot_vision.bring_forward()
        sleep(2)
        input.keyDown('ctrl')
        input.press('z')
        input.keyUp('ctrl')

        sleep(1)

        pos, match = self.bot_vision.match_template('resources/friend_icon.png')
        input.rightClick()
        self.bot_vision.right_click(pos)
        sleep(2)

        pos, match = self.bot_vision.match_template('resources/invite_to_team_button.png')
        self.bot_vision.click(pos)

        sleep(2)

        input.keyDown('ctrl')
        input.press('z')
        input.keyUp('ctrl')

    def accept_team(self):
        self.bot_vision.bring_forward()
        sleep(2)

        pos, match = self.bot_vision.match_template('resources/join_team_button.png')
        self.bot_vision.click(pos)

    def team_up(self):
        if self.role == "Farming Leader":
            self.invite_team()
        elif self.role == "Farming":
            self.accept_team()
        else:
            pass


if __name__ == "__main__":
    with open('userInfo.json') as userInfo:
        data = json.load(userInfo)

        # farm leader is first
        account_data = data['accounts'][0]
        leader_account = Account(account_data['username'], account_data['password'],  account_data['role'], account_data['class'])

        leader_login = LoginAutomator(leader_account)
        sleep(5)
        leader_login.skip_startup()
        leader_login.invite_team()

