import requests
import cv2
import numpy as np
import base64

# Flask 서버 URL
url = 'http://127.0.0.1:5000/process_image2'

# 테스트할 이미지 파일 경로
image_path = 'image/recTest_7.png'

# 이미지를 읽어서 전송
with open(image_path, 'rb') as image_file:
    files = {'image': image_file}
    response = requests.post(url, files=files)

# 응답 데이터 처리
response_data = response.json()

# 에러 메시지가 있는지 확인
if 'error' in response_data:
    print("Error from server:", response_data['error'])
else:
    x = response_data['x']
    y = response_data['y']
    w = response_data['width']
    h = response_data['height']

    # 원본 이미지 읽기
    original_img = cv2.imread(image_path)

    # 좌표에 빨간색 사각형 그리기
    cv2.rectangle(original_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # 결과 이미지 표시
    cv2.imshow('Processed Image with Rectangle', original_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


