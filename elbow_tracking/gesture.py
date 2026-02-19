import math

import mediapipe as mp
import cv2
from pathlib import Path

MODEL_PATH = str(Path(__file__).parent / "hand_landmarker.task")

# Hand landmark indices (see MediaPipe hand landmark model documentation).
WRIST = 0
FINGERS = {
    "index": (8, 5),    # INDEX_FINGER_TIP, INDEX_FINGER_MCP
    "middle": (12, 9),  # MIDDLE_FINGER_TIP, MIDDLE_FINGER_MCP
    "ring": (16, 13),   # RING_FINGER_TIP, RING_FINGER_MCP
    "pinky": (20, 17),  # PINKY_TIP, PINKY_MCP
}

EXTENDED_THRESHOLD = 1.5   # tip/mcp distance ratio to count as extended
CURLED_THRESHOLD = 1.2     # below this counts as curled


def _dist(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2)


def _finger_ratio(landmarks, tip, mcp):
    """Ratio of tip-to-wrist distance over mcp-to-wrist distance."""
    wrist = landmarks[WRIST]
    d_tip = _dist(landmarks[tip], wrist)
    d_mcp = _dist(landmarks[mcp], wrist)
    if d_mcp < 1e-6:
        return 0.0
    return d_tip / d_mcp


def _is_middle_finger(landmarks):
    """True if only the middle finger is extended (works at any hand angle)."""
    middle_extended = _finger_ratio(landmarks, *FINGERS["middle"]) > EXTENDED_THRESHOLD
    others_curled = all(
        _finger_ratio(landmarks, *FINGERS[f]) < CURLED_THRESHOLD
        for f in ("index", "ring", "pinky")
    )
    return middle_extended and others_curled


class GestureDetector:
    def __init__(self):
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=MODEL_PATH),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.frame_timestamp = 0

    def detect_middle_finger(self, frame):
        """Returns True if any detected hand is showing the middle finger."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.frame_timestamp += 33
        results = self.landmarker.detect_for_video(mp_image, self.frame_timestamp)

        if not results.hand_landmarks:
            return False

        return any(_is_middle_finger(hand) for hand in results.hand_landmarks)

    def close(self):
        self.landmarker.close()
