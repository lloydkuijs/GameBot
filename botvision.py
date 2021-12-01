import numpy as np
import win32con
import win32ui
import pydirectinput
import win32gui
from time import time
import cv2 as cv

# Captures the first window it can find on the screen,
class BotVision:

    # properties
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    border_pixels = 12
    titleBar_pixels = 30

    # Constructor used for testing
    def __init__(self):
        pass

    # constructor
    def __init__(self, hwnd):
        self.target_window(hwnd)

    def target_window(self, hwnd):
        self.hwnd = hwnd

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]

        # account for the window border and titlebar and cut them off
        self.w = self.w - (self.border_pixels * 2)
        self.h = self.h - self.titleBar_pixels - self.border_pixels
        self.cropped_x = self.border_pixels
        self.cropped_y = self.titleBar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y

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
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        #dataBitMap.SaveBitmapFile(cDC, 'debug.bmp')
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

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
