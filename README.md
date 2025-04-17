# 📱 Instagram Automation Manager

Ce projet permet de **gérer plusieurs téléphones Android** et de **planifier automatiquement des publications Instagram** (photos ou reels), en utilisant **Appium** et une interface React simple. Il a été conçu pour gérer **plusieurs comptes sur plusieurs appareils**, avec un système de file d’attente intelligent.

---

## ✨ Fonctionnalités principales

- 🔍 Scan automatique des téléphones Android connectés
- 🔁 Détection des comptes Instagram sur chaque téléphone
- 📅 Planification de publications avec contenu (photo/vidéo), texte, heure précise, et compte ciblé
- 🧠 Bascule automatique entre les comptes Instagram
- 📊 Tableau de bord d'administration :
  - Vue par appareil
  - Filtres par statut (`En attente`, `En cours`, `Succès`, `Échec`)
  - Affichage détaillé des publications

---

## 🧩 Structure du projet

```
project/
├── api/                 # Backend Flask (Python)
│   ├── api.py           # Serveur API principal
│   ├── database.py      # Requêtes SQL / SQLite
│   ├── worker.py        # Thread Appium pour chaque device
│   ├── scheduler.py     # Gestion de la file d’attente
│
├── frontend/            # Interface React (Vite + Tailwind + Shadcn)
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   └── AdminDashboard.tsx
│
├── uploads/             # Dossier des fichiers media temporaires
├── database.db          # Fichier SQLite
└── README.md
```

---

## 🧑‍💻 Installation complète (Windows 10)

### 1. Prérequis à installer

#### 🐍 Python 3.10+

- Télécharger ici : [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
- Cochez **"Add Python to PATH"** pendant l'installation

#### 📦 Node.js + npm

- Télécharger ici : [https://nodejs.org/](https://nodejs.org/)
- Vérifiez avec :  
  ```bash
  node -v
  npm -v
  ```

#### 📱 Appium + Android

- Installez Appium en global :  
  ```bash
  npm install -g appium
  ```
- Installez l’interface Appium Desktop si vous préférez une UI : [https://github.com/appium/appium-desktop/releases](https://github.com/appium/appium-desktop/releases)
- Installez `uiautomator2` sur chaque téléphone :
  ```bash
  adb devices
  appium driver install uiautomator2
  ```

---

### 2. Installation du projet

#### Backend (Python + Flask)

```bash
cd api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### Frontend (React)

```bash
cd frontend
npm install
```

---

## 🚀 Lancement de l'application

> 💡 **Attention : lancer Appium avant tout.**

### Étapes dans 3 terminaux différents :

#### 1. Lancer Appium
```bash
appium
```

#### 2. Lancer l’API (Flask)
```bash
cd api
venv\Scripts\activate
python api.py
```

#### 3. Lancer le Scheduler
```bash
cd api
venv\Scripts\activate
python scheduler.py
```

#### 4. Lancer le Frontend
```bash
cd frontend
npm run dev
```

---

## 📱 Gestion multi-téléphones

> Le système est conçu pour **gérer plusieurs téléphones Android connectés en même temps**.

Chaque téléphone scanné :
- sera ajouté à la base automatiquement
- ses comptes Instagram seront détectés
- une **file d’attente propre par appareil** sera créée

➡️ Le Scheduler enverra les tâches à chaque téléphone au moment prévu, sans collision.

---

## 🧪 Exemple avec 3 téléphones

- `emulator-5554` → comptes : `@john`, `@jane`, `@test1`
- `emulator-5556` → comptes : `@mike`, `@alex`, `@backup1`
- `emulator-5558` → comptes : `@agency1`, `@agency2`, `@agency3`

📋 Une tâche pour `@john` planifiée à 17h sur le `emulator-5554` va déclencher :
- Appium ouvre Instagram
- Bascule de compte
- Poste à l’heure prévue
- Met à jour le statut en `completed` ou `failed`

---

## 🛠 Déboguer à distance

Vous pouvez donner un accès à distance avec **AnyDesk** :
1. Télécharger depuis : [https://anydesk.com/fr](https://anydesk.com/fr)
2. Installer AnyDesk et configurer un mot de passe pour accès non surveillé
3. Envoyer votre ID + mot de passe au développeur

---

## 🔐 Recommandations

- Toujours laisser les téléphones déverrouillés
- Activer le **mode développeur + USB debugging**
- Laisser les câbles connectés en USB

---

## 📎 À venir

- Prise en charge des stories
- Logs par appareil
- Notification d’échec
- Gestion des files de plus de 600 posts/jour

---

## 🙋 Support

Si besoin d’assistance :
- 📧 contact : `tonemail@tondomaine.com`
- 💻 Support AnyDesk disponible