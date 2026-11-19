import cv2 as cv
import pyautogui as py
import win32api
from time import time
from win_cap_module import WindowCapture
from bot_config import Bot, BotState
from template_matching import UIFinder

DEBUG = True
window_name = "Bluestacks App Player"
print("Bot starting... Press 'q' anywhere to quit.")

try: 
    wincap = WindowCapture(window_name)
except Exception as e:
    print(f"Error: {e}")
    print("Is the emulator (BlueStacks) running and named correctly?")
    exit()

uifinder = UIFinder(wincap)
bot = Bot(wincap, uifinder)

wincap.start()
bot.start()

loop_time = time()
# Clear any prior key state for 'Q' before entering the loop
win32api.GetAsyncKeyState(ord('Q'))

try:
    while(True):
        screenshot = wincap.screenshot
        if screenshot is None:
            if win32api.GetAsyncKeyState(ord('Q')) != 0:
                wincap.stop()
                bot.stop()
                cv.destroyAllWindows()
                print("\nBot stopped.")
                break
            continue  

        bot.update_screenshot(screenshot)

        if DEBUG:
            debug_image = bot.get_debug_image()
            
            cv.imshow("TheWolfBoxOpener - Debug", debug_image)

        fps = 1 / (time() - loop_time)
        loop_time = time()
        # print(f"FPS {fps:.2f} - State: {bot.state.name}", end='\r')

        # Press 'q' anywhere on the screen to exit the script
        key = cv.waitKey(1) & 0xFF
        if key in (ord('q'), ord('Q')) or win32api.GetAsyncKeyState(ord('Q')) != 0:
            wincap.stop()
            bot.stop()
            cv.destroyAllWindows()
            print("\nBot stopped.")
            break

except KeyboardInterrupt:
    wincap.stop()
    bot.stop()
    cv.destroyAllWindows()
    print("\nBot stopped (KeyboardInterrupt).")

    