import urllib.parse

def extract_image_name_from_url(url):
    # URL에서 파일 경로 추출
    parsed_url = urllib.parse.urlparse(url)
    # 파일 경로에서 파일 이름 부분만 추출
    path = parsed_url.path
     # '%2F'를 '/'로 변환 (URL에서 '/'가 '%2F'로 인코딩됨)
    decoded_path = urllib.parse.unquote(path)
    file_name = decoded_path.split('/')[-1]
    return file_name

filename = extract_image_name_from_url("https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/sceneImage%2Fimage__27128?alt=media&token=4839396d-982b-447f-90ce-4f61207aed39")
print(filename)