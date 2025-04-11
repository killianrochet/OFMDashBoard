import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
import json
from datetime import datetime

class InstagramAutomationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instagram Automation Manager")
        self.db = Database()
        
        # Configuration de la fenêtre principale
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        
        # Style
        self.style = ttk.Style()
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Création du notebook pour les onglets
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Onglet Appareils
        self.devices_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.devices_frame, text="Appareils")
        self.setup_devices_tab()
        
        # Onglet Planification
        self.schedule_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.schedule_frame, text="Planification")
        self.setup_schedule_tab()
        
        # Barre de statut
        self.status_bar = ttk.Label(
            self.root,
            text="Prêt",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_devices_tab(self):
        # Frame pour l'ajout d'appareil
        add_frame = ttk.LabelFrame(
            self.devices_frame,
            text="Ajouter un appareil",
            padding="10"
        )
        add_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Champs pour l'ajout
        ttk.Label(add_frame, text="Nom:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(add_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="Modèle:").grid(row=0, column=2, padx=5, pady=5)
        self.model_entry = ttk.Entry(add_frame)
        self.model_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(
            add_frame,
            text="Ajouter",
            command=self.add_device
        ).grid(row=0, column=4, padx=5, pady=5)
        
        # Liste des appareils
        list_frame = ttk.LabelFrame(
            self.devices_frame,
            text="Appareils enregistrés",
            padding="10"
        )
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour les appareils
        self.tree = ttk.Treeview(
            list_frame,
            columns=("ID", "Nom", "Modèle", "Statut", "Date d'ajout"),
            show="headings"
        )
        
        # Configuration des colonnes
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nom", text="Nom")
        self.tree.heading("Modèle", text="Modèle")
        self.tree.heading("Statut", text="Statut")
        self.tree.heading("Date d'ajout", text="Date d'ajout")
        
        # Ajustement des colonnes
        self.tree.column("ID", width=50)
        self.tree.column("Nom", width=150)
        self.tree.column("Modèle", width=150)
        self.tree.column("Statut", width=100)
        self.tree.column("Date d'ajout", width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Placement des éléments
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Boutons d'action
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            button_frame,
            text="Rafraîchir",
            command=self.refresh_devices
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Supprimer",
            command=self.delete_device
        ).pack(side=tk.LEFT, padx=5)
        
        # Charger les appareils
        self.refresh_devices()
        
    def setup_schedule_tab(self):
        # Frame pour la planification
        schedule_frame = ttk.LabelFrame(
            self.schedule_frame,
            text="Planification des posts",
            padding="10"
        )
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Sélection de l'appareil
        ttk.Label(
            schedule_frame,
            text="Appareil:"
        ).grid(row=0, column=0, padx=5, pady=5)
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(
            schedule_frame,
            textvariable=self.device_var
        )
        self.device_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Heures de début et fin
        ttk.Label(
            schedule_frame,
            text="Début:"
        ).grid(row=1, column=0, padx=5, pady=5)
        self.start_entry = ttk.Entry(schedule_frame)
        self.start_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(
            schedule_frame,
            text="Fin:"
        ).grid(row=1, column=2, padx=5, pady=5)
        self.end_entry = ttk.Entry(schedule_frame)
        self.end_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # Intervalle
        ttk.Label(
            schedule_frame,
            text="Intervalle (minutes):"
        ).grid(row=2, column=0, padx=5, pady=5)
        self.interval_entry = ttk.Entry(schedule_frame)
        self.interval_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Bouton de planification
        ttk.Button(
            schedule_frame,
            text="Planifier",
            command=self.schedule_posts
        ).grid(row=3, column=0, columnspan=2, pady=20)
        
    def add_device(self):
        name = self.name_entry.get()
        model = self.model_entry.get()
        
        if not name or not model:
            messagebox.showerror(
                "Erreur",
                "Veuillez remplir tous les champs"
            )
            return
            
        try:
            self.db.add_device(name, model)
            self.refresh_devices()
            self.name_entry.delete(0, tk.END)
            self.model_entry.delete(0, tk.END)
            self.status_bar.config(text="Appareil ajouté avec succès")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
            
    def refresh_devices(self):
        # Effacer la liste actuelle
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Charger les appareils depuis la base de données
        devices = self.db.get_devices()
        for device in devices:
            self.tree.insert(
                "",
                tk.END,
                values=device
            )
            
    def delete_device(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Attention",
                "Veuillez sélectionner un appareil"
            )
            return
            
        if messagebox.askyesno(
            "Confirmation",
            "Voulez-vous vraiment supprimer cet appareil ?"
        ):
            for item in selected:
                device_id = self.tree.item(item)['values'][0]
                self.db.delete_device(device_id)
            self.refresh_devices()
            self.status_bar.config(text="Appareil supprimé avec succès")
            
    def schedule_posts(self):
        # TODO: Implémenter la planification des posts
        messagebox.showinfo(
            "Info",
            "Fonctionnalité en cours de développement"
        )

if __name__ == "__main__":
    root = tk.Tk()
    app = InstagramAutomationApp(root)
    root.mainloop()