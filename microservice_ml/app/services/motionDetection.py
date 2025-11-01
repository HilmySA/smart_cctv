import cv2
import mediapipe as mp

mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(static_image_mode=True)
last_hip_position = None

def detect_movement_by_hip(frame):
    global last_hip_position
    frame_height, frame_width, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = holistic.process(rgb)

    motion_result = {
        "status": "No movement",
        "hip": None
    }

    if results.pose_landmarks:
        left_hip = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_HIP]
        right_hip = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_HIP]

        if left_hip.visibility > 0.5 and right_hip.visibility > 0.5:
            hip_x = (left_hip.x + right_hip.x) / 2
            hip_y = (left_hip.y + right_hip.y) / 2

            if last_hip_position is not None:
                dx = abs(hip_x - last_hip_position[0])
                dy = abs(hip_y - last_hip_position[1])
                if dx > 0.01 or dy > 0.01:
                    motion_result["status"] = "Movement detected"

            last_hip_position = (hip_x, hip_y)
            motion_result["hip"] = {
                "x": int(hip_x * frame_width),
                "y": int(hip_y * frame_height)
            }

    return motion_result
