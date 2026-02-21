import cv2 as cv
import numpy as np

class UIFinder:
    """
    This class uses OpenCV's Template Matching to find images on the screen.
    This replaces the need for a YOLO model for simple UI tasks.
    """
    
    # Cache loaded templates to avoid reading from disk every time
    template_cache = {}

    def __init__(self, wincap):
        self.wincap = wincap

    def _load_template(self, template_path):
        """
        Loads a template image from disk and caches it.
        """
        if template_path in self.template_cache:
            return self.template_cache[template_path]
        
        try:
            template = cv.imread(template_path)
            if template is None:
                raise FileNotFoundError(f"Template image not found at: {template_path}. "
                                        "Did you forget to create it in the 'templates' folder?")
            self.template_cache[template_path] = template
            return template
        except Exception as e:
            print(f"Error loading template: {e}")
            # Stop the bot if a template is missing
            self.wincap.stop()
            return None

    def find_template(self, template_path, screenshot, confidence=0.8):
        """
        Finds the best match for a template on the screenshot.
        
        Args:
            template_path (str): The file path to the template image.
            screenshot (np.array): The current game screenshot.
            confidence (float): The minimum match confidence (0.0 to 1.0).

        Returns:
            tuple: (x, y) coordinates of the center of the best match, or None.
        """
        template = self._load_template(template_path)
        if template is None:
            return None

        # Get template dimensions
        template_h, template_w = template.shape[:2]

        # Run template matching
        # TM_CCOEFF_NORMED is a good method for finding best/worst matches
        try:
            result = cv.matchTemplate(screenshot, template, cv.TM_CCOEFF_NORMED)
        except cv.error as e:
            print(f"OpenCV Error: {e}")
            print("This can happen if the template image is larger than the screenshot.")
            return None

        # Find the location of the best match
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        print(f"Highest match confidence found: {max_val}")
        
        if max_val >= confidence:
            # max_loc is the top-left corner of the match
            top_left = max_loc
            
            # Calculate the center of the found rectangle
            center_x = top_left[0] + template_w // 2
            center_y = top_left[1] + template_h // 2
            
            return (center_x, center_y)
        
        return None

    def draw_template_matches(self, image, template_path, confidence=0.8):
        """
        Draws green rectangles around all matches found (for debugging).
        """
        template = self._load_template(template_path)
        if template is None:
            return

        template_h, template_w = template.shape[:2]
        
        try:
            result = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
        except cv.error:
            return # Template is probably larger than the image
            
        # Find all locations above the confidence threshold
        locations = np.where(result >= confidence)
        locations = list(zip(*locations[::-1])) # Switch (y, x) to (x, y)

        if locations:
            for top_left in locations:
                bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
                cv.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)



        