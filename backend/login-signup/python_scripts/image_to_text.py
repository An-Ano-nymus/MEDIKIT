
import sys
import os
import platform
import numpy as np
from PIL import Image

try:
    import cv2
    CV_AVAILABLE = True
except ImportError:
    cv2 = None
    CV_AVAILABLE = False

try:
    import pytesseract
    from pytesseract import TesseractNotFoundError
    PYTESS_AVAILABLE = True
except ImportError:
    pytesseract = None
    TesseractNotFoundError = RuntimeError
    PYTESS_AVAILABLE = False

try:
    import easyocr
    EASY_AVAILABLE = True
except ImportError:
    easyocr = None
    EASY_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    fitz = None
    PYMUPDF_AVAILABLE = False


EASY_READER = None


def to_grayscale(image_array, color_order='bgr'):
    if image_array is None:
        return None
    if image_array.ndim == 2:
        return image_array
    if CV_AVAILABLE:
        if color_order == 'rgb':
            return cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        return cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    weights = np.array([0.2989, 0.5870, 0.1140])
    if color_order == 'bgr':
        weights = weights[::-1]
    gray = np.tensordot(image_array[..., :3], weights, axes=([-1], [0]))
    return gray.astype(np.uint8)


def load_image(path):
    if CV_AVAILABLE:
        image = cv2.imread(path)
        if image is not None:
            return image, 'bgr'
    with Image.open(path) as img:
        rgb_img = img.convert('RGB')
        return np.array(rgb_img), 'rgb'


def get_easyocr_reader():
    global EASY_READER
    if not EASY_AVAILABLE:
        raise RuntimeError('EasyOCR is not installed')
    if EASY_READER is None:
        EASY_READER = easyocr.Reader(['en'], gpu=False)
    return EASY_READER


def try_tesseract(gray_image):
    if not PYTESS_AVAILABLE:
        return None
    tesseract_path = os.environ.get('TESSERACT_PATH')
    if not tesseract_path and platform.system().lower().startswith('win'):
        tesseract_path = r"python_scripts\Image to text via tesseract\tesseract.exe"
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    try:
        return pytesseract.image_to_string(gray_image, lang='eng')
    except (TesseractNotFoundError, FileNotFoundError, OSError):
        return None


def ocr_image_array(image_array, color_order='bgr'):
    if image_array is None:
        return ''
    gray = to_grayscale(image_array, color_order=color_order)
    text = try_tesseract(gray)
    if text:
        return text
    if EASY_AVAILABLE:
        reader = get_easyocr_reader()
        result = reader.readtext(gray, detail=0, paragraph=True)
        return '\n'.join(result)
    raise RuntimeError('No OCR engine available (Tesseract/EasyOCR).')


def img_to_string(image_path):
    image, order = load_image(image_path)
    return ocr_image_array(image, color_order=order)


def pdf_to_text(pdf_path):
    if not PYMUPDF_AVAILABLE:
        raise RuntimeError('PyMuPDF is required for PDF processing without Poppler.')
    doc = fitz.open(pdf_path)
    text_all = []
    for page_index, page in enumerate(doc):
        page_text = page.get_text().strip()
        if page_text:
            text_all.append(f"\n--- Page {page_index + 1} (text) ---\n{page_text}")
            continue

        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
        image_array = np.array(img)
        color_order = 'rgb'
        if CV_AVAILABLE:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
            color_order = 'bgr'
        ocr_text = ocr_image_array(image_array, color_order=color_order)
        text_all.append(f"\n--- Page {page_index + 1} (ocr) ---\n{ocr_text}")
    doc.close()
    return '\n'.join(text_all)


def auto_text(file_path):
    if file_path.lower().endswith('.pdf'):
        return pdf_to_text(file_path)
    return img_to_string(file_path)


if __name__ == '__main__':
    path_arg = sys.argv[1]
    auto_text(path_arg)






#WORKING DEMO FOR USECASE


# file_path = r'D:\Raghav\EVOLUTION\GOD_DEMON_IS_BACK\MEDICINE_API\files_for_test\TEXT_TEST.png'

# if file_path.lower().endswith('.pdf'):
#     output_text = pdf_to_text(file_path)
# else:
#     output_text = img_to_string(file_path)

# print("\nExtracted Text:\n", output_text)


# file_path = r'D:\Raghav\EVOLUTION\GOD_DEMON_IS_BACK\MEDICINE_API\files_for_test\Medical.pdf'

# if file_path.lower().endswith('.pdf'):
#     output_text = pdf_to_text(file_path)
# else:
#     output_text = img_to_string(file_path)

# print("\nExtracted Text:\n", output_text)