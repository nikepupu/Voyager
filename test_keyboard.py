import pyautogui
import time

time.sleep(5)
pyautogui.press('t')
time.sleep(0.5)
pyautogui.press('backspace')
pyautogui.write("Hello,Minecraft!")
time.sleep(0.5)
pyautogui.press('enter')