from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64

app = Flask(__name__)

@app.route('/process_image2', methods=['POST'])
def process_image2():
    image_data = request.files['image'].read()

    # Convert image data to numpy array
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and improve contour detection
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imwrite('edges_detected_image2.png', edges)

    # Apply adaptive thresholding to detect contours
    #thresh = cv2.adaptiveThreshold(edges, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    #                               cv2.THRESH_BINARY_INV, 11, 2)

    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize list for contours and their bounding rectangles
    contours_info = []

    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        contours_info.append((area, x, y, w, h))

        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0

        # 컨투어의 면적을 이미지에 텍스트로 표시합니다
        cv2.putText(img, f"{int(area)}", (cX - 20, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        # 컨투어를 이미지에 그립니다
        cv2.drawContours(img, [contour], -1, (255, 0, 0), 2)
    
    cv2.imwrite('contour_area_image.png', img)

    # Sort contours by area in descending order
    contours_info = sorted(contours_info, key=lambda r: r[0], reverse=True)

    if len(contours_info) > 1:
        # Get the second largest contour
        _, x, y, w, h = contours_info[0]
        # Draw the bounding rectangle on the original image
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
    else:
        return jsonify({"error": "Not enough contours found"}), 400

    # Convert the processed image back to bytes
    _, img_encoded = cv2.imencode('.png', img)
    img_base64 = base64.b64encode(img_encoded).decode('utf-8')

    response_data = {
        'image': img_base64,
        'x': x,
        'y': y,
        'width': w,
        'height': h
    }

    # Return the response JSON object as the response
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
