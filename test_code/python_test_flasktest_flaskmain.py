import requests
import cv2
import os
import json
import firebase_admin
from firebase_admin import credentials, storage
import math
import time
from gtts import gTTS


# Firebase 초기화
cred = credentials.Certificate("secretkey/diagramproject-f4e78-firebase-adminsdk-c102g-787640d862.json")  # 서비스 계정 키 파일 경로
firebase_admin.initialize_app(cred, {
    'storageBucket': 'diagramproject-f4e78.appspot.com'  # Firebase Storage 버킷 이름
})
bucket = storage.bucket()

# 비디오와 API 정보
VIDEO_PATH = "video/real_test_video.mp4"  # 비디오 파일 경로
API_URL = "http://127.0.0.1:8000/find_scenes"  # Flask 서버의 엔드포인트 URL
TEMP_DIR = "temp_frames"  # 임시로 이미지를 저장할 디렉토리
os.makedirs(TEMP_DIR, exist_ok=True)

def upload_frame_to_firebase(frame_path, frame_index):
    """Firebase에 이미지를 업로드하고 URL을 반환합니다."""
    blob = bucket.blob(f"scenes/frame_{frame_index}.jpg")
    blob.upload_from_filename(frame_path)
    blob.make_public()  # 이미지를 공개 상태로 설정
    return blob.public_url

def extract_and_upload_frames(video_path, timestamps):
    """주어진 타임스탬프에 해당하는 프레임을 추출하고 Firebase에 업로드합니다."""
    video_capture = cv2.VideoCapture(video_path)
    frame_urls = []

    for index, timestamp in enumerate(timestamps):
        # 타임스탬프를 초 단위로 변환 (예: HH:MM:SS.mmm -> 초)
        try:
            parts = timestamp.split(":")
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])  # 초 부분을 float로 처리
            total_seconds = hours * 3600 + minutes * 60 + seconds +1
        except ValueError as e:
            print(f"Error parsing timestamp {timestamp}: {e}")
            continue

        fps = video_capture.get(cv2.CAP_PROP_FPS)
        frame_number = int(total_seconds * fps)

        # 해당 프레임으로 이동 후 캡처
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = video_capture.read()

        if ret:
            frame_path = os.path.join(TEMP_DIR, f"frame_{index}.jpg")
            cv2.imwrite(frame_path, frame)

            # Firebase에 업로드
            public_url = upload_frame_to_firebase(frame_path, index)
            frame_urls.append(public_url)
        else:
            print(f"Failed to capture frame for timestamp {timestamp}.")

    video_capture.release()
    return frame_urls

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

def combined_test(image_url):
    # 테스트 시작 시간
    start = time.time()

    # 보낼 이미지 URL
    #image_url = "https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__4654?alt=media&token=d1d01839-609a-4a2c-ac58-c261a217278b"

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
        print("장면 안의 텍스트는 다음과 같습니다:\n", infer_texts)

    # 두 번째 요청 (Diagram Analysis)
    diagram_url = "http://127.0.0.1:5000/diagram_analysis"
    diagram_response = send_request(diagram_url, image_url)

    if diagram_response:
        print("시각 자료 해설은 다음과 같습니다:")
        for idx, response in enumerate(diagram_response):
            print(response)

def combined_test_with_audio(image_url, index):
    # 테스트 시작 시간
    start = time.time()

    # OCR 요청 URL
    ocr_url = "http://127.0.0.1:5000/ocr_request"
    ocr_response = send_request(ocr_url, image_url)

    text_to_speak = ""  # 음성 파일로 변환할 텍스트

    if ocr_response:
        # inferText를 자연스럽게 연결하여 출력
        infer_texts = ""
        for infer_text in ocr_response:
            if infer_text.endswith(('.', '?', '!', '·')):
                infer_texts += infer_text + "\n"
            else:
                infer_texts += infer_text + " "
        print(f"[URL {index}] 장면 안의 텍스트는 다음과 같습니다:\n", infer_texts)
        text_to_speak += f"[URL {index}] 장면 안의 텍스트는 다음과 같습니다.\n" + infer_texts + "\n"

    # Diagram 분석 요청 URL
    diagram_url = "http://127.0.0.1:5000/diagram_analysis"
    diagram_response = send_request(diagram_url, image_url)

    if diagram_response:
        print(f"[URL {index}] 시각 자료 해설은 다음과 같습니다:")
        text_to_speak += f"[URL {index}] 시각 자료 해설은 다음과 같습니다.\n"
        for idx, response in enumerate(diagram_response):
            print(response)
            text_to_speak += f"{idx + 1}. {response}\n"

    # 음성 파일 생성 (인덱스 포함)
    audio_filename = f"output_audio_{index}.mp3"
    tts = gTTS(text=text_to_speak, lang='ko')  # 한국어로 설정
    tts.save(audio_filename)
    print(f"[URL {index}] 출력된 텍스트를 음성 파일로 저장했습니다: {audio_filename}")
    


def main():
    # 1. Flask 서버에 요청
    response = requests.post(API_URL, data={'video_path': VIDEO_PATH})
    if response.status_code != 200:
        print(f"Error: Failed to get response from API. Status code: {response.status_code}")
        return

    # 2. 응답 데이터에서 타임스탬프 추출
    scene_data = json.loads(response.text)
    timestamps = [scene[0] for scene in scene_data]  # 시작 타임스탬프만 추출
    print("Timestamps:", timestamps)

    # 3. 타임스탬프에 해당하는 프레임 추출 및 업로드
    frame_urls = extract_and_upload_frames(VIDEO_PATH, timestamps)

    # 4. 결과 출력
    print("Uploaded Frame URLs:")
    for url in frame_urls:
        print(url)
    
    #5. flask_main에 보내서 해설 생성
    # for url in frame_urls:
    #     combined_test(url)
    for idx, url in enumerate(frame_urls):
        combined_test_with_audio(url, idx)

if __name__ == "__main__":
    main()
