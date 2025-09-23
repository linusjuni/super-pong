import cv2
import mediapipe as mp

class ElbowTracker:
    def __init__(self):
        # Initialize MediaPipe pose detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        
        # Initialize pose detection with high confidence for better accuracy
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        
        # Camera setup
        self.cap = cv2.VideoCapture(0)
        
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Table edge line
        self.table_edge_x = None
        self.calibration_mode = True
        
        print("Elbow Tracker MVP")
        print("Instructions:")
        print("1. Position yourself so your throwing arm is visible")
        print("2. Click on the screen to set the 'table edge' line")
        print("3. Make throwing motions to test elbow detection")
        print("4. Press 'q' to quit, 'r' to reset table edge")
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse clicks to set table edge"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.table_edge_x = x
            self.calibration_mode = False
            print(f"Table edge set at x={x}")
    
    def check_elbow_violation(self, elbow_x, frame_width):
        """Check if elbow crosses the table edge"""
        if self.table_edge_x is None:
            return False
            
        # Convert normalized coordinates to pixel coordinates
        elbow_pixel_x = int(elbow_x * frame_width)
        
        # Check if elbow crosses the table edge line
        return elbow_pixel_x > self.table_edge_x
    
    def run(self):
        # Set up mouse callback for table edge calibration
        cv2.namedWindow('Elbow Tracker')
        cv2.setMouseCallback('Elbow Tracker', self.mouse_callback)
        
        while self.cap.isOpened():
            success, image = self.cap.read()
            if not success:
                print("Failed to read from camera")
                continue
            
            # Flip the image horizontally for mirror effect
            image = cv2.flip(image, 1)
            height, width, _ = image.shape
            
            # Convert BGR to RGB for MediaPipe
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rgb_image.flags.writeable = False
            
            # Process the image for pose detection
            results = self.pose.process(rgb_image)
            
            # Convert back to BGR for OpenCV
            rgb_image.flags.writeable = True
            image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
            
            # Draw pose landmarks
            if results.pose_landmarks:
                # Draw full pose
                self.mp_drawing.draw_landmarks(
                    image,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                # Get elbow landmarks
                landmarks = results.pose_landmarks.landmark
                right_elbow = landmarks[self.mp_pose.PoseLandmark.RIGHT_ELBOW]
                left_elbow = landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW]
                
                # Convert to pixel coordinates
                right_elbow_x = int(right_elbow.x * width)
                right_elbow_y = int(right_elbow.y * height)
                left_elbow_x = int(left_elbow.x * width)
                left_elbow_y = int(left_elbow.y * height)
                
                # Draw elbow points with larger circles
                cv2.circle(image, (right_elbow_x, right_elbow_y), 10, (0, 255, 0), -1)
                cv2.circle(image, (left_elbow_x, left_elbow_y), 10, (0, 255, 255), -1)
                
                # Add labels (swapped to match visual appearance in mirror)
                cv2.putText(image, 'L', (right_elbow_x + 15, right_elbow_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(image, 'R', (left_elbow_x + 15, left_elbow_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                
                # Check for violations
                right_violation = self.check_elbow_violation(right_elbow.x, width)
                left_violation = self.check_elbow_violation(left_elbow.x, width)
                
                if right_violation or left_violation:
                    cv2.putText(image, 'ELBOW VIOLATION!', (50, 50), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
            
            # Draw table edge line
            if self.table_edge_x is not None:
                cv2.line(image, (self.table_edge_x, 0), (self.table_edge_x, height), 
                        (0, 0, 255), 3)
                cv2.putText(image, 'Table Edge', (self.table_edge_x + 5, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Draw instructions
            if self.calibration_mode:
                cv2.putText(image, 'Click to set table edge line', (20, height - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            else:
                cv2.putText(image, 'Table edge set - try throwing motions!', (20, height - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Display coordinate info for debugging
            if results.pose_landmarks:
                cv2.putText(image, f'Visual left elbow: ({right_elbow_x}, {right_elbow_y})', 
                           (20, height - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(image, f'Visual right elbow: ({left_elbow_x}, {left_elbow_y})', 
                           (20, height - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Elbow Tracker', image)
            
            # Handle key presses
            key = cv2.waitKey(5) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.table_edge_x = None
                self.calibration_mode = True
                print("Table edge reset - click to set new position")
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    tracker = ElbowTracker()
    tracker.run()
