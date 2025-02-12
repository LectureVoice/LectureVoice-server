from flask import Flask, jsonify, request
import scenedetect, json
from scenedetect import detect, ContentDetector, SceneManager, open_video

app = Flask(__name__)

@app.route('/find_scenes', methods=["POST"])

#threshold changing code
def find_scenes():
    #video_posted = request.form
    #video = open_video("test_pythonLecture.mp4")
    video_path = request.form['video_path']
    print("video path = " + video_path)
    video = open_video(video_path)
    #video = open_video("https://firebasestorage.googleapis.com/v0/b/diagramproject-f4e78.appspot.com/o/video%2FOS_cutfile_11sec.mp4?alt=media&token=7eee1017-e066-4236-97b2-23b6ea9b72ce")
    #OS_cutfile_11sec.mp4
    #test_pythonLecture

    #video = open_video(video)
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=5.0))
    # Detect all scenes in video from current position to end.
    scene_manager.detect_scenes(video)
    scene_list = scene_manager.get_scene_list()
    # `get_scene_list` returns a list of start/end timecode pairs
    # for each scene that was found.


    scene_result = [[1 for j in range(4)] for i in range(len(scene_list))]
    #print(len(scene_list))

    for i, scene in enumerate(scene_list):
        scene_result[i][0] = scene[0].get_timecode()
        scene_result[i][1] = scene[1].get_timecode()
        scene_result[i][2] = scene[0].get_frames()
        scene_result[i][3] = scene[1].get_frames()

        print('Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
            i,
            scene[0].get_timecode(), scene[0].get_frames(),
            scene[1].get_timecode(), scene[1].get_frames(),))
        
        
    return json.dumps(scene_result)

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True, port=8000,)


    