from ultralytics import YOLO
import cv2
import time
import mediapipe as mp
import numpy as np

def initialize_camera(camera_source=0):
    """
    Initialize the camera with the specified source and settings.
    """
    cap = cv2.VideoCapture(camera_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise Exception("Error: Cannot open the webcam")
    return cap

def display_pose_with_yolo(results, frame):
    if results and len(results) > 0:
        annotated_frame = results[0].plot()
        #print(results[0].plot)
    else:
        annotated_frame = frame.copy()
    return annotated_frame

def calculate_angle(a, b, c):
    """
    Calculate the angle between three points (in degrees).
    """
    a = np.array(a)  # First point
    b = np.array(b)  # Middle point (joint)
    c = np.array(c)  # Last point

    ab = a - b  # Vector from b to a
    cb = c - b  # Vector from b to c

    # Compute the cosine of the angle using dot product formula
    cosine_angle = np.dot(ab, cb) / (np.linalg.norm(ab) * np.linalg.norm(cb))
    
    # Convert from cosine to degrees
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))  
    return np.degrees(angle)

def main(camera_source=1):

    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

    cap = initialize_camera(camera_source)
    cv2.namedWindow('Webcam')
    prev_frame_time = 0

    font = cv2.FONT_HERSHEY_SIMPLEX
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read the frame from the webcam")
            break
        new_frame_time = time.time()
        
        frame_rgb  = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
     

        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * 640
                thumb_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * 480

                wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * 640
                wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y * 480

                vector_thumb = np.array([thumb_tip_x - wrist_x, thumb_tip_y - wrist_y])
                
                vector_up = np.array([0, -1])

                dot_product = np.dot(vector_thumb, vector_up)
                norm_thumb = np.linalg.norm(vector_thumb)
                norm_up = np.linalg.norm(vector_up)

                if norm_thumb != 0:  # Éviter division par zéro
                    angle = np.arccos(dot_product / (norm_thumb * norm_up)) * (180.0 / np.pi)
                    cv2.putText(frame, f'Angle: {angle:.2f}', (10, 40), font, 0.5, (255, 255, 0), 2)
                    
                    if angle < 60:  # Pouce vers le haut
                        cv2.putText(frame, 'Thumbs up', (10, 60), font, 0.5, (0, 255, 0), 2)
                        print("Thumbs up!")
                    elif angle > 110:  # Pouce vers le bas
                        cv2.putText(frame, 'Thumbs down', (10, 60), font, 0.5, (0, 0, 255), 2)
                        print("Thumbs down")
                    else:
                        cv2.putText(frame, 'Neutral thumbs', (10, 60), font, 0.5, (255, 0, 0), 2)
                        print("Position neutre")
                #frame = cv2.line(frame, (0 ,wrist_y), (640 , wrist_y), (0, 255, 0), 1)
        #FPS
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        cv2.putText(frame, f'FPS: {fps}', (10, 20), font, 0.5, (100, 255, 0), 2)

        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

    
if __name__ == '__main__':
    main(camera_source=1)