import cv2

def preprocess_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (224, 224))
        frames.append(frame)
    cap.release()
    frames = np.array(frames) / 255.0
    return frames

if __name__ == "__main__":
    video_frames = preprocess_video('sample_video.mp4')
    print(f"Processed Video Frames Shape: {video_frames.shape}")
