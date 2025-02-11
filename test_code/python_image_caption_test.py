import base64
import requests
from googletrans import Translator

def translate(text_to_translate):
    # 번역기 객체 생성
    translator = Translator()

    # 번역 실행 (영어 -> 한국어)
    translated = translator.translate(text_to_translate, src='en', dest='ko')

    # 번역 결과 출력
    print("Original Text:", text_to_translate)
    print("Translated Text:", translated.text)
    return translated.text


# Firebase Storage에서 이미지 다운로드 (URL이 공개적으로 접근 가능한 경우)
image_url = "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/cropped_image__27128.png?alt=media&token=0b8a3b0d-f7b5-4cc5-a9ff-3598b3864414"
response = requests.get(image_url)
image_data = response.content
your_access_token = 'ya29.a0AcM612zgRdqwfVRb3KPK3lvEQfj1jOdeuQ3VxkhrCh2zdLdtfJOrmN-lvZxSgDiI8bd88-5oK4oP6eP3Hpx3V6IOOTJMNQwAKgYjLLdT0JLy_qc3PtKf5dnjrJRZSET7gr-oQgfc2s5BjXOZJj3PoqvffNy9_-CQxgAYcH07P6-R6QaCgYKAf0SARISFQHGX2MiuN9_ZkbR4DN8XF7EsrlFBA0181'

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

    translate(prediction_text)

except requests.exceptions.JSONDecodeError:
    print("응답이 JSON 형식이 아닙니다.")
    print(response2.text)

