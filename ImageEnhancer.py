import cv2
import numpy as np
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class ImageEnhancer:
#IMAGE ENHANCEMENT FUNCTIONS OF GRACESCAN
    @staticmethod
    def auto_rotate(image):
        if image is None:
            return None
        try:
            osd = pytesseract.image_to_osd(image, output_type = pytesseract.Output.DICT)
            rotation = osd.get("rotate",0)
            if rotation == 90:
                image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
            elif rotation == 180:
                image = cv2.rotate(image, cv2.ROTATE_180)
            elif rotation == 270:
                image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
            return image
        except Exception: 
            return image

    @staticmethod
    def auto_deskew(image):
        if image is None:
            return None
        if len(image.shape)==3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray= image.copy()
        _,thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coords = cv2.findNonZero(thresh)
        if coords is None:
            return image
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = 90 + angle

        (h, w) = image.shape[:2] 
        center = (w //2, h //2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, matrix, (w, h), flags = cv2.INTER_CUBIC, borderMode = cv2.BORDER_REPLICATE)
        

    @staticmethod
    def auto_crop(image):
        if image is None:
            return None
        if len(image.shape)==3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray= image.copy()
        _,thresh = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return image
        largest = max(contours, key = cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)
        return image[y:y+h, x:x+w]

    @staticmethod
    def remove_black_border(image):
        if image is None:
            return None
        if len(image.shape)==3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray= image.copy()
        _,thresh = cv2.threshold(gray, 15, 255, cv2.THRESH_BINARY)
        coords = cv2.findNonZero(thresh)
        if coords is None:
            return image
        x, y, w, h = cv2.boundingRect(coords)
        return image[y:y+h, x:x+w]
        

    @staticmethod
    def enhance_text(image):
        if image is None:
            return None
        if len(image.shape)==3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray= image.copy()
        clache = cv2.createCLACHE(clipLimit=2.0, tileGridSize = (8, 8))
        enhanced = clache.apply(gray)
        return enhanced

    @staticmethod
    def remove_noise(image):
        if image is None:
            return None
        if len(image.shape)==3:
            return cv2.fastNIMeansDenoisingColored(image, None, 10, 10, 7, 21)
            return cv2.fastNIMeansDenoising(image, None, 10, 7,21)

    @staticmethod
    def sharpen_image(image):
        if image is None:
            return None
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype = np.float32)
        sharpened = cv2.filter2D(image, -1, kernel)
        final_image = cv2.addWeighted(image, 0.85, sharpened, 0.15,0)
        return final_image

    #LEADER PROGRAM
    @staticmethod
    def enhance_image(image):
        if image is None:
            return None
        #GEOMETRY CORRECTION
        image = ImageEnhancer.auto_rotate(image)
        image = ImageEnhancer.auto_deskew(image)
        
        #PAGE CLEANUP
        image = ImageEnhancer.auto_crop(image)
        image = ImageEnhancer.remove_black_border(image)
        
        #IMAGE ENHANCEMENT
        image = ImageEnhancer.remove_noise(image)
        image = ImageEnhancer.enhance_text(image)
        image = ImageEnhancer.sharpen_image(image)
        return image 
