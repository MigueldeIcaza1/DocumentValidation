**Document Validation Using Python (AI)**
Validates a document by checking if all form fields are filled and whether a signature or handwriting is present. 
The code uses several libraries like **Tesseract OCR, OpenCV, and PIL** to process the PDF files. 

**The main tasks performed by this script:**
  Extracting fields that need to be filled.
  Checking if the user has filled the required fields.
  Comparing the original and user-filled documents.
  Detecting signatures or handwriting.

**Libraries Used:**
  Tesseract OCR for extracting text from images.
  OpenCV for image processing (detecting contours and processing grayscale images).
  PIL for handling images.
  pdf2image for converting PDF pages to images.
  NumPy for array manipulation.
  cv2 for image processing.

  
**Limitations:**
  Valid only for printed text not for handwritten text (except signature)
  Fields should be in the format -  User filled data above the underline of field to be filled
  Example as shown below: 
  ![image](https://github.com/user-attachments/assets/1322c734-0341-4f51-b1d8-5af8c0eb9699)


**Result:**
  Run the code in colab with the commads placed at the top of main.py.
  First upload a original document and then upload a document that is filled by user.
  It returns fields to be filled and fields filled by user as a key value pair.
  If a value is empty, then the document is invalid.
