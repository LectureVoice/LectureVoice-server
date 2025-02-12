from flask import Flask, request, jsonify
import cv2
import json
import numpy as np
import base64
from PIL import Image

app = Flask(__name__)

@app.route('/process_image', methods=['POST'])


def process_image():
    image_data = request.files['image'].read()

    # Convert image data to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Image processing to detect second-largest contour
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    cv2.imwrite('blurred_image1.png', blurred)
    ret, thresh = cv2.threshold(blurred, 100, 255, 0)
    contours, _ = cv2.findContours(thresh, 1, 2)

    # Sort contours based on their areas in descending order
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    print(len(contours))

    # The first contour in the sorted list will be the largest one (background), so we skip it
    if len(contours) > 1:
        second_largest_contour = contours[1]
        x, y, w, h = cv2.boundingRect(second_largest_contour)
        #x,y는 왼쪽 상단 좌표
        #boundingRect()은 컨투어를 감싸는 사각형 반환
        
        cropImage = img[y:(y+h), x:(x+w)]

    # Convert the processed image back to bytes
    _, img_encoded = cv2.imencode('.png', cropImage)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    response_data = {
        'image': img_base64,
        'x': x,
        'y': y,
        'width': w,
        'height': h
    }
    print("x y w h ")
    print(x, " ", y, " ", w, " ", h)

    # Return the response JSON object as the response
    return json.dumps(response_data)

if __name__ == '__main__':
    app.run(debug=True)
