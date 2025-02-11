from moviepy.editor import VideoFileClip
import speech_recognition as sr
from pathlib import Path
import wave

def extract_audio_and_transcribe(video_path):
    """Extract audio from a video and transcribe it completely."""
    video = VideoFileClip(video_path)
    audio = video.audio
    video_file_name = Path(video_path).stem

    # Extract the entire audio
    audio_path = f"extracted_audio_{video_file_name}.wav"
    audio.write_audiofile(audio_path)

    # Verify audio format and duration
    with wave.open(audio_path, "rb") as wf:
        frame_rate = wf.getframerate()
        channels = wf.getnchannels()
        duration = wf.getnframes() / frame_rate
        print(f"Audio Frame Rate: {frame_rate}, Channels: {channels}, Duration: {duration} seconds")

    # Initialize speech recognizer
    recognizer = sr.Recognizer()

    # Transcribe the audio
    with sr.AudioFile(audio_path) as source:
        try:
            print("Extracting and converting audio to text...")
            audio_data = recognizer.record(source, duration=duration)
            text = recognizer.recognize_google(audio_data, language='ko-KR')
        except sr.UnknownValueError:
            text = "[Unintelligible]"
        except sr.RequestError as e:
            text = f"[Error: {e}]"
        except Exception as e:
            text = f"[General Error: {e}]"

    return text

if __name__ == "__main__":
    # Video file path
    video_path = "video/chat5_deeplearning.mp4"  # Replace with your video file path

    # Extract and transcribe
    transcription = extract_audio_and_transcribe(video_path)
    print(transcription)

    # Save transcription to a file
    # with open("transcription.txt", "w", encoding="utf-8") as text_file:
    #     text_file.write(transcription)

    print("Transcription saved to transcription.txt")
