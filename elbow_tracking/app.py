import collections
import os
import platform
import subprocess
import sys

# Suppress noisy OpenCV/FFmpeg/TF warnings before importing cv2
os.environ["OPENCV_LOG_LEVEL"] = "ERROR"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import cv2
from detector import PoseDetector
from gesture import GestureDetector
from violation import check_violation
import renderer

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
REPLAY_BUFFER_SIZE = 300  # ~10s at 30fps
PUNISHMENT_DURATION = 90  # ~3s at 30fps
OUTPUT_WIDTH = 1920
OUTPUT_HEIGHT = 1080
MAX_CAMERA_PROBE = 8


def discover_cameras():
    """Probe available cameras and return list of (index, name) tuples."""
    # Get camera names from macOS system_profiler if available
    names = {}
    if platform.system() == "Darwin":
        try:
            out = subprocess.check_output(
                ["system_profiler", "SPCameraDataType"],
                text=True, timeout=5,
            )
            idx = 0
            for line in out.splitlines():
                line = line.strip()
                # Camera names appear as lines ending with ':'
                # that aren't section headers like "Camera:"
                if line.endswith(":") and not line.startswith("Camera"):
                    names[idx] = line.rstrip(":")
                    idx += 1
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    # Use AVFoundation backend on macOS to avoid noisy FFmpeg fallback.
    # Redirect stderr to suppress C++-level "out device of bound" warnings
    # that OpenCV emits when probing non-existent camera indices.
    backend = cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY
    cameras = []
    stderr_fd = sys.stderr.fileno()
    saved_stderr = os.dup(stderr_fd)
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, stderr_fd)
    try:
        for i in range(MAX_CAMERA_PROBE):
            cap = cv2.VideoCapture(i, backend)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    name = names.get(i, f"Camera {i}")
                    cameras.append((i, name))
                cap.release()
    finally:
        os.dup2(saved_stderr, stderr_fd)
        os.close(saved_stderr)
        os.close(devnull)
    return cameras


def select_camera():
    """Show a terminal menu of available cameras and return the selected index."""
    print("Scanning for cameras...")
    cameras = discover_cameras()

    if not cameras:
        print("No cameras found.")
        sys.exit(1)

    if len(cameras) == 1:
        idx, name = cameras[0]
        print(f"Using: {name} (index {idx})")
        return idx

    print("\nAvailable cameras:")
    for i, (idx, name) in enumerate(cameras):
        print(f"  [{i + 1}] {name}  (index {idx})")

    while True:
        choice = input(f"\nSelect camera [1-{len(cameras)}]: ").strip()
        try:
            num = int(choice)
            if 1 <= num <= len(cameras):
                idx, name = cameras[num - 1]
                print(f"Using: {name} (index {idx})")
                return idx
        except ValueError:
            pass
        print("Invalid choice, try again.")


class ElbowTracker:
    def __init__(self, camera_index=0):
        self.detector = PoseDetector()
        self.gesture_detector = GestureDetector()
        self.table_edge_x = None
        self.calibrating = True
        self.camera_index = camera_index
        backend = cv2.CAP_AVFOUNDATION if platform.system() == "Darwin" else cv2.CAP_ANY
        self.cap = cv2.VideoCapture(camera_index, backend)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self.frame_buffer = collections.deque(maxlen=REPLAY_BUFFER_SIZE)
        self.window_name = f"Elbow Tracker - Camera {camera_index}"
        self.punishment_timer = 0

    def on_mouse(self, event, x, y, flags, param):
        """Handle mouse clicks, scaling from output image space to camera frame space."""
        if event == cv2.EVENT_LBUTTONDOWN:
            # With WINDOW_NORMAL, OpenCV reports coords in image-pixel space
            frame_x = int(x * CAMERA_WIDTH / OUTPUT_WIDTH)
            self.table_edge_x = frame_x
            self.calibrating = False
            print(f"Table edge set at x={frame_x} (image click: {x})")

    def reset_calibration(self):
        self.table_edge_x = None
        self.calibrating = True
        print("Table edge reset - click to set new position")

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self.on_mouse)

        print("Elbow Tracker (PiP)")
        print(f"  Output: {OUTPUT_WIDTH}x{OUTPUT_HEIGHT}")
        print(f"  Replay buffer: {REPLAY_BUFFER_SIZE} frames (~10s)")
        print("  Click to set table edge | 'r' to reset | 'q' to quit")

        while self.cap.isOpened():
            success, frame = self.cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)

            elbows, pose_results = self.detector.detect(frame)

            renderer.draw_pose(frame, pose_results)

            if elbows:
                renderer.draw_elbows(frame, elbows)

                if check_violation(elbows, self.table_edge_x):
                    renderer.draw_violation_warning(frame)
                else:
                    renderer.reset_violation_warning()

            renderer.draw_table_edge(frame, self.table_edge_x)
            renderer.draw_status(frame, self.calibrating)

            # Easter egg: middle finger triggers punishment bong
            if self.gesture_detector.detect_middle_finger(frame):
                self.punishment_timer = PUNISHMENT_DURATION
            if self.punishment_timer > 0:
                renderer.draw_punishment(frame)
                self.punishment_timer -= 1

            # Push the fully rendered frame into the replay buffer
            self.frame_buffer.append(frame.copy())

            # Compose PiP: replay (delayed) fills output, live is small overlay
            if len(self.frame_buffer) == REPLAY_BUFFER_SIZE:
                replay_frame = self.frame_buffer[0]
                display = renderer.compose_pip(
                    replay_frame, frame, OUTPUT_WIDTH, OUTPUT_HEIGHT)
            else:
                buffering = renderer.draw_buffering(OUTPUT_WIDTH, OUTPUT_HEIGHT)
                display = renderer.compose_pip(
                    buffering, frame, OUTPUT_WIDTH, OUTPUT_HEIGHT)

            cv2.imshow(self.window_name, display)

            key = cv2.waitKey(5) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("r"):
                self.reset_calibration()

        self.cap.release()
        self.detector.close()
        self.gesture_detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    camera_index = select_camera()
    tracker = ElbowTracker(camera_index)
    tracker.run()
