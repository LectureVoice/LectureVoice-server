import requests, json, os

def send_to_clova_ocr(image_url, image_name_from_url):
    # Send image to Naver Clova OCR and return the result
    url = "NAVER_CLOVA_OCR_URL"
    header = {'Content-Type': 'application/json', 
              'X-OCR-SECRET':'X_OCR_SECRET_KEY'}
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
        print("******** RESPONSE **********")
        print(res)

        # JSON 응답 데이터를 파싱
        ocr_data = res.json()
        print("OCR Result:", ocr_data)

        # 디렉토리 생성 (존재하지 않으면)
        directory = './ocrResult'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # JSON 데이터를 파일로 저장
        jsonfile_name = 'ocr_result_{}.json'.format(image_name_from_url)
        file_path = os.path.join(directory, jsonfile_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ocr_data, f, ensure_ascii=False, indent=4)

        print(f"OCR result saved to {file_path}")
        return res
    
@app.route('/ocr_request', methods=['POST'])
def ocr_request():
    image_urls = request.json['image_urls']
    for url in image_urls:
        image_name_from_url = extract_image_name_from_url(url)
        # Step 2: Send image to Clova OCR
        ocr_result = send_to_clova_ocr(url, image_name_from_url)
    return ocr_result






def 설명_생성(arrow_count, rec_center, requestResult_join):
    # 화살표가 없으면 표로 간주
    if arrow_count == 0:
        # 표 설명 생성
        sentence_result = "이 그림은 표입니다.\n"

        # 행 계산
        y_values = 정렬([center[1] for center in rec_center])
        unique_y_values = 고유_값(y_values)
        num_rows = 길이(고유_값(y_values))
        
        # 열 계산
        threshold = 0.5
        x_values = 정렬([center[0] for center in rec_center])
        unique_x_values = []
        for x in x_values:
            if unique_x_values가_비어있거나(abs(unique_x_values[-1] - x) > threshold):
                unique_x_values에_추가(x)
        num_cols = 길이(unique_x_values)

        # 행과 열 정보 추가
        sentence_result += f"이 표의 행은 {num_rows} 개이며 열은 {num_cols} 개입니다.\n"
        
        # 각 셀의 설명 생성
        temp_idx = 0
        for row in range(num_rows):
            for col in range(num_cols):
                if requestResult_join[temp_idx]:
                    sentence_result += f"{row+1}번째 행의 {col+1}번째 열은 {requestResult_join[temp_idx]}입니다.\n"
                    temp_idx += 1

    # 화살표가 있으면 다이어그램으로 간주
    else:
        sentence_result = "이 그림은 다이어그램입니다.\n"
    
    return sentence_result
