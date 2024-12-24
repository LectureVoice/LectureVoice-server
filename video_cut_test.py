from scenedetect import detect, ContentDetector, SceneManager, open_video

#threshold changing code
def find_scenes(video_path, threshold=10.0):
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(
        ContentDetector(threshold=threshold))
    # Detect all scenes in video from current position to end.
    scene_manager.detect_scenes(video)
    # `get_scene_list` returns a list of start/end timecode pairs
    # for each scene that was found.
    return scene_manager.get_scene_list()


#scene_list = detect('OS_modityFile.mp4', ContentDetector())
scene_list = find_scenes('OS_modityFile.mp4')

for i, scene in enumerate(scene_list):
    print('Scene %2d: Start %s / Frame %d, End %s / Frame %d' % (
        i+1,
        scene[0].get_timecode(), scene[0].get_frames(),
        scene[1].get_timecode(), scene[1].get_frames(),))
    

    
#만약 scene의 총 길이가 1초 미만이면 삭제하는 것도 고려
#여기에서 처리하면 될 듯