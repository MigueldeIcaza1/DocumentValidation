!sudo apt-get install tesseract-ocr
!pip install pytesseract
!pip install Pillow
!apt-get install -y poppler-utils
!pip install pdf2image


import cv2
import numpy as np
import pytesseract
import io

from google.colab import files
from PIL import Image
from pdf2image import convert_from_path

from difflib import SequenceMatcher



def get_fields_to_be_filled(pil_image):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    form_fields = []

    for contour in contours:
        [x, y, w, h] = cv2.boundingRect(contour)
        if w > 30 and h < 10:
            roi = image[max(0, y-40):y, x:x+w]
            text_above = pytesseract.image_to_string(roi)

            roi_below = gray[y+h:y+h+40, x:x+w]
            text_below = pytesseract.image_to_string(roi_below)

            if not text_above.strip():
                form_fields.append(text_below.strip())

            # Optionally draw rectangles around detected lines and text for debugging
            cv2.rectangle(image, (x, y+h), (x + w, y+h+40), (0, 0, 255), 2)

    cv2.imwrite("debug_unfiiled_image_with_rois.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR)) #To see where the data is extracting
    return form_fields

def get_user_filled_data(pil_image):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    form_fields = {}

    for contour in contours:
        [x, y, w, h] = cv2.boundingRect(contour)
        if w > 30 and h < 10:
            roi = image[max(0, y-40):y, x:x+w]
            text_above = pytesseract.image_to_string(roi)

            roi_below = gray[y+h:y+h+40, x:x+w]
            text_below = pytesseract.image_to_string(roi_below)

            text_above = text_above.replace("\n", "")
            text_below = text_below.replace("\n", "")

            if text_above and text_below:
                form_fields[text_below] = text_above
            elif text_below:
                form_fields[text_below] = None

            # Optionally draw rectangles around detected lines and text for debugging
            cv2.rectangle(image, (x, y-40), (x + w, y), (0, 255, 0), 2)
            cv2.rectangle(image, (x, y+h), (x + w, y+h+40), (0, 0, 255), 2)

    cv2.imwrite("debug_image_with_rois.png", cv2.cvtColor(image, cv2.COLOR_RGB2BGR)) #To see where the data is extracting
    return form_fields

def compare_images_text(image1, image2):
    image1 = np.array(image1)
    image2 = np.array(image2)
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Apply OCR to extract text from images
    original_text = pytesseract.image_to_string(gray1)
    edited_text = pytesseract.image_to_string(gray2)

    return text_similarity(original_text, edited_text)

def text_similarity(text1, text2, threshold=0.5):
    matcher = SequenceMatcher(None, text1, text2)
    similarity_ratio = matcher.ratio()
    return similarity_ratio >= threshold

def has_signature_or_handwritten(pil_image):
    image = np.array(pil_image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for c in contours:
        if cv2.contourArea(c) > 10:
            return True
    return False

def remove_form_feed(text):
    return text.replace('\x0c', '')

def extract_form_values_with_pytesseract(original_image, edited_image):
    fields_to_be_filled = get_fields_to_be_filled(original_image)
    print("Fields to be filled:", fields_to_be_filled)

    user_form_fileds = get_user_filled_data(edited_image)
    # print("extracted fields to be filled:", user_form_fileds)

    cleaned_user_form_fields = {remove_form_feed(key): remove_form_feed(value) for key, value in user_form_fileds.items()}

    filtered_extracted_fields = {key: cleaned_user_form_fields[key] for key in fields_to_be_filled if key in cleaned_user_form_fields}
    return filtered_extracted_fields

def validate_vraa(original_images, edited_images):
  last_page_index = len(edited_images) - 1
  empty_fields = []
  form_fields = []

  # checking template is valid or not
  for page_num in range(last_page_index):
          edited_image = edited_images[page_num]
          original_image = original_images[page_num]
          isSameImage = compare_images_text(original_image, edited_image)

          if(isSameImage):
              continue
          else:
              empty_fields.append("Uploaded a different file or corrupted one")
              return empty_fields, form_fields

  edited_image = edited_images[last_page_index]
  original_image = original_images[last_page_index]

  if has_signature_or_handwritten(edited_image):
    form_fields = extract_form_values_with_pytesseract(original_image, edited_image)
    return form_fields



#code execution begins
uploaded = files.upload()
file_name = list(uploaded.keys())[0]



uploaded_edit = files.upload()
file_name_2 = list(uploaded_edit.keys())[0]

# Convert the PDF to a list of images
original_images = convert_from_path(file_name)
edited_images = convert_from_path(file_name_2)

form_fields = validate_vraa(original_images, edited_images)
print("Form Fields:", form_fields)

empty_fields = []
unfilled_value_found = False

if form_fields:
    for key, value in form_fields.items():
        if value is None or value == "":
            print(f"Unfilled value found for key: {key}")
            formatted_text = key.replace("\n", " ")
            empty_fields.append(formatted_text)
            unfilled_value_found = True
    if not unfilled_value_found:
        print("All fields are filled")

