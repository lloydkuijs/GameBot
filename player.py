import random
import time
from time import sleep
import pydirectinput as input
import enum
import json
from botvision import BotVision

import time

class FarmComponent:

    def __init__(self, bot_vision):
        self.bot_vision = bot_vision

    def perform(self):
        pos, match = self.bot_vision.match_template('resources/enemy_health.png')

        if match < 0.9:
            print("Enemies not found, switching screens")
        else:
            self.bot_vision.click(pos)



    def update(self):
        self.health = self.read_integer("health")
        self.mp = self.read_integer("mp")
        self.max_mp = self.read_integer("maxMp")
        self.x = self.read_float("x")
        self.y = self.read_float("y")
        self.z = self.read_float("z")
        self.camera_x = self.read_float("cameraX")
        self.camera_y = self.read_float("cameraY")
        self.camera_z = self.read_float("cameraZ")

        self.target_selected = not self.read_bool("targetSelected")

    def is_moving(self):
        self.old_x = self.x
        self.old_y = self.y
        self.old_z = self.z

        sleep(0.02)
        self.update()

        if self.x != self.old_x or self.y != self.old_y or self.z != self.old_z:
            return True

        return False

    def turn_camera(self):
        offset = 50

        new_x = self.x
        new_y = self.y
        new_z = self.z + 50

        if self.direction == Direction.UNDEFINED:
            self.direction = Direction.FORWARD
            new_x = self.x
            new_y = self.y - 120
            new_z = self.z + 50
        elif self.direction == Direction.FORWARD:
            self.direction = Direction.BACKWARD
            new_x = new_x
            new_y = new_y - 120
        elif self.direction == Direction.BACKWARD:
            self.direction = Direction.RIGHT
            new_x = new_x
            new_y = new_y + 120
        elif self.direction == Direction.RIGHT:
            self.direction = Direction.LEFT
            new_x = new_x + 120
            new_y = new_y
        elif self.direction == Direction.LEFT:
            self.direction = Direction.FORWARD
            new_x = new_x - 120
            new_y = new_y
        else:
            raise Exception("Direction is undefined")

        self.write_float("cameraX", new_x)
        self.write_float("cameraY", new_y)
        self.write_float("cameraZ", new_z)

        self.update()
        sleep(2)

    def collect_items(self):
        for i in range(random.randint(3, 5)):
            input.press('f3')
            sleep(0.5)

    def untarget_enemy(self):
        window_pos = self.winCap.match_template('resources/untarget_button.PNG')
        self.__win_capture.click(window_pos)

    def attack_enemy(self):
        window_pos = self.winCap.match_template('resources/enemy-health.PNG')

        window_pos = int(window_pos[0]), int(window_pos[1] + 50)
        self.__win_capture.click(window_pos)

        # wait for target to update
        sleep(1)
        self.update()

        if self.target_selected:
            self.combat_start = time.time()

    def combo(self):
        self.update()
        pass

class TaskPerformer:

    def __init__(self, className):
        gameClass = None

        with open('classes.json') as userInfo:
            classes = json.load(userInfo)

if __name__ == '__main__':
    botVision = BotVision()
    sleep(5)
    botVision.attach_top_window()

    component = FarmComponent(botVision)
    component.perform()
    quit()


class Direction(enum.Enum):
    UNDEFINED = -1
    FORWARD = 0
    BACKWARD = 1
    RIGHT = 2
    LEFT = 3

