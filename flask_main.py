from flask import Flask, request, jsonify
import requests, json
import cv2
import numpy as np
import base64
import os
from PIL import Image
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, storage
import urllib.parse
from googletrans import Translator
from flask_diagram_detect import main_diagram_detect
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Flutter 클라이언트: Firebase에서 이미지 URL 배열을 받아 Flask 서버로 전달.
# Flask 서버:
#   1. Naver Clova OCR로 이미지 전송 후 텍스트 정보 반환.
#   2. 이미지에서 사각형을 탐지하고 좌표를 반환.
#   3. 필요한 경우 사각형 영역을 크롭한 뒤 OCR을 다시 수행.
#   4. 크롭된 이미지에 대해 추가 처리(/arrow_detect) 수행.
#   5. 최종 결과를 Flutter 클라이언트로 반환.
# Flutter 클라이언트: 결과를 사용자에게 표시.

app = Flask(__name__)

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content  # 이미지 데이터를 바이트 형태로 반환
    else:
        raise Exception(f"Failed to download image: {image_url}")
    
def extract_image_name_from_url(url):
    # URL에서 파일 경로 추출
    parsed_url = urllib.parse.urlparse(url)
    # 파일 경로에서 파일 이름 부분만 추출
    path = parsed_url.path
     # '%2F'를 '/'로 변환 (URL에서 '/'가 '%2F'로 인코딩됨)
    decoded_path = urllib.parse.unquote(path)
    file_name = decoded_path.split('/')[-1]
    return file_name

#@app.route('/process_image2', methods=['POST'])
def process_image2(image_data):
    #image_data = request.files['image'].read()
    #image_data = download_image(image_url)

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
        largest_area, x, y, w, h = contours_info[0]

        if largest_area > 5000:
            # Draw the bounding rectangle on the original image
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
        else:
            return None
    else:
        #return jsonify({"error": "Not enough contours found"}), 400
        return None

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
    #return jsonify(response_data)
    return response_data


def send_to_clova_ocr(image_url, image_name_from_url):
    # Send image to Naver Clova OCR and return the result
    url = "https://tc61wu7n11.apigw.ntruss.com/custom/v1/20088/38629e69fbf3c3640428ce080d3b72bdfd5c15b29f5e9472460db30cf365cf48/general"
    header = {'Content-Type': 'application/json', 'X-OCR-SECRET':'Z3lMQ1VMS0F5cWdobFhaWmRIVFRMbmxGU05LWHR3SEU='}
    data = {"images": [
            {
                "format": "png",
                "name": "medium",
                "url": image_url
            }
            ],
            "lang": "ko",
            "requestId": "string",
            "resultType": "string",
            "timestamp": 0,
            "version": "V1"}

    try:
        res = requests.post(url, headers=header, data=json.dumps(data))

    except requests.exceptions.Timeout as errd:
        print("Timeout Error : ", errd)
        
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting : ", errc)
        
    except requests.exceptions.HTTPError as errb:
        print("Http Error : ", errb)

    # Any Error except upper exception
    except requests.exceptions.RequestException as erra:
        print("AnyException : ", erra)

    else:
        # 성공적으로 요청이 처리된 경우
        print("********res**********")
        print(res)

        # JSON 응답 데이터를 파싱
        ocr_data = res.json()
        print("OCR Result:", ocr_data)

        # 디렉토리 생성 (존재하지 않으면)
        directory = './ocrResult'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # JSON 데이터를 파일로 저장
        #jsonfile_name = 'ocr_result_{image_name_from_url}.json'
        jsonfile_name = 'ocr_result_{}.json'.format(image_name_from_url)
        file_path = os.path.join(directory, jsonfile_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_data, f, ensure_ascii=False, indent=4)

        print(f"OCR result saved to {file_path}")
        return res

def crop_image(image_file, rect_coords):
    # Crop the image based on rectangle coordinates
    img = Image.open(BytesIO(image_file))

    # 좌표 추출
    x = rect_coords['x']
    y = rect_coords['y']
    width = rect_coords['width']
    height = rect_coords['height']

    # 이미지 자르기 (crop)
    cropped_img = img.crop((x, y, x + width, y + height))

    # 크기만 2배로 늘리기
    new_size = (int(cropped_img.width * 2), int(cropped_img.height * 2))
    resized_img = cropped_img.resize(new_size, Image.LANCZOS)

    return resized_img 

cred = credentials.Certificate("secretkey/diagramproject-f4e78-firebase-adminsdk-c102g-787640d862.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'diagramproject-f4e78.appspot.com'
})

def upload_to_firebase(image, file_name):
    # Firebase Storage 버킷 가져오기
    bucket = storage.bucket()

    # BytesIO 객체에 이미지 저장
    image_io = BytesIO()
    image.save(image_io, format='PNG')
    image_io.seek(0)

    # Firebase Storage에 이미지 업로드
    blob = bucket.blob(file_name)
    blob.upload_from_file(image_io, content_type='image/png')

    # 이미지의 다운로드 URL 생성
    blob.make_public()  # 공개적으로 접근할 수 있는 URL 생성
    return blob.public_url

def translate(text_to_translate):
    # 번역기 객체 생성
    translator = Translator()

    # 번역 실행 (영어 -> 한국어)
    translated = translator.translate(text_to_translate, src='en', dest='ko')

    # 번역 결과 출력
    print("Original Text:", text_to_translate)
    print("Translated Text:", translated.text)
    return translated.text


