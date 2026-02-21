import cv2 as cv
import pyautogui as py
from time import time
from win_cap_module import WindowCapture
from bot_config import Bot, BotState
from template_matching import UIFinder

# Set this to True to see a debug window
DEBUG = True
window_name = "Bluestacks App Player"
print("Bot starting... Press 'q' in the debug window to quit.")

# Initialize all our modules
try: 
    wincap = WindowCapture(window_name)
except Exception as e:
    print(f"Error: {e}")
    print("Is the emulator (BlueStacks) running and named correctly?")
    exit()

uifinder = UIFinder(wincap)
bot = Bot(wincap, uifinder)

# Start the bot's logic thread
wincap.start()
bot.start()

loop_time = time()

try:
    while(True):
        # Get the latest screenshot
        screenshot = wincap.screenshot
        if screenshot is None:
            continue  

        # Update the bot with the new screenshot
        bot.update_screenshot(screenshot)

        if DEBUG:
            # Create a copy for drawing
            debug_image = bot.get_debug_image()
            
            # Show the debug window
            cv.imshow("TheWolfBoxOpener - Debug", debug_image)

        # Calculate and display FPS
        fps = 1 / (time() - loop_time)
        loop_time = time()
        # print(f"FPS {fps:.2f} - State: {bot.state.name}", end='\r')

        # Press 'q' to exit the script
        key = cv.waitKey(1)
        if key == ord('q'):
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

    