class Player:

    __win_capture = None
    __pym = None
    addresses = {}

    name = ""
    health = 0
    mp = 0
    max_mp = 0

    x = 0
    y = 0
    z = 0

    old_x = 0
    old_y = 0
    old_z = 0

    camera_x = 0
    camera_y = 0
    camera_z = 0

    target_selected = 0
    combat_start = 0

    direction = Direction.UNDEFINED

    def __init__(self, win_capture, pym, addresses, abilities):
        self.__win_capture = win_capture
        self.__pym = pym

        self.addresses = addresses
        self.abilities = abilities

        self.update()
        self.turn_camera()
        self.update()

    # Finds the last address within a series of pointers + offsets
    def find_last_address(self, attr, offsets):

        if len(offsets) == 0:
            return self.addresses[attr]

        value = self.__pym.read_int(self.addresses[attr])

        for i in range(len(offsets)):
            offset = offsets[i]

            if i + 1 == len(offsets):
                value = value + offsets[i]
                break

            value = self.__pym.read_int(value + offset)

        return value

    # Gets the value as integer directly or from a series of nested pointers
    def read_integer(self, attr, offsets=[]):
        return self.__pym.read_int(self.find_last_address(attr, offsets))

    # Gets the final value as integer directly or from a series of nested addresses
    def read_float(self, attr, offsets=[]):
        return self.__pym.read_float(self.find_last_address(attr, offsets))

    # Reads a string directly from the given address
    def read_string(self, attr, offsets=[]):
        return self.__pym.read_string(self.find_last_address(attr, offsets))

    def read_bool(self, attr, offsets=[]):
        return bool(self.read_integer(attr, offsets))

    def read_bool(self, attr, offsets=[]):
        return self.__pym.read_bool(self.find_last_address(attr, offsets))

    def write_float(self, attr, value, offsets=[]):
        self.__pym.write_float(self.find_last_address(attr, offsets), value)

    def update(self):
        self.health = self.read_integer("health")
        self.mp = self.read_integer("mp")
        self.max_mp = self.read_integer("maxMp")
        self.x = self.read_float("x")
        self.y = self.read_float("y")
        self.z = self.read_float("z")
        self.camera_x = self.read_float("cameraX")
        self.camera_y = self.read_float("cameraY")
        self.camera_z = self.read_float("cameraZ")

        self.target_selected = not self.read_bool("targetSelected")

    def is_moving(self):
        self.old_x = self.x
        self.old_y = self.y
        self.old_z = self.z

        sleep(0.02)
        self.update()

        if self.x != self.old_x or self.y != self.old_y or self.z != self.old_z:
            return True

        return False

    def turn_camera(self):
        offset = 50

        new_x = self.x
        new_y = self.y
        new_z = self.z + 50

        if self.direction == Direction.UNDEFINED:
            self.direction = Direction.FORWARD
            new_x = self.x
            new_y = self.y - 120
            new_z = self.z + 50
        elif self.direction == Direction.FORWARD:
            self.direction = Direction.BACKWARD
            new_x = new_x
            new_y = new_y - 120
        elif self.direction == Direction.BACKWARD:
            self.direction = Direction.RIGHT
            new_x = new_x
            new_y = new_y + 120
        elif self.direction == Direction.RIGHT:
            self.direction = Direction.LEFT
            new_x = new_x + 120
            new_y = new_y
        elif self.direction == Direction.LEFT:
            self.direction = Direction.FORWARD
            new_x = new_x - 120
            new_y = new_y
        else:
            raise Exception("Direction is undefined")

        self.write_float("cameraX", new_x)
        self.write_float("cameraY", new_y)
        self.write_float("cameraZ", new_z)

        self.update()
        sleep(2)

    def collect_items(self):
        for i in range(random.randint(3, 5)):
            input.press('f3')
            sleep(0.5)

    def untarget_enemy(self):
        window_pos = self.winCap.match_template('resources/untarget_button.PNG')
        self.__win_capture.click(window_pos)

    def attack_enemy(self):
        window_pos = self.winCap.match_template('resources/enemy-health.PNG')

        window_pos = int(window_pos[0]), int(window_pos[1] + 50)
        self.__win_capture.click(window_pos)

        # wait for target to update
        sleep(1)
        self.update()

        if self.target_selected:
            self.combat_start = time.time()

    def combo(self):
        self.update()
        pass





