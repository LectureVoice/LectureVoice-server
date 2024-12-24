# Flask 애플리케이션을 초기화

# 이미지 전처리 함수 정의
def preprocess(image):
    - 이미지를 그레이스케일로 변환
    - 블러 처리하여 잡음 제거
    - 에지 감지를 통해 윤곽선 검출
    - 팽창과 침식을 사용하여 윤곽선 강화
    - 처리된 이미지를 반환

# 중심점과 꼭짓점을 기반으로 컨투어 병합 함수 정의
def merge_contours_by_center_with_vertex_preference(contours, distance_threshold):
    - 빈 리스트를 생성하여 병합된 컨투어 저장
    - 각 컨투어에 대해:
        - 컨투어의 중심점 계산
        - 다른 컨투어와 중심점 간의 거리를 비교
        - 거리가 임계값 이하인 경우, 꼭짓점 수가 더 많은 컨투어 선택
    - 병합된 컨투어 리스트 반환

# 다이어그램 탐지 함수 정의
def main_diagram_detect(image_data, ocr_result_file):
    - OCR 결과 파일 이름 출력
    - 이미지와 OCR 결과 파일을 사용하여 다이어그램 탐지 로직 실행
    - 결과 반환

# Flask 경로 설정
- POST 요청을 받아 이미지를 처리하는 경로 정의
    - 요청에서 이미지를 읽어들임
    - 다이어그램 탐지 함수 호출
    - 탐지 결과 반환

# 애플리케이션을 디버그 모드에서 실행


