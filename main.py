from ultralytics import YOLO
import cv2
import time
import mediapipe as mp
import numpy as np

# Initialisation MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def initialize_camera(camera_source=0):
    cap = cv2.VideoCapture(camera_source)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        raise Exception("Error: Cannot open the webcam")
    return cap

def display_pose_with_yolo(results, frame):
    if results and len(results) > 0:
        return results[0].plot()
    return frame.copy()

def detect_thumb_gesture(hand_landmarks):
    # Récupère les points clés du pouce et du poignet
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
    
    # Conversion en coordonnées pixels
    thumb_tip = np.array([thumb_tip.x * 640, thumb_tip.y * 480])
    wrist = np.array([wrist.x * 640, wrist.y * 480])
    
    # Calcul du vecteur pouce
    vector_thumb = thumb_tip - wrist
    vector_up = np.array([0, -1])  # Vecteur vertical vers le haut
    
    # Calcul de l'angle
    cosine_angle = np.dot(vector_thumb, vector_up) / (np.linalg.norm(vector_thumb) * np.linalg.norm(vector_up))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0)) * (180 / np.pi)
    
    if angle < 60:
        return "up"
    elif angle > 110:
        return "down"
    return "neutral"

def detect_hand_translation(current_x, prev_x, threshold=5):
    if prev_x is None:
        return "immobile"
    delta = current_x - prev_x
    if delta < -threshold:
        return "right"
    if delta > threshold:
        return "left"
    return "immobile"

def main(camera_source=1):
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
    cap = initialize_camera(camera_source)
    prev_positions = {"left": None, "right": None}
    font = cv2.FONT_HERSHEY_SIMPLEX

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Traitement des mains
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if results.multi_hand_landmarks:
            for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Détection de la main (gauche/droite)
                handedness = results.multi_handedness[i].classification[0].label.lower()
                
                # Dessin des landmarks
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Détection geste pouce
                thumb_state = detect_thumb_gesture(hand_landmarks)
                cv2.putText(frame, f"{handedness} thumb: {thumb_state}", 
                          (10, 60 + 40*i), font, 0.7, (0,255,0), 2)
                
                # Détection mouvement
                wrist_x = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x * 640
                prev_x = prev_positions[handedness]
                move_state = detect_hand_translation(wrist_x, prev_x)
                prev_positions[handedness] = wrist_x
                
                cv2.putText(frame, f"{handedness} move: {move_state}", 
                          (10, 80 + 40*i), font, 0.7, (0,0,255), 2)

        # Affichage FPS
        cv2.imshow('Webcam', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main(camera_source=1)