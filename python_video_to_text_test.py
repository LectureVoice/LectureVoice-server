# from moviepy.editor import VideoFileClip
# import speech_recognition as sr
# from pathlib import Path

# # 비디오 경로 설정
# video_path = "video/real_test_video.mp4"
# video = VideoFileClip(video_path)
# audio = video.audio
# video_file_name = Path(video_path).stem

# # 타임스탬프 배열
# timestamps = ['00:00:00.000', '00:00:06.142', '00:00:18.657', '00:00:30.644', '00:00:36.886', '00:00:41.806']

# # 타임스탬프를 초 단위로 변환하는 함수
# def timestamp_to_seconds(timestamp):
#     h, m, s = map(float, timestamp.split(':'))
#     return h * 3600 + m * 60 + s

# # 초 단위로 변환된 타임스탬프 리스트
# timestamps_seconds = [timestamp_to_seconds(ts) for ts in timestamps]

# # 오디오-텍스트 변환기 초기화
# recognizer = sr.Recognizer()

# # 결과 저장
# results = []

# # 각 구간 처리
# for i in range(len(timestamps_seconds) - 1):
#     start_time = timestamps_seconds[i]
#     end_time = timestamps_seconds[i + 1]
    
#     # 특정 시간 범위의 오디오 추출
#     audio_segment = audio.subclip(start_time, end_time)
#     audio_path = f"video/extracted_audio_{video_file_name}_{i}.wav"
#     audio_segment.write_audiofile(audio_path)
    
#     # 오디오를 텍스트로 변환
#     with sr.AudioFile(audio_path) as source:
#         try:
#             audio_data = recognizer.record(source)
#             text = recognizer.recognize_google(audio_data, language='ko-KR')
#         except sr.UnknownValueError:
#             text = "[Unintelligible]"
#         except sr.RequestError as e:
#             text = f"[Error: {e}]"
    
#     # 결과 저장
#     results.append({
#         "segment": f"{timestamps[i]} - {timestamps[i+1]}",
#         "text": text
#     })

# # 결과 출력
# for result in results:
#     print(f"Segment: {result['segment']}\nText: {result['text']}\n")

from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pathlib import Path

# 비디오 경로 설정
video_path = "video/chap6_deeplearning.mp4"
video = VideoFileClip(video_path)
audio = video.audio
video_file_name = Path(video_path).stem

# 타임스탬프 배열
timestamps = ['00:00:00.000', '00:00:06.142', '00:00:18.657', '00:00:30.644', '00:00:36.886', '00:00:41.806']

# 타임스탬프를 초 단위로 변환하는 함수
def timestamp_to_seconds(timestamp):
    h, m, s = map(float, timestamp.split(':'))
    return h * 3600 + m * 60 + s

# 초 단위로 변환된 타임스탬프 리스트
timestamps_seconds = [timestamp_to_seconds(ts) for ts in timestamps]

# 비디오의 총 길이를 추가
if timestamps_seconds[-1] < video.duration:
    timestamps_seconds.append(video.duration)

# 오디오-텍스트 변환기 초기화
recognizer = sr.Recognizer()

# 결과 저장
results = []

# 각 구간 처리
for i in range(len(timestamps_seconds) - 1):
    start_time = timestamps_seconds[i]
    end_time = timestamps_seconds[i + 1]
    
    # 특정 시간 범위의 오디오 추출
    audio_segment = audio.subclip(start_time, end_time)
    audio_path = f"video/extracted_audio_{video_file_name}_{i}.wav"
    audio_segment.write_audiofile(audio_path)
    
    # 오디오를 텍스트로 변환
    with sr.AudioFile(audio_path) as source:
        try:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language='ko-KR')
        except sr.UnknownValueError:
            text = "[Unintelligible]"
        except sr.RequestError as e:
            text = f"[Error: {e}]"
    
    # 결과 저장
    results.append({
        "segment": f"{timestamps[i]} - {timestamps[i+1]}" if i < len(timestamps) - 1 else f"{timestamps[i]} - End",
        "text": text
    })

# 결과 출력
for result in results:
    print(f"Segment: {result['segment']}\nText: {result['text']}\n")
