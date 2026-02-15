import cv2
import mediapipe as mp
from detector import ElbowPositions

draw_landmarks = mp.tasks.vision.drawing_utils.draw_landmarks
PoseLandmarksConnections = mp.tasks.vision.PoseLandmarksConnections

GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)
WHITE = (255, 255, 255)


def draw_pose(frame, pose_results):
    """Draw the full MediaPipe pose skeleton."""
    if pose_results.pose_landmarks and len(pose_results.pose_landmarks) > 0:
        draw_landmarks(
            frame,
            pose_results.pose_landmarks[0],
            PoseLandmarksConnections.POSE_LANDMARKS,
        )


def draw_elbows(frame, elbows: ElbowPositions):
    """Draw elbow markers with labels (swapped for mirror view)."""
    cv2.circle(frame, (elbows.right_x, elbows.right_y), 10, GREEN, -1)
    cv2.circle(frame, (elbows.left_x, elbows.left_y), 10, YELLOW, -1)
    cv2.putText(frame, "L", (elbows.right_x + 15, elbows.right_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, GREEN, 2)
    cv2.putText(frame, "R", (elbows.left_x + 15, elbows.left_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW, 2)


def draw_table_edge(frame, table_edge_x: int | None):
    """Draw the vertical table edge line."""
    if table_edge_x is None:
        return
    height = frame.shape[0]
    cv2.line(frame, (table_edge_x, 0), (table_edge_x, height), RED, 3)
    cv2.putText(frame, "Table Edge", (table_edge_x + 5, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED, 2)


def draw_violation_warning(frame):
    """Draw the violation warning text."""
    cv2.putText(frame, "ELBOW VIOLATION!", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, RED, 3)


def draw_status(frame, calibrating: bool):
    """Draw calibration/status text at the bottom."""
    height = frame.shape[0]
    if calibrating:
        text = "Click to set table edge line"
    else:
        text = "Table edge set - try throwing motions!"
    cv2.putText(frame, text, (20, height - 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)


def draw_debug(frame, elbows: ElbowPositions):
    """Draw elbow coordinate debug info."""
    height = frame.shape[0]
    cv2.putText(frame, f"Visual left elbow: ({elbows.right_x}, {elbows.right_y})",
                (20, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    cv2.putText(frame, f"Visual right elbow: ({elbows.left_x}, {elbows.left_y})",
                (20, height - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
