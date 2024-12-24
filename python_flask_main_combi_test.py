import requests
import json
import time

def send_request(url, image_url):
    # JSON 데이터 준비
    data = {
        "image_urls": [image_url]
    }

    # POST 요청 보내기
    response = requests.post(url, json=data)

    # 응답 상태 코드 확인
    if response.status_code == 200:
        #print(f"Request to {url} succeeded")
        print("")
    else:
        print(f"Request to {url} failed with status code {response.status_code}")
        return None  # 에러 발생 시 None 반환

    # 응답 데이터 확인
    try:
        return response.json()  # JSON 응답 파싱
    except ValueError:
        print(f"Invalid JSON response from {url}")
        return None  # JSON 파싱 에러 발생 시 None 반환

def combined_test():
    # 테스트 시작 시간
    start = time.time()

    # 보낼 이미지 URL
    image_url = "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__4654?alt=media&token=d1d01839-609a-4a2c-ac58-c261a217278b"

    # 첫 번째 요청 (OCR Request)
    ocr_url = "http://127.0.0.1:5000/ocr_request"
    ocr_response = send_request(ocr_url, image_url)

    if ocr_response:
        # inferText를 자연스럽게 연결하여 출력
        infer_texts = ""
        for infer_text in ocr_response:
            if infer_text.endswith(('.', '?', '!', '·')):
                infer_texts += infer_text + "\n"
            else:
                infer_texts += infer_text + " "
        print("OCR Infer Text Results:\n", infer_texts)

    # 두 번째 요청 (Diagram Analysis)
    diagram_url = "http://127.0.0.1:5000/diagram_analysis"
    diagram_response = send_request(diagram_url, image_url)

    if diagram_response:
        print("Diagram Analysis Response Data:")
        for idx, response in enumerate(diagram_response):
            print(response)

    # 테스트 종료 시간 및 실행 시간 출력
    end = time.time()
    print(f"Test completed in {end - start:.5f} seconds")

# 테스트 함수 실행
combined_test()
