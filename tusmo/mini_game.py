import cv2
import mediapipe as mp
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import random
from tkinter import messagebox
import math

# ==== Partie Mediapipe et Tkinter ====
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)

root = tk.Tk()
root.title("Tusmo & Clavier Interactif")
root.geometry("1200x800")  # Taille de la fenêtre augmentée

# ==== Partie Tusmo (à gauche) ====
frame_tusmo = tk.Frame(root, width=600, height=600)
frame_tusmo.pack(side="left", fill="both", expand=True)

MOTS = ["PYTHON", "TUSMO", "CODAGE", "FENETRE", "BOUTON"]
MOT_A_TROUVER = random.choice(MOTS)
TENTATIVES_MAX = 6

class TusmoGame:
    def __init__(self, root):
        self.tentative = 0
        self.letters_found = [None] * len(MOT_A_TROUVER)
        
        self.label = tk.Label(frame_tusmo, text=f"Trouve le mot ({len(MOT_A_TROUVER)} lettres) :", font=("Arial", 12))
        self.label.pack(pady=5)
        
        self.grid_frame = tk.Frame(frame_tusmo)
        self.grid_frame.pack()
        self.cells = []
        for i in range(TENTATIVES_MAX):
            row = []
            for j in range(len(MOT_A_TROUVER)):
                entry = tk.Entry(self.grid_frame, width=4, font=("Arial", 12), justify='center')
                entry.grid(row=i, column=j, padx=3, pady=3)
                row.append(entry)
            self.cells.append(row)
        
        self.cells[0][0].insert(0, MOT_A_TROUVER[0])
        self.cells[0][0].config(state='disabled', disabledbackground='green', disabledforeground='white')
        self.letters_found[0] = MOT_A_TROUVER[0]
        
        self.button = tk.Button(frame_tusmo, text="Valider", command=self.valider_mot, font=("Arial", 12))
        self.button.pack(pady=5)

    def valider_mot(self):
        if self.tentative >= TENTATIVES_MAX:
            return
        
        mot_propose = "".join(cell.get().upper() for cell in self.cells[self.tentative])
        if len(mot_propose) != len(MOT_A_TROUVER):
            messagebox.showerror("Erreur", f"Le mot doit contenir {len(MOT_A_TROUVER)} lettres !")
            return
        
        for j, lettre in enumerate(mot_propose):
            if lettre == MOT_A_TROUVER[j]:
                self.cells[self.tentative][j].config(state='disabled', disabledbackground='green', disabledforeground='white')
                self.letters_found[j] = lettre
            elif lettre in MOT_A_TROUVER:
                self.cells[self.tentative][j].config(bg='yellow', fg='black')
            else:
                self.cells[self.tentative][j].config(bg='gray', fg='white')
        
        if mot_propose == MOT_A_TROUVER:
            messagebox.showinfo("Bravo !", "Félicitations, tu as trouvé le mot !")
            root.quit()
        
        self.tentative += 1
        if self.tentative < TENTATIVES_MAX:
            for j in range(len(MOT_A_TROUVER)):
                if self.letters_found[j]:
                    self.cells[self.tentative][j].insert(0, self.letters_found[j])
                    self.cells[self.tentative][j].config(state='disabled', disabledbackground='green', disabledforeground='white')
        
        if self.tentative >= TENTATIVES_MAX:
            messagebox.showinfo("Perdu", f"Le mot était : {MOT_A_TROUVER}")
            root.quit()

    def insert_letter(self, letter):
        if self.tentative >= TENTATIVES_MAX:
            return
        
        for j in range(len(MOT_A_TROUVER)):
            if self.cells[self.tentative][j].get() == "":
                self.cells[self.tentative][j].insert(0, letter)
                break

    def effacer_lettre(self):
        if self.tentative >= TENTATIVES_MAX:
            return
        
        for j in range(len(MOT_A_TROUVER) - 1, -1, -1):
            if self.cells[self.tentative][j].get() != "":
                self.cells[self.tentative][j].delete(0, tk.END)
                break

tusmo_game = TusmoGame(root)

# ==== Partie Clavier Interactif (à droite) ====
frame_keyboard = tk.Frame(root, width=600, height=600)
frame_keyboard.pack(side="right", fill="both", expand=True)

