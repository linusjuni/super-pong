import cv2
from detector import PoseDetector
from violation import check_violation
import renderer

WINDOW_NAME = "Elbow Tracker"
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720


class ElbowTracker:
    def __init__(self):
        self.detector = PoseDetector()
        self.table_edge_x = None
        self.calibrating = True
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.table_edge_x = x
            self.calibrating = False
            print(f"Table edge set at x={x}")

    def reset_calibration(self):
        self.table_edge_x = None
        self.calibrating = True
        print("Table edge reset - click to set new position")

    def run(self):
        cv2.namedWindow(WINDOW_NAME)
        cv2.setMouseCallback(WINDOW_NAME, self.on_mouse)

        print("Elbow Tracker")
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
                renderer.draw_debug(frame, elbows)

                if check_violation(elbows, self.table_edge_x):
                    renderer.draw_violation_warning(frame)

            renderer.draw_table_edge(frame, self.table_edge_x)
            renderer.draw_status(frame, self.calibrating)

            cv2.imshow(WINDOW_NAME, frame)

            key = cv2.waitKey(5) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("r"):
                self.reset_calibration()

        self.cap.release()
        self.detector.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    tracker = ElbowTracker()
    tracker.run()
