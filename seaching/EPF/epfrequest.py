import requests
from PIL import Image, ImageEnhance, ImageFilter, UnidentifiedImageError
from io import BytesIO
import pytesseract
import cv2
import numpy as np
import os
import time

# Define cookies and headers
cookies = {
    'JSESSIONID': 'web10102~swpu4mHFDvdATLza4+CbsSEo.e2d04d01-5fe2-398d-acac-4eea04cafdd4',
    'SERVERID': 'ha101',
    'ADRUM_BTa': '"R:0|g:e95b35a4-4205-4aa6-902d-dbfbde3a3eaa|n:customer1_1be52fc1-75a2-4fac-afe1-69c44734915b"',
    'SameSite': 'None',
    'ADRUM_BT1': '"R:0|i:4586|e:0|d:0"',
}

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://unifiedportal-emp.epfindia.gov.in',
    'Referer': 'https://unifiedportal-emp.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

captcha_url = 'https://unifiedportal-emp.epfindia.gov.in/publicPortal/no-auth/captcha/createCaptcha?_HDIV_STATE_=14-3-C84A039B4120B8E441CD7FAA251ACEA7'

# Create a directory to store captcha images if it doesn't exist
os.makedirs("captchas", exist_ok=True)

# Function to preprocess and save each image step
def preprocess_and_save_images(image, attempt):
    # Save original image
    image.save(f"captchas/captcha_attempt_{attempt}_original.png")

    # Convert to grayscale
    grayscale_image = image.convert("L")
    grayscale_image.save(f"captchas/captcha_attempt_{attempt}_grayscale.png")

    # High contrast adjustment
    high_contrast_image = ImageEnhance.Contrast(grayscale_image).enhance(3)
    high_contrast_image.save(f"captchas/captcha_attempt_{attempt}_high_contrast.png")

    # Adaptive thresholding
    image_np = np.array(grayscale_image)
    adaptive_thresh = cv2.adaptiveThreshold(image_np, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    adaptive_thresh_image = Image.fromarray(adaptive_thresh)
    adaptive_thresh_image.save(f"captchas/captcha_attempt_{attempt}_adaptive_thresh.png")

    # Dilation to make text more solid
    kernel = np.ones((2, 2), np.uint8)
    dilated_image = cv2.dilate(adaptive_thresh, kernel, iterations=1)
    dilated_image_pil = Image.fromarray(dilated_image)
    dilated_image_pil.save(f"captchas/captcha_attempt_{attempt}_dilated.png")

    return high_contrast_image, adaptive_thresh_image, dilated_image_pil

# Function to attempt captcha recognition with retries
def recognize_captcha():
    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            # Fetch captcha image
            captcha_response = requests.get(captcha_url, cookies=cookies, headers=headers, timeout=10)
            if captcha_response.status_code != 200:
                print(f"Attempt {attempt}: Failed to fetch captcha (status code {captcha_response.status_code}). Retrying...")
                continue
            
            # Ensure content is an image
            captcha_image = Image.open(BytesIO(captcha_response.content))
            
            # Preprocess and save images
            high_contrast_image, adaptive_thresh_image, dilated_image_pil = preprocess_and_save_images(captcha_image, attempt)
            
            # OCR on different preprocessed images
            for processed_image, name in zip([high_contrast_image, adaptive_thresh_image, dilated_image_pil],
                                             ["High Contrast", "Adaptive Threshold", "Dilated"]):
                captcha_text = pytesseract.image_to_string(
                    processed_image, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                ).strip()
                
                print(f"Attempt {attempt} ({name}): Recognized Captcha: {captcha_text}")
                
                # Validate captcha length
                if len(captcha_text) == 5:
                    return captcha_text
            
            print(f"Attempt {attempt} failed. Retrying...")
            time.sleep(1)  # Short delay before retrying

        except UnidentifiedImageError:
            print(f"Attempt {attempt}: Failed to identify image file. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt}: Request error ({e}). Retrying...")
        time.sleep(1)  # Delay before next attempt if an error occurs

    return ""

# Execute captcha recognition and send request if valid
captcha_text = recognize_captcha()
if captcha_text:
    json_data = {
        'EstName': 'aaa',
        'EstCode': '',
        'captcha': captcha_text,
    }

    # Send POST request with recognized captcha
    post_url = 'https://unifiedportal-emp.epfindia.gov.in/publicPortal/no-auth/estSearch/searchEstablishment'
    try:
        response = requests.post(post_url, params={'_HDIV_STATE_': '6-0-0E3EC28111B4F8362D040FE696B45067'}, cookies=cookies, headers=headers, json=json_data)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during POST request: {e}")
else:
    print("Failed to recognize a valid 5-character captcha after multiple attempts.")