# 서비스 계정 파일 경로
SERVICE_ACCOUNT_FILE = 'secretkey/diagramproject-f4e78-firebase-adminsdk-c102g-787640d862.json'

# 서비스 계정 자격 증명 로드
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)

# 자격 증명으로 액세스 토큰 생성
credentials.refresh(Request())
access_token = credentials.token


def image_captioning_request(image_url) :
    # Firebase Storage에서 이미지 다운로드 (URL이 공개적으로 접근 가능한 경우)
    #image_url = "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/cropped_image__27128.png?alt=media&token=0b8a3b0d-f7b5-4cc5-a9ff-3598b3864414"
    
    response = requests.get(image_url)
    image_data = response.content

    #gcloud auth print-access-token 터미널에
    your_access_token = 'ya29.a0AeDClZBUdh3tB860KZLhjdJMqCNxNZFbZ1ZAKaPww1TQMtMuahosWVZejjhvgdWQZ8jxumsK2w2edbLAvUP-xBxrrpLaYIBIX4RqLnDy5aDJ2u2xy3dClUzVhsLT4Wb3WomsQw56Fo60Bz12rTVroXdAXufQ7ppd9sFrLcF2RB0p3u9xaCgYKAe4SARISFQHGX2MiC8ySSasnVAH2roW2dzAaEg0183'

    # 이미지를 Base64로 인코딩
    encoded_image = base64.b64encode(image_data).decode('utf-8')

    # API 요청에 사용
    api_url = "https://us-central1-aiplatform.googleapis.com/v1/projects/ethereal-terra-374106/locations/us-central1/publishers/google/models/imagetext:predict"
    headers = {
        "Authorization": f"Bearer {your_access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "instances": [
            {
            "image": {
                "bytesBase64Encoded": encoded_image,
            }
            }
        ],
        "parameters": {
            "sampleCount": 1,
            "language": "en"
        }
    }

    # API 요청 보내기
    response2 = requests.post(api_url, json=data, headers=headers)
    # 응답 상태 코드 확인
    print("Status Code:", response2.status_code)

    # 예외 처리하여 응답 내용 출력
    try:
        json_data = response2.json()
        print(json_data)
        prediction_text = json_data['predictions'][0]

        korean_result = translate(prediction_text)
        return korean_result

    except requests.exceptions.JSONDecodeError:
        print("응답이 JSON 형식이 아닙니다.")
        print(response2.text)
        return 'ERROR image captionning request'


@app.route('/diagram_analysis', methods=['POST'])
def flask_main():
    image_urls = request.json['image_urls']
    results = []
    for url in image_urls:
        image_name_from_url = extract_image_name_from_url(url)

        # Step 2: Send image to Clova OCR
        #ocr_result = send_to_clova_ocr(url, image_name_from_url)
        img_file = download_image(url)
        
        # Step 3: Send image to /process_image2 for rectangle detection
        rect_coords = process_image2(img_file)
        
        # Step 4-5: If rectangle found, crop and check OCR, then send to /arrow_detect
        if rect_coords:
            cropped_image = crop_image(img_file, rect_coords)
            cropped_download_url = upload_to_firebase(cropped_image, 'cropped_{}.png'.format(image_name_from_url))

            #jsonfile_name = 'ocr_result_{}.json'.format(image_name_from_url)
            cropped_ocr_result_json_file_name = 'cropped_{}'.format(image_name_from_url)
            cropped_ocr_result_response = send_to_clova_ocr(cropped_download_url, cropped_ocr_result_json_file_name)
            # JSON 데이터를 파싱
            cropped_ocr_result = cropped_ocr_result_response.json()

            #if cropped_ocr_result:
            if cropped_ocr_result and cropped_ocr_result.get('images') and cropped_ocr_result['images'][0].get('fields'):
                #'ocr_result_{}.json'.format(cropped_ocr_result_json_file_name)
                arrow_result = main_diagram_detect(cropped_image, 'ocr_result_{}.json'.format(cropped_ocr_result_json_file_name))
                results.append(arrow_result)
            else:
                # 이미지 안에 cropped image는 있지만, cropped image에 글자는 없는 경우
                # image to text 해야함

                image_caption = image_captioning_request(cropped_download_url)
                results.append(f"\n이 장면 이미지에는 그림이 포함되어 있습니다.\n그림 설명은 다음과 같습니다.\n{image_caption}")
                #results.append(image_caption)
        else:
            results.append("ppt안에 해설 필요한 이미지 없음")

    print("###FINAL RESULT###")
    print(results)
    return jsonify(results)


@app.route('/ocr_request', methods=['POST'])
def ocr_request():
    image_urls = request.json['image_urls']
    all_infer_texts = []  # 모든 inferText 값을 저장할 리스트

    for url in image_urls:
        image_name_from_url = extract_image_name_from_url(url)

        # Step 2: Send image to Clova OCR
        ocr_result = send_to_clova_ocr(url, image_name_from_url)

        # 응답을 JSON으로 변환
        ocr_result = ocr_result.json()

        # OCR 결과에서 inferText 추출
        if ocr_result.get('images'):
            for image in ocr_result['images']:
                for field in image.get('fields', []):
                    infer_text = field.get('inferText')
                    if infer_text:
                        all_infer_texts.append(infer_text)

    # 모든 추출된 inferText를 반환
    return jsonify(all_infer_texts)



if __name__ == '__main__':
    app.run(debug=True)
