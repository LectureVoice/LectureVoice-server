import cv2
import pytesseract
import numpy as np

# Tesseract 경로 설정 (필요한 경우)
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def is_text_present(image):
    """
    이미지에서 텍스트가 있는지 확인합니다.
    """
    text = pytesseract.image_to_string(image)
    print("+++++++++++++++")
    print(text)
    print("\n")
    return len(text.strip()) > 10  # 텍스트 길이가 10자 이상이면 텍스트가 포함되어 있다고 판단

def is_diagram(image):
    """
    이미지가 다이어그램인지 확인합니다.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_pixel_ratio = np.sum(edges > 0) / edges.size
    return edge_pixel_ratio > 0.05  # 엣지 픽셀 비율이 5% 이상이면 다이어그램으로 판단

def classify_image(image_path):
    """
    이미지를 다이어그램, 사진으로 분류합니다.
    """
    image = cv2.imread(image_path)
    
    if is_text_present(image):
        print(f"{image_path}: 이 이미지는 텍스트가 포함된 다이어그램일 가능성이 큽니다.")
        return "Diagram with Text"
    
    if is_diagram(image):
        print(f"{image_path}: 이 이미지는 다이어그램일 가능성이 큽니다.")
        return "Diagram"
    else:
        print(f"{image_path}: 이 이미지는 사진일 가능성이 큽니다.")
        return "Photo"

# 이미지 파일 경로 리스트를 정의합니다.
image_list = ['image/compare_image1.png', 'image/compare_image2.png', 'image/compare_image3.png']  # 예시 이미지 리스트

# 각 이미지에 대해 다이어그램인지 사진인지 분류합니다.
for image_path in image_list:
    result = classify_image(image_path)
