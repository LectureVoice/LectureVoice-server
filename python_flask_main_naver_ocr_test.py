import requests
import json
import time

def test_flask_ocr_request():
    # 테스트 시작 시간
    start = time.time()

    # Flask 애플리케이션의 기본 URL (ocr_request 엔드포인트)
    url = "http://127.0.0.1:5000/ocr_request"

    # 테스트할 이미지 URL 목록
    test_image_urls = [
        "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__27128?alt=media&token=fd97f70e-45d4-44d7-9c01-e09f87d23a1e",
        # 다른 이미지 URL 추가 가능
    ]

    # JSON 데이터 준비
    data = {
        "image_urls": test_image_urls
    }

    # POST 요청 보내기
    response = requests.post(url, json=data)

    # 응답 상태 코드 확인
    if response.status_code == 200:
        print("Request succeeded")
    else:
        print(f"Request failed with status code {response.status_code}")
        return  # 에러가 발생하면 테스트 종료

    # 응답 데이터 확인
    try:
        response_data = response.json()  # JSON 응답 파싱
    except ValueError:
        print("Invalid JSON response")
        return  # JSON 파싱 에러 발생 시 종료

    # inferText를 자연스럽게 연결하여 출력
    infer_texts = ""
    for infer_text in response_data:
        # 문장 끝을 의미하는 기호로 끝나면 줄바꿈 추가
        if infer_text.endswith(('.', '?', '!', '·')):
            infer_texts += infer_text + "\n"
        else:
            infer_texts += infer_text + " "

    print("Infer Text Results:\n", infer_texts)

    # 테스트 결과 검증
    assert isinstance(response_data, list), "Response should be a list"
    assert len(response_data) == len(test_image_urls), "Response length should match the number of image URLs"
    for infer_text in response_data:
        assert infer_text is not None, "InferText should not be None"

    # 테스트 종료 시간 및 실행 시간 출력
    end = time.time()
    print(f"Test completed in {end - start:.5f} seconds")

# 테스트 함수 실행
test_flask_ocr_request()
