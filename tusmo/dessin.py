import cv2
import mediapipe as mp
import math
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw, ImageOps, ImageFilter
import pytesseract  # OCR pour la reconnaissance de lettres

# Définis le chemin de Tesseract (à adapter selon ton installation)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Initialisation de Mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# Fenêtre Tkinter
root = tk.Tk()
root.title("Reconnaissance de lettres dessinées")

canvas_width, canvas_height = 640, 480
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Champ d'entrée pour stocker la lettre reconnue
entry = tk.Entry(root, font=("Arial", 20))
entry.pack()

# Ajout d'un Label pour afficher la lettre reconnue
letter_display_label = tk.Label(root, font=("Arial", 30))
letter_display_label.pack()

# Capture vidéo
cap = cv2.VideoCapture(0)

drawing = False
previous_point = None
image_pil = Image.new("RGB", (canvas_width, canvas_height), "white")
draw = ImageDraw.Draw(image_pil)

def clear_canvas():
    """Efface le dessin après 3 secondes"""
    global image_pil, draw
    image_pil = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(image_pil)
    canvas.delete("all")

def calculate_distance(p1, p2):
    """Calcule la distance entre deux points"""
    x1, y1 = p1
    x2, y2 = p2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def reset_button(is_button_pressed):
    """Réinitialise l'état du bouton après 5 secondes"""
    return False  # Permet à nouveau de cliquer

def recognize_letter():
    """Utilise Tesseract pour reconnaître la lettre avec un meilleur prétraitement"""
    global image_pil, draw

    # Convertir l'image en niveaux de gris et appliquer un flou pour réduire les artefacts
    image_pil = image_pil.convert("L")  # Grayscale
    image_pil = image_pil.filter(ImageFilter.GaussianBlur(1))  # Appliquer un flou

    # Binarisation améliorée (seuillage dynamique pour mieux isoler les lettres)
    image_pil = ImageOps.invert(image_pil)  # Inverser les couleurs (fond noir, écriture blanche)
    image_pil = image_pil.point(lambda x: 0 if x < 180 else 255, '1')  # Seuillage

    # OCR avec Tesseract
    recognized_text = pytesseract.image_to_string(image_pil, config='--psm 10').strip()[:1]

    # Afficher la lettre reconnue dans l'entrée Tkinter
    entry.delete(0, tk.END)
    entry.insert(0, recognized_text)

    # Effacement du dessin après 3 secondes
    root.after(3000, clear_canvas)

def update_frame():
    """Met à jour la vidéo et détecte la main"""
    global drawing, previous_point, image_pil, draw

    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)  # Effet miroir
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            thumb_tip = hand_landmarks.landmark[4]  
            index_tip = hand_landmarks.landmark[8]  
            middle_tip = hand_landmarks.landmark[12]  # Majeur

            h, w, _ = frame.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)
            middle_x, middle_y = int(middle_tip.x * w), int(middle_tip.y * h)

            # Calcul de la distance entre l'index et le majeur
            distance_index_middle = calculate_distance((index_x, index_y), (middle_x, middle_y))

            canvas.delete("cursor")
            canvas.create_oval(index_x - 5, index_y - 5, index_x + 5, index_y + 5, fill="red", tags="cursor")

            if distance_index_middle < 20:  # Seuil pour considérer que l'index et le majeur se touchent
                is_button_pressed = True
                recognize_letter()  # Appel à la fonction pour reconnaître la lettre
                root.after(5000, reset_button(is_button_pressed))
                
            # Calcul de la distance entre le pouce et l'index pour dessiner
            distance = calculate_distance((thumb_x, thumb_y), (index_x, index_y))

            if distance < 40:  # Seuil pour dessiner
                if drawing and previous_point:
                    canvas.create_line(previous_point[0], previous_point[1], index_x, index_y, fill="black", width=5)
                    draw.line([previous_point, (index_x, index_y)], fill="black", width=5)

                previous_point = (index_x, index_y)
                drawing = True
            else:
                drawing = False  # Fin du tracé

    frame_rgb = Image.fromarray(frame)
    frame_rgb = ImageTk.PhotoImage(frame_rgb)
    label.config(image=frame_rgb)
    label.image = frame_rgb

    root.after(1, update_frame)


# Ajouter un bouton pour reconnaître la lettre
btn_recognize = tk.Button(root, text="Reconnaître la lettre", command=recognize_letter)
btn_recognize.pack()

label = tk.Label(root)
label.pack()

update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()
