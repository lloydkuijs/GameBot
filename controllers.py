import random
import time
from time import sleep
import pydirectinput as input
import enum
import json
import keyboard

class BaseController:
    def initialize(self):
        pass

    def run(self):
        pass

    def stop(self):
        pass

    def on_message_received(self, message: str):
        pass

class FarmingController(BaseController):
    player = None
    winCap = None
    combat_time_out = 6

    should_stop = False

    def __init__(self, player, winCap, combat_time_out=6):
        self.player = player
        self.winCap = winCap
        self.combat_time_out = combat_time_out

    # TODO: To be implemented
    def initialize(self):
        pass

    def run(self):
        self.player.update()

        # Still in combat
        if not self.player.target_selected:
            print("Searching for enemy...")
            self.player.attack_enemy()

            if self.player.target_selected:
                print("Enemy found!")
                start_attack = time.time()
            else:
                print("No enemy was found.. Turning camera.")
                self.player.turn_camera()

        elif self.player.target_selected:
            # Reset time if the player had to move to reach the target
            if self.player.is_moving():
                start_attack = time.time()
                return

            if self.should_stop:
                return

            # # Un-target if time out occurred and turn the camera
            # if time.time() - start_attack > self.combat_time_out:
            #     print("Time-out occurred.. Re-targeting.")
            #     self.player.untarget_enemy(self.winCap.match_template('resources/untarget_button.png'))
            #     self.player.turn_camera()
            #     in_combat = False
            #     searching_enemy = True

            self.player.combo()

            if not self.player.target_selected:
                # sleep(1)
                # player.collect_items()
                in_combat = False
                searching_enemy = True

    def stop(self):
        self.should_stop = True

    # TODO: message received should be implemented where the bot is temporarily paused to send back a message etc
    def on_message_received(self, message: str):
        pass
