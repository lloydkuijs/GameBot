import pymem
import botvision
from time import sleep
import win32gui
import win32process

vision = botvision.BotVision()
sleep(5)
vision.target_top_window()
hwnd = vision.hwnd

tid, pid = win32process.GetWindowThreadProcessId(hwnd)
mem = pymem.Pymem()
mem.open_process_from_id(pid)

addr = mem.base_address + 0x6310CC
print(mem.read_int(addr))
