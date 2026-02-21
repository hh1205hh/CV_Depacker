import numpy as np
import tkinter
from time import time, sleep
import win32gui, win32ui, win32con, win32com.client
from threading import Thread, Lock
from ctypes import windll

class WindowCapture:

    # threading properties
    stopped = True
    lock = None
    screenshot = None
     
    w = 0
    h = 0
    hwnd = None
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    def __init__(self, window_name=None):
        # Make program aware of DPI scaling
        user32 = windll.user32
        user32.SetProcessDPIAware()
        # get DPI
        root = tkinter.Tk()
        dpi = root.winfo_fpixels('1i')
        deafault_dpi = 96
        self.scaling = int(dpi/deafault_dpi)
        # close tkinter
        root.destroy()
        # create a thread lock object
        self.lock = Lock()
        # find the handle for the window we want to capture.
        if window_name is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = win32gui.FindWindow(None, window_name)
            if not self.hwnd:
                raise Exception(f"Window '{window_name}' not found. \n"
                                "Please open the emulator or change the window_name")

        # get the window size
        window_rect = win32gui.GetWindowRect(self.hwnd)
        self.w = window_rect[2] - window_rect[0]
        self.h = window_rect[3] - window_rect[1]
        
        # top left and bottom right coordinate of the window
        self.left = window_rect[0]
        self.top = window_rect[1]
        self.right = window_rect[2]
        self.bottom = window_rect[3]
        
        # screen resolution
        self.screen_resolution = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

        # account for the window border and titlebar and cut them off
        self.border_pixels = int(1*self.scaling)
        self.titlebar_pixels = int(33*self.scaling)
        self.w = self.w - (self.border_pixels * 2)
        self.h = self.h - self.titlebar_pixels - self.border_pixels
        self.cropped_x = self.border_pixels
        self.cropped_y = self.titlebar_pixels

        # set the cropped coordinates offset so we can translate screenshot
        # images into actual screen positions
        self.offset_x = window_rect[0] + self.cropped_x
        self.offset_y = window_rect[1] + self.cropped_y
        self.offsets = (self.offset_x,self.offset_y)

        # Use focused_window=False logic by default
        self.window = None
        self.cropped = (self.offset_x, self.offset_y)
    
    def get_dimension(self):
        """
        get the width and the height of the select window
        """
        return self.w, self.h 

    def get_screenshot(self):
        """
        take a screenshot
        """
        # get the window image data
        # Using GetWindowDC(None) captures the whole screen
        wDC = win32gui.GetWindowDC(self.window) 
        dcObj = win32ui.CreateDCFromHandle(wDC)
        cDC = dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        
        # BitBlt from the correct offset
        cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (self.cropped[0], self.cropped[1]), win32con.SRCCOPY)

        # convert the raw data into a format opencv can read
        signedIntsArray = dataBitMap.GetBitmapBits(True)
        img = np.fromstring(signedIntsArray, dtype='uint8')
        img.shape = (self.h, self.w, 4)

        # free resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(self.hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())

        # drop the alpha channel
        img = img[...,:3]
        img = np.ascontiguousarray(img)

        return img

    # threading methods
    def start(self):
        """
        start windowcapture
        """
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        """
        stop windowcapture
        """
        self.stopped = True

    def run(self):
        while not self.stopped:
            # get an updated image of the game
            screenshot = self.get_screenshot()
            
            # lock the thread while updating the results
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()
            
            # Limit capture rate slightly
            sleep(0.01)