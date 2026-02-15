import mediapipe as mp
import cv2
from dataclasses import dataclass
from pathlib import Path

MODEL_PATH = str(Path(__file__).parent / "pose_landmarker_full.task")

PoseLandmark = mp.tasks.vision.PoseLandmark


@dataclass
class ElbowPositions:
    right_x: int
    right_y: int
    left_x: int
    left_y: int


class PoseDetector:
    def __init__(self, min_detection_confidence=0.8, min_tracking_confidence=0.8):
        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            min_pose_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)
        self.frame_timestamp = 0

    def detect(self, frame):
        """Process a frame and return elbow positions, or None if no pose detected."""
        height, width, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

        self.frame_timestamp += 33  # ~30fps
        results = self.landmarker.detect_for_video(mp_image, self.frame_timestamp)

        if not results.pose_landmarks or len(results.pose_landmarks) == 0:
            return None, results

        landmarks = results.pose_landmarks[0]
        right = landmarks[PoseLandmark.RIGHT_ELBOW]
        left = landmarks[PoseLandmark.LEFT_ELBOW]

        elbows = ElbowPositions(
            right_x=int(right.x * width),
            right_y=int(right.y * height),
            left_x=int(left.x * width),
            left_y=int(left.y * height),
        )
        return elbows, results

    def close(self):
        self.landmarker.close()
