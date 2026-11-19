## Project classification: Practical 


# The Wolf MMORPG - Automated Loot Box Bot

This project is an automated, computer-vision-driven bot designed to interact with "The Wolf MMORPG" running inside the BlueStacks 5 Android emulator on Windows. Specifically, it automates the tedious process of opening loot boxes and collecting rewards.

## Demo 

<!-- the lower line of code does not wrk because it is  -->
![TW_MMORPG Bot Demo](demo-ezgif.gif) 

## Requirements

* **OS:** Windows *(relies on `win32gui` / `win32ui` for hardware-accelerated window capture).*
* **Environment:** Python 3.x.
* **Emulator:** [BlueStacks 5](https://www.bluestacks.com/bluestacks-5.html).


## Instructions

1. Install [BlueStacks 5](https://www.bluestacks.com/bluestacks-5.html).
2. Open a new BlueStacks 5 instance.
   * **Crucial:** The window title must be exactly `"Bluestacks App Player"`. The `WindowCapture` module uses this strict string to hook the window handle (`hwnd`) and calculate DPI-aware crop offsets.
3. Download and sideload **"The Wolf MMORPG Modded APK (Free shopping)"** into the configured BlueStacks instance.
4. Launch the game within the emulator and navigate to the target UI state (e.g., the box-opening view).
5. Run `main.py`
6. Press **`q`** (or **`Q`**) anywhere on the screen to quit, regardless of your cursor's screen coordinates or which window is currently focused.

---

## Safe Exit

* **Safe Exit:** Do not forcefully close the emulator or terminal.
* Press **`q`** anywhere on the screen (you do not need to click on the simulation window's top bar first).
* This sends the interrupt signal to gracefully terminate the capture and bot threads (`wincap.stop()`, `bot.stop()`) and safely release memory/window handles.
