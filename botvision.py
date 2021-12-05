import numpy as np
import win32con
import win32ui
import win32gui
import win32process
import pydirectinput
import pymem
from time import sleep
import cv2 as cv

# Captures the first window it can find on the screen,
class BotVision:

    # properties
    win_width = 0
    win_height = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    border_pixels = 12
    titleBar_pixels = 30
    memory = None

    # Constructor used for testing
    def __init__(self):
        pass

    # Attaches
    def target_top_window(self):
        self.target_window(win32gui.GetForegroundWindow())

    def target_window(self, hwnd):
        self.hwnd = hwnd

        # Initialize memory reader (Pymem library)
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)
        self.memory = pymem.Pymem()
        self.memory.open_process_from_id(pid)

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.win_width = window_rect[2] - window_rect[0]
        self.win_height = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        self.win_width = self.win_width - (self.border_pixels * 2)
        self.win_height = self.win_height - self.titleBar_pixels - self.border_pixels
        self.cropped_x = self.border_pixels
        self.cropped_y = self.titleBar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

    # Finds the last address within a series of pointers + offsets and offsets the given address by the
    # game's base address
    def find_last_address(self, address, offsets):

        address = self.memory.base_address + address

        if len(offsets) == 0:
            return address

        subAddress = self.memory.read_int(address)

        for i in range(len(offsets)):
            offset = offsets[i]

            if i + 1 == len(offsets):
                subAddress = subAddress + offsets[i]
                break

            subAddress = self.memory.read_int(subAddress + offset)

        return subAddress

    # Gets the value as integer directly or from a series of nested pointers
    def read_integer(self, address, offsets=[]):
        return self.memory.read_int(self.find_last_address(address, offsets))

    # Gets the final value as integer directly or from a series of nested addresses
    def read_float(self, address, offsets=[]):
        return self.memory.read_float(self.find_last_address(address, offsets))

    # Reads a string directly from the given address
    def read_string(self, address, offsets=[]):
        return self.memory.read_string(self.find_last_address(address, offsets))

    def read_bool(self, address, offsets=[]):
        return bool(self.read_integer(address, offsets))

    def read_bool(self, address, offsets=[]):
        return self.memory.read_bool(self.find_last_address(address, offsets))

    def write_float(self, address, value, offsets=[]):
        self.memory.write_float(self.find_last_address(address, offsets), value)

    # Returns the center location of the best match for the given template and its related match percentage
    def match_template(self, template_path):
        template = cv.imread(template_path, cv.IMREAD_UNCHANGED)

        print(template is None)
        template_width = template.shape[1]
        template_height = template.shape[0]

        # get an updated image of the game
        snapshot = self.get_snapshot()

        result = cv.matchTemplate(snapshot, template, cv.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        center_match = max_loc[0] + template_width / 2, max_loc[1] + template_height

        return center_match, max_val

    # Checks if the given window is on the foreground
    def window_active(self):
        return win32gui.GetForegroundWindow() == self.hwnd

    def get_snapshot(self):

        # get the window image data
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.win_width, self.win_height)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.win_width, self.win_height), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.win_height, self.win_width, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # NOTE: Commented out since this was actually causing the exact error it was  supposed to prevent,
        # uncomment if any alpha errors occur.
        #img = img[...,:3]

        img = np.ascontiguousarray(img)

        return img

    # translate a pixel position on a screenshot image to a pixel position on the screen.
    # pos = (x, y)
    # WARNING: if you move the window being captured after execution is started, this will
    # return incorrect coordinates, because the window position is only calculated in
    # the __init__ constructor.
    def get_screen_position(self, pos):
        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

        return pos[0] + self.offset_x, pos[1] + self.offset_y

    # Brings forward the currently used window
    def bring_forward(self):
        win32gui.SetForegroundWindow(self.hwnd)

    # Converts the given window position to screen position and attempts to click on it
    def click(self, windowPos=None):
        self.bring_forward()
        if windowPos is not None:
            screenPos = self.get_screen_position(windowPos)
            pydirectinput.moveTo(int(screenPos[0]), int(screenPos[1]))

        pydirectinput.mouseDown()
        pydirectinput.mouseUp()

    # Converts the given window position to screen position and attempts to click on it
    def right_click(self, windowPos=None):
        self.bring_forward()
        if windowPos is not None:
            screenPos = self.get_screen_position(windowPos)
            pydirectinput.moveTo(int(screenPos[0]), int(screenPos[1]))

        pydirectinput.mouseDown(button='right')
        pydirectinput.mouseUp(button='right')


if __name__ == '__main__':
    vision = BotVision()
    sleep(2)
    vision.target_top_window()
    health = vision.read_integer(0x6310CC)

    print(health)