canvas = tk.Canvas(frame_keyboard, width=600, height=600, bg='white')
canvas.pack()

keys = [["A", "B", "C", "D", "E", "<--"],
        ["F", "G", "H", "I", "J"],
        ["K", "L", "M", "N", "O"],
        ["P", "Q", "R", "S", "T", "Ent"],
        ["U", "V", "W", "X", "Y", "Z"]]

key_size = 80
key_spacing = 10
start_x, start_y = 50, 50  # Position de départ du clavier

# Dictionnaire pour stocker les rectangles et les textes des touches
key_rectangles = {}
key_texts = {}

# Variable pour désactiver temporairement le clavier
keyboard_active = True

def draw_keyboard():
    global key_buttons
    key_buttons = {}
    for i, row in enumerate(keys):
        for j, key in enumerate(row):
            x1 = start_x + j * (key_size + key_spacing)
            y1 = start_y + i * (key_size + key_spacing)
            x2, y2 = x1 + key_size, y1 + key_size
            key_buttons[key] = (x1, y1, x2, y2)
            # Dessiner le rectangle de la touche
            rect = canvas.create_rectangle(x1, y1, x2, y2, fill='lightgray', outline='black')
            # Dessiner le texte de la touche
            text = canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=key, font=('Arial', 20))
            # Stocker les références pour pouvoir les modifier plus tard
            key_rectangles[key] = rect
            key_texts[key] = text

draw_keyboard()

cursor = canvas.create_oval(0, 0, 20, 20, fill='red')

def update_cursor(x, y):
    canvas.coords(cursor, x-10, y-10, x+10, y+10)

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def highlight_key(key):
    """Change la couleur de la touche lorsqu'elle est survolée."""
    canvas.itemconfig(key_rectangles[key], fill='orange')  # Couleur de survol
    canvas.itemconfig(key_texts[key], fill='black')  # Couleur du texte

def unhighlight_key(key):
    """Rétablit la couleur d'origine de la touche."""
    canvas.itemconfig(key_rectangles[key], fill='lightgray')  # Couleur d'origine
    canvas.itemconfig(key_texts[key], fill='black')  # Couleur du texte

def recognize_letter(key):
    """Insère la lettre dans le jeu Tusmo ou exécute une action spéciale."""
    global keyboard_active
    if not keyboard_active:  # Si le clavier est désactivé, ne rien faire
        return
    
    # Désactiver temporairement le clavier
    keyboard_active = False
    if key == "<--":
        tusmo_game.effacer_lettre()
    elif key == "Ent":
        tusmo_game.valider_mot()
    else:
        tusmo_game.insert_letter(key)
    
    # Réactiver le clavier après 3 secondes
    root.after(3000, reenable_keyboard)

def reenable_keyboard():
    """Réactive le clavier après 3 secondes."""
    global keyboard_active
    keyboard_active = True

def update_frame():
    """Met à jour la vidéo et détecte la main"""
    ret, frame = cap.read()
    if not ret:
        root.after(1, update_frame)
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

            # Calcul de la distance entre l'index et le majeur
            distance_index_middle = calculate_distance((index_x, index_y), (thumb_x, thumb_y))

            canvas.delete("cursor")
            canvas.create_oval(index_x - 5, index_y - 5, index_x + 5, index_y + 5, fill="red", tags="cursor")

            # Désélectionner toutes les touches
            for key in key_buttons:
                unhighlight_key(key)
            
            # Vérifier si le curseur est sur une touche
            for key, (x1, y1, x2, y2) in key_buttons.items():
                if x1 <= index_x <= x2 and y1 <= index_y <= y2:
                    highlight_key(key)  # Mettre en surbrillance la touche
                    if distance_index_middle < 20:  # Seuil pour considérer que l'index et le majeur se touchent
                        recognize_letter(key)  # Reconnaître la lettre ou exécuter l'action
                    break

    frame_rgb = Image.fromarray(frame_rgb)
    frame_rgb = ImageTk.PhotoImage(frame_rgb)
    label.config(image=frame_rgb)
    label.image = frame_rgb

    root.after(1, update_frame)

# ==== Partie Vidéo ====
label = tk.Label(root)
label.pack()

cap = cv2.VideoCapture(0)
update_frame()
root.mainloop()
cap.release()
cv2.destroyAllWindows()
