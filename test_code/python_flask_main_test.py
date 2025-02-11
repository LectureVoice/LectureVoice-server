import requests
import json
import math
import time

def test_flask_main():
    # Flask 애플리케이션의 기본 URL
    start = time.time()
    url = "http://127.0.0.1:5000/diagram_analysis"

    # 테스트할 이미지 URL 목록
    test_image_urls = [
        
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__4654?alt=media&token=d1d01839-609a-4a2c-ac58-c261a217278b",
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__19603?alt=media&token=6db27696-83ed-450e-aea1-8220f46b4a54",
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__22507?alt=media&token=4355fbde-9e96-4818-af08-70d77988c086",
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__27128?alt=media&token=fd97f70e-45d4-44d7-9c01-e09f87d23a1e",   
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__11155?alt=media&token=f5cf35e2-d25d-4a3b-9294-255dcc5fb14b",
        "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__1?alt=media&token=e1dfd97c-e00c-43b6-9e46-d5d33cf22a33",
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__14752?alt=media&token=dbd4482e-35ed-476e-a495-a35383f94356",
        #"https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/paperTestImage.png?alt=media&token=2862f009-e6b0-47c2-b543-427020a0e3e9",
        "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/scenes%2Fnew_frame_0.jpg?alt=media&token=a53aede6-c839-4b43-974a-c3ae93a9960e"
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

    # 응답 데이터 확인
    response_data = response.json()
    #print("Response Data:", response_data)
    print("Response Data")
    for response in range(len(response_data)):
        print('{}번째 response \n'.format(response))
        print(response_data[response])

    # 테스트 결과 검증
    assert isinstance(response_data, list)
    assert len(response_data) == len(test_image_urls)
    for result in response_data:
        assert result is not None

    end = time.time()
    print(f"{end - start:.5f} sec")

# 테스트 함수 실행
test_flask_main()


