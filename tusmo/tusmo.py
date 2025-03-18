import tkinter as tk
from tkinter import messagebox
import random

# Liste de mots possibles (à compléter ou charger depuis un fichier)
MOTS = ["PYTHON", "TUSMO", "CODAGE", "FENETRE", "BOUTON"]
MOT_A_TROUVER = random.choice(MOTS)
TENTATIVES_MAX = 6

class TusmoGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Tusmo - Jeu de mots")
        self.tentative = 0
        self.letters_found = [None] * len(MOT_A_TROUVER)  # Stocke les lettres trouvées

        self.label = tk.Label(root, text=f"Trouve le mot ({len(MOT_A_TROUVER)} lettres) :", font=("Arial", 14))
        self.label.pack(pady=10)

        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack()
        self.cells = []
        for i in range(TENTATIVES_MAX):
            row = []
            for j in range(len(MOT_A_TROUVER)):
                entry = tk.Entry(self.grid_frame, width=4, font=("Arial", 14), justify='center')
                entry.grid(row=i, column=j, padx=5, pady=5)
                entry.bind("<KeyRelease>", lambda event, row=i, col=j: self.move_to_next(event, row, col))
                row.append(entry)
            self.cells.append(row)
        
        # Afficher la première lettre dès le début
        self.cells[0][0].insert(0, MOT_A_TROUVER[0])
        self.cells[0][0].config(state='disabled', disabledbackground='green', disabledforeground='white')
        self.letters_found[0] = MOT_A_TROUVER[0]
        
        self.button = tk.Button(root, text="Valider", command=self.valider_mot, font=("Arial", 14))
        self.button.pack(pady=10)

    def move_to_next(self, event, row, col):
        if event.keysym.isalpha() and col < len(MOT_A_TROUVER) - 1:
            self.cells[row][col + 1].focus_set()

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
                self.letters_found[j] = lettre  # Mémoriser la lettre trouvée
            elif lettre in MOT_A_TROUVER:
                self.cells[self.tentative][j].config(bg='yellow', fg='black')
            else:
                self.cells[self.tentative][j].config(bg='gray', fg='white')
        
        if mot_propose == MOT_A_TROUVER:
            messagebox.showinfo("Bravo !", "Félicitations, tu as trouvé le mot !")
            self.root.quit()
        
        self.tentative += 1
        if self.tentative < TENTATIVES_MAX:
            for j in range(len(MOT_A_TROUVER)):
                if self.letters_found[j]:
                    self.cells[self.tentative][j].insert(0, self.letters_found[j])
                    self.cells[self.tentative][j].config(state='disabled', disabledbackground='green', disabledforeground='white')

        if self.tentative >= TENTATIVES_MAX:
            messagebox.showinfo("Perdu", f"Le mot était : {MOT_A_TROUVER}")
            self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    game = TusmoGame(root)
    root.mainloop()
