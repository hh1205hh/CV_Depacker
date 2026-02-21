import cv2 as cv
import pyautogui as py
from threading import Thread, Lock
from time import time, sleep
from enum import Enum


TEMPLATE_BOX = "assets/templates/box.png"
TEMPLATE_OPEN = "assets/templates/open.png"
TEMPLATE_SKIP_ALL = "assets/templates/skipall.png"
TEMPLATE_COLLECT = "assets/templates/collect.png"
DEFAULT_CONFIDENCE = 0.8
CLICK_DELAY = 1
IDLE_DELAY = 0.5 # seconds - how long to wait when idle


class BotState(Enum):
    """
    Defines the current state of the bot's logic.
    """
    INITIALIZING = 0
    SEARCHING_FOR_BOX = 1   
    OPENING_BOX = 2         
    SKIP_ALL = 3
    COLLECT = 4           
    IDLE = 6             

class Bot:
    """
    This class contains the bot's main logic (the state machine) and
    handles all automated mouse inputs.
    """
    
    # Threading properties
    stopped = True
    lock = None
    screenshot = None
    
    # State properties
    state = BotState.INITIALIZING
    timestamp = 0  # To manage delays
    
    # Modules
    wincap = None
    uifinder = None
    
    # Debug
    debug_image = None
    last_click_pos = None
    
    def __init__(self, wincap, uifinder):
        self.lock = Lock()
        self.wincap = wincap
        self.uifinder = uifinder
        self.timestamp = time()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def update_screenshot(self, screenshot):
        """
        Receives the latest screenshot from the main thread.
        """
        self.lock.acquire()
        self.screenshot = screenshot
        
        # Create a copy for drawing debug info
        self.debug_image = screenshot.copy()
        
        self.lock.release()

    def get_debug_image(self):
        """ 
        Returns the debug image with annotations.
        """
        self.lock.acquire()
        
        # Draw a green box around what we're looking for
        if self.state == BotState.SEARCHING_FOR_BOX:
            self.uifinder.draw_template_matches(self.debug_image, TEMPLATE_BOX, DEFAULT_CONFIDENCE)
        elif self.state == BotState.OPENING_BOX:
            self.uifinder.draw_template_matches(self.debug_image, TEMPLATE_OPEN, DEFAULT_CONFIDENCE)
        elif self.state == BotState.SKIP_ALL:
            self.uifinder.draw_template_matches(self.debug_image, TEMPLATE_COLLECT, DEFAULT_CONFIDENCE)
        elif self.state == BotState.COLLECT:
            self.uifinder.draw_template_matches(self.debug_image, TEMPLATE_COLLECT, DEFAULT_CONFIDENCE)


        # Draw a red circle where we last clicked
        if self.last_click_pos:
            cv.circle(self.debug_image, self.last_click_pos, 10, (0, 0, 255), 2)
            
        img = self.debug_image
        self.lock.release()
        return img

    def click_location(self, pos):
        """
        Clicks at a position given in screenshot coordinates.
        Translates screenshot (x,y) to actual screen coordinates using WindowCapture offsets.
        """
        if pos is None:
            return
        x, y = int(pos[0]), int(pos[1])
        # Save for debug drawing (debug image uses screenshot coords)
        self.last_click_pos = (x, y)

        # Translate to absolute screen coordinates
        try:
            screen_x = x + self.wincap.offset_x
            screen_y = y + self.wincap.offset_y
        except Exception:
            # Fallback: assume no offset available
            screen_x, screen_y = x, y

        # Optionally bring the window to foreground before clicking
        try:
            self.wincap.set_window()
        except Exception:
            pass

        try:
            py.click(x=screen_x, y=screen_y)
        except Exception as e:
            print(f"Click error: {e}")

    def set_state(self, new_state, delay_seconds=0):
        """
        Set the bot's state and schedule the next allowed action after delay_seconds.
        """
        self.state = new_state
        # record the earliest time at which the next action may run
        self.timestamp = time() + (delay_seconds or 0)

    def is_delay_over(self):
        """Return True when the scheduled delay (set in set_state) has passed."""
        return time() >= self.timestamp

    def run(self):
        """
        This is the main logic loop of the bot, run in a separate thread.
        """
        while self.stopped is False and self.screenshot is None:
            print("Bot waiting for first screenshot...")
            sleep(1)
        
        print("Bot logic started.")
        self.state = BotState.SEARCHING_FOR_BOX

        while not self.stopped:
            # Aggressive mode: if any known UI templates appear, click them immediately.
            # This makes the bot respond to any opening/collect UI anywhere on screen.
            if self.is_delay_over():
                for tpl_name, tpl_path in [("TEMPLATE_BOX", TEMPLATE_BOX), ("TEMPLATE_OPEN", TEMPLATE_OPEN), ("TEMPLATE_SKIP_ALL", TEMPLATE_SKIP_ALL), ("TEMPLATE_COLLECT", TEMPLATE_COLLECT)]:
                    if tpl_path:
                        tpl_pos = self.uifinder.find_template(tpl_path, self.screenshot, DEFAULT_CONFIDENCE)
                        if tpl_pos:
                            print(f"Aggressive click: found {tpl_name}. Clicking now.")
                            self.click_location(tpl_pos)
                            # After an aggressive click, wait a short time for UI to update
                            self.set_state(BotState.IDLE, CLICK_DELAY)
                            break

            

            """
            # State 1: Look for a new box
            if self.state == BotState.SEARCHING_FOR_BOX:
                box_pos = self.uifinder.find_template(TEMPLATE_BOX, self.screenshot, DEFAULT_CONFIDENCE)
                if box_pos:
                    print("Found a box. Clicking it.")
                    self.click_location(box_pos)
                    self.set_state(BotState.OPENING_BOX, CLICK_DELAY)
                else:
                    print("No boxes found. Going idle.")
                    self.set_state(BotState.IDLE, IDLE_DELAY)
            
            # State 2: Look for the "Open" button (after clicking a box)
            elif self.state == BotState.OPENING_BOX:
                if self.is_delay_over():
                    open_pos = self.uifinder.find_template(TEMPLATE_OPEN, self.screenshot, DEFAULT_CONFIDENCE)
                    if open_pos:
                        print("Found 'Open' button. Clicking it.")
                        self.click_location(open_pos)
                        self.set_state(BotState.SKIP_ALL, CLICK_DELAY)
                    else:
                        print("No boxes found. Going idle.")
                        self.set_state(BotState.IDLE, IDLE_DELAY)

            # State 3: Look for "Skip All" button to skip animations
            elif self.state == BotState.SKIP_ALL:
                if self.is_delay_over():
                    skip_pos = self.uifinder.find_template(TEMPLATE_SKIP_ALL, self.screenshot, DEFAULT_CONFIDENCE)
                    if skip_pos:
                        print("Found 'Skip All'. Clicking it.")
                        self.click_location(skip_pos)
                        self.set_state(BotState.COLLECT, CLICK_DELAY)
                    else:
                        print("No boxes found. Going idle.")
                        self.set_state(BotState.IDLE, IDLE_DELAY)

            # State 4: Look for "Collect" button to collect rewards
            elif self.state == BotState.COLLECT:
                if self.is_delay_over():
                    collect_pos = self.uifinder.find_template(TEMPLATE_COLLECT, self.screenshot, DEFAULT_CONFIDENCE)
                    if collect_pos:
                        print("Found 'Collect'. Clicking it.")
                        self.click_location(collect_pos)
                        self.set_state(BotState.SEARCHING_FOR_BOX, CLICK_DELAY)
                    else:
                        print("No boxes found. Going idle.")
                        self.set_state(BotState.IDLE, IDLE_DELAY)

"""

