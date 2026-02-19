import cv2
import numpy as np
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
    cv2.putText(frame, "TABLE EDGE", (table_edge_x + 5, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED, 2)


_violation_frame_count = 0


def draw_violation_warning(frame):
    """Draw flashing red border and violation text."""
    global _violation_frame_count
    _violation_frame_count += 1

    # Flash on/off every 4 frames
    if (_violation_frame_count // 4) % 2 == 0:
        h, w = frame.shape[:2]
        border = 20
        cv2.rectangle(frame, (0, 0), (w - 1, h - 1), RED, border)

    cv2.putText(frame, "ELBOW VIOLATION!", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, RED, 3)


def reset_violation_warning():
    """Reset the flash counter when no violation is active."""
    global _violation_frame_count
    _violation_frame_count = 0


def draw_status(frame, calibrating: bool):
    """Draw calibration status text at the bottom."""
    if not calibrating:
        return
    height = frame.shape[0]
    cv2.putText(frame, "CALIBRATING - Click to set table edge",
                (20, height - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, YELLOW, 2)


def draw_debug(frame, elbows: ElbowPositions):
    """Draw elbow coordinate debug info."""
    height = frame.shape[0]
    cv2.putText(frame, f"Visual left elbow: ({elbows.right_x}, {elbows.right_y})",
                (20, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    cv2.putText(frame, f"Visual right elbow: ({elbows.left_x}, {elbows.left_y})",
                (20, height - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)


def draw_feed_label(frame, text):
    """Draw a 'LIVE' or 'REPLAY' label in the bottom-right corner of a feed."""
    h, w = frame.shape[:2]
    bg_color = RED if text == "LIVE" else (200, 120, 0)
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    pad = 6
    x = w - tw - pad * 2 - 8
    y = h - th - pad * 2 - 8
    cv2.rectangle(frame, (x, y), (x + tw + pad * 2, y + th + pad * 2), bg_color, -1)
    cv2.putText(frame, text, (x + pad, y + th + pad),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)


def draw_buffering(screen_w, screen_h):
    """Return a black frame with a 'Buffering...' message centered."""
    frame = np.zeros((screen_h, screen_w, 3), dtype=np.uint8)
    text = "REPLAY LOADING..."
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 3)
    x = (screen_w - tw) // 2
    y = (screen_h + th) // 2
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 2.0, WHITE, 3)
    return frame


def compose_pip(replay_frame, live_frame, screen_w, screen_h):
    """Compose a fullscreen PiP: replay fills the screen, live is a small overlay."""
    # Resize replay to fill the screen
    canvas = cv2.resize(replay_frame, (screen_w, screen_h))
    draw_feed_label(canvas, "REPLAY")

    # PiP size: 1/4 width, maintain aspect ratio
    pip_w = screen_w // 4
    pip_h = int(pip_w * live_frame.shape[0] / live_frame.shape[1])
    pip = cv2.resize(live_frame, (pip_w, pip_h))
    draw_feed_label(pip, "LIVE")

    # Position in top-right corner with a margin and border
    margin = 16
    border = 3
    x1 = screen_w - pip_w - margin
    y1 = margin

    # Draw border
    cv2.rectangle(canvas,
                  (x1 - border, y1 - border),
                  (x1 + pip_w + border, y1 + pip_h + border),
                  WHITE, border)

    # Overlay PiP
    canvas[y1:y1 + pip_h, x1:x1 + pip_w] = pip

    return canvas


def draw_punishment(frame):
    """Draw a 'PUNISHMENT BONG!' overlay centered on the frame."""
    h, w = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, h // 3), (w, 2 * h // 3), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

    text = "PUNISHMENT BONG"
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2.5, 4)
    x = (w - tw) // 2
    y = (h + th) // 2 - 20
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, 2.5, RED, 4)

    sub = "Don't disrespect the elbow tracker!"
    (sw, sh), _ = cv2.getTextSize(sub, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)
    cv2.putText(frame, sub, ((w - sw) // 2, y + th + 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, WHITE, 2)


