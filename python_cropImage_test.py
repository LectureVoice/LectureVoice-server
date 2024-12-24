from PIL import Image
import requests
from io import BytesIO
import firebase_admin
from firebase_admin import credentials, storage

# Firebase Admin SDK 초기화 (위에서 설명한 대로)
cred = credentials.Certificate("secretkey/diagramproject-f4e78-firebase-adminsdk-c102g-787640d862.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'diagramproject-f4e78.appspot.com'
})

def crop_image(image_url, rect_coords):
    # 이미지 URL에서 이미지 다운로드
    response = requests.get(image_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download image from URL: {image_url}")
    
    # 이미지를 PIL 이미지 객체로 변환
    img = Image.open(BytesIO(response.content))

    # 좌표 추출
    x = rect_coords['x']
    y = rect_coords['y']
    width = rect_coords['width']
    height = rect_coords['height']

    # 이미지 자르기 (crop)
    cropped_img = img.crop((x, y, x + width, y + height))

    return cropped_img  # PIL 이미지 객체 반환

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

rect_coords = {
    'x': 100,
    'y': 150,
    'width': 200,
    'height': 300
}

cropped_image = crop_image("https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__27128?alt=media&token=4839396d-982b-447f-90ce-4f61207aed39", rect_coords)

# 크롭된 이미지를 Firebase에 업로드하고 다운로드 URL 얻기
file_name = 'cropped_image.png'
download_url = upload_to_firebase(cropped_image, file_name)

print(f"Cropped image URL: {download_url}")